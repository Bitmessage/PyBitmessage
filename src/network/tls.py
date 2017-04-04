"""
SSL/TLS negotiation.
"""

from network.advanceddispatcher import AdvancedDispatcher
import network.asyncore_pollchoose as asyncore
import socket
import ssl
import sys

import protocol

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
            self.sslSocket = context.wrap_socket(self.sock, server_side = self.server_side, do_handshake_on_connect=False)
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
#        if hasattr(self.socket, "context"):
#            self.socket.context.set_ecdh_curve("secp256k1")

    def writable(self):
        if self.tlsStarted and not self.tlsDone:
            return self.want_write
        else:
            return AdvancedDispacher.writable(self)

    def readable(self):
        if self.tlsStarted and not self.tlsDone:
            return self.want_read
        else:
            return AdvancedDispacher.readable(self)

    def handle_read(self):
        if self.tlsStarted and not self.tlsDone:
            self._handshake()
        else:
            return AdvancedDispacher.handle_read(self)

    def handle_write(self):
        if self.tlsStarted and not not self.tlsDone:
            self._handshake()
        else:
            return AdvancedDispacher.handle_write(self)

    def state_tls_handshake(self):
        """
        Perform the handshake.
        """
        try:
            self.sslSocket.do_handshake()
        except ssl.SSLError, err:
            self.want_read = self.want_write = False
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                self.want_read = True
            elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self.want_write = True
            else:
                raise
        else:
            # The handshake has completed, so remove this channel and...
            self.del_channel()
            self.set_socket(self.sslSocket)
            self.tlsDone = True
