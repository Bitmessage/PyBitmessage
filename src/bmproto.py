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
    # ~1.6 MB which is the maximum possible size of an inv message.
    maxMessageSize = 1600100

    def __init__(self, address=None, sock=None):
        AdvancedDispatcher.__init__(self, sock)
        self.verackReceived = False
        self.verackSent = False
        if address is None and sock is not None:
            self.destination = self.addr()
            self.isOutbound = False
            print "received connection in background from %s:%i" % (self.destination[0], self.destination[1])
        else:
            self.destination = address
            self.isOutbound = True
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(self.destination)
            print "connecting in background to %s:%i" % (self.destination[0], self.destination[1])

    def bm_proto_reset(self):
        self.magic = None
        self.command = None
        self.payloadLength = None
        self.checksum = None
        self.payload = None
        self.invalid = False

    def state_init(self):
        self.bm_proto_reset()
        self.write_buf += protocol.assembleVersionMessage(self.destination[0], self.destination[1], (1,), False)
        if True:
            print "Sending version (%ib)"  % len(self.write_buf)
            self.set_state("bm_header", 0)
        return False

    def state_bm_header(self):
        if len(self.read_buf) < protocol.Header.size:
            print "Length below header size"
            return False
        self.magic, self.command, self.payloadLength, self.checksum = protocol.Header.unpack(self.read_buf[:protocol.Header.size])
        self.command = self.command.rstrip('\x00')
        if self.magic != 0xE9BEB4D9:
            # skip 1 byte in order to sync
            self.bm_proto_reset()
            self.set_state("bm_header", 1)
            print "Bad magic"
        if self.payloadLength > BMConnection.maxMessageSize:
            self.invalid = True
        self.set_state("bm_command", protocol.Header.size)
        return True
        
    def state_bm_command(self):
        if len(self.read_buf) < self.payloadLength:
            print "Length below announced object length"
            return False
        print "received %s (%ib)" % (self.command, self.payloadLength)
        self.payload = self.read_buf[:self.payloadLength]
        if self.checksum != hashlib.sha512(self.payload).digest()[0:4]:
            print "Bad checksum, ignoring"
            self.invalid = True
        if not self.invalid:
            try:
                getattr(self, "bm_command_" + str(self.command))()
            except AttributeError:
                # unimplemented command
                print "unimplemented command %s" % (self.command)
        else:
            print "Skipping command %s due to invalid data" % (self.command)
        self.set_state("bm_header", self.payloadLength)
        self.bm_proto_reset()
        return True

    def bm_command_verack(self):
        self.verackReceived = True
        return True

    def bm_command_version(self):
        self.remoteProtocolVersion, self.services, self.timestamp, padding1, self.myExternalIP, padding2, self.remoteNodeIncomingPort = protocol.VersionPacket.unpack(self.payload[:protocol.VersionPacket.size])
        print "remoteProtocolVersion: %i" % (self.remoteProtocolVersion)
        print "services: %08X" % (self.services)
        print "time offset: %i" % (self.timestamp - int(time.time()))
        print "my external IP: %s" % (socket.inet_ntoa(self.myExternalIP))
        print "remote node incoming port: %i" % (self.remoteNodeIncomingPort)
        useragentLength, lengthOfUseragentVarint = addresses.decodeVarint(self.payload[80:84])
        readPosition = 80 + lengthOfUseragentVarint
        self.userAgent = self.payload[readPosition:readPosition + useragentLength]
        readPosition += useragentLength
        print "user agent: %s" % (self.userAgent)
        return True


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


class BMServer(AdvancedDispatcher):
    port = 8444

    def __init__(self, port=None):
        if not hasattr(self, '_map'):
            AdvancedDispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        if port is None:
            port = BMServer.port
        self.bind(('127.0.0.1', port))
        self.connections = 0
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            BMConnection(sock=sock)


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
