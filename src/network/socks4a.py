import socket
import struct

from proxy import Proxy, ProxyError, GeneralProxyError

class Socks4aError(ProxyError):
    errorCodes = ("Request granted",
        "Request rejected or failed",
        "Request rejected because SOCKS server cannot connect to identd on the client",
        "Request rejected because the client program and identd report different user-ids",
        "Unknown error")


class Socks4a(Proxy):
    def __init__(self, address=None):
        Proxy.__init__(self, address)
        self.ipaddr = None
        self.destport = address[1]

    def state_init(self):
        self.set_state("auth_done", 0)
        return True

    def state_pre_connect(self):
        # Get the response
        if self.read_buf[0:1] != chr(0x00).encode():
            # bad data
            self.close()
            raise GeneralProxyError(1)
        elif self.read_buf[1:2] != chr(0x5A).encode():
            # Connection failed
            self.close()
            if ord(self.read_buf[1:2]) in (91, 92, 93):
                # socks 4 error
                raise Socks4aError(ord(self.read_buf[1:2]) - 90)
            else:
                raise Socks4aError(4)
        # Get the bound address/port
        self.boundport = struct.unpack(">H", self.read_buf[2:4])[0]
        self.boundaddr = self.read_buf[4:]
        self.__proxysockname = (self.boundaddr, self.boundport)
        if self.ipaddr:
            self.__proxypeername = (socket.inet_ntoa(self.ipaddr), self.destination[1])
        else:
            self.__proxypeername = (self.destination[0], self.destport)
        self.set_state("proxy_handshake_done", length=8)
        return True

    def proxy_sock_name(self):
       return socket.inet_ntoa(self.__proxysockname[0])


class Socks4aConnection(Socks4a):
    def __init__(self, address):
        Socks4a.__init__(self, address=address)

    def state_auth_done(self):
        # Now we can request the actual connection
        rmtrslv = False
        self.append_write_buf(struct.pack('>BBH', 0x04, 0x01, self.destination[1]))
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            self.ipaddr = socket.inet_aton(self.destination[0])
            self.append_write_buf(self.ipaddr)
        except socket.error:
            # Well it's not an IP number,  so it's probably a DNS name.
            if Proxy._remote_dns:
                # Resolve remotely
                rmtrslv = True
                self.ipaddr = None
                self.append_write_buf(struct.pack("BBBB", 0x00, 0x00, 0x00, 0x01))
            else:
                # Resolve locally
                self.ipaddr = socket.inet_aton(socket.gethostbyname(self.destination[0]))
                self.append_write_buf(self.ipaddr)
        if self._auth:
            self.append_write_buf(self._auth[0])
        self.append_write_buf(chr(0x00).encode())
        if rmtrslv:
            self.append_write_buf(self.destination[0] + chr(0x00).encode())
        self.set_state("pre_connect", length=0, expectBytes=8)
        return True

    def state_pre_connect(self):
        try:
            return Socks4a.state_pre_connect(self)
        except Socks4aError as e:
            self.handle_close(e.message)


class Socks4aResolver(Socks4a):
    def __init__(self, host):
        self.host = host
        self.port = 8444
        Socks4a.__init__(self, address=(self.host, self.port))

    def state_auth_done(self):
        # Now we can request the actual connection
        self.append_write_buf(struct.pack('>BBH', 0x04, 0xF0, self.destination[1]))
        self.append_write_buf(struct.pack("BBBB", 0x00, 0x00, 0x00, 0x01))
        if self._auth:
            self.append_write_buf(self._auth[0])
        self.append_write_buf(chr(0x00).encode())
        self.append_write_buf(self.host + chr(0x00).encode())
        self.set_state("pre_connect", length=0, expectBytes=8)
        return True

    def resolved(self):
        print "Resolved %s as %s" % (self.host, self.proxy_sock_name())
