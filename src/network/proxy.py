"""
src/network/proxy.py
====================
"""
# pylint: disable=protected-access
import socket
import time

import network.asyncore_pollchoose as asyncore
import state
from network.advanceddispatcher import AdvancedDispatcher
from bmconfigparser import BMConfigParser
from debug import logger


class ProxyError(Exception):
    """Base proxy exception class"""
    errorCodes = ("Unknown error",)

    def __init__(self, code=-1):
        self.code = code
        try:
            self.message = self.errorCodes[code]
        except IndexError:
            self.message = self.errorCodes[-1]
        super(ProxyError, self).__init__(self.message)


class GeneralProxyError(ProxyError):
    """General proxy error class (not specfic to an implementation)"""
    errorCodes = (
        "Success",
        "Invalid data",
        "Not connected",
        "Not available",
        "Bad proxy type",
        "Bad input",
        "Timed out",
        "Network unreachable",
        "Connection refused",
        "Host unreachable"
    )


class Proxy(AdvancedDispatcher):
    """Base proxy class"""
    # these are global, and if you change config during runtime,
    # all active/new instances should change too
    _proxy = ("127.0.0.1", 9050)
    _auth = None
    _onion_proxy = None
    _onion_auth = None
    _remote_dns = True

    @property
    def proxy(self):
        """Return proxy IP and port"""
        return self.__class__._proxy

    @proxy.setter
    def proxy(self, address):
        """Set proxy IP and port"""
        if (not isinstance(address, tuple) or len(address) < 2 or
                not isinstance(address[0], str) or
                not isinstance(address[1], int)):
            raise ValueError
        self.__class__._proxy = address

    @property
    def auth(self):
        """Return proxy authentication settings"""
        return self.__class__._auth

    @auth.setter
    def auth(self, authTuple):
        """Set proxy authentication (username and password)"""
        self.__class__._auth = authTuple

    @property
    def onion_proxy(self):
        """
        Return separate proxy IP and port for use only with onion
        addresses. Untested.
        """
        return self.__class__._onion_proxy

    @onion_proxy.setter
    def onion_proxy(self, address):
        """Set onion proxy address"""
        if address is not None and (
                not isinstance(address, tuple) or len(address) < 2 or
                not isinstance(address[0], str) or
                not isinstance(address[1], int)):
            raise ValueError
        self.__class__._onion_proxy = address

    @property
    def onion_auth(self):
        """Return proxy authentication settings for onion hosts only"""
        return self.__class__._onion_auth

    @onion_auth.setter
    def onion_auth(self, authTuple):
        """Set proxy authentication for onion hosts only. Untested."""
        self.__class__._onion_auth = authTuple

    def __init__(self, address):
        if not isinstance(address, state.Peer):
            raise ValueError
        AdvancedDispatcher.__init__(self)
        self.destination = address
        self.isOutbound = True
        self.fullyEstablished = False
        self.connectedAt = 0
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        if BMConfigParser().safeGetBoolean(
                "bitmessagesettings", "socksauthentication"):
            self.auth = (
                BMConfigParser().safeGet(
                    "bitmessagesettings", "socksusername"),
                BMConfigParser().safeGet(
                    "bitmessagesettings", "sockspassword")
            )
        else:
            self.auth = None
        self.connect(
            self.onion_proxy
            if address.host.endswith(".onion") and self.onion_proxy else
            self.proxy
        )

    def handle_connect(self):
        """Handle connection event (to the proxy)"""
        self.set_state("init")
        try:
            AdvancedDispatcher.handle_connect(self)
        except socket.error as e:
            if e.errno in asyncore._DISCONNECTED:
                logger.debug(
                    "%s:%i: Connection failed: %s",
                    self.destination.host, self.destination.port, e)
                return
        self.state_init()

    def state_proxy_handshake_done(self):
        """Handshake is complete at this point"""
        self.connectedAt = time.time()      # pylint: disable=attribute-defined-outside-init
        return False
