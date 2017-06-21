"""
SSL/TLS negotiation.
"""

import os
import socket
import ssl
import sys

from debug import logger
from network.advanceddispatcher import AdvancedDispatcher
import network.asyncore_pollchoose as asyncore
import paths
import protocol

_DISCONNECTED_SSL = frozenset((ssl.SSL_ERROR_EOF,))

class TLSDispatcher(AdvancedDispatcher):
    def __init__(self, address=None, sock=None,
                 certfile=None, keyfile=None, server_side=False, ciphers=protocol.sslProtocolCiphers):
        self.want_read = self.want_write = True
        if certfile is None:
            self.certfile = os.path.join(paths.codePath(), 'sslkeys', 'cert.pem')
        else:
            self.certfile = certfile
        if keyfile is None:
            self.keyfile = os.path.join(paths.codePath(), 'sslkeys', 'key.pem')
        else:
            self.keyfile = keyfile
        self.server_side = server_side
        self.ciphers = ciphers
        self.tlsStarted = False
        self.tlsDone = False
        self.isSSL = False

    def state_tls_init(self):
        self.isSSL = True
        self.tlsStarted = True
        # Once the connection has been established, it's safe to wrap the
        # socket.
        if sys.version_info >= (2,7,9):
            context = ssl.create_default_context(purpose = ssl.Purpose.SERVER_AUTH if self.server_side else ssl.Purpose.CLIENT_AUTH)
            context.set_ciphers(self.ciphers)
            context.set_ecdh_curve("secp256k1")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # also exclude TLSv1 and TLSv1.1 in the future
            context.options = ssl.OP_ALL | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_SINGLE_ECDH_USE | ssl.OP_CIPHER_SERVER_PREFERENCE
            self.sslSocket = context.wrap_socket(self.socket, server_side = self.server_side, do_handshake_on_connect=False)
        else:
            self.sslSocket = ssl.wrap_socket(self.socket,
                                         server_side=self.server_side,
                                         ssl_version=protocol.sslProtocolVersion,
                                         certfile=self.certfile,
                                         keyfile=self.keyfile,
                                         ciphers=self.ciphers,
                                         do_handshake_on_connect=False)
        self.sslSocket.setblocking(0)
        self.want_read = self.want_write = True
        self.set_state("bm_header")
#        if hasattr(self.socket, "context"):
#            self.socket.context.set_ecdh_curve("secp256k1")

    def writable(self):
        try:
            if self.tlsStarted and not self.tlsDone and len(self.write_buf) == 0 and self.writeQueue.empty():
                #print "tls writable, %r" % (self.want_write)
                return self.want_write
            else:
                return AdvancedDispatcher.writable(self)
        except AttributeError:
            return AdvancedDispatcher.writable(self)

    def readable(self):
        try:
            if self.tlsStarted and not self.tlsDone and len(self.write_buf) == 0 and self.writeQueue.empty():
                #print "tls readable, %r" % (self.want_read)
                return self.want_read
            else:
                return AdvancedDispatcher.readable(self)
        except AttributeError:
            return AdvancedDispatcher.readable(self)

    def handle_read(self):
        try:
            # wait for write buffer flush
            if self.tlsStarted and not self.tlsDone and len(self.write_buf) == 0 and self.writeQueue.empty():
                #print "handshaking (read)"
                self.tls_handshake()
            else:
                #print "not handshaking (read)"
                return AdvancedDispatcher.handle_read(self)
        except AttributeError:
            return AdvancedDispatcher.handle_read(self)
        except ssl.SSLError as err:
            if err.errno == ssl.SSL_ERROR_WANT_READ:
                return
            elif err.errno in _DISCONNECTED_SSL:
                self.handle_close()
                return
            else:
                raise

    def handle_write(self):
        try:
            # wait for write buffer flush
            if self.tlsStarted and not self.tlsDone and len(self.write_buf) == 0 and self.writeQueue.empty():
                #print "handshaking (write)"
                self.tls_handshake()
            else:
                #print "not handshaking (write)"
                return AdvancedDispatcher.handle_write(self)
        except AttributeError:
            return AdvancedDispatcher.handle_read(self)
        except ssl.SSLError as err:
            if err.errno == ssl.SSL_ERROR_WANT_WRITE:
                return 0
            elif err.errno in _DISCONNECTED_SSL:
                self.handle_close()
                return 0
            else:
                raise

    def tls_handshake(self):
        # wait for flush
        if len(self.write_buf) > 0:
            return False
        # Perform the handshake.
        try:
            #print "handshaking (internal)"
            self.sslSocket.do_handshake()
        except ssl.SSLError, err:
            #print "%s:%i: handshake fail" % (self.destination.host, self.destination.port)
            self.want_read = self.want_write = False
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                #print "want read"
                self.want_read = True
            if err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                #print "want write"
                self.want_write = True
            if not (self.want_write or self.want_read):
                raise
        else:
            logger.debug("%s:%i: TLS handshake success%s", self.destination.host, self.destination.port, ", TLS protocol version: %s" % (self.sslSocket.version()) if sys.version_info >= (2, 7, 9) else "")
            # The handshake has completed, so remove this channel and...
            self.del_channel()
            self.set_socket(self.sslSocket)
            self.tlsDone = True
            self.set_state("bm_header")
            self.set_connection_fully_established()
        return False
