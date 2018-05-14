import socket
import time

from advanceddispatcher import AdvancedDispatcher
import asyncore_pollchoose as asyncore
from debug import logger
import network.connectionpool
import state

class ProxyError(Exception):
    errorCodes = ("UnknownError")

    def __init__(self, code=-1):
        self.code = code
        try:
            self.message = self.__class__.errorCodes[self.code]
        except IndexError:
            self.message = self.__class__.errorCodes[-1]
        super(ProxyError, self).__init__(self.message)


class GeneralProxyError(ProxyError):
    errorCodes = ("Success",
        "Invalid data",
        "Not connected",
        "Not available",
        "Bad proxy type",
        "Bad input",
        "Timed out",
        "Network unreachable",
        "Connection refused",
        "Host unreachable")


class Proxy(AdvancedDispatcher):
    # these are global, and if you change config during runtime, all active/new
    # instances should change too
    _proxy = ("127.0.0.1", 9050)
    _auth = None
    _onion_proxy = None
    _onion_auth = None
    _remote_dns = True

    @property
    def proxy(self):
        return self.__class__._proxy

    @proxy.setter
    def proxy(self, address):
        if not isinstance(address, tuple) or (len(address) < 2) or \
                (not isinstance(address[0], str) or not isinstance(address[1], int)):
            raise ValueError
        self.__class__._proxy = address

    @property
    def auth(self):
        return self.__class__._auth

    @auth.setter
    def auth(self, authTuple):
        self.__class__._auth = authTuple

    @property
    def onion_proxy(self):
        return self.__class__._onion_proxy

    @onion_proxy.setter
    def onion_proxy(self, address):
        if address is not None and (not isinstance(address, tuple) or (len(address) < 2) or \
                (not isinstance(address[0], str) or not isinstance(address[1], int))):
            raise ValueError
        self.__class__._onion_proxy = address

    @property
    def onion_auth(self):
        return self.__class__._onion_auth

    @onion_auth.setter
    def onion_auth(self, authTuple):
        self.__class__._onion_auth = authTuple

    def __init__(self, address):
        if not isinstance(address, state.Peer):
            raise ValueError
        AdvancedDispatcher.__init__(self)
        self.destination = address
        self.isOutbound = True
        self.fullyEstablished = False
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        if address.host.endswith(".onion") and self.onion_proxy is not None:
            self.connect(self.onion_proxy)
        else:
            self.connect(self.proxy)

    def handle_connect(self):
        self.set_state("init")
        try:
            AdvancedDispatcher.handle_connect(self)
        except socket.error as e:
            if e.errno in asyncore._DISCONNECTED:
                logger.debug("%s:%i: Connection failed: %s", self.destination.host, self.destination.port, str(e))
                return
        self.state_init()

    def state_proxy_handshake_done(self):
        self.connectedAt = time.time()
        return False
