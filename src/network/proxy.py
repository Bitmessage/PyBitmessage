import socket

from advanceddispatcher import AdvancedDispatcher
import asyncore_pollchoose as asyncore

class ProxyError(Exception): pass
class GeneralProxyError(ProxyError): pass

class Proxy(AdvancedDispatcher):
    # these are global, and if you change config during runtime, all active/new
    # instances should change too
    _proxy = ("127.0.0.1", 9050)
    _auth = None
    _remote_dns = True

    @property
    def proxy(self):
        return self.__class__._proxy

    @proxy.setter
    def proxy(self, address):
        if type(address) != tuple or (len(address) < 2) or (type(str(address[0])) != type('')) or (type(address[1]) != int):
            raise ValueError
        self.__class__._proxy = address

    @property
    def auth(self):
        return self.__class__._auth

    @auth.setter
    def auth(self, authTuple):
        self.__class__._auth = authTuple

    def __init__(self, address):
        if type(address) != tuple or (len(address) < 2) or (type(str(address[0])) != type('')) or (type(address[1]) != int):
            raise ValueError
        AdvancedDispatcher.__init__(self)
        self.destination = address
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(self.proxy)
        print "connecting in background to %s:%i" % (self.proxy[0], self.proxy[1])
