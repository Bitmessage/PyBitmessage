"""
src/network/httpd.py
=======================
"""
import asyncore
import socket

from tls import TLSHandshake


class HTTPRequestHandler(asyncore.dispatcher):
    """Handling HTTP request"""
    response = """HTTP/1.0 200 OK\r
    Date: Sun, 23 Oct 2016 18:02:00 GMT\r
    Content-Type: text/html; charset=UTF-8\r
    Content-Encoding: UTF-8\r
    Content-Length: 136\r
    Last-Modified: Wed, 08 Jan 2003 23:11:55 GMT\r
    Server: Apache/1.3.3.7 (Unix) (Red-Hat/Linux)\r
    ETag: "3f80f-1b6-3e1cb03b"\r
    Accept-Ranges: bytes\r
    Connection: close\r
    \r
    <html>
    <head>
      <title>An Example Page</title>
    </head>
      <body>
         Hello World, this is a very simple HTML document.
      </body>
    </html>"""

    def __init__(self, sock):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self, sock)
        self.inbuf = ""
        self.ready = True
        self.busy = False
        self.respos = 0

    def handle_close(self):
        self.close()

    def readable(self):
        return self.ready

    def writable(self):
        return self.busy

    def handle_read(self):
        self.inbuf += self.recv(8192)
        if self.inbuf[-4:] == "\r\n\r\n":
            self.busy = True
            self.ready = False
            self.inbuf = ""
        elif self.inbuf == "":
            pass

    def handle_write(self):
        if self.busy and self.respos < len(HTTPRequestHandler.response):
            written = 0
            written = self.send(HTTPRequestHandler.response[self.respos:65536])
            self.respos += written
        elif self.busy:
            self.busy = False
            self.ready = True
            self.close()


class HTTPSRequestHandler(HTTPRequestHandler, TLSHandshake):
    """Handling HTTPS request"""
    def __init__(self, sock):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self, sock)        # pylint: disable=non-parent-init-called
        # self.tlsDone = False
        TLSHandshake.__init__(
            self,
            sock=sock,
            certfile='/home/shurdeek/src/PyBitmessage/src/sslkeys/cert.pem',
            keyfile='/home/shurdeek/src/PyBitmessage/src/sslkeys/key.pem',
            server_side=True)
        HTTPRequestHandler.__init__(self, sock)

    def handle_connect(self):
        TLSHandshake.handle_connect(self)

    def handle_close(self):
        if self.tlsDone:
            HTTPRequestHandler.close(self)
        else:
            TLSHandshake.close(self)

    def readable(self):
        if self.tlsDone:
            return HTTPRequestHandler.readable(self)
        return TLSHandshake.readable(self)

    def handle_read(self):
        if self.tlsDone:
            HTTPRequestHandler.handle_read(self)
        else:
            TLSHandshake.handle_read(self)

    def writable(self):
        if self.tlsDone:
            return HTTPRequestHandler.writable(self)
        return TLSHandshake.writable(self)

    def handle_write(self):
        if self.tlsDone:
            HTTPRequestHandler.handle_write(self)
        else:
            TLSHandshake.handle_write(self)


class HTTPServer(asyncore.dispatcher):
    """Handling HTTP Server"""
    port = 12345

    def __init__(self):
        if not hasattr(self, '_map'):
            asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('127.0.0.1', HTTPServer.port))
        self.connections = 0
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            # print 'Incoming connection from %s' % repr(addr)
            self.connections += 1
            # if self.connections % 1000 == 0:
            #       print "Processed %i connections, active %i" % (self.connections, len(asyncore.socket_map))
            HTTPRequestHandler(sock)


class HTTPSServer(HTTPServer):
    """Handling HTTPS Server"""
    port = 12345

    def __init__(self):
        if not hasattr(self, '_map'):
            HTTPServer.__init__(self)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            # print 'Incoming connection from %s' % repr(addr)
            self.connections += 1
            # if self.connections % 1000 == 0:
            #       print "Processed %i connections, active %i" % (self.connections, len(asyncore.socket_map))
            HTTPSRequestHandler(sock)


if __name__ == "__main__":
    client = HTTPSServer()
    asyncore.loop()
