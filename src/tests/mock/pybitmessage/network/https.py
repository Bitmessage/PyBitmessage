import asyncore

from http import HTTPClient
from tls import TLSHandshake

"""
self.sslSock = ssl.wrap_socket(
    self.sock,
    keyfile=os.path.join(paths.codePath(), 'sslkeys', 'key.pem'),
    certfile=os.path.join(paths.codePath(), 'sslkeys', 'cert.pem'),
    server_side=not self.initiatedConnection,
    ssl_version=ssl.PROTOCOL_TLSv1,
    do_handshake_on_connect=False,
    ciphers='AECDH-AES256-SHA')
"""


class HTTPSClient(HTTPClient, TLSHandshake):
    def __init__(self, host, path):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self)
        self.tlsDone = False
        """
        TLSHandshake.__init__(
            self,
            address=(host, 443),
            certfile='/home/shurdeek/src/PyBitmessage/sslsrc/keys/cert.pem',
            keyfile='/home/shurdeek/src/PyBitmessage/src/sslkeys/key.pem',
            server_side=False,
            ciphers='AECDH-AES256-SHA')
        """
        HTTPClient.__init__(self, host, path, connect=False)
        TLSHandshake.__init__(self, address=(host, 443), server_side=False)

    def handle_connect(self):
        TLSHandshake.handle_connect(self)

    def handle_close(self):
        if self.tlsDone:
            HTTPClient.close(self)
        else:
            TLSHandshake.close(self)

    def readable(self):
        if self.tlsDone:
            return HTTPClient.readable(self)
        else:
            return TLSHandshake.readable(self)

    def handle_read(self):
        if self.tlsDone:
            HTTPClient.handle_read(self)
        else:
            TLSHandshake.handle_read(self)

    def writable(self):
        if self.tlsDone:
            return HTTPClient.writable(self)
        else:
            return TLSHandshake.writable(self)

    def handle_write(self):
        if self.tlsDone:
            HTTPClient.handle_write(self)
        else:
            TLSHandshake.handle_write(self)


if __name__ == "__main__":
    client = HTTPSClient('anarchy.economicsofbitcoin.com', '/')
    asyncore.loop()
