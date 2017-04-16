import hashlib
import time
from pprint import pprint
import socket
from struct import unpack

from network.advanceddispatcher import AdvancedDispatcher
from network.node import Node
import network.asyncore_pollchoose as asyncore
from network.proxy import Proxy, ProxyError, GeneralProxyError
from network.socks5 import Socks5Connection, Socks5Resolver, Socks5AuthError, Socks5Error
from network.socks4a import Socks4aConnection, Socks4aResolver, Socks4aError
from network.tls import TLSDispatcher

import addresses
from bmconfigparser import BMConfigParser
import shared
import protocol

class BMProtoError(ProxyError): pass


class BMConnection(TLSDispatcher):
    # ~1.6 MB which is the maximum possible size of an inv message.
    maxMessageSize = 1600100
    # protocol specification says max 1000 addresses in one addr command
    maxAddrCount = 1000
    # protocol specification says max 50000 objects in one inv command
    maxObjectCount = 50000

    def __init__(self, address=None, sock=None):
        AdvancedDispatcher.__init__(self, sock)
        self.verackReceived = False
        self.verackSent = False
        if address is None and sock is not None:
            self.destination = self.addr()
            self.isOutbound = False
            TLSDispatcher.__init__(self, sock, server_side=True)
            print "received connection in background from %s:%i" % (self.destination[0], self.destination[1])
        else:
            self.destination = address
            self.isOutbound = True
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(self.destination)
            TLSDispatcher.__init__(self, sock, server_side=False)
            print "connecting in background to %s:%i" % (self.destination[0], self.destination[1])

    def bm_proto_reset(self):
        self.magic = None
        self.command = None
        self.payloadLength = None
        self.checksum = None
        self.payload = None
        self.invalid = False
        self.payloadOffset = 0

    def state_init(self):
        self.bm_proto_reset()
        self.append_write_buf(protocol.assembleVersionMessage(self.destination[0], self.destination[1], (1,), False))
        if True:
            print "Sending version (%ib)"  % len(self.write_buf)
            self.set_state("bm_header")
        return False

    def state_bm_ready(self):
        print "doing bm ready"
        self.sendAddr()
        self.sendBigInv()
        self.set_state("bm_header")
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
        retval = True
        if not self.invalid:
            try:
                retval = getattr(self, "bm_command_" + str(self.command).lower())()
            except AttributeError:
                # unimplemented command
                print "unimplemented command %s" % (self.command)
        else:
            print "Skipping command %s due to invalid data" % (self.command)
        if retval:
            self.set_state("bm_header", self.payloadLength)
            self.bm_proto_reset()
        # else assume the command requires a different state to follow
        return True

    def decode_payload_string(self, length):
        value = self.payload[self.payloadOffset:self.payloadOffset+length]
        self.payloadOffset += length
        return value

    def decode_payload_varint(self):
        value, offset = addresses.decodeVarint(self.payload[self.payloadOffset:])
        self.payloadOffset += offset
        return value

    def decode_payload_node(self):
        services, address, port = self.decode_payload_content("Q16sH")
        return Node(services, address, port)

    def decode_payload_content(self, pattern = "v"):
        # l = varint indicating the length of the next item
        # v = varint (or array)
        # H = uint16
        # I = uint32
        # Q = uint64
        # i = net_addr (without time and stream number)
        # s = string
        # 0-9 = length of the next item
        # , = end of array

        retval = []
        size = 0
        insideDigit = False

        for i in range(len(pattern)):
            if pattern[i] in "0123456789":
                size = size * 10 + int(pattern[i])
                continue
            elif pattern[i] == "l":
                size = self.decode_payload_varint()
                continue
            if size > 0:
                innerval = []
                if pattern[i] == "s":
                    retval.append(self.payload[self.payloadOffset:self.payloadOffset + size])
                    self.payloadOffset += size
                else:
                    for j in range(size):
                        if "," in pattern[i:]:
                            retval.append(self.decode_payload_content(pattern[i:pattern.index(",")]))
                        else:
                            retval.append(self.decode_payload_content(pattern[i:]))
                size = 0
            else:
                if pattern[i] == "v":
                    retval.append(self.decode_payload_varint())
                if pattern[i] == "i":
                    retval.append(self.decode_payload_node())
                if pattern[i] == "H":
                    retval.append(unpack(">H", self.payload[self.payloadOffset:self.payloadOffset+2])[0])
                    self.payloadOffset += 2
                if pattern[i] == "I":
                    retval.append(unpack(">I", self.payload[self.payloadOffset:self.payloadOffset+4])[0])
                    self.payloadOffset += 4
                if pattern[i] == "Q":
                    retval.append(unpack(">Q", self.payload[self.payloadOffset:self.payloadOffset+8])[0])
                    self.payloadOffset += 8
        return retval

    def bm_command_error(self):
        fatalStatus, banTime, inventoryVector, errorText = self.decode_payload_content("vvlsls")

    def bm_command_getdata(self):
        items = self.decode_payload_content("l32s")
        #self.antiIntersectionDelay(True) # only handle getdata requests if we have been connected long enough
        for i in items:
            logger.debug('received getdata request for item:' + hexlify(i))
            if self.objectHashHolderInstance.hasHash(i):
                self.antiIntersectionDelay()
            else:
                if i in Inventory():
                    self.append_write_buf(protocol.CreatePacket('object', Inventory()[i].payload))
                else:
                    #self.antiIntersectionDelay()
                    logger.warning('%s asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. We probably cleaned it out after advertising it but before they got around to asking for it.' % (self.peer,))

    def bm_command_object(self):
        lengthOfTimeWeShouldUseToProcessThisMessage = shared.checkAndShareObjectWithPeers(self.payload)
        self.downloadQueue.task_done(calculateInventoryHash(self.payload))

    def bm_command_addr(self):
        addresses = self.decode_payload_content("lQbQ16sH")

    def bm_command_ping(self):
        self.append_write_buf(protocol.CreatePacket('pong'))

    def bm_command_pong(self):
        # nothing really
        pass

    def bm_command_verack(self):
        self.verackReceived = True
        if self.verackSent:
            if self.isSSL:
                self.set_state("tls_init", self.payloadLength)
            else:
                self.set_state("bm_ready", self.payloadLength)
        else:
            self.set_state("bm_header", self.payloadLength)
        self.bm_proto_reset()
        return False

    def bm_command_version(self):
        #self.remoteProtocolVersion, self.services, self.timestamp, padding1, self.myExternalIP, padding2, self.remoteNodeIncomingPort = protocol.VersionPacket.unpack(self.payload[:protocol.VersionPacket.size])
        self.remoteProtocolVersion, self.services, self.timestamp, self.sockNode, self.peerNode, self.nonce, self.userAgent, self.streams = self.decode_payload_content("IQQiiQlslv")
        self.timeOffset = self.timestamp - int(time.time())
        print "remoteProtocolVersion: %i" % (self.remoteProtocolVersion)
        print "services: %08X" % (self.services)
        print "time offset: %i" % (self.timestamp - int(time.time()))
        print "my external IP: %s" % (self.sockNode.address)
        print "remote node incoming port: %i" % (self.peerNode.port)
        print "user agent: %s" % (self.userAgent)
        if not self.peerValidityChecks():
            # TODO ABORT
            return True
        self.append_write_buf(protocol.CreatePacket('verack'))
        self.verackSent = True
        if ((self.services & protocol.NODE_SSL == protocol.NODE_SSL) and
                protocol.haveSSL(not self.isOutbound)):
            self.isSSL = True
        if self.verackReceived:
            if self.isSSL:
                self.set_state("tls_init", self.payloadLength)
            else:
                self.set_state("bm_ready", self.payloadLength)
        self.bm_proto_reset()
        return False

    def peerValidityChecks(self):
        if self.remoteProtocolVersion < 3:
            self.append_write_buf(protocol.assembleErrorMessage(fatal=2,
                errorText="Your is using an old protocol. Closing connection."))
            logger.debug ('Closing connection to old protocol version %s, node: %s',
                str(self.remoteProtocolVersion), str(self.peer))
            return False
        if self.timeOffset > 3600:
            self.append_write_buf(protocol.assembleErrorMessage(fatal=2,
                errorText="Your time is too far in the future compared to mine. Closing connection."))
            logger.info("%s's time is too far in the future (%s seconds). Closing connection to it.",
                self.peer, self.timeOffset)
            shared.timeOffsetWrongCount += 1
            return False
        elif self.timeOffset < -3600:
            self.append_write_buf(protocol.assembleErrorMessage(fatal=2,
                errorText="Your time is too far in the past compared to mine. Closing connection."))
            logger.info("%s's time is too far in the past (timeOffset %s seconds). Closing connection to it.",
                self.peer, self.timeOffset)
            shared.timeOffsetWrongCount += 1
            return False
        else:
            shared.timeOffsetWrongCount = 0
        if len(self.streams) == 0:
            self.append_write_buf(protocol.assembleErrorMessage(fatal=2,
                errorText="We don't have shared stream interests. Closing connection."))
            logger.debug ('Closed connection to %s because there is no overlapping interest in streams.',
                str(self.peer))
            return False
        return True

    def sendAddr(self):
        def sendChunk():
            if numberOfAddressesInAddrMessage == 0:
                return
            self.append_write_buf(protocol.CreatePacket('addr', \
                addresses.encodeVarint(numberOfAddressesInAddrMessage) + payload))

        # We are going to share a maximum number of 1000 addrs (per overlapping
        # stream) with our peer. 500 from overlapping streams, 250 from the
        # left child stream, and 250 from the right child stream.
        maxAddrCount = BMConfigParser().safeGetInt("bitmessagesettings", "maxaddrperstreamsend", 500)

        # init
        addressCount = 0
        payload = ''

        for stream in self.streams:
            addrsInMyStream = {}
            addrsInChildStreamLeft = {}
            addrsInChildStreamRight = {}

            with knownnodes.knownNodesLock:
                if len(knownnodes.knownNodes[stream]) > 0:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream].items()
                        if v > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount:
                        elemCount = maxAddrCount
                    # only if more recent than 3 hours
                    addrsInMyStream = random.sample(filtered.items(), elemCount)
                # sent 250 only if the remote isn't interested in it
                if len(knownnodes.knownNodes[stream * 2]) > 0 and stream not in self.streams:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream*2].items()
                        if v > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount / 2:
                        elemCount = int(maxAddrCount / 2)
                    addrsInChildStreamLeft = random.sample(filtered.items(), elemCount)
                if len(knownnodes.knownNodes[(stream * 2) + 1]) > 0 and stream not in self.streams:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream*2+1].items()
                        if v > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount / 2:
                        elemCount = int(maxAddrCount / 2)
                    addrsInChildStreamRight = random.sample(filtered.items(), elemCount)
            for (HOST, PORT), timeLastReceivedMessageFromThisNode in addrsInMyStream:
                addressCount += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', stream)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += protocol.encodeHost(HOST)
                payload += pack('>H', PORT)  # remote port
                if addressCount >= BMConnection.maxAddrCount:
                    sendChunk()
                    payload = ''
                    addressCount = 0
            for (HOST, PORT), timeLastReceivedMessageFromThisNode in addrsInChildStreamLeft:
                addressCount += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', stream * 2)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += protocol.encodeHost(HOST)
                payload += pack('>H', PORT)  # remote port
                if addressCount >= BMConnection.maxAddrCount:
                    sendChunk()
                    payload = ''
                    addressCount = 0
            for (HOST, PORT), timeLastReceivedMessageFromThisNode in addrsInChildStreamRight:
                addressCount += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', (stream * 2) + 1)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += protocol.encodeHost(HOST)
                payload += pack('>H', PORT)  # remote port
                if addressCount >= BMConnection.maxAddrCount:
                    sendChunk()
                    payload = ''
                    addressCount = 0
    
        # flush
        sendChunk()

    def sendBigInv(self):
        def sendChunk():
            if objectCount == 0:
                return
            payload = encodeVarint(objectCount) + payload
            logger.debug('Sending huge inv message with %i objects to just this one peer',
                str(numberOfObjects))
            self.append_write_buf(protocol.CreatePacket('inv', payload))

        # Select all hashes for objects in this stream.
        bigInvList = {}
        for stream in self.streams:
            for hash in Inventory().unexpired_hashes_by_stream(stream):
                if not self.objectHashHolderInstance.hasHash(hash):
                    bigInvList[hash] = 0
        objectCount = 0
        payload = ''
        # Now let us start appending all of these hashes together. They will be
        # sent out in a big inv message to our new peer.
        for hash, storedValue in bigInvList.items():
            payload += hash
            objectCount += 1
            if objectCount >= BMConnection.maxObjectCount:
                self.sendChunk()
                payload = ''
                objectCount = 0

        # flush
        sendChunk()


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
            asyncore.loop(timeout=10, count=1)
        continue

        proxy = Socks5BMConnection(host)
        while len(asyncore.socket_map) > 0:
#            print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=10, count=1)

        proxy = Socks4aBMConnection(host)
        while len(asyncore.socket_map) > 0:
#            print "loop, state = %s" % (proxy.state)
            asyncore.loop(timeout=10, count=1)
