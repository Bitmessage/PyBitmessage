"""
SSL/TLS negotiation.
"""

import asyncore
import socket
import ssl
import sys

import protocol

class TLSHandshake(asyncore.dispatcher):
    """
    Negotiates a SSL/TLS connection before handing itself spawning a
    dispatcher that can deal with the overlying protocol as soon as the
    handshake has been completed.

    `handoff` is a function/method called when the handshake has completed.
    `address` is a tuple consisting of hostname/address and port to connect to
    if nothing is passed in `sock`, which can take an already-connected socket.
    `certfile` can take a path to a certificate bundle, and `server_side`
    indicates whether the socket is intended to be a server-side or client-side
    socket.
    """

    def __init__(self, address=None, sock=None,
                 certfile=None, keyfile=None, server_side=False, ciphers=None, init_parent=True):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self, sock)
        self.want_read = self.want_write = True
        self.certfile = certfile
        self.keyfile = keyfile
        self.server_side = server_side
        self.ciphers = ciphers
        self.tlsDone = False
        if sock is None:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
#            logger.info('Connecting to %s%d', address[0], address[1])
            self.connect(address)
        elif self.connected:
            # Initiate the handshake for an already-connected socket.
            self.handle_connect()

    def handle_connect(self):
        # Once the connection has been established, it's safe to wrap the
        # socket.
        if sys.version_info >= (2,7,9):
            context = ssl.create_default_context(purpose = ssl.Purpose.SERVER_AUTH if self.server_side else ssl.Purpose.CLIENT_AUTH)
            context.set_ciphers(self.ciphers)
            # context.set_ecdh_curve("secp256k1")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # also exclude TLSv1 and TLSv1.1 in the future
            context.options |= ssl.OP_NOSSLv2 | ssl.OP_NOSSLv3
            self.sslSock = context.wrap_socket(self.sock, server_side = self.server_side, do_handshake_on_connect=False)
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
        return self.want_write

    def readable(self):
        return self.want_read

    def handle_read(self):
        if not self.tlsDone:
            self._handshake()

    def handle_write(self):
        if not self.tlsDone:
            self._handshake()

    def _handshake(self):
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
