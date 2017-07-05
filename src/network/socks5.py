import socket
import struct

from proxy import Proxy, ProxyError, GeneralProxyError

class Socks5AuthError(ProxyError):
    errorCodes = ("Succeeded",
        "Authentication is required",
        "All offered authentication methods were rejected",
        "Unknown username or invalid password",
        "Unknown error")


class Socks5Error(ProxyError):
    errorCodes = ("Succeeded",
        "General SOCKS server failure",
        "Connection not allowed by ruleset",
        "Network unreachable",
        "Host unreachable",
        "Connection refused",
        "TTL expired",
        "Command not supported",
        "Address type not supported",
        "Unknown error")


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
            raise GeneralProxyError(1)
        elif ret[1] == 0:
            # no auth required
            self.set_state("auth_done", 2)
        elif ret[1] == 2:
            # username/password
            self.writeQueue.put(struct.pack('BB', 1, len(self._auth[0])) + \
                self._auth[0] + struct.pack('B', len(self._auth[1])) + \
                self._auth[1])
            self.set_state("auth_needed", 2)
        else:
            if ret[1] == 0xff:
                # auth error
                raise Socks5AuthError(2)
            else:
                # other error
                raise GeneralProxyError(1)

    def state_auth_needed(self):
        if not self.read_buf_sufficient(2):
            return False
        ret = struct.unpack('BB', self.read_buf)
        if ret[0] != 1:
            # general error
            raise GeneralProxyError(1)
        if ret[1] != 0:
            # auth error
            raise Socks5AuthError(3)
        # all ok
        self.set_state = ("auth_done", 2)

    def state_pre_connect(self):
        if not self.read_buf_sufficient(4):
            return False
        # Get the response
        if self.read_buf[0:1] != chr(0x05).encode():
            self.close()
            raise GeneralProxyError(1)
        elif self.read_buf[1:2] != chr(0x00).encode():
            # Connection failed
            self.close()
            if ord(self.read_buf[1:2])<=8:
                raise Socks5Error(ord(self.read_buf[1:2]))
            else:
                raise Socks5Error(9)
        # Get the bound address/port
        elif self.read_buf[3:4] == chr(0x01).encode():
            self.set_state("proxy_addr_1", 4)
        elif self.read_buf[3:4] == chr(0x03).encode():
            self.set_state("proxy_addr_2_1", 4)
        else:
            self.close()
            raise GeneralProxyError(1)

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
        self.boundaddr = self.read_buf
        self.set_state("proxy_port", self.address_length)

    def state_proxy_port(self):
        if not self.read_buf_sufficient(2):
            return False
        self.boundport = struct.unpack(">H", self.read_buf[0:2])[0]
        self.__proxysockname = (self.boundaddr, self.boundport)
        if self.ipaddr is not None:
            self.__proxypeername = (socket.inet_ntoa(self.ipaddr), self.destination[1])
        else:
            self.__proxypeername = (self.destination[0], self.destport)
        self.set_state("proxy_handshake_done", 2)

    def proxy_sock_name(self):
        return socket.inet_ntoa(self.__proxysockname[0])


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

    def state_pre_connect(self):
        try:
            Socks5.state_pre_connect(self)
        except Socks5Error as e:
            self.handle_close(e.message)


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
