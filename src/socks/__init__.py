"""SocksiPy - Python SOCKS module.
Version 1.00

Copyright 2006 Dan-Haim. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 1. Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
 3. Neither the name of Dan Haim nor the names of his contributors may be used
    to endorse or promote products derived from this software without specific
    prior written permission.

THIS SOFTWARE IS PROVIDED BY DAN HAIM "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL DAN HAIM OR HIS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMANGE.


This module provides a standard socket-like interface for Python
for tunneling connections through SOCKS proxies.

"""

import socket
import struct

"""

Minor modifications made by Christopher Gilbert (http://motomastyle.com/)
for use in PyLoris (http://pyloris.sourceforge.net/)

Minor modifications made by Mario Vilas (http://breakingcode.wordpress.com/)
mainly to merge bug fixes found in Sourceforge

"""


proxy_type_socks4 = 1
proxy_type_socks5 = 2
proxy_type_http = 3

_default_proxy = None
_org_socket = socket.socket


class ProxyError(Exception):
    pass


class GeneralProxyError(ProxyError):
    pass


class Socks5AuthError(ProxyError):
    pass


class Socks5Error(ProxyError):
    pass


class Socks4Error(ProxyError):
    pass


class HTTPError(ProxyError):
    pass


_generalerrors = ("success",
                  "invalid data",
                  "not connected",
                  "not available",
                  "bad proxy type",
                  "bad input",
                  "timed out",
                  "network unreachable",
                  "connection refused",
                  "host unreachable")

_socks5errors = ("succeeded",
                 "general SOCKS server failure",
                 "connection not allowed by ruleset",
                 "Network unreachable",
                 "Host unreachable",
                 "Connection refused",
                 "TTL expired",
                 "Command not supported",
                 "Address type not supported",
                 "Unknown error")

_socks5autherrors = ("succeeded",
                     "authentication is required",
                     "all offered authentication methods were rejected",
                     "unknown username or invalid password",
                     "unknown error")

_socks4errors = ("request granted",
                 "request rejected or failed",
                 "request rejected because SOCKS server cannot connect to identd on the client",
                 "request rejected because the client program and identd report different user-ids",
                 "unknown error")


def setdefaultproxy(proxytype=None, addr=None, port=None, rdns=True, username=None, password=None):
    """setdefaultproxy(proxytype, addr[, port[, rdns[, username[, password]]]])
    Sets a default proxy which all further socksocket objects will use,
    unless explicitly changed.
    """
    global _default_proxy
    _default_proxy = (proxytype, addr, port, rdns, username, password)


def wrapmodule(module):
    """wrapmodule(module)
    Attempts to replace a module's socket library with a SOCKS socket. Must set
    a default proxy using setdefaultproxy(...) first.
    This will only work on modules that import socket directly into the namespace;
    most of the Python Standard Library falls into this category.
    """
    if _default_proxy is not None:
        module.socket.socket = SockSocket
    else:
        raise GeneralProxyError((4, "no proxy specified"))


class SockSocket(socket.socket):
    """socksocket([family[, type[, proto]]]) -> socket object
    Open a SOCKS enabled socket. The parameters are the same as
    those of the standard socket init. In order for SOCKS to work,
    you must specify family=AF_INET, type=SOCK_STREAM and proto=0.
    """

    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        _org_socket.__init__(self, family, type, proto, _sock)
        if _default_proxy is not None:
            self.__proxy = _default_proxy
        else:
            self.__proxy = (None, None, None, None, None, None)
        self.__proxy_sock_name = None
        self.__proxy_peer_name = None

    def __recvall(self, count):
        """__recvall(count) -> data
        Receive EXACTLY the number of bytes requested from the socket.
        Blocks until the required number of bytes have been received.
        """
        try:
            data = self.recv(count)
        except socket.timeout:
            raise GeneralProxyError((6, "timed out"))
        while len(data) < count:
            d = self.recv(count - len(data))
            if not d:
                raise GeneralProxyError((0, "connection closed unexpectedly"))
            data = data + d
        return data

    def setproxy(self, proxytype=None, addr=None, port=None, rdns=True, username=None, password=None):
        """setproxy(proxytype, addr[, port[, rdns[, username[, password]]]])
        Sets the proxy to be used.

         proxytype
           The type of the proxy to be used. Three types
           are supported: PROXY_TYPE_SOCKS4 (including socks4a),
           PROXY_TYPE_SOCKS5 and PROXY_TYPE_HTTP

        addr
           The address of the server (IP or DNS).

        port
           The port of the server. Defaults to 1080 for SOCKS
           servers and 8080 for HTTP proxy servers.

        rdns
           Should DNS queries be preformed on the remote side
           (rather than the local side). The default is True.
           Note: This has no effect with SOCKS4 servers.

        username
           Username to authenticate with to the server.
           The default is no authentication.

        password
           Password to authenticate with to the server.
           Only relevant when username is also provided.

        """
        self.__proxy = (proxytype, addr, port, rdns, username, password)

    def __negotiatesocks5(self):
        """__negotiatesocks5(self,destaddr,destport)
        Negotiates a connection through a SOCKS5 server.
        """
        # First we'll send the authentication packages we support.
        if self.__proxy[4] is not None and self.__proxy[5] is not None:
            # The username/password details were supplied to the
            # setproxy method so we support the USERNAME/PASSWORD
            # authentication (in addition to the standard none).
            self.sendall(struct.pack('BBBB', 0x05, 0x02, 0x00, 0x02))
        else:
            # No username/password were entered, therefore we
            # only support connections with no authentication.
            self.sendall(struct.pack('BBB', 0x05, 0x01, 0x00))
        # We'll receive the server's response to determine which
        # method was selected
        chosenauth = self.__recvall(2)
        if chosenauth[0:1] != chr(0x05).encode():
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))
        # Check the chosen authentication method
        if chosenauth[1:2] == chr(0x00).encode():
            # No authentication is required
            pass
        elif chosenauth[1:2] == chr(0x02).encode():
            # Okay, we need to perform a basic username/password
            # authentication.
            self.sendall(
                chr(0x01).encode() + chr(len(self.__proxy[4])) + self.__proxy[4] + chr(
                    len(self.__proxy[5])) + self.__proxy[5]
            )
            authstat = self.__recvall(2)
            if authstat[0:1] != chr(0x01).encode():
                # Bad response
                self.close()
                raise GeneralProxyError((1, _generalerrors[1]))
            if authstat[1:2] != chr(0x00).encode():
                # Authentication failed
                self.close()
                raise Socks5AuthError((3, _socks5autherrors[3]))
            # Authentication succeeded
        else:
            # Reaching here is always bad
            self.close()
            if chosenauth[1] == chr(0xFF).encode():
                raise Socks5AuthError((2, _socks5autherrors[2]))
            else:
                raise GeneralProxyError((1, _generalerrors[1]))

    def __connectsocks5(self, destaddr, destport):
        # Now we can request the actual connection
        req = struct.pack('BBB', 0x05, 0x01, 0x00)
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            ipaddr = socket.inet_aton(destaddr)
            req = req + chr(0x01).encode() + ipaddr
        except socket.error:
            # Well it's not an IP number,  so it's probably a DNS name.
            if self.__proxy[3]:
                # Resolve remotely
                ipaddr = None
                req = req + chr(0x03).encode() + chr(len(destaddr)).encode() + destaddr
            else:
                # Resolve locally
                ipaddr = socket.inet_aton(socket.gethostbyname(destaddr))
                req = req + chr(0x01).encode() + ipaddr
        req = req + struct.pack(">H", destport)
        self.sendall(req)
        # Get the response
        resp = self.__recvall(4)
        if resp[0:1] != chr(0x05).encode():
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))
        elif resp[1:2] != chr(0x00).encode():
            # Connection failed
            self.close()
            if ord(resp[1:2]) <= 8:
                raise Socks5Error((ord(resp[1:2]), _socks5errors[ord(resp[1:2])]))
            else:
                raise Socks5Error((9, _socks5errors[9]))
        # Get the bound address/port
        elif resp[3:4] == chr(0x01).encode():
            boundaddr = self.__recvall(4)
        elif resp[3:4] == chr(0x03).encode():
            resp = resp + self.recv(1)
            boundaddr = self.__recvall(ord(resp[4:5]))
        else:
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))
        boundport = struct.unpack(">H", self.__recvall(2))[0]
        self.__proxy_sock_name = (boundaddr, boundport)
        if ipaddr:
            self.__proxy_peer_name = (socket.inet_ntoa(ipaddr), destport)
        else:
            self.__proxy_peer_name = (destaddr, destport)

    def __resolvesocks5(self, host):
        # Now we can request the actual connection
        req = struct.pack('BBB', 0x05, 0xF0, 0x00)
        req += chr(0x03).encode() + chr(len(host)).encode() + host
        req = req + struct.pack(">H", 8444)
        self.sendall(req)
        # Get the response

        resp = self.__recvall(4)
        if resp[0:1] != chr(0x05).encode():
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))
        elif resp[1:2] != chr(0x00).encode():
            # Connection failed
            self.close()
            if ord(resp[1:2]) <= 8:
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
            raise GeneralProxyError((1, _generalerrors[1]))
        return ip

    def getproxysockname(self):
        """getsockname() -> address info
        Returns the bound IP address and port number at the proxy.
        """
        return self.__proxy_sock_name

    def getproxypeername(self):
        """getproxypeername() -> address info
        Returns the IP and port number of the proxy.
        """
        return _org_socket.getpeername(self)

    def getpeername(self):
        """getpeername() -> address info
        Returns the IP address and port number of the destination
        machine (note: getproxypeername returns the proxy)
        """
        return self.__proxy_peer_name

    def getproxytype(self):
        return self.__proxy[0]

    def __negotiatesocks4(self, destination_address, destination_port):
        """__negotiatesocks4(self,destaddr,destport)
        Negotiates a connection through a SOCKS4 server.
        """
        # Check if the destination address provided is an IP address
        rmtrslv = False
        try:
            ipaddr = socket.inet_aton(destination_address)
        except socket.error:
            # It's a DNS name. Check where it should be resolved.
            if self.__proxy[3]:
                ipaddr = struct.pack("BBBB", 0x00, 0x00, 0x00, 0x01)
                rmtrslv = True
            else:
                ipaddr = socket.inet_aton(socket.gethostbyname(destination_address))
        # Construct the request packet
        req = struct.pack(">BBH", 0x04, 0x01, destination_port) + ipaddr
        # The username parameter is considered userid for SOCKS4
        if self.__proxy[4] is not None:
            req = req + self.__proxy[4]
        req = req + chr(0x00).encode()
        # DNS name if remote resolving is required
        # NOTE: This is actually an extension to the SOCKS4 protocol
        # called SOCKS4A and may not be supported in all cases.
        if rmtrslv:
            req = req + destination_address + chr(0x00).encode()
        self.sendall(req)
        # Get the response from the server
        resp = self.__recvall(8)
        if resp[0:1] != chr(0x00).encode():
            # Bad data
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))
        if resp[1:2] != chr(0x5A).encode():
            # Server returned an error
            self.close()
            if ord(resp[1:2]) in (91, 92, 93):
                self.close()
                raise Socks4Error((ord(resp[1:2]), _socks4errors[ord(resp[1:2]) - 90]))
            else:
                raise Socks4Error((94, _socks4errors[4]))
        # Get the bound address/port
        self.__proxy_sock_name = (socket.inet_ntoa(resp[4:]), struct.unpack(">H", resp[2:4])[0])
        if rmtrslv is not None:
            self.__proxy_peer_name = (socket.inet_ntoa(ipaddr), destination_port)
        else:
            self.__proxy_peer_name = (destination_address, destination_port)

    def __negotiatehttp(self, destination_address, destination_port):
        """__negotiatehttp(self,destaddr,destport)
        Negotiates a connection through an HTTP server.
        """
        # If we need to resolve locally, we do this now
        if not self.__proxy[3]:
            addr = socket.gethostbyname(destination_address)
        else:
            addr = destination_address
        self.sendall(
            ("CONNECT {} : {} HTTP/1.1\r\n Host: {} \r\n\r\n".format(
                addr, str(destination_port), destination_address)).encode())
        # We read the response until we get the string "\r\n\r\n"
        resp = self.recv(1)
        while resp.find("\r\n\r\n".encode()) == -1:
            resp = resp + self.recv(1)
        # We just need the first line to check if the connection
        # was successful
        status_line = resp.splitlines()[0].split(" ".encode(), 2)

        if status_line[0] not in ("HTTP/1.0".encode(), "HTTP/1.1".encode()):
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))
        try:
            statuscode = int(status_line[1])
        except ValueError:
            self.close()
            raise GeneralProxyError((1, _generalerrors[1]))

        if statuscode != 200:
            self.close()
            raise HTTPError((statuscode, status_line[2]))
        self.__proxy_sock_name = ("0.0.0.0", 0)
        self.__proxy_peer_name = (addr, destination_port)

    def connect(self, destination_pair):
        """connect(self, despair)
        Connects to the specified destination through a proxy.
        destpar - A tuple of the IP/DNS address and the port number.
        (identical to socket's connect).
        To select the proxy server use setproxy().
        """
        # Do a minimal input check first
        if (not isinstance(destination_pair, (list, tuple))) or (len(destination_pair) < 2) \
                or not isinstance(destination_pair[0], str) or not isinstance(destination_pair[1], int):
            raise GeneralProxyError((5, _generalerrors[5]))

        if self.__proxy[0] == proxy_type_socks5:
            port_number = self.__proxy[2] if self.__proxy[2] is not None else 1080
            try:
                _org_socket.connect(self, (self.__proxy[1], port_number))
            except socket.error as e:
                # ENETUNREACH, WSAENETUNREACH
                if e[0] in [101, 10051]:
                    raise GeneralProxyError((7, _generalerrors[7]))
                # ECONNREFUSED, WSAECONNREFUSED
                if e[0] in [111, 10061]:
                    raise GeneralProxyError((8, _generalerrors[8]))
                # EHOSTUNREACH, WSAEHOSTUNREACH
                if e[0] in [113, 10065]:
                    raise GeneralProxyError((9, _generalerrors[9]))
                raise
            self.__negotiatesocks5()
            self.__connectsocks5(destination_pair[0], destination_pair[1])

        elif self.__proxy[0] == proxy_type_socks4:
            port_number = self.__proxy[2] if self.__proxy[2] is not None else 1080
            _org_socket.connect(self, (self.__proxy[1], port_number))
            self.__negotiatesocks4(destination_pair[0], destination_pair[1])

        elif self.__proxy[0] == proxy_type_http:
            port_number = self.__proxy[2] if self.__proxy[2] is not None else 8080
            try:
                _org_socket.connect(self, (self.__proxy[1], port_number))
            except socket.error as e:
                # ENETUNREACH, WSAENETUNREACH
                if e[0] in [101, 10051]:
                    raise GeneralProxyError((7, _generalerrors[7]))
                # ECONNREFUSED, WSAECONNREFUSED
                if e[0] in [111, 10061]:
                    raise GeneralProxyError((8, _generalerrors[8]))
                # EHOSTUNREACH, WSAEHOSTUNREACH
                if e[0] in [113, 10065]:
                    raise GeneralProxyError((9, _generalerrors[9]))
                raise
            self.__negotiatehttp(destination_pair[0], destination_pair[1])

        elif not self.__proxy[0]:
            _org_socket.connect(self, (destination_pair[0], destination_pair[1]))
        else:
            raise GeneralProxyError((4, _generalerrors[4]))

    def resolve(self, host):
        if self.__proxy[0] == proxy_type_socks5:
            port_number = self.__proxy[2] if self.__proxy[2] is not None else 1080
            _org_socket.connect(self, (self.__proxy[1], port_number))
            self.__negotiatesocks5()
            return self.__resolvesocks5(host)
        else:
            return None
