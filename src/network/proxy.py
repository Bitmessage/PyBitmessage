# SOCKS5 only

import asyncore
import socket
import struct


class Proxy(asyncore.dispatcher):
    # these are global, and if you change config during runtime, all active/new
    # instances should change too
    _proxy = ["", 1080]
    _auth = None
    _buf_len = 131072
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
        asyncore.dispatcher.__init__(self, self.sock)
        self.destination = address
        self.read_buf = ""
        self.write_buf = ""
        self.stage = "init"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sslSocket.setblocking(0)
        self.connect(self.proxy)

    def process(self):
        try:
            getattr(self, "state_" + str(self.stage))()
        except AttributeError:
            # missing stage
            raise

    def set_state(self, state):
        self.state = state
        self.read_buf = ""

    def writable(self):
        return len(self.write_buf) > 0

    def readable(self):
        return len(self.read_buf) < Proxy._buf_len

    def handle_read(self):
        self.read_buf += self.recv(Proxy._buf_len)
        self.process()

    def handle_write(self):
        written = self.send(self.write_buf)
        self.write_buf = self.write_buf[written:]
        self.process()


class SOCKS5(Proxy):
    def __init__(self, address=None, sock=None):
        Proxy.__init__(self, address)
        self.state = 0

    def handle_connect(self):
        self.process()

    def state_init(self):
        if self._auth:
            self.write_buf += struct.pack('BBBB', 0x05, 0x02, 0x00, 0x02)
        else:
            self.write_buf += struct.pack('BBB', 0x05, 0x01, 0x00)
        self.set_state("auth_1")

    def state_auth_1(self):
        if len(self.read_buf) < 2:
            return
        ret = struct.unpack('BB', self.read_buf)
        self.read_buf = self.read_buf[2:]
        if ret[0] != 5:
            # general error
            raise
        elif ret[1] == 0:
            # no auth required
            self.set_state("auth_done")
        elif ret[1] == 2:
            # username/password
            self.write_buf += struct.pack('BB', 1, len(self._auth[0])) + \
                self._auth[0] + struct.pack('B', len(self._auth[1])) + \
                self._auth[1]
            self.set_state("auth_1")
        else:
            if ret[1] == 0xff:
                # auth error
                raise
            else:
                # other error
                raise

    def state_auth_needed(self):
        if len(self.read_buf) < 2:
            return
        ret = struct.unpack('BB', self.read_buf)
        if ret[0] != 1:
            # general error
            raise
        if ret[1] != 0:
            # auth error
            raise
        # all ok
        self.set_state = ("auth_done")


class SOCKS5Connection(SOCKS5):
    def __init__(self, address):
        SOCKS5.__init__(self, address)

    def state_auth_done(self):
        # Now we can request the actual connection
        self.write_buf += struct.pack('BBB', 0x05, 0x01, 0x00)
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            ipaddr = socket.inet_aton(self.destination[0])
            self.write_buf += chr(0x01).encode() + ipaddr
        except socket.error:
            # Well it's not an IP number,  so it's probably a DNS name.
            if Proxy._remote_dns:
                # Resolve remotely
                ipaddr = None
                self.write_buf += chr(0x03).encode() + chr(len(self.destination[0])).encode() + self.destination[0]
            else:
                # Resolve locally
                ipaddr = socket.inet_aton(socket.gethostbyname(self.destination[0]))
                self.write_buf += chr(0x01).encode() + ipaddr
        self.write_buf += struct.pack(">H", self.destination[1])
        self.set_state = ("pre_connect")

    def state_pre_connect(self):
        if len(self.read_buf) < 4:
            return
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
        elif self_read_buf[3:4] == chr(0x01).encode():
            self.set_state("proxy_addr_long")
        elif resp[3:4] == chr(0x03).encode():
            self.set_state("proxy_addr_short")
        else:
            self.close()
            raise GeneralProxyError((1,_generalerrors[1]))
        boundport = struct.unpack(">H", self.__recvall(2))[0]
        self.__proxysockname = (boundaddr, boundport)
        if ipaddr != None:
            self.__proxypeername = (socket.inet_ntoa(ipaddr), destport)
        else:
            self.__proxypeername = (destaddr, destport)

    def state_proxy_addr_long(self):
        if len(self.read_buf) < 4:
            return
        self.boundaddr = self.read_buf[0:4]
        self.set_state("proxy_port")

    def state_proxy_addr_short(self):
        if len(self.read_buf) < 1:
            return
        self.boundaddr = self.read_buf[0:1]
        self.set_state("proxy_port")

    def state_proxy_port(self):
        if len(self.read_buf) < 2:
            return
        self.boundport = struct.unpack(">H", self.read_buf[0:2])[0]
        self.__proxysockname = (self.boundaddr, self.boundport)
        if ipaddr != None:
            self.__proxypeername = (socket.inet_ntoa(ipaddr), destport)
        else:
            self.__proxypeername = (destaddr, destport)


class SOCKS5Resolver(SOCKS5):
    def __init__(self, destpair):
        SOCKS5.__init__(self, destpair)

    def state_auth_done(self):
        # Now we can request the actual connection
        req = struct.pack('BBB', 0x05, 0xF0, 0x00)
        req += chr(0x03).encode() + chr(len(host)).encode() + host
        req = req + struct.pack(">H", 8444)
        self.sendall(req)
        # Get the response
        ip = ""
        resp = self.__recvall(4)
        if resp[0:1] != chr(0x05).encode():
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))
        elif resp[1:2] != chr(0x00).encode():
            # Connection failed
            self.close()
            if ord(resp[1:2])<=8:
                raise Socks5Error((ord(resp[1:2]), _socks5errors[ord(resp[1:2])]))
            else:
                raise Socks5Error((9, _socks5errors[9]))
        # Get the bound address/port
        elif resp[3:4] == chr(0x01).encode():
            ip = socket.inet_ntoa(self.__recvall(4))
        elif resp[3:4] == chr(0x03).encode():
            resp = resp + self.recv(1)
            ip = self.__recvall(ord(resp[4:5]))
        else:
            self.close()
            raise GeneralProxyError((1,_generalerrors[1]))
        boundport = struct.unpack(">H", self.__recvall(2))[0]
        return ip
