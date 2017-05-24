import base64
from binascii import hexlify
import hashlib
import math
import time
from pprint import pprint
import socket
import struct
import random
import traceback

from addresses import calculateInventoryHash
from debug import logger
from inventory import Inventory
import knownnodes
from network.advanceddispatcher import AdvancedDispatcher
from network.bmobject import BMObject, BMObjectInsufficientPOWError, BMObjectInvalidDataError, BMObjectExpiredError, BMObjectUnwantedStreamError, BMObjectInvalidError, BMObjectAlreadyHaveError
import network.connectionpool
from network.downloadqueue import DownloadQueue
from network.node import Node
import network.asyncore_pollchoose as asyncore
from network.proxy import Proxy, ProxyError, GeneralProxyError
from network.bmqueues import BMQueues
from network.socks5 import Socks5Connection, Socks5Resolver, Socks5AuthError, Socks5Error
from network.socks4a import Socks4aConnection, Socks4aResolver, Socks4aError
from network.uploadqueue import UploadQueue, UploadElem, AddrUploadQueue, ObjUploadQueue
from network.tls import TLSDispatcher

import addresses
from bmconfigparser import BMConfigParser
from queues import objectProcessorQueue
import shared
import state
import protocol

class BMProtoError(ProxyError): pass


class BMProtoInsufficientDataError(BMProtoError): pass


class BMProtoExcessiveDataError(BMProtoError): pass


class BMConnection(TLSDispatcher, BMQueues):
    # ~1.6 MB which is the maximum possible size of an inv message.
    maxMessageSize = 1600100
    # 2**18 = 256kB is the maximum size of an object payload
    maxObjectPayloadSize = 2**18
    # protocol specification says max 1000 addresses in one addr command
    maxAddrCount = 1000
    # protocol specification says max 50000 objects in one inv command
    maxObjectCount = 50000

    def __init__(self, address=None, sock=None):
        AdvancedDispatcher.__init__(self, sock)
        self.verackReceived = False
        self.verackSent = False
        self.lastTx = time.time()
        self.connectionFullyEstablished = False
        self.connectedAt = 0
        self.skipUntil = 0
        if address is None and sock is not None:
            self.destination = state.Peer(sock.getpeername()[0], sock.getpeername()[1])
            self.isOutbound = False
            TLSDispatcher.__init__(self, sock, server_side=True)
            self.connectedAt = time.time()
            print "received connection in background from %s:%i" % (self.destination.host, self.destination.port)
        else:
            self.destination = address
            self.isOutbound = True
            if ":" in address.host:
                self.create_socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            TLSDispatcher.__init__(self, sock, server_side=False)
            self.connect(self.destination)
            print "connecting in background to %s:%i" % (self.destination.host, self.destination.port)
        shared.connectedHostsList[self.destination] = 0
        BMQueues.__init__(self)

    def bm_proto_reset(self):
        self.magic = None
        self.command = None
        self.payloadLength = 0
        self.checksum = None
        self.payload = None
        self.invalid = False
        self.payloadOffset = 0
        self.object = None

    def state_init(self):
        self.bm_proto_reset()
        if self.isOutbound:
            self.append_write_buf(protocol.assembleVersionMessage(self.destination.host, self.destination.port, network.connectionpool.BMConnectionPool().streams, False))
            print "%s:%i: Sending version (%ib)"  % (self.destination.host, self.destination.port, len(self.write_buf))
        self.set_state("bm_header")
        return True

    def antiIntersectionDelay(self, initial = False):
        # estimated time for a small object to propagate across the whole network
        delay = math.ceil(math.log(max(len(knownnodes.knownNodes[x]) for x in knownnodes.knownNodes) + 2, 20)) * (0.2 + UploadQueue.queueCount/2)
        # take the stream with maximum amount of nodes
        # +2 is to avoid problems with log(0) and log(1)
        # 20 is avg connected nodes count
        # 0.2 is avg message transmission time
        if delay > 0:
            if initial:
                self.skipUntil = self.connectedAt + delay
                if self.skipUntil > time.time():
                    logger.debug("Skipping processing for %.2fs", self.skipUntil - time.time())
            else:
                logger.debug("Skipping processing due to missing object for %.2fs", self.skipUntil - time.time())
                self.skipUntil = time.time() + now

    def set_connection_fully_established(self):
        self.antiIntersectionDelay(True)
        self.connectionFullyEstablished = True
        self.sendAddr()
        self.sendBigInv()

    def state_bm_header(self):
        #print "%s:%i: header" % (self.destination.host, self.destination.port)
        if len(self.read_buf) < protocol.Header.size:
            #print "Length below header size"
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
            #print "Length below announced object length"
            return False
        print "%s:%i: command %s (%ib)" % (self.destination.host, self.destination.port, self.command, self.payloadLength)
        self.payload = self.read_buf[:self.payloadLength]
        if self.checksum != hashlib.sha512(self.payload).digest()[0:4]:
            print "Bad checksum, ignoring"
            self.invalid = True
        retval = True
        if not self.connectionFullyEstablished and self.command not in ("version", "verack"):
            logger.error("Received command %s before connection was fully established, ignoring", self.command)
            self.invalid = True
        if not self.invalid:
            try:
                retval = getattr(self, "bm_command_" + str(self.command).lower())()
            except AttributeError:
                # unimplemented command
                print "unimplemented command %s" % (self.command)
            except BMProtoInsufficientDataError:
                print "packet length too short, skipping"
            except BMProtoExcessiveDataError:
                print "too much data, skipping"
            except BMObjectInsufficientPOWError:
                print "insufficient PoW, skipping"
            except BMObjectInvalidDataError:
                print "object invalid data, skipping"
            except BMObjectExpiredError:
                print "object expired, skipping"
            except BMObjectUnwantedStreamError:
                print "object not in wanted stream, skipping"
            except BMObjectInvalidError:
                print "object invalid, skipping"
            except BMObjectAlreadyHaveError:
                print "already got object, skipping"
            except struct.error:
                print "decoding error, skipping"
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
        services, host, port = self.decode_payload_content("Q16sH")
        if host[0:12] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
            host = socket.inet_ntop(socket.AF_INET, host[12:])
        elif host[0:6] == '\xfd\x87\xd8\x7e\xeb\x43':
            # Onion, based on BMD/bitcoind
            host = base64.b32encode(host[6:]).lower() + ".onion"
        else:
            host = socket.inet_ntop(socket.AF_INET6, host)
        if host == "":
            # This can happen on Windows systems which are not 64-bit compatible 
            # so let us drop the IPv6 address. 
            host = socket.inet_ntop(socket.AF_INET, host[12:])

        return Node(services, host, port)

    def decode_payload_content(self, pattern = "v"):
        # l = varint indicating the length of the next array
        # L = varint indicating the length of the next item
        # v = varint (or array)
        # H = uint16
        # I = uint32
        # Q = uint64
        # i = net_addr (without time and stream number)
        # s = string
        # 0-9 = length of the next item
        # , = end of array

        retval = []
        size = None
        insideDigit = False
        i = 0

        while i < len(pattern):
            if pattern[i] in "0123456789" and (i == 0 or pattern[i-1] not in "lL"):
                if size is None:
                    size = 0
                size = size * 10 + int(pattern[i])
                i += 1
                continue
            elif pattern[i] == "l" and size is None:
                size = self.decode_payload_varint()
                i += 1
                continue
            elif pattern[i] == "L" and size is None:
                size = self.decode_payload_varint()
                i += 1
                continue
            if size is not None:
                if pattern[i] == "s":
                    retval.append(self.payload[self.payloadOffset:self.payloadOffset + size])
                    self.payloadOffset += size
                    i += 1
                else:
                    if "," in pattern[i:]:
                        subpattern = pattern[i:pattern.index(",")]
                    else:
                        subpattern = pattern[i:]

                    for j in range(size):
                        if pattern[i-1:i] == "L":
                            retval.extend(self.decode_payload_content(subpattern))
                        else:
                            retval.append(self.decode_payload_content(subpattern))
                    i += len(subpattern)
                size = None
            else:
                if pattern[i] == "v":
                    retval.append(self.decode_payload_varint())
                if pattern[i] == "i":
                    retval.append(self.decode_payload_node())
                if pattern[i] == "H":
                    retval.append(struct.unpack(">H", self.payload[self.payloadOffset:self.payloadOffset+2])[0])
                    self.payloadOffset += 2
                if pattern[i] == "I":
                    retval.append(struct.unpack(">I", self.payload[self.payloadOffset:self.payloadOffset+4])[0])
                    self.payloadOffset += 4
                if pattern[i] == "Q":
                    retval.append(struct.unpack(">Q", self.payload[self.payloadOffset:self.payloadOffset+8])[0])
                    self.payloadOffset += 8
                i += 1
        if self.payloadOffset > self.payloadLength:
            print "Insufficient data %i/%i" % (self.payloadOffset, self.payloadLength)
            raise BMProtoInsufficientDataError()
        return retval

    def bm_command_error(self):
        fatalStatus, banTime, inventoryVector, errorText = self.decode_payload_content("vvlsls")
        print "%s:%i error: %i, %s" % (self.destination.host, self.destination.port, fatalStatus, errorText)
        return True

    def bm_command_getdata(self):
        items = self.decode_payload_content("L32s")
#        if time.time() < self.skipUntil:
#            print "skipping getdata"
#            return True
        for i in items:
            #print "received getdata request for item %s" % (hexlify(i))
            #logger.debug('received getdata request for item:' + hexlify(i))
            #if i in ObjUploadQueue.streamElems(1):
            if False:
                self.antiIntersectionDelay()
            else:
                if i in Inventory():
                    self.append_write_buf(protocol.CreatePacket('object', Inventory()[i].payload))
                else:
                    self.antiIntersectionDelay()
                    logger.warning('%s asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. We probably cleaned it out after advertising it but before they got around to asking for it.' % (self.peer,))
        return True

    def bm_command_inv(self):
        items = self.decode_payload_content("L32s")

        if len(items) >= BMConnection.maxObjectCount:
            logger.error("Too many items in inv message!")
            raise BMProtoExcessiveDataError()
        else:
            pass
            #print "items in inv: %i" % (len(items))

        startTime = time.time()
        #advertisedSet = set()
        for i in items:
            #advertisedSet.add(i)
            self.handleReceivedObj(i)
        #objectsNewToMe = advertisedSet
        #for stream in self.streams:
            #objectsNewToMe -= Inventory().hashes_by_stream(stream)
        logger.info('inv message lists %i objects. Of those %i are new to me. It took %f seconds to figure that out.', len(items), len(self.objectsNewToMe), time.time()-startTime)

        payload = addresses.encodeVarint(len(self.objectsNewToMe)) + ''.join(self.objectsNewToMe.keys())
        self.append_write_buf(protocol.CreatePacket('getdata', payload))

#        for i in random.sample(self.objectsNewToMe, len(self.objectsNewToMe)):
#            DownloadQueue().put(i)
        return True

    def bm_command_object(self):
        objectOffset = self.payloadOffset
        nonce, expiresTime, objectType, version, streamNumber = self.decode_payload_content("QQIvv")
        self.object = BMObject(nonce, expiresTime, objectType, version, streamNumber, self.payload)

        if len(self.payload) - self.payloadOffset > BMConnection.maxObjectPayloadSize:
            logger.info('The payload length of this object is too large (%s bytes). Ignoring it.' % len(self.payload) - self.payloadOffset)
            raise BMProtoExcessiveDataError()

        self.object.checkProofOfWorkSufficient()
        self.object.checkEOLSanity()
        self.object.checkStream()

        try:
            if self.object.objectType == protocol.OBJECT_GETPUBKEY:
                self.object.checkGetpubkey()
            elif self.object.objectType == protocol.OBJECT_PUBKEY:
                self.object.checkPubkey(self.payload[self.payloadOffset:self.payloadOffset+32])
            elif self.object.objectType == protocol.OBJECT_MSG:
                self.object.checkMessage()
            elif self.object.objectType == protocol.OBJECT_BROADCAST:
                self.object.checkBroadcast(self.payload[self.payloadOffset:self.payloadOffset+32])
            # other objects don't require other types of tests
        except BMObjectAlreadyHaveError:
            pass
        else:
            Inventory()[self.object.inventoryHash] = (
                    self.object.objectType, self.object.streamNumber, self.payload[objectOffset:], self.object.expiresTime, self.object.tag)
            objectProcessorQueue.put((self.object.objectType,self.object.data))
            #DownloadQueue().task_done(self.object.inventoryHash)
            network.connectionpool.BMConnectionPool().handleReceivedObject(self, self.object.streamNumber, self.object.inventoryHash)
            #ObjUploadQueue().put(UploadElem(self.object.streamNumber, self.object.inventoryHash))
            #broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))
        return True

    def bm_command_addr(self):
        addresses = self.decode_payload_content("lQIQ16sH")
        return True

    def bm_command_ping(self):
        self.append_write_buf(protocol.CreatePacket('pong'))
        return True

    def bm_command_pong(self):
        # nothing really
        return True

    def bm_command_verack(self):
        self.verackReceived = True
        if self.verackSent:
            if self.isSSL:
                self.set_state("tls_init", self.payloadLength)
                self.bm_proto_reset()
                return False
            else:
                self.set_connection_fully_established()
                return True
        return True

    def bm_command_version(self):
        #self.remoteProtocolVersion, self.services, self.timestamp, padding1, self.myExternalIP, padding2, self.remoteNodeIncomingPort = protocol.VersionPacket.unpack(self.payload[:protocol.VersionPacket.size])
        self.remoteProtocolVersion, self.services, self.timestamp, self.sockNode, self.peerNode, self.nonce, self.userAgent, self.streams = self.decode_payload_content("IQQiiQlslv")
        self.timeOffset = self.timestamp - int(time.time())
        print "remoteProtocolVersion: %i" % (self.remoteProtocolVersion)
        print "services: %08X" % (self.services)
        print "time offset: %i" % (self.timestamp - int(time.time()))
        print "my external IP: %s" % (self.sockNode.host)
        print "remote node incoming port: %i" % (self.peerNode.port)
        print "user agent: %s" % (self.userAgent)
        if not self.peerValidityChecks():
            # TODO ABORT
            return True
        shared.connectedHostsList[self.destination] = self.streams[0]
        self.append_write_buf(protocol.CreatePacket('verack'))
        self.verackSent = True
        if not self.isOutbound:
            self.append_write_buf(protocol.assembleVersionMessage(self.destination.host, self.destination.port, network.connectionpool.BMConnectionPool().streams, True))
            print "%s:%i: Sending version (%ib)"  % (self.destination.host, self.destination.port, len(self.write_buf))
        if ((self.services & protocol.NODE_SSL == protocol.NODE_SSL) and
                protocol.haveSSL(not self.isOutbound)):
            self.isSSL = True
        if self.verackReceived:
            if self.isSSL:
                self.set_state("tls_init", self.payloadLength)
                self.bm_proto_reset()
                return False
            else:
                self.set_connection_fully_established()
                return True
        return True

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
        if self.destination in network.connectionpool.BMConnectionPool().inboundConnections:
            try:
                if not protocol.checkSocksIP(self.destination.host):
                    self.append_write_buf(protocol.assembleErrorMessage(fatal=2,
                        errorText="Too many connections from your IP. Closing connection."))
                    logger.debug ('Closed connection to %s because we are already connected to that IP.',
                        str(self.peer))
                    return False
            except:
                pass
        return True

    def sendAddr(self):
        def sendChunk():
            if addressCount == 0:
                return
            self.append_write_buf(protocol.CreatePacket('addr', \
                addresses.encodeVarint(addressCount) + payload))

        # We are going to share a maximum number of 1000 addrs (per overlapping
        # stream) with our peer. 500 from overlapping streams, 250 from the
        # left child stream, and 250 from the right child stream.
        maxAddrCount = BMConfigParser().safeGetInt("bitmessagesettings", "maxaddrperstreamsend", 500)

        # init
        addressCount = 0
        payload = b''

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
                payload += struct.pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += struct.pack('>I', stream)
                payload += struct.pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += protocol.encodeHost(HOST)
                payload += struct.pack('>H', PORT)  # remote port
                if addressCount >= BMConnection.maxAddrCount:
                    sendChunk()
                    payload = b''
                    addressCount = 0
            for (HOST, PORT), timeLastReceivedMessageFromThisNode in addrsInChildStreamLeft:
                addressCount += 1
                payload += struct.pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += struct.pack('>I', stream * 2)
                payload += struct.pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += protocol.encodeHost(HOST)
                payload += struct.pack('>H', PORT)  # remote port
                if addressCount >= BMConnection.maxAddrCount:
                    sendChunk()
                    payload = b''
                    addressCount = 0
            for (HOST, PORT), timeLastReceivedMessageFromThisNode in addrsInChildStreamRight:
                addressCount += 1
                payload += struct.pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += struct.pack('>I', (stream * 2) + 1)
                payload += struct.pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += protocol.encodeHost(HOST)
                payload += struct.pack('>H', PORT)  # remote port
                if addressCount >= BMConnection.maxAddrCount:
                    sendChunk()
                    payload = b''
                    addressCount = 0
    
        # flush
        sendChunk()

    def sendBigInv(self):
        def sendChunk():
            if objectCount == 0:
                return
            logger.debug('Sending huge inv message with %i objects to just this one peer', objectCount)
            self.append_write_buf(protocol.CreatePacket('inv', addresses.encodeVarint(objectCount) + payload))

        # Select all hashes for objects in this stream.
        bigInvList = {}
        for stream in self.streams:
            for hash in Inventory().unexpired_hashes_by_stream(stream):
                bigInvList[hash] = 0
#            for hash in ObjUploadQueue().streamHashes(stream):
#                try:
#                    del bigInvList[hash]
#                except KeyError:
#                    pass
        objectCount = 0
        payload = b''
        # Now let us start appending all of these hashes together. They will be
        # sent out in a big inv message to our new peer.
        for hash, storedValue in bigInvList.items():
            payload += hash
            objectCount += 1
            if objectCount >= BMConnection.maxObjectCount:
                self.sendChunk()
                payload = b''
                objectCount = 0

        # flush
        sendChunk()

    def handle_connect_event(self):
        try:
            asyncore.dispatcher.handle_connect_event(self)
            self.connectedAt = time.time()
        except socket.error as e:
            print "%s:%i: socket error: %s" % (self.destination.host, self.destination.port, str(e))
            self.close()

    def handle_read_event(self):
        try:
            asyncore.dispatcher.handle_read_event(self)
        except socket.error as e:
            print "%s:%i: socket error: %s" % (self.destination.host, self.destination.port, str(e))
            self.close()

    def handle_write_event(self):
        try:
            asyncore.dispatcher.handle_write_event(self)
        except socket.error as e:
            print "%s:%i: socket error: %s" % (self.destination.host, self.destination.port, str(e))
            self.close()

    def close(self, reason=None):
        if reason is None:
            print "%s:%i: closing" % (self.destination.host, self.destination.port)
            #traceback.print_stack()
        else:
            print "%s:%i: closing, %s" % (self.destination.host, self.destination.port, reason)
        network.connectionpool.BMConnectionPool().removeConnection(self)
        try:
            asyncore.dispatcher.close(self)
        except AttributeError:
            pass


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
    def __init__(self, host='127.0.0.1', port=8444):
        if not hasattr(self, '_map'):
            AdvancedDispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            network.connectionpool.BMConnectionPool().addConnection(BMConnection(sock=sock))


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
