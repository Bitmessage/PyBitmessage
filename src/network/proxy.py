# SOCKS5 only

import asyncore
import socket
import struct

from advanceddispatcher import AdvancedDispatcher

class Proxy(AdvancedDispatcher):
    # these are global, and if you change config during runtime, all active/new
    # instances should change too
    _proxy = ["", 1080]
    _auth = None
    _remote_dns = True

    @property
    def proxy(self):
        return self.__class__._proxy

    @proxy.setter
    def proxy(self, address):
        if (not type(address) in (list,tuple)) or (len(address) < 2) or (type(address[0]) != type('')) or (type(address[1]) != int):
            raise
        self.__class__._proxy = address

    @property
    def auth(self):
        return self.__class__._auth

    @auth.setter
    def auth(self, authTuple):
        self.__class__._auth = authTuple

    def __init__(self, address=None):
        if (not type(address) in (list,tuple)) or (len(address) < 2) or (type(address[0]) != type('')) or (type(address[1]) != int):
            raise
        AdvancedDispatcher.__init__(self, self.sock)
        self.destination = address
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sslSocket.setblocking(0)
        self.connect(self.proxy)


class SOCKS5(Proxy):
    def __init__(self, address=None, sock=None):
        Proxy.__init__(self, address)
        self.state = "init"

    def handle_connect(self):
        self.process()

    def state_init(self):
        if self._auth:
            self.write_buf += struct.pack('BBBB', 0x05, 0x02, 0x00, 0x02)
        else:
            self.write_buf += struct.pack('BBB', 0x05, 0x01, 0x00)
        self.set_state("auth_1", 0)

    def state_auth_1(self):
        if not self.read_buf_sufficient(2):
            return False
        ret = struct.unpack('BB', self.read_buf)
        self.read_buf = self.read_buf[2:]
        if ret[0] != 5:
            # general error
            raise
        elif ret[1] == 0:
            # no auth required
            self.set_state("auth_done", 2)
        elif ret[1] == 2:
            # username/password
            self.write_buf += struct.pack('BB', 1, len(self._auth[0])) + \
                self._auth[0] + struct.pack('B', len(self._auth[1])) + \
                self._auth[1]
            self.set_state("auth_1", 2)
        else:
            if ret[1] == 0xff:
                # auth error
                raise
            else:
                # other error
                raise

    def state_auth_needed(self):
        if not self.read_buf_sufficient(2):
            return False
        ret = struct.unpack('BB', self.read_buf)
        if ret[0] != 1:
            # general error
            raise
        if ret[1] != 0:
            # auth error
            raise
        # all ok
        self.set_state = ("auth_done", 2)

    def state_pre_connect(self):
        if not self.read_buf_sufficient(4):
            return False
        # Get the response
        if self.read_buf[0:1] != chr(0x05).encode():
            # general error
            self.close()
            raise
        elif self.read_buf[1:2] != chr(0x00).encode():
            # Connection failed
            self.close()
            if ord(self.read_buf[1:2])<=8:
                # socks 5 erro
                raise
                #raise Socks5Error((ord(resp[1:2]), _socks5errors[ord(resp[1:2])]))
            else:
                raise
                #raise Socks5Error((9, _socks5errors[9]))
        # Get the bound address/port
        elif self.read_buf[3:4] == chr(0x01).encode():
            self.set_state("proxy_addr_1", 4)
        elif self.read_buf[3:4] == chr(0x03).encode():
            self.set_state("proxy_addr_2_1", 4)
        else:
            self.close()
            raise GeneralProxyError((1,_generalerrors[1]))

    def state_proxy_addr_1(self):
        if not self.read_buf_sufficient(4):
            return False
        self.boundaddr = self.read_buf[0:4]
        self.set_state("proxy_port", 4)

    def state_proxy_addr_2_1(self):
        if not self.read_buf_sufficient(1):
            return False
        self.address_length = ord(self.read_buf[0:1])
        self.set_state("proxy_addr_2_2", 1)

    def state_proxy_addr_2_2(self):
        if not self.read_buf_sufficient(self.address_length):
            return False
        self.boundaddr = read_buf
        self.set_state("proxy_port", self.address_length)

    def state_proxy_port(self):
        if not self.read_buf_sufficient(2):
            return False
        self.boundport = struct.unpack(">H", self.read_buf[0:2])[0]
        self.__proxysockname = (self.boundaddr, self.boundport)
        if self.ipaddr != None:
            self.__proxypeername = (socket.inet_ntoa(self.ipaddr), self.destination[1])
        else:
            self.__proxypeername = (self.destination[1], destport)


class SOCKS5Connection(SOCKS5):
    def __init__(self, address):
        SOCKS5.__init__(self, address)

    def state_auth_done(self):
        # Now we can request the actual connection
        self.write_buf += struct.pack('BBB', 0x05, 0x01, 0x00)
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            self.ipaddr = socket.inet_aton(self.destination[0])
            self.write_buf += chr(0x01).encode() + ipaddr
        except socket.error:
            # Well it's not an IP number,  so it's probably a DNS name.
            if Proxy._remote_dns:
                # Resolve remotely
                self.ipaddr = None
                self.write_buf += chr(0x03).encode() + chr(len(self.destination[0])).encode() + self.destination[0]
            else:
                # Resolve locally
                self.ipaddr = socket.inet_aton(socket.gethostbyname(self.destination[0]))
                self.write_buf += chr(0x01).encode() + ipaddr
        self.write_buf += struct.pack(">H", self.destination[1])
        self.set_state = ("pre_connect", 0)


class SOCKS5Resolver(SOCKS5):
    def __init__(self, host):
        self.host = host
        self.port = 8444
        SOCKS5.__init__(self, [self.host, self.port])

    def state_auth_done(self):
        # Now we can request the actual connection
        self.write_buf += struct.pack('BBB', 0x05, 0xF0, 0x00)
        self.write_buf += chr(0x03).encode() + chr(len(self.host)).encode() + self.host
        self.write_buf += struct.pack(">H", self.port)
        self.state = "pre_connect"
