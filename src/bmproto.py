import hashlib
import time
import socket

from network.advanceddispatcher import AdvancedDispatcher
import network.asyncore_pollchoose as asyncore
from network.proxy import Proxy, ProxyError, GeneralProxyError
from network.socks5 import Socks5Connection, Socks5Resolver, Socks5AuthError, Socks5Error
from network.socks4a import Socks4aConnection, Socks4aResolver, Socks4aError

import addresses
import protocol

class BMProtoError(ProxyError): pass


class BMConnection(AdvancedDispatcher):
    def __init__(self, address):
        AdvancedDispatcher.__init__(self)
        self.destination = address
        self.payload = None
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(self.destination)
        print "connecting in background to %s:%i" % (self.destination[0], self.destination[1])

    def bm_proto_len_sufficient(self):
        if len(self.read_buf) < protocol.Header.size:
            print "Length below header size"
            return False
        if not self.payload:
            self.magic, self.command, self.payloadLength, self.checksum = protocol.Header.unpack(self.read_buf[:protocol.Header.size])
            self.command = self.command.rstrip('\x00')
            if self.payloadLength > 1600100:  # ~1.6 MB which is the maximum possible size of an inv message.
                return False
        if len(self.read_buf) < self.payloadLength + protocol.Header.size:
            print "Length below announced object length"
            return False
        self.payload = self.read_buf[protocol.Header.size:self.payloadLength + protocol.Header.size]
        return True

    def bm_check_command(self):
        if self.magic != 0xE9BEB4D9:
            self.set_state("crap", protocol.Header.size)
            print "Bad magic"
            self.payload = None
            return False
        if self.checksum != hashlib.sha512(self.payload).digest()[0:4]:
            self.set_state("crap", protocol.Header.size)
            self.payload = None
            print "Bad checksum"
            return False
        print "received %s (%ib)" % (self.command, self.payloadLength)
        return True

    def state_init(self):
        self.write_buf += protocol.assembleVersionMessage(self.destination[0], self.destination[1], (1,), False)
        if True:
            print "Sending version (%ib)"  % len(self.write_buf)
            self.set_state("bm_reccommand", 0)
        return False

    def state_bm_reccommand(self):
        if not self.bm_proto_len_sufficient():
            return False
        if not self.bm_check_command():
            return False
        if self.command == "version":
            self.bm_recversion()
        elif self.command == "verack":
            self.bm_recverack()
        else:
            print "unimplemented command %s" % (self.command)
        self.set_state("bm_reccommand", protocol.Header.size + self.payloadLength)
        self.payload = None
        print "buffer length = %i" % (len(self.read_buf))
        return False

    def bm_recverack(self):
        self.verackReceived = True
        return False

    def bm_recversion(self):
        self.remoteProtocolVersion, self.services, timestamp, padding1, self.myExternalIP, padding2, self.remoteNodeIncomingPort = protocol.VersionPacket.unpack(self.payload[:82])
        print "remoteProtocolVersion: %i" % (self.remoteProtocolVersion)
        print "services: %08X" % (self.services)
        print "time offset: %i" % (timestamp - int(time.time()))
        print "my external IP: %s" % (socket.inet_ntoa(self.myExternalIP))
        print "remote node incoming port: %i" % (self.remoteNodeIncomingPort)
        useragentLength, lengthofUseragentVarint = addresses.decodeVarint(self.payload[80:84])
        readPosition = 80 + lengthOfUseragentVarint
        self.userAgent = self.payload[readPosition:readPosition + useragentLength]
        readPosition += useragentLength
        print "user agent: %s" % (self.userAgent)
        return False

    def state_http_request_sent(self):
        if len(self.read_buf) > 0:
            print self.read_buf
            self.read_buf = b""
        if not self.connected:
            self.set_state("close", 0)
        return False


class Socks5BMConnection(Socks5Connection, BMConnection):
    def __init__(self, address):
        Socks5Connection.__init__(self, address=address)

    def state_socks_handshake_done(self):
        BMConnection.state_init(self)
        return False


class Socks4aBMConnection(Socks4aConnection, BMConnection):
    def __init__(self, address):
        Socks4aConnection.__init__(self, address=address)

    def state_socks_handshake_done(self):
        BMConnection.state_init(self)
        return False


if __name__ == "__main__":
    # initial fill

    for host in (("127.0.0.1", 8448),):
        direct = BMConnection(host)
        while len(asyncore.socket_map) > 0:
            print "loop, state = %s" % (direct.state)
            asyncore.loop(timeout=1, count=1)
        continue

        proxy = Socks5BMConnection(host)
        while len(asyncore.socket_map) > 0:
#            print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=1, count=1)

        proxy = Socks4aBMConnection(host)
        while len(asyncore.socket_map) > 0:
#            print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=1, count=1)
