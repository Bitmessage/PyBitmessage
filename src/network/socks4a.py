import socket
import struct

from advanceddispatcher import AdvancedDispatcher
import asyncore_pollchoose as asyncore
from proxy import Proxy, ProxyError, GeneralProxyError

class Socks4aError(ProxyError): pass


class Socks4a(Proxy):
    def __init__(self, address=None):
        Proxy.__init__(self, address)
        self.ipaddr = None
        self.destport = address[1]

    def state_init(self):
        self.set_state("auth_done", 0)

    def state_pre_connect(self):
        if not self.read_buf_sufficient(8):
            return False
        # Get the response
        if self.read_buf[0:1] != chr(0x00).encode():
            # bad data
            self.close()
            raise Socks4aError
        elif self.read_buf[1:2] != chr(0x5A).encode():
            # Connection failed
            self.close()
            if ord(self.read_buf[1:2]) in (91, 92, 93):
                # socks 4 erro
                raise Socks4aError
                #raise Socks5Error((ord(resp[1:2]), _socks5errors[ord(resp[1:2])-90]))
            else:
                raise Socks4aError
                #raise Socks4aError((94, _socks4aerrors[4]))
        # Get the bound address/port
        self.boundport = struct.unpack(">H", self.read_buf[2:4])[0]
        self.boundaddr = self.read_buf[4:]
        self.__proxysockname = (self.boundaddr, self.boundport)
        if self.ipaddr != None:
            self.__proxypeername = (socket.inet_ntoa(self.ipaddr), self.destination[1])
        else:
            self.__proxypeername = (self.destination[0], self.destport)
        self.set_state("proxy_handshake_done", 8)

    def proxy_sock_name(self):
       return socket.inet_ntoa(self.__proxysockname[0])

    def state_socks_handshake_done(self):
        return False


class Socks4aConnection(Socks4a):
    def __init__(self, address):
        Socks4a.__init__(self, address=address)

    def state_auth_done(self):
        # Now we can request the actual connection
        rmtrslv = False
        self.writeQueue.put(struct.pack('>BBH', 0x04, 0x01, self.destination[1]))
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            self.ipaddr = socket.inet_aton(self.destination[0])
            self.writeQueue.put(self.ipaddr)
        except socket.error:
            # Well it's not an IP number,  so it's probably a DNS name.
            if Proxy._remote_dns:
                # Resolve remotely
                rmtrslv = True
                self.ipaddr = None
                self.writeQueue.put(struct.pack("BBBB", 0x00, 0x00, 0x00, 0x01))
            else:
                # Resolve locally
                self.ipaddr = socket.inet_aton(socket.gethostbyname(self.destination[0]))
                self.writeQueue.put(self.ipaddr)
        if self._auth:
            self.writeQueue.put(self._auth[0])
        self.writeQueue.put(chr(0x00).encode())
        if rmtrslv:
            self.writeQueue.put(self.destination[0] + chr(0x00).encode())
        self.set_state("pre_connect", 0)


class Socks4aResolver(Socks4a):
    def __init__(self, host):
        self.host = host
        self.port = 8444
        Socks4a.__init__(self, address=(self.host, self.port))

    def state_auth_done(self):
        # Now we can request the actual connection
        self.writeQueue.put(struct.pack('>BBH', 0x04, 0xF0, self.destination[1]))
        self.writeQueue.put(struct.pack("BBBB", 0x00, 0x00, 0x00, 0x01))
        if self._auth:
            self.writeQueue.put(self._auth[0])
        self.writeQueue.put(chr(0x00).encode())
        self.writeQueue.put(self.host + chr(0x00).encode())
        self.set_state("pre_connect", 0)

    def resolved(self):
        print "Resolved %s as %s" % (self.host, self.proxy_sock_name())
