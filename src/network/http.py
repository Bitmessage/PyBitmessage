import socket

from advanceddispatcher import AdvancedDispatcher
import asyncore_pollchoose as asyncore
from network.proxy import ProxyError
from socks5 import Socks5Connection, Socks5Resolver
from socks4a import Socks4aConnection, Socks4aResolver


class HttpError(ProxyError):
    pass


class HttpConnection(AdvancedDispatcher):
    def __init__(self, host, path="/"):     # pylint: disable=redefined-outer-name
        AdvancedDispatcher.__init__(self)
        self.path = path
        self.destination = (host, 80)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(self.destination)
        print "connecting in background to %s:%i" % (self.destination[0], self.destination[1])

    def state_init(self):
        self.append_write_buf(
            "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (
                self.path, self.destination[0]))
        print "Sending %ib" % (len(self.write_buf))
        self.set_state("http_request_sent", 0)
        return False

    def state_http_request_sent(self):
        if self.read_buf:
            print "Received %ib" % (len(self.read_buf))
            self.read_buf = b""
        if not self.connected:
            self.set_state("close", 0)
        return False


class Socks5HttpConnection(Socks5Connection, HttpConnection):
    def __init__(self, host, path="/"):     # pylint: disable=super-init-not-called, redefined-outer-name
        self.path = path
        Socks5Connection.__init__(self, address=(host, 80))

    def state_socks_handshake_done(self):
        HttpConnection.state_init(self)
        return False


class Socks4aHttpConnection(Socks4aConnection, HttpConnection):
    def __init__(self, host, path="/"):     # pylint: disable=super-init-not-called, redefined-outer-name
        Socks4aConnection.__init__(self, address=(host, 80))
        self.path = path

    def state_socks_handshake_done(self):
        HttpConnection.state_init(self)
        return False


if __name__ == "__main__":
    # initial fill
    for host in ("bootstrap8080.bitmessage.org", "bootstrap8444.bitmessage.org"):
        proxy = Socks5Resolver(host=host)
        while asyncore.socket_map:
            print "loop %s, len %i" % (proxy.state, len(asyncore.socket_map))
            asyncore.loop(timeout=1, count=1)
        proxy.resolved()

        proxy = Socks4aResolver(host=host)
        while asyncore.socket_map:
            print "loop %s, len %i" % (proxy.state, len(asyncore.socket_map))
            asyncore.loop(timeout=1, count=1)
        proxy.resolved()

    for host in ("bitmessage.org",):
        direct = HttpConnection(host)
        while asyncore.socket_map:
            # print "loop, state = %s" % (direct.state)
            asyncore.loop(timeout=1, count=1)

        proxy = Socks5HttpConnection(host)
        while asyncore.socket_map:
            # print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=1, count=1)

        proxy = Socks4aHttpConnection(host)
        while asyncore.socket_map:
            # print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=1, count=1)
