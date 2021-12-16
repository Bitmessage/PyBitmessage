"""
SSL/TLS negotiation.
"""
import logging
import os
import socket
import ssl
import sys

import network.asyncore_pollchoose as asyncore
import paths
from network.advanceddispatcher import AdvancedDispatcher
from queues import receiveDataQueue

logger = logging.getLogger('default')

_DISCONNECTED_SSL = frozenset((ssl.SSL_ERROR_EOF,))

if sys.version_info >= (2, 7, 13):
    # this means TLSv1 or higher
    # in the future change to
    # ssl.PROTOCOL_TLS1.2
    sslProtocolVersion = ssl.PROTOCOL_TLS  # pylint: disable=no-member
elif sys.version_info >= (2, 7, 9):
    # this means any SSL/TLS.
    # SSLv2 and 3 are excluded with an option after context is created
    sslProtocolVersion = ssl.PROTOCOL_SSLv23
else:
    # this means TLSv1, there is no way to set "TLSv1 or higher"
    # or "TLSv1.2" in < 2.7.9
    sslProtocolVersion = ssl.PROTOCOL_TLSv1


# ciphers
if (
    ssl.OPENSSL_VERSION_NUMBER >= 0x10100000
    and not ssl.OPENSSL_VERSION.startswith(b"LibreSSL")
):
    sslProtocolCiphers = "AECDH-AES256-SHA@SECLEVEL=0"
else:
    sslProtocolCiphers = "AECDH-AES256-SHA"


class TLSDispatcher(AdvancedDispatcher):
    """TLS functionality for classes derived from AdvancedDispatcher"""
    # pylint: disable=too-many-instance-attributes, too-many-arguments
    # pylint: disable=super-init-not-called
    def __init__(self, _=None, sock=None, certfile=None, keyfile=None,
                 server_side=False, ciphers=sslProtocolCiphers):
        self.want_read = self.want_write = True
        self.certfile = certfile or os.path.join(
            paths.codePath(), 'sslkeys', 'cert.pem')
        self.keyfile = keyfile or os.path.join(
            paths.codePath(), 'sslkeys', 'key.pem')
        self.server_side = server_side
        self.ciphers = ciphers
        self.tlsStarted = False
        self.tlsDone = False
        self.tlsVersion = "N/A"
        self.isSSL = False

    def state_tls_init(self):
        """Prepare sockets for TLS handshake"""
        self.isSSL = True
        self.tlsStarted = True
        # Once the connection has been established,
        # it's safe to wrap the socket.
        if sys.version_info >= (2, 7, 9):
            context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH
                if self.server_side else ssl.Purpose.CLIENT_AUTH)
            context.set_ciphers(self.ciphers)
            context.set_ecdh_curve("secp256k1")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # also exclude TLSv1 and TLSv1.1 in the future
            context.options = ssl.OP_ALL | ssl.OP_NO_SSLv2 |\
                ssl.OP_NO_SSLv3 | ssl.OP_SINGLE_ECDH_USE |\
                ssl.OP_CIPHER_SERVER_PREFERENCE
            self.sslSocket = context.wrap_socket(
                self.socket, server_side=self.server_side,
                do_handshake_on_connect=False)
        else:
            self.sslSocket = ssl.wrap_socket(
                self.socket, server_side=self.server_side,
                ssl_version=sslProtocolVersion,
                certfile=self.certfile, keyfile=self.keyfile,
                ciphers=self.ciphers, do_handshake_on_connect=False)
        self.sslSocket.setblocking(0)
        self.want_read = self.want_write = True
        self.set_state("tls_handshake")
        return False

    @staticmethod
    def state_tls_handshake():
        """
        Do nothing while TLS handshake is pending, as during this phase
        we need to react to callbacks instead
        """
        return False

    def writable(self):
        """Handle writable checks for TLS-enabled sockets"""
        try:
            if self.tlsStarted and not self.tlsDone and not self.write_buf:
                return self.want_write
        except AttributeError:
            pass
        return AdvancedDispatcher.writable(self)

    def readable(self):
        """Handle readable check for TLS-enabled sockets"""
        try:
            # during TLS handshake, and after flushing write buffer,
            # return status of last handshake attempt
            if self.tlsStarted and not self.tlsDone and not self.write_buf:
                logger.debug('tls readable, %r', self.want_read)
                return self.want_read
            # prior to TLS handshake,
            # receiveDataThread should emulate synchronous behaviour
            if not self.fullyEstablished and (
                    self.expectBytes == 0 or not self.write_buf_empty()):
                return False
        except AttributeError:
            pass
        return AdvancedDispatcher.readable(self)

    def handle_read(self):
        """
        Handle reads for sockets during TLS handshake. Requires special
        treatment as during the handshake, buffers must remain empty
        and normal reads must be ignored.
        """
        try:
            # wait for write buffer flush
            if self.tlsStarted and not self.tlsDone and not self.write_buf:
                self.tls_handshake()
            else:
                AdvancedDispatcher.handle_read(self)
        except AttributeError:
            AdvancedDispatcher.handle_read(self)
        except ssl.SSLError as err:
            if err.errno == ssl.SSL_ERROR_WANT_READ:
                return
            if err.errno not in _DISCONNECTED_SSL:
                logger.info("SSL Error: %s", err)
            self.close_reason = "SSL Error in handle_read"
            self.handle_close()

    def handle_write(self):
        """
        Handle writes for sockets during TLS handshake. Requires special
        treatment as during the handshake, buffers must remain empty
        and normal writes must be ignored.
        """
        try:
            # wait for write buffer flush
            if self.tlsStarted and not self.tlsDone and not self.write_buf:
                self.tls_handshake()
            else:
                AdvancedDispatcher.handle_write(self)
        except AttributeError:
            AdvancedDispatcher.handle_write(self)
        except ssl.SSLError as err:
            if err.errno == ssl.SSL_ERROR_WANT_WRITE:
                return
            if err.errno not in _DISCONNECTED_SSL:
                logger.info("SSL Error: %s", err)
            self.close_reason = "SSL Error in handle_write"
            self.handle_close()

    def tls_handshake(self):
        """Perform TLS handshake and handle its stages"""
        # wait for flush
        if self.write_buf:
            return False
        # Perform the handshake.
        try:
            logger.debug("handshaking (internal)")
            self.sslSocket.do_handshake()
        except ssl.SSLError as err:
            self.close_reason = "SSL Error in tls_handshake"
            logger.info("%s:%i: handshake fail", *self.destination)
            self.want_read = self.want_write = False
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                logger.debug("want read")
                self.want_read = True
            if err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                logger.debug("want write")
                self.want_write = True
            if not (self.want_write or self.want_read):
                raise
        except socket.error as err:
            # pylint: disable=protected-access
            if err.errno in asyncore._DISCONNECTED:
                self.close_reason = "socket.error in tls_handshake"
                self.handle_close()
            else:
                raise
        else:
            if sys.version_info >= (2, 7, 9):
                self.tlsVersion = self.sslSocket.version()
                logger.debug(
                    '%s:%i: TLS handshake success, TLS protocol version: %s',
                    self.destination.host, self.destination.port,
                    self.tlsVersion)
            else:
                self.tlsVersion = "TLSv1"
                logger.debug(
                    '%s:%i: TLS handshake success',
                    self.destination.host, self.destination.port)
            # The handshake has completed, so remove this channel and...
            self.del_channel()
            self.set_socket(self.sslSocket)
            self.tlsDone = True

            self.bm_proto_reset()
            self.set_state("connection_fully_established")
            receiveDataQueue.put(self.destination)
        return False
