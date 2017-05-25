import socket
import struct

from advanceddispatcher import AdvancedDispatcher
import asyncore_pollchoose as asyncore
from proxy import Proxy, ProxyError, GeneralProxyError

class Socks5AuthError(ProxyError): pass
class Socks5Error(ProxyError): pass


class Socks5(Proxy):
    def __init__(self, address=None):
        Proxy.__init__(self, address)
        self.ipaddr = None
        self.destport = address[1]

    def state_init(self):
        if self._auth:
            self.writeQueue.put(struct.pack('BBBB', 0x05, 0x02, 0x00, 0x02))
        else:
            self.writeQueue.put(struct.pack('BBB', 0x05, 0x01, 0x00))
        self.set_state("auth_1", 0)

    def state_auth_1(self):
        if not self.read_buf_sufficient(2):
            return False
        ret = struct.unpack('BB', self.read_buf)
        self.read_buf = self.read_buf[2:]
        if ret[0] != 5:
            # general error
            raise GeneralProxyError
        elif ret[1] == 0:
            # no auth required
            self.set_state("auth_done", 2)
        elif ret[1] == 2:
            # username/password
            self.writeQueue.put(struct.pack('BB', 1, len(self._auth[0])) + \
                self._auth[0] + struct.pack('B', len(self._auth[1])) + \
                self._auth[1])
            self.set_state("auth_1", 2)
        else:
            if ret[1] == 0xff:
                # auth error
                raise Socks5AuthError
            else:
                # other error
                raise Socks5Error

    def state_auth_needed(self):
        if not self.read_buf_sufficient(2):
            return False
        ret = struct.unpack('BB', self.read_buf)
        if ret[0] != 1:
            # general error
            raise Socks5Error
        if ret[1] != 0:
            # auth error
            raise Socks5AuthError
        # all ok
        self.set_state = ("auth_done", 2)

    def state_pre_connect(self):
        if not self.read_buf_sufficient(4):
            return False
        # Get the response
        if self.read_buf[0:1] != chr(0x05).encode():
            # general error
            self.close()
            raise Socks5Error
        elif self.read_buf[1:2] != chr(0x00).encode():
            # Connection failed
            self.close()
            if ord(self.read_buf[1:2])<=8:
                # socks 5 erro
                raise Socks5Error
                #raise Socks5Error((ord(resp[1:2]), _socks5errors[ord(resp[1:2])]))
            else:
                raise Socks5Error
                #raise Socks5Error((9, _socks5errors[9]))
        # Get the bound address/port
        elif self.read_buf[3:4] == chr(0x01).encode():
            self.set_state("proxy_addr_1", 4)
        elif self.read_buf[3:4] == chr(0x03).encode():
            self.set_state("proxy_addr_2_1", 4)
        else:
            self.close()
            #raise GeneralProxyError((1,_generalerrors[1]))
            raise GeneralProxyError

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
            self.__proxypeername = (self.destination[0], self.destport)
        self.set_state("socks_handshake_done", 2)

    def proxy_sock_name(self):
       return socket.inet_ntoa(self.__proxysockname[0])

    def state_socks_handshake_done(self):
        return False


class Socks5Connection(Socks5):
    def __init__(self, address):
        Socks5.__init__(self, address=address)

    def state_auth_done(self):
        # Now we can request the actual connection
        self.writeQueue.put(struct.pack('BBB', 0x05, 0x01, 0x00))
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            self.ipaddr = socket.inet_aton(self.destination[0])
            self.writeQueue.put(chr(0x01).encode() + self.ipaddr)
        except socket.error:
            # Well it's not an IP number,  so it's probably a DNS name.
            if Proxy._remote_dns:
                # Resolve remotely
                self.ipaddr = None
                self.writeQueue.put(chr(0x03).encode() + chr(len(self.destination[0])).encode() + self.destination[0])
            else:
                # Resolve locally
                self.ipaddr = socket.inet_aton(socket.gethostbyname(self.destination[0]))
                self.writeQueue.put(chr(0x01).encode() + self.ipaddr)
        self.writeQueue.put(struct.pack(">H", self.destination[1]))
        self.set_state("pre_connect", 0)


class Socks5Resolver(Socks5):
    def __init__(self, host):
        self.host = host
        self.port = 8444
        Socks5.__init__(self, address=(self.host, self.port))

    def state_auth_done(self):
        # Now we can request the actual connection
        self.writeQueue.put(struct.pack('BBB', 0x05, 0xF0, 0x00))
        self.writeQueue.put(chr(0x03).encode() + chr(len(self.host)).encode() + str(self.host))
        self.writeQueue.put(struct.pack(">H", self.port))
        self.set_state("pre_connect", 0)

    def resolved(self):
        print "Resolved %s as %s" % (self.host, self.proxy_sock_name())
