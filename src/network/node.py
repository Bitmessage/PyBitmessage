import socket
import protocol

class Node (object):
    TYPE_IPV4 = 1
    TYPE_IPV6 = 2
    TYPE_ONION = 3
    TYPE_LOCAL = 4
    TYPE_LOOPBACK = 8
    TYPE_UNDEF = 12

    def __init__(self, services, address, port):
        self.services = services
        self.address, self.addressType = Node.decodeIPAddress(address)
        self.port = port

    def isLocal(self):
        return self.addressType | Node.TYPE_LOCAL > 0

    def isGlobal(self):
        return self.addressType <= Node.TYPE_ONION

    def isOnion(self):
        return self.addressType | Node.TYPE_ONION > 0

    def isLoopback(self):
        return self.addressType | Node.TYPE_LOOPBACK > 0

    @staticmethod
    def decodeIPAddress(host):
        if host[0:12] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
            hostStandardFormat = socket.inet_ntop(socket.AF_INET, host[12:])
            return Node.decodeIPv4Address(host[12:], hostStandardFormat)
        elif host[0:6] == '\xfd\x87\xd8\x7e\xeb\x43':
            # Onion, based on BMD/bitcoind
            hostStandardFormat = base64.b32encode(host[6:]).lower() + ".onion"
            return hostStandardFormat, Node.TYPE_ONION
        else:
            hostStandardFormat = socket.inet_ntop(socket.AF_INET6, host)
            if hostStandardFormat == "":
                # This can happen on Windows systems which are not 64-bit compatible 
                # so let us drop the IPv6 address. 
                return hostStandardFormat, Node.TYPE_IPV6|Node.TYPE_UNDEF
            return Node.decodeIPv6Address(host, hostStandardFormat)

    @staticmethod
    def decodeIPv4Address(host, hostStandardFormat):
        if host[0] == '\x7F': # 127/8
            return hostStandardFormat, Node.TYPE_IPV4|Node.TYPE_LOOPBACK
        if host[0] == '\x0A': # 10/8
            return hostStandardFormat, Node.TYPE_IPV4|Node.TYPE_LOCAL
        if host[0:2] == '\xC0\xA8': # 192.168/16
            return hostStandardFormat, Node.TYPE_IPV4|Node.TYPE_LOCAL
        if host[0:2] >= '\xAC\x10' and host[0:2] < '\xAC\x20': # 172.16/12
            return hostStandardFormat, Node.TYPE_IPV4|Node.TYPE_LOCAL
        return hostStandardFormat, Node.TYPE_IPV4

    @staticmethod
    def _checkIPv6Address(host, hostStandardFormat):
        if host == ('\x00' * 15) + '\x01':
            return hostStandardFormat, Node.TYPE_IPV6|Node.TYPE_LOOPBACK
        if host[0] == '\xFE' and (ord(host[1]) & 0xc0) == 0x80:
            return hostStandardFormat, Node.TYPE_IPV6|Node.TYPE_LOCAL
        if (ord(host[0]) & 0xfe) == 0xfc:
            return hostStandardFormat, Node.TYPE_IPV6|Node.TYPE_UNDEF
        return hostStandardFormat, Node.TYPE_IPV6
