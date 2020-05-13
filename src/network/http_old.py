"""
src/network/http_old.py
"""
import asyncore
import socket
import time

requestCount = 0
parallel = 50
duration = 60


class HTTPClient(asyncore.dispatcher):
    """An asyncore dispatcher"""
    port = 12345

    def __init__(self, host, path, connect=True):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self)
        if connect:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((host, HTTPClient.port))
        self.buffer = 'GET %s HTTP/1.0\r\n\r\n' % path

    def handle_close(self):
        # pylint: disable=global-statement
        global requestCount
        requestCount += 1
        self.close()

    def handle_read(self):
        # print self.recv(8192)
        self.recv(8192)

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]


if __name__ == "__main__":
    # initial fill
    for i in range(parallel):
        HTTPClient('127.0.0.1', '/')
    start = time.time()
    while time.time() - start < duration:
        if len(asyncore.socket_map) < parallel:
            for i in range(parallel - len(asyncore.socket_map)):
                HTTPClient('127.0.0.1', '/')
        print("Active connections: %i" % (len(asyncore.socket_map)))
        asyncore.loop(count=len(asyncore.socket_map) / 2)
        if requestCount % 100 == 0:
            print("Processed %i total messages" % (requestCount))
