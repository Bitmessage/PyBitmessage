import asyncore

from http import HTTPClient
import paths
from tls import TLSHandshake



class HTTPSClient(HTTPClient, TLSHandshake):
    def __init__(self, host, path):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self)
        self.tlsDone = False
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
