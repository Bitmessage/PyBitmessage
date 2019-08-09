from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function




##########################
# src/network/bmproto.py #
##########################




from future import standard_library
standard_library.install_aliases()
from builtins import map
from builtins import str
from builtins import range
from builtins import *
from past.utils import old_div
from builtins import object
import time

import protocol
import state
from addresses import calculateInventoryHash
from debug import logger
from inventory import Inventory


class BMObjectInsufficientPOWError(Exception):
    """Exception indicating the object doesn't have sufficient proof of work."""
    errorCodes = ("Insufficient proof of work")


class BMObjectInvalidDataError(Exception):
    """Exception indicating the data being parsed does not match the specification."""
    errorCodes = ("Data invalid")


class BMObjectExpiredError(Exception):
    """Exception indicating the object's lifetime has expired."""
    errorCodes = ("Object expired")


class BMObjectUnwantedStreamError(Exception):
    """Exception indicating the object is in a stream we didn't advertise as being interested in."""
    errorCodes = ("Object in unwanted stream")


class BMObjectInvalidError(Exception):
    """The object's data does not match object specification."""
    errorCodes = ("Invalid object")


class BMObjectAlreadyHaveError(Exception):
    """We received a duplicate object (one we already have)"""
    errorCodes = ("Already have this object")


class BMObject(object):
    """Bitmessage Object as a class."""
    # pylint: disable=too-many-instance-attributes

    # max TTL, 28 days and 3 hours
    maxTTL = 28 * 24 * 60 * 60 + 10800
    # min TTL, 3 hour (in the past
    minTTL = -3600

    def __init__(
            self,
            nonce,
            expiresTime,
            objectType,
            version,
            streamNumber,
            data,
            payloadOffset
    ):  # pylint: disable=too-many-arguments
        self.nonce = nonce
        self.expiresTime = expiresTime
        self.objectType = objectType
        self.version = version
        self.streamNumber = streamNumber
        self.inventoryHash = calculateInventoryHash(data)
        # copy to avoid memory issues
        self.data = bytearray(data)
        self.tag = self.data[payloadOffset:payloadOffset + 32]

    def checkProofOfWorkSufficient(self):
        """Perform a proof of work check for sufficiency."""
        # Let us check to make sure that the proof of work is sufficient.
        if not protocol.isProofOfWorkSufficient(self.data):
            logger.info('Proof of work is insufficient.')
            raise BMObjectInsufficientPOWError()

    def checkEOLSanity(self):
        """Check if object's lifetime isn't ridiculously far in the past or future."""
        # EOL sanity check
        if self.expiresTime - int(time.time()) > BMObject.maxTTL:
            logger.info(
                'This object\'s End of Life time is too far in the future. Ignoring it. Time is %i',
                self.expiresTime)
            # .. todo::  remove from download queue
            raise BMObjectExpiredError()

        if self.expiresTime - int(time.time()) < BMObject.minTTL:
            logger.info(
                'This object\'s End of Life time was too long ago. Ignoring the object. Time is %i',
                self.expiresTime)
            # .. todo::  remove from download queue
            raise BMObjectExpiredError()

    def checkStream(self):
        """Check if object's stream matches streams we are interested in"""
        if self.streamNumber not in state.streamsInWhichIAmParticipating:
            logger.debug('The streamNumber %i isn\'t one we are interested in.', self.streamNumber)
            raise BMObjectUnwantedStreamError()

    def checkAlreadyHave(self):
        """
        Check if we already have the object (so that we don't duplicate it in inventory or advertise it unnecessarily)
        """
        # if it's a stem duplicate, pretend we don't have it
        if Dandelion().hasHash(self.inventoryHash):
            return
        if self.inventoryHash in Inventory():
            raise BMObjectAlreadyHaveError()

    def checkObjectByType(self):
        """Call a object type specific check (objects can have additional checks based on their types)"""
        if self.objectType == protocol.OBJECT_GETPUBKEY:
            self.checkGetpubkey()
        elif self.objectType == protocol.OBJECT_PUBKEY:
            self.checkPubkey()
        elif self.objectType == protocol.OBJECT_MSG:
            self.checkMessage()
        elif self.objectType == protocol.OBJECT_BROADCAST:
            self.checkBroadcast()
        # other objects don't require other types of tests

    def checkMessage(self):
        """"Message" object type checks."""
        # pylint: disable=no-self-use
        return

    def checkGetpubkey(self):
        """"Getpubkey" object type checks."""
        if len(self.data) < 42:
            logger.info('getpubkey message doesn\'t contain enough data. Ignoring.')
            raise BMObjectInvalidError()

    def checkPubkey(self):
        """"Pubkey" object type checks."""
        if len(self.data) < 146 or len(self.data) > 440:  # sanity check
            logger.info('pubkey object too short or too long. Ignoring.')
            raise BMObjectInvalidError()

    def checkBroadcast(self):
        """"Broadcast" object type checks."""
        if len(self.data) < 180:
            logger.debug(
                'The payload length of this broadcast packet is unreasonably low.'
                ' Someone is probably trying funny business. Ignoring message.')
            raise BMObjectInvalidError()

        # this isn't supported anymore
        if self.version < 2:
            raise BMObjectInvalidError()




###############################
# src/network/objectracker.py #
###############################




import time
from threading import RLock

from randomtrackingdict import RandomTrackingDict

haveBloom = False

try:
    # pybloomfiltermmap
    from pybloomfilter import BloomFilter
    haveBloom = True
except ImportError:
    try:
        # pybloom
        from pybloom import BloomFilter
        haveBloom = True
    except ImportError:
        pass

# it isn't actually implemented yet so no point in turning it on
haveBloom = False

# tracking pending downloads globally, for stats
missingObjects = {}


class ObjectTracker(object):
    invCleanPeriod = 300
    invInitialCapacity = 50000
    invErrorRate = 0.03
    trackingExpires = 3600
    initialTimeOffset = 60

    def __init__(self):
        self.objectsNewToMe = RandomTrackingDict()
        self.objectsNewToThem = {}
        self.objectsNewToThemLock = RLock()
        self.initInvBloom()
        self.initAddrBloom()
        self.lastCleaned = time.time()

    def initInvBloom(self):
        if haveBloom:
            # lock?
            self.invBloom = BloomFilter(capacity=ObjectTracker.invInitialCapacity,
                                        error_rate=ObjectTracker.invErrorRate)

    def initAddrBloom(self):
        if haveBloom:
            # lock?
            self.addrBloom = BloomFilter(capacity=ObjectTracker.invInitialCapacity,
                                         error_rate=ObjectTracker.invErrorRate)

    def clean(self):
        if self.lastCleaned < time.time() - ObjectTracker.invCleanPeriod:
            if haveBloom:
                if len(missingObjects) == 0:
                    self.initInvBloom()
                self.initAddrBloom()
            else:
                # release memory
                deadline = time.time() - ObjectTracker.trackingExpires
                with self.objectsNewToThemLock:
                    self.objectsNewToThem = {k: v for k, v in self.objectsNewToThem.items() if v >= deadline}
            self.lastCleaned = time.time()

    def hasObj(self, hashid):
        if haveBloom:
            return hashid in self.invBloom
        else:
            return hashid in self.objectsNewToMe

    def handleReceivedInventory(self, hashId):
        if haveBloom:
            self.invBloom.add(hashId)
        try:
            with self.objectsNewToThemLock:
                del self.objectsNewToThem[hashId]
        except KeyError:
            pass
        if hashId not in missingObjects:
            missingObjects[hashId] = time.time()
        self.objectsNewToMe[hashId] = True

    def handleReceivedObject(self, streamNumber, hashid):
        for i in list(BMConnectionPool().inboundConnections.values()) + list(BMConnectionPool().outboundConnections.values()):
            if not i.fullyEstablished:
                continue
            try:
                del i.objectsNewToMe[hashid]
            except KeyError:
                if streamNumber in i.streams and \
                    (not Dandelion().hasHash(hashid) or \
                    Dandelion().objectChildStem(hashid) == i):
                    with i.objectsNewToThemLock:
                        i.objectsNewToThem[hashid] = time.time()
                    # update stream number, which we didn't have when we just received the dinv
                    # also resets expiration of the stem mode
                    Dandelion().setHashStream(hashid, streamNumber)

            if i == self:
                try:
                    with i.objectsNewToThemLock:
                        del i.objectsNewToThem[hashid]
                except KeyError:
                    pass
        self.objectsNewToMe.setLastObject()

    def hasAddr(self, addr):
        if haveBloom:
            return addr in self.invBloom

    def addAddr(self, hashid):
        if haveBloom:
            self.addrBloom.add(hashid)

# addr sending -> per node upload queue, and flush every minute or so
# inv sending -> if not in bloom, inv immediately, otherwise put into a per node upload queue and flush every minute or so
# data sending -> a simple queue

# no bloom
# - if inv arrives
#   - if we don't have it, add tracking and download queue
#   - if we do have it, remove from tracking
# tracking downloads
# - per node hash of items the node has but we don't
# tracking inv
# - per node hash of items that neither the remote node nor we have
#




##########################
# src/network/bmproto.py #
##########################




import base64
import hashlib
import socket
import struct
import time
from binascii import hexlify

import addresses
import knownnodes
import protocol
import state
from bmconfigparser import BMConfigParser
from debug import logger
from inventory import Inventory
from network.advanceddispatcher import AdvancedDispatcher
from network.node import Node
from network.proxy import ProxyError
from queues import objectProcessorQueue, portCheckerQueue, invQueue, addrQueue
from randomtrackingdict import RandomTrackingDict


class BMProtoError(ProxyError):
    """A Bitmessage Protocol Base Error"""
    errorCodes = ("Protocol error")


class BMProtoInsufficientDataError(BMProtoError):
    """A Bitmessage Protocol Insufficient Data Error"""
    errorCodes = ("Insufficient data")


class BMProtoExcessiveDataError(BMProtoError):
    """A Bitmessage Protocol Excessive Data Error"""
    errorCodes = ("Too much data")


class BMProto(AdvancedDispatcher, ObjectTracker):
    """A parser for the Bitmessage Protocol"""
    # ~1.6 MB which is the maximum possible size of an inv message.
    maxMessageSize = 1600100
    # 2**18 = 256kB is the maximum size of an object payload
    maxObjectPayloadSize = 2**18
    # protocol specification says max 1000 addresses in one addr command
    maxAddrCount = 1000
    # protocol specification says max 50000 objects in one inv command
    maxObjectCount = 50000
    # address is online if online less than this many seconds ago
    addressAlive = 10800
    # maximum time offset
    maxTimeOffset = 3600
    timeOffsetWrongCount = 0

    def __init__(self, address=None, sock=None):
        AdvancedDispatcher.__init__(self, sock)
        self.isOutbound = False
        # packet/connection from a local IP
        self.local = False
        self.pendingUpload = RandomTrackingDict()

    def bm_proto_reset(self):
        """Reset the bitmessage object parser"""
        self.magic = None
        self.command = None
        self.payloadLength = 0
        self.checksum = None
        self.payload = None
        self.invalid = False
        self.payloadOffset = 0
        self.expectBytes = protocol.Header.size
        self.object = None

    def state_bm_header(self):
        """Process incoming header"""
        self.magic, self.command, self.payloadLength, self.checksum = \
            protocol.Header.unpack(self.read_buf[:protocol.Header.size])
        self.command = self.command.rstrip('\x00')
        if self.magic != 0xE9BEB4D9:
            # skip 1 byte in order to sync
            self.set_state("bm_header", length=1)
            self.bm_proto_reset()
            logger.debug('Bad magic')
            if self.socket.type == socket.SOCK_STREAM:
                self.close_reason = "Bad magic"
                self.set_state("close")
            return False
        if self.payloadLength > BMProto.maxMessageSize:
            self.invalid = True
        self.set_state(
            "bm_command",
            length=protocol.Header.size, expectBytes=self.payloadLength)
        return True

    def state_bm_command(self):
        """Process incoming command"""
        self.payload = self.read_buf[:self.payloadLength]
        if self.checksum != hashlib.sha512(self.payload).digest()[0:4]:
            logger.debug('Bad checksum, ignoring')
            self.invalid = True
        retval = True
        if not self.fullyEstablished and self.command not in (
                "error", "version", "verack"):
            logger.error(
                'Received command %s before connection was fully'
                ' established, ignoring', self.command)
            self.invalid = True
        if not self.invalid:
            try:
                retval = getattr(
                    self, "bm_command_" + str(self.command).lower())()
            except AttributeError:
                # unimplemented command
                logger.debug('unimplemented command %s', self.command)
            except BMProtoInsufficientDataError:
                logger.debug('packet length too short, skipping')
            except BMProtoExcessiveDataError:
                logger.debug('too much data, skipping')
            except BMObjectInsufficientPOWError:
                logger.debug('insufficient PoW, skipping')
            except BMObjectInvalidDataError:
                logger.debug('object invalid data, skipping')
            except BMObjectExpiredError:
                logger.debug('object expired, skipping')
            except BMObjectUnwantedStreamError:
                logger.debug('object not in wanted stream, skipping')
            except BMObjectInvalidError:
                logger.debug('object invalid, skipping')
            except BMObjectAlreadyHaveError:
                logger.debug(
                    '%(host)s:%(port)i already got object, skipping',
                    self.destination._asdict())
            except struct.error:
                logger.debug('decoding error, skipping')
        elif self.socket.type == socket.SOCK_DGRAM:
            # broken read, ignore
            pass
        else:
            logger.debug('Closing due to invalid command %s', self.command)
            self.close_reason = "Invalid command %s" % self.command
            self.set_state("close")
            return False
        if retval:
            self.set_state("bm_header", length=self.payloadLength)
            self.bm_proto_reset()
        # else assume the command requires a different state to follow
        return True

    def decode_payload_string(self, length):
        """Read and return `length` bytes from payload"""
        value = self.payload[self.payloadOffset:self.payloadOffset + length]
        self.payloadOffset += length
        return value

    def decode_payload_varint(self):
        """Decode a varint from the payload"""
        value, offset = addresses.decodeVarint(self.payload[self.payloadOffset:])
        self.payloadOffset += offset
        return value

    def decode_payload_node(self):
        """Decode node details from the payload"""
        # protocol.checkIPAddress()
        services, host, port = self.decode_payload_content("Q16sH")
        if host[0:12] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
            host = socket.inet_ntop(socket.AF_INET, str(host[12:16]))
        elif host[0:6] == '\xfd\x87\xd8\x7e\xeb\x43':
            # Onion, based on BMD/bitcoind
            host = base64.b32encode(host[6:]).lower() + ".onion"
        else:
            host = socket.inet_ntop(socket.AF_INET6, str(host))
        if host == "":
            # This can happen on Windows systems which are not 64-bit
            # compatible so let us drop the IPv6 address.
            host = socket.inet_ntop(socket.AF_INET, str(host[12:16]))

        return Node(services, host, port)

    def decode_payload_content(self, pattern="v"):
        """
        Decode the payload depending on pattern:

        L = varint indicating the length of the next array
        l = varint indicating the length of the next item
        v = varint (or array)
        H = uint16
        I = uint32
        Q = uint64
        i = net_addr (without time and stream number)
        s = string
        0-9 = length of the next item
        , = end of array
        """

        def decode_simple(self, char="v"):
            """Decode the payload using one char pattern"""
            if char == "v":
                return self.decode_payload_varint()
            if char == "i":
                return self.decode_payload_node()
            if char == "H":
                self.payloadOffset += 2
                return struct.unpack(">H", self.payload[
                    self.payloadOffset - 2:self.payloadOffset])[0]
            if char == "I":
                self.payloadOffset += 4
                return struct.unpack(">I", self.payload[
                    self.payloadOffset - 4:self.payloadOffset])[0]
            if char == "Q":
                self.payloadOffset += 8
                return struct.unpack(">Q", self.payload[
                    self.payloadOffset - 8:self.payloadOffset])[0]

        size = None
        isArray = False

        # size
        # iterator starting from size counting to 0
        # isArray?
        # subpattern
        # position of parser in subpattern
        # retval (array)
        parserStack = [[1, 1, False, pattern, 0, []]]

        while True:
            i = parserStack[-1][3][parserStack[-1][4]]
            if i in "0123456789" and (
                size is None or parserStack[-1][3][parserStack[-1][4] - 1]
                    not in "lL"):
                try:
                    size = size * 10 + int(i)
                except TypeError:
                    size = int(i)
                isArray = False
            elif i in "Ll" and size is None:
                size = self.decode_payload_varint()
                isArray = i == "L"
            elif size is not None:
                if isArray:
                    parserStack.append([
                        size, size, isArray,
                        parserStack[-1][3][parserStack[-1][4]:], 0, []
                    ])
                    parserStack[-2][4] = len(parserStack[-2][3])
                else:
                    for j in range(parserStack[-1][4], len(parserStack[-1][3])):
                        if parserStack[-1][3][j] not in "lL0123456789":
                            break
                    parserStack.append([
                        size, size, isArray,
                        parserStack[-1][3][parserStack[-1][4]:j + 1], 0, []
                    ])
                    parserStack[-2][4] += len(parserStack[-1][3]) - 1
                size = None
                continue
            elif i == "s":
                # if parserStack[-2][2]:
                #    parserStack[-1][5].append(self.payload[
                #        self.payloadOffset:self.payloadOffset + parserStack[-1][0]])
                # else:
                parserStack[-1][5] = self.payload[
                    self.payloadOffset:self.payloadOffset + parserStack[-1][0]]
                self.payloadOffset += parserStack[-1][0]
                parserStack[-1][1] = 0
                parserStack[-1][2] = True
                # del parserStack[-1]
                size = None
            elif i in "viHIQ":
                parserStack[-1][5].append(decode_simple(
                    self, parserStack[-1][3][parserStack[-1][4]]))
                size = None
            else:
                size = None
            for depth in range(len(parserStack) - 1, -1, -1):
                parserStack[depth][4] += 1
                if parserStack[depth][4] >= len(parserStack[depth][3]):
                    parserStack[depth][1] -= 1
                    parserStack[depth][4] = 0
                    if depth > 0:
                        if parserStack[depth][2]:
                            parserStack[depth - 1][5].append(
                                parserStack[depth][5])
                        else:
                            parserStack[depth - 1][5].extend(
                                parserStack[depth][5])
                        parserStack[depth][5] = []
                    if parserStack[depth][1] <= 0:
                        if depth == 0:
                            # we're done, at depth 0 counter is at 0
                            # and pattern is done parsing
                            return parserStack[depth][5]
                        del parserStack[-1]
                        continue
                    break
                break
        if self.payloadOffset > self.payloadLength:
            logger.debug(
                'Insufficient data %i/%i',
                self.payloadOffset, self.payloadLength)
            raise BMProtoInsufficientDataError()

    def bm_command_error(self):
        """Decode an error message and log it"""
        fatalStatus, banTime, inventoryVector, errorText = \
            self.decode_payload_content("vvlsls")
        logger.error(
            '%s:%i error: %i, %s', self.destination.host,
            self.destination.port, fatalStatus, errorText)
        return True

    def bm_command_getdata(self):
        """
        Incoming request for object(s).
        If we have them and some other conditions are fulfilled,
        append them to the write queue.
        """
        items = self.decode_payload_content("l32s")
        # skip?
        now = time.time()
        if now < self.skipUntil:
            return True
        for i in items:
            self.pendingUpload[str(i)] = now
        return True

    def _command_inv(self, dandelion=False):
        items = self.decode_payload_content("l32s")

        if len(items) > BMProto.maxObjectCount:
            logger.error(
                'Too many items in %sinv message!', 'd' if dandelion else '')
            raise BMProtoExcessiveDataError()

        # ignore dinv if dandelion turned off
        if dandelion and not state.dandelion:
            return True

        for i in map(str, items):
            if i in Inventory() and not Dandelion().hasHash(i):
                continue
            if dandelion and not Dandelion().hasHash(i):
                Dandelion().addHash(i, self)
            self.handleReceivedInventory(i)

        return True

    def bm_command_inv(self):
        """Non-dandelion announce"""
        return self._command_inv(False)

    def bm_command_dinv(self):
        """Dandelion stem announce"""
        return self._command_inv(True)

    def bm_command_object(self):
        """Incoming object, process it"""
        objectOffset = self.payloadOffset
        nonce, expiresTime, objectType, version, streamNumber = \
            self.decode_payload_content("QQIvv")
        self.object = BMObject(
            nonce, expiresTime, objectType, version, streamNumber,
            self.payload, self.payloadOffset)

        if len(self.payload) - self.payloadOffset > BMProto.maxObjectPayloadSize:
            logger.info(
                'The payload length of this object is too large (%d bytes).'
                ' Ignoring it.', len(self.payload) - self.payloadOffset)
            raise BMProtoExcessiveDataError()

        try:
            self.object.checkProofOfWorkSufficient()
            self.object.checkEOLSanity()
            self.object.checkAlreadyHave()
        except (BMObjectExpiredError, BMObjectAlreadyHaveError,
                BMObjectInsufficientPOWError):
            BMProto.stopDownloadingObject(self.object.inventoryHash)
            raise
        try:
            self.object.checkStream()
        except BMObjectUnwantedStreamError:
            acceptmismatch = BMConfigParser().get(
                "inventory", "acceptmismatch")
            BMProto.stopDownloadingObject(
                self.object.inventoryHash, acceptmismatch)
            if not acceptmismatch:
                raise

        try:
            self.object.checkObjectByType()
            objectProcessorQueue.put((
                self.object.objectType, buffer(self.object.data)))
        except BMObjectInvalidError:
            BMProto.stopDownloadingObject(self.object.inventoryHash, True)
        else:
            try:
                del missingObjects[self.object.inventoryHash]
            except KeyError:
                pass

        if self.object.inventoryHash in Inventory() and Dandelion().hasHash(self.object.inventoryHash):
            Dandelion().removeHash(self.object.inventoryHash, "cycle detection")

        Inventory()[self.object.inventoryHash] = (
            self.object.objectType, self.object.streamNumber,
            buffer(self.payload[objectOffset:]), self.object.expiresTime,
            buffer(self.object.tag)
        )
        self.handleReceivedObject(
            self.object.streamNumber, self.object.inventoryHash)
        invQueue.put((
            self.object.streamNumber, self.object.inventoryHash,
            self.destination))
        return True

    def _decode_addr(self):
        return self.decode_payload_content("LQIQ16sH")

    def bm_command_addr(self):
        """Incoming addresses, process them"""
        addresses = self._decode_addr()
        for i in addresses:
            seenTime, stream, services, ip, port = i
            decodedIP = protocol.checkIPAddress(str(ip))
            if stream not in state.streamsInWhichIAmParticipating:
                continue
            if (
                decodedIP and time.time() - seenTime > 0 and
                seenTime > time.time() - BMProto.addressAlive and
                port > 0
            ):
                peer = state.Peer(decodedIP, port)
                try:
                    if knownnodes.knownNodes[stream][peer]["lastseen"] > seenTime:
                        continue
                except KeyError:
                    pass
                if len(knownnodes.knownNodes[stream]) < BMConfigParser().safeGetInt("knownnodes", "maxnodes"):
                    with knownnodes.knownNodesLock:
                        try:
                            knownnodes.knownNodes[stream][peer]["lastseen"] = seenTime
                        except (TypeError, KeyError):
                            knownnodes.knownNodes[stream][peer] = {
                                "lastseen": seenTime,
                                "rating": 0,
                                "self": False,
                            }
                addrQueue.put((stream, peer, self.destination))
        return True

    def bm_command_portcheck(self):
        """Incoming port check request, queue it."""
        portCheckerQueue.put(state.Peer(self.destination, self.peerNode.port))
        return True

    def bm_command_ping(self):
        """Incoming ping, respond to it."""
        self.append_write_buf(protocol.CreatePacket('pong'))
        return True

    def bm_command_pong(self):
        """
        Incoming pong.
        Ignore it. PyBitmessage pings connections after about 5 minutes
        of inactivity, and leaves it to the TCP stack to handle actual
        timeouts. So there is no need to do anything when a pong arrives.
        """
        # nothing really
        return True

    def bm_command_verack(self):
        """
        Incoming verack.
        If already sent my own verack, handshake is complete (except
        potentially waiting for buffers to flush), so we can continue
        to the main connection phase. If not sent verack yet,
        continue processing.
        """
        self.verackReceived = True
        if not self.verackSent:
            return True
        self.set_state(
            "tls_init" if self.isSSL else "connection_fully_established",
            length=self.payloadLength, expectBytes=0)
        return False

    def bm_command_version(self):
        """
        Incoming version.
        Parse and log, remember important things, like streams, bitfields, etc.
        """
        (self.remoteProtocolVersion, self.services, self.timestamp,
         self.sockNode, self.peerNode, self.nonce, self.userAgent,
         self.streams) = self.decode_payload_content("IQQiiQlsLv")
        self.nonce = struct.pack('>Q', self.nonce)
        self.timeOffset = self.timestamp - int(time.time())
        logger.debug('remoteProtocolVersion: %i', self.remoteProtocolVersion)
        logger.debug('services: 0x%08X', self.services)
        logger.debug('time offset: %i', self.timestamp - int(time.time()))
        logger.debug('my external IP: %s', self.sockNode.host)
        logger.debug(
            'remote node incoming address: %s:%i',
            self.destination.host, self.peerNode.port)
        logger.debug('user agent: %s', self.userAgent)
        logger.debug('streams: [%s]', ','.join(map(str, self.streams)))
        if not self.peerValidityChecks():
            # ABORT afterwards
            return True
        self.append_write_buf(protocol.CreatePacket('verack'))
        self.verackSent = True
        if not self.isOutbound:
            self.append_write_buf(protocol.assembleVersionMessage(
                self.destination.host, self.destination.port,
                BMConnectionPool().streams, True,
                nodeid=self.nodeid))
            logger.debug(
                '%(host)s:%(port)i sending version',
                self.destination._asdict())
        if ((self.services & protocol.NODE_SSL == protocol.NODE_SSL) and
                protocol.haveSSL(not self.isOutbound)):
            self.isSSL = True
        if not self.verackReceived:
            return True
        self.set_state(
            "tls_init" if self.isSSL else "connection_fully_established",
            length=self.payloadLength, expectBytes=0)
        return False

    def peerValidityChecks(self):
        """Check the validity of the peer"""
        if self.remoteProtocolVersion < 3:
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="Your is using an old protocol. Closing connection.",
                fatal=2))
            logger.debug(
                'Closing connection to old protocol version %s, node: %s',
                self.remoteProtocolVersion, self.destination)
            return False
        if self.timeOffset > BMProto.maxTimeOffset:
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="Your time is too far in the future compared to mine."
                " Closing connection.", fatal=2))
            logger.info(
                "%s's time is too far in the future (%s seconds)."
                " Closing connection to it.", self.destination, self.timeOffset)
            BMProto.timeOffsetWrongCount += 1
            return False
        elif self.timeOffset < -BMProto.maxTimeOffset:
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="Your time is too far in the past compared to mine."
                " Closing connection.", fatal=2))
            logger.info(
                "%s's time is too far in the past (timeOffset %s seconds)."
                " Closing connection to it.", self.destination, self.timeOffset)
            BMProto.timeOffsetWrongCount += 1
            return False
        else:
            BMProto.timeOffsetWrongCount = 0
        if not self.streams:
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="We don't have shared stream interests."
                " Closing connection.", fatal=2))
            logger.debug(
                'Closed connection to %s because there is no overlapping interest'
                ' in streams.', self.destination)
            return False
        if self.destination in BMConnectionPool().inboundConnections:
            try:
                if not protocol.checkSocksIP(self.destination.host):
                    self.append_write_buf(protocol.assembleErrorMessage(
                        errorText="Too many connections from your IP."
                        " Closing connection.", fatal=2))
                    logger.debug(
                        'Closed connection to %s because we are already connected'
                        ' to that IP.', self.destination)
                    return False
            except:
                pass
        if not self.isOutbound:
            # incoming from a peer we're connected to as outbound,
            # or server full report the same error to counter deanonymisation
            if (
                state.Peer(self.destination.host, self.peerNode.port) in
                BMConnectionPool().inboundConnections or
                len(BMConnectionPool().inboundConnections) +
                len(BMConnectionPool().outboundConnections) >
                BMConfigParser().safeGetInt("bitmessagesettings", "maxtotalconnections") +
                BMConfigParser().safeGetInt("bitmessagesettings", "maxbootstrapconnections")
            ):
                self.append_write_buf(protocol.assembleErrorMessage(
                    errorText="Server full, please try again later.", fatal=2))
                logger.debug(
                    'Closed connection to %s due to server full'
                    ' or duplicate inbound/outbound.', self.destination)
                return False
        if BMConnectionPool().isAlreadyConnected(
                self.nonce):
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="I'm connected to myself. Closing connection.",
                fatal=2))
            logger.debug(
                "Closed connection to %s because I'm connected to myself.",
                self.destination)
            return False

        return True

    @staticmethod
    def assembleAddr(peerList):
        """Build up a packed address"""
        if isinstance(peerList, state.Peer):
            peerList = (peerList)
        if not peerList:
            return b''
        retval = b''
        for i in range(0, len(peerList), BMProto.maxAddrCount):
            payload = addresses.encodeVarint(
                len(peerList[i:i + BMProto.maxAddrCount]))
            for address in peerList[i:i + BMProto.maxAddrCount]:
                stream, peer, timestamp = address
                payload += struct.pack(
                    '>Q', timestamp)  # 64-bit time
                payload += struct.pack('>I', stream)
                payload += struct.pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += protocol.encodeHost(peer.host)
                payload += struct.pack('>H', peer.port)  # remote port
            retval += protocol.CreatePacket('addr', payload)
        return retval

    @staticmethod
    def stopDownloadingObject(hashId, forwardAnyway=False):
        """Stop downloading an object"""
        for connection in (
            list(BMConnectionPool().inboundConnections.values()) +
            list(BMConnectionPool().outboundConnections.values())
        ):
            try:
                del connection.objectsNewToMe[hashId]
            except KeyError:
                pass
            if not forwardAnyway:
                try:
                    with connection.objectsNewToThemLock:
                        del connection.objectsNewToThem[hashId]
                except KeyError:
                    pass
        try:
            del missingObjects[hashId]
        except KeyError:
            pass

    def handle_close(self):
        """Handle close"""
        self.set_state("close")
        if not (self.accepting or self.connecting or self.connected):
            # already disconnected
            return
        try:
            logger.debug(
                '%s:%i: closing, %s', self.destination.host,
                self.destination.port, self.close_reason)
        except AttributeError:
            try:
                logger.debug(
                    '%(host)s:%(port)i: closing', self.destination._asdict())
            except AttributeError:
                logger.debug('Disconnected socket closing')
        AdvancedDispatcher.handle_close(self)


class BMStringParser(BMProto):
    """
    A special case of BMProto used by objectProcessor to send ACK
    """
    def __init__(self):
        super(BMStringParser, self).__init__()
        self.destination = state.Peer('127.0.0.1', 8444)
        self.payload = None
        ObjectTracker.__init__(self)

    def send_data(self, data):
        """Send object given by the data string"""
        # This class is introduced specially for ACK sending, please
        # change log strings if you are going to use it for something else
        self.bm_proto_reset()
        self.payload = data
        try:
            self.bm_command_object()
        except BMObjectAlreadyHaveError:
            pass  # maybe the same msg received on different nodes
        except BMObjectExpiredError:
            logger.debug(
                'Sending ACK failure (expired): %s', hexlify(data))
        except Exception as e:
            logger.debug(
                'Exception of type %s while sending ACK',
                type(e), exc_info=True)




############################
# src/network/dandelion.py #
############################




from collections import namedtuple
from random import choice, sample, expovariate
from threading import RLock
import time

import state
from debug import logging
from queues import invQueue
from singleton import Singleton

# randomise routes after 600 seconds
REASSIGN_INTERVAL = 600

# trigger fluff due to expiration
FLUFF_TRIGGER_FIXED_DELAY = 10
FLUFF_TRIGGER_MEAN_DELAY = 30

MAX_STEMS = 2

Stem = namedtuple('Stem', ['child', 'stream', 'timeout'])


@Singleton
class Dandelion(object):
    """Dandelion class for tracking stem/fluff stages."""
    def __init__(self):
        # currently assignable child stems
        self.stem = []
        # currently assigned parent <-> child mappings
        self.nodeMap = {}
        # currently existing objects in stem mode
        self.hashMap = {}
        # when to rerandomise routes
        self.refresh = time.time() + REASSIGN_INTERVAL
        self.lock = RLock()

    def poissonTimeout(self, start=None, average=0):
        """Generate deadline using Poisson distribution"""
        if start is None:
            start = time.time()
        if average == 0:
            average = FLUFF_TRIGGER_MEAN_DELAY
        return start + expovariate(1.0 / average) + FLUFF_TRIGGER_FIXED_DELAY

    def addHash(self, hashId, source=None, stream=1):
        """Add inventory vector to dandelion stem"""
        if not state.dandelion:
            return
        with self.lock:
            self.hashMap[hashId] = Stem(
                self.getNodeStem(source),
                stream,
                self.poissonTimeout())

    def setHashStream(self, hashId, stream=1):
        """
        Update stream for inventory vector (as inv/dinv commands don't
        include streams, we only learn this after receiving the object)
        """
        with self.lock:
            if hashId in self.hashMap:
                self.hashMap[hashId] = Stem(
                    self.hashMap[hashId].child,
                    stream,
                    self.poissonTimeout())

    def removeHash(self, hashId, reason="no reason specified"):
        """Switch inventory vector from stem to fluff mode"""
        logging.debug(
            "%s entering fluff mode due to %s.",
            ''.join('%02x' % ord(i) for i in hashId), reason)
        with self.lock:
            try:
                del self.hashMap[hashId]
            except KeyError:
                pass

    def hasHash(self, hashId):
        """Is inventory vector in stem mode?"""
        return hashId in self.hashMap

    def objectChildStem(self, hashId):
        """Child (i.e. next) node for an inventory vector during stem mode"""
        return self.hashMap[hashId].child

    def maybeAddStem(self, connection):
        """
        If we had too few outbound connections, add the current one to the
        current stem list. Dandelion as designed by the authors should
        always have two active stem child connections.
        """
        # fewer than MAX_STEMS outbound connections at last reshuffle?
        with self.lock:
            if len(self.stem) < MAX_STEMS:
                self.stem.append(connection)
                for k in (k for k, v in self.nodeMap.items() if v is None):
                    self.nodeMap[k] = connection
                for k, v in {
                    k: v for k, v in self.hashMap.items()
                    if v.child is None
                }.items():
                    self.hashMap[k] = Stem(
                        connection, v.stream, self.poissonTimeout())
                    invQueue.put((v.stream, k, v.child))

    def maybeRemoveStem(self, connection):
        """
        Remove current connection from the stem list (called e.g. when
        a connection is closed).
        """
        # is the stem active?
        with self.lock:
            if connection in self.stem:
                self.stem.remove(connection)
                # active mappings to pointing to the removed node
                for k in (
                    k for k, v in self.nodeMap.items() if v == connection
                ):
                    self.nodeMap[k] = None
                for k, v in {
                    k: v for k, v in self.hashMap.items()
                    if v.child == connection
                }.items():
                    self.hashMap[k] = Stem(
                        None, v.stream, self.poissonTimeout())

    def pickStem(self, parent=None):
        """
        Pick a random active stem, but not the parent one
        (the one where an object came from)
        """
        try:
            # pick a random from available stems
            stem = choice(list(range(len(self.stem))))
            if self.stem[stem] == parent:
                # one stem available and it's the parent
                if len(self.stem) == 1:
                    return None
                # else, pick the other one
                return self.stem[1 - stem]
            # all ok
            return self.stem[stem]
        except IndexError:
            # no stems available
            return None

    def getNodeStem(self, node=None):
        """
        Return child stem node for a given parent stem node
        (the mapping is static for about 10 minutes, then it reshuffles)
        """
        with self.lock:
            try:
                return self.nodeMap[node]
            except KeyError:
                self.nodeMap[node] = self.pickStem(node)
                return self.nodeMap[node]

    def expire(self):
        """Switch expired objects from stem to fluff mode"""
        with self.lock:
            deadline = time.time()
            toDelete = [
                [v.stream, k, v.child] for k, v in self.hashMap.items()
                if v.timeout < deadline
            ]

            for row in toDelete:
                self.removeHash(row[1], 'expiration')
                invQueue.put(row)
        return toDelete

    def reRandomiseStems(self):
        """Re-shuffle stem mapping (parent <-> child pairs)"""
        with self.lock:
            try:
                # random two connections
                self.stem = sample(
                    list(BMConnectionPool(
                    ).outboundConnections.values()), MAX_STEMS)
            # not enough stems available
            except ValueError:
                self.stem = list(BMConnectionPool(
                ).outboundConnections.values())
            self.nodeMap = {}
            # hashMap stays to cater for pending stems
        self.refresh = time.time() + REASSIGN_INTERVAL




#################################
# src/network/connectionpool.py #
#################################




import errno
import re
import socket
import time

from . import asyncore_pollchoose as asyncore
import helper_bootstrap
import helper_random
import knownnodes
import protocol
import state
from bmconfigparser import BMConfigParser
from .connectionchooser import chooseConnection
from debug import logger
from .proxy import Proxy
from singleton import Singleton
from .udp import UDPSocket


@Singleton
class BMConnectionPool(object):
    """Pool of all existing connections"""
    def __init__(self):
        asyncore.set_rates(
            BMConfigParser().safeGetInt(
                "bitmessagesettings", "maxdownloadrate"),
            BMConfigParser().safeGetInt(
                "bitmessagesettings", "maxuploadrate")
        )
        self.outboundConnections = {}
        self.inboundConnections = {}
        self.listeningSockets = {}
        self.udpSockets = {}
        self.streams = []
        self.lastSpawned = 0
        self.spawnWait = 2
        self.bootstrapped = False

    def connectToStream(self, streamNumber):
        """Connect to a bitmessage stream"""
        self.streams.append(streamNumber)

    def getConnectionByAddr(self, addr):
        """
        Return an (existing) connection object based on a `Peer` object
        (IP and port)
        """
        try:
            return self.inboundConnections[addr]
        except KeyError:
            pass
        try:
            return self.inboundConnections[addr.host]
        except (KeyError, AttributeError):
            pass
        try:
            return self.outboundConnections[addr]
        except KeyError:
            pass
        try:
            return self.udpSockets[addr.host]
        except (KeyError, AttributeError):
            pass
        raise KeyError

    def isAlreadyConnected(self, nodeid):
        """Check if we're already connected to this peer"""
        for i in (
            list(self.inboundConnections.values()) +
            list(self.outboundConnections.values())
        ):
            try:
                if nodeid == i.nodeid:
                    return True
            except AttributeError:
                pass
        return False

    def addConnection(self, connection):
        """Add a connection object to our internal dict"""
        if isinstance(connection, UDPSocket):
            return
        if connection.isOutbound:
            self.outboundConnections[connection.destination] = connection
        else:
            if connection.destination.host in self.inboundConnections:
                self.inboundConnections[connection.destination] = connection
            else:
                self.inboundConnections[connection.destination.host] = \
                    connection

    def removeConnection(self, connection):
        """Remove a connection from our internal dict"""
        if isinstance(connection, UDPSocket):
            del self.udpSockets[connection.listening.host]
        elif isinstance(connection, TCPServer):
            del self.listeningSockets[state.Peer(
                connection.destination.host, connection.destination.port)]
        elif connection.isOutbound:
            try:
                del self.outboundConnections[connection.destination]
            except KeyError:
                pass
        else:
            try:
                del self.inboundConnections[connection.destination]
            except KeyError:
                try:
                    del self.inboundConnections[connection.destination.host]
                except KeyError:
                    pass
        connection.handle_close()

    def getListeningIP(self):
        """What IP are we supposed to be listening on?"""
        if BMConfigParser().safeGet(
                "bitmessagesettings", "onionhostname").endswith(".onion"):
            host = BMConfigParser().safeGet(
                "bitmessagesettings", "onionbindip")
        else:
            host = '127.0.0.1'
        if (BMConfigParser().safeGetBoolean(
                "bitmessagesettings", "sockslisten") or
            BMConfigParser().safeGet(
                "bitmessagesettings", "socksproxytype") == "none"):
            # python doesn't like bind + INADDR_ANY?
            # host = socket.INADDR_ANY
            host = BMConfigParser().get("network", "bind")
        return host

    def startListening(self, bind=None):
        """Open a listening socket and start accepting connections on it"""
        if bind is None:
            bind = self.getListeningIP()
        port = BMConfigParser().safeGetInt("bitmessagesettings", "port")
        # correct port even if it changed
        ls = TCPServer(host=bind, port=port)
        self.listeningSockets[ls.destination] = ls

    def startUDPSocket(self, bind=None):
        """
        Open an UDP socket. Depending on settings, it can either only
        accept incoming UDP packets, or also be able to send them.
        """
        if bind is None:
            host = self.getListeningIP()
            udpSocket = UDPSocket(host=host, announcing=True)
        else:
            if bind is False:
                udpSocket = UDPSocket(announcing=False)
            else:
                udpSocket = UDPSocket(host=bind, announcing=True)
        self.udpSockets[udpSocket.listening.host] = udpSocket

    def loop(self):
        """Main Connectionpool's loop"""
        # defaults to empty loop if outbound connections are maxed
        spawnConnections = False
        acceptConnections = True
        if BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'dontconnect'):
            acceptConnections = False
        elif BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'sendoutgoingconnections'):
            spawnConnections = True
        socksproxytype = BMConfigParser().safeGet(
            'bitmessagesettings', 'socksproxytype', '')
        onionsocksproxytype = BMConfigParser().safeGet(
            'bitmessagesettings', 'onionsocksproxytype', '')
        if (socksproxytype[:5] == 'SOCKS' and
            not BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'sockslisten') and
            '.onion' not in BMConfigParser().safeGet(
                'bitmessagesettings', 'onionhostname', '')):
            acceptConnections = False

        if spawnConnections:
            if not knownnodes.knownNodesActual:
                helper_bootstrap.dns()
            if not self.bootstrapped:
                self.bootstrapped = True
                Proxy.proxy = (
                    BMConfigParser().safeGet(
                        'bitmessagesettings', 'sockshostname'),
                    BMConfigParser().safeGetInt(
                        'bitmessagesettings', 'socksport')
                )
                # TODO AUTH
                # TODO reset based on GUI settings changes
                try:
                    if not onionsocksproxytype.startswith("SOCKS"):
                        raise ValueError
                    Proxy.onion_proxy = (
                        BMConfigParser().safeGet(
                            'network', 'onionsockshostname', None),
                        BMConfigParser().safeGet(
                            'network', 'onionsocksport', None)
                    )
                except ValueError:
                    Proxy.onion_proxy = None
            established = sum(
                1 for c in list(self.outboundConnections.values())
                if (c.connected and c.fullyEstablished))
            pending = len(self.outboundConnections) - established
            if established < BMConfigParser().safeGetInt(
                    'bitmessagesettings', 'maxoutboundconnections'):
                for i in range(
                        state.maximumNumberOfHalfOpenConnections - pending):
                    try:
                        chosen = chooseConnection(
                            helper_random.randomchoice(self.streams))
                    except ValueError:
                        continue
                    if chosen in self.outboundConnections:
                        continue
                    if chosen.host in self.inboundConnections:
                        continue
                    # don't connect to self
                    if chosen in state.ownAddresses:
                        continue

                    try:
                        if (chosen.host.endswith(".onion") and
                                Proxy.onion_proxy is not None):
                            if onionsocksproxytype == "SOCKS5":
                                self.addConnection(Socks5BMConnection(chosen))
                            elif onionsocksproxytype == "SOCKS4a":
                                self.addConnection(Socks4aBMConnection(chosen))
                        elif socksproxytype == "SOCKS5":
                            self.addConnection(Socks5BMConnection(chosen))
                        elif socksproxytype == "SOCKS4a":
                            self.addConnection(Socks4aBMConnection(chosen))
                        else:
                            self.addConnection(TCPConnection(chosen))
                    except socket.error as e:
                        if e.errno == errno.ENETUNREACH:
                            continue

                    self.lastSpawned = time.time()
        else:
            for i in (
                list(self.inboundConnections.values()) +
                list(self.outboundConnections.values())
            ):
                # FIXME: rating will be increased after next connection
                i.handle_close()

        if acceptConnections:
            if not self.listeningSockets:
                if BMConfigParser().safeGet('network', 'bind') == '':
                    self.startListening()
                else:
                    for bind in re.sub(
                        "[^\w.]+", " ",
                        BMConfigParser().safeGet('network', 'bind')
                    ).split():
                        self.startListening(bind)
                logger.info('Listening for incoming connections.')
            if not self.udpSockets:
                if BMConfigParser().safeGet('network', 'bind') == '':
                    self.startUDPSocket()
                else:
                    for bind in re.sub(
                        "[^\w.]+", " ",
                        BMConfigParser().safeGet('network', 'bind')
                    ).split():
                        self.startUDPSocket(bind)
                    self.startUDPSocket(False)
                logger.info('Starting UDP socket(s).')
        else:
            if self.listeningSockets:
                for i in list(self.listeningSockets.values()):
                    i.close_reason = "Stopping listening"
                    i.accepting = i.connecting = i.connected = False
                logger.info('Stopped listening for incoming connections.')
            if self.udpSockets:
                for i in list(self.udpSockets.values()):
                    i.close_reason = "Stopping UDP socket"
                    i.accepting = i.connecting = i.connected = False
                logger.info('Stopped udp sockets.')

        loopTime = float(self.spawnWait)
        if self.lastSpawned < time.time() - self.spawnWait:
            loopTime = 2.0
        asyncore.loop(timeout=loopTime, count=1000)

        reaper = []
        for i in (
            list(self.inboundConnections.values()) +
            list(self.outboundConnections.values())
        ):
            minTx = time.time() - 20
            if i.fullyEstablished:
                minTx -= 300 - 20
            if i.lastTx < minTx:
                if i.fullyEstablished:
                    i.append_write_buf(protocol.CreatePacket('ping'))
                else:
                    i.close_reason = "Timeout (%is)" % (
                        time.time() - i.lastTx)
                    i.set_state("close")
        for i in (
            list(self.inboundConnections.values()) +
            list(self.outboundConnections.values()) +
            list(self.listeningSockets.values()) +
            list(self.udpSockets.values())
        ):
            if not (i.accepting or i.connecting or i.connected):
                reaper.append(i)
            else:
                try:
                    if i.state == "close":
                        reaper.append(i)
                except AttributeError:
                    pass
        for i in reaper:
            self.removeConnection(i)




######################
# src/network/tcp.py #
######################




import math
import random
import socket
import time

import addresses
from . import asyncore_pollchoose as asyncore
import helper_random
import knownnodes
import protocol
import shared
import state
from bmconfigparser import BMConfigParser
from debug import logger
from helper_random import randomBytes
from inventory import Inventory
from network.advanceddispatcher import AdvancedDispatcher
from network.socks4a import Socks4aConnection
from network.socks5 import Socks5Connection
from network.tls import TLSDispatcher
from queues import UISignalQueue, invQueue, receiveDataQueue


class TCPConnection(BMProto, TLSDispatcher):
    # pylint: disable=too-many-instance-attributes
    """

    .. todo:: Look to understand and/or fix the non-parent-init-called
    """

    def __init__(self, address=None, sock=None):
        BMProto.__init__(self, address=address, sock=sock)
        self.verackReceived = False
        self.verackSent = False
        self.streams = [0]
        self.fullyEstablished = False
        self.connectedAt = 0
        self.skipUntil = 0
        if address is None and sock is not None:
            self.destination = state.Peer(*sock.getpeername())
            self.isOutbound = False
            TLSDispatcher.__init__(self, sock, server_side=True)
            self.connectedAt = time.time()
            logger.debug(
                'Received connection from %s:%i',
                self.destination.host, self.destination.port)
            self.nodeid = randomBytes(8)
        elif address is not None and sock is not None:
            TLSDispatcher.__init__(self, sock, server_side=False)
            self.isOutbound = True
            logger.debug(
                'Outbound proxy connection to %s:%i',
                self.destination.host, self.destination.port)
        else:
            self.destination = address
            self.isOutbound = True
            self.create_socket(
                socket.AF_INET6 if ":" in address.host else socket.AF_INET,
                socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            TLSDispatcher.__init__(self, sock, server_side=False)
            self.connect(self.destination)
            logger.debug(
                'Connecting to %s:%i',
                self.destination.host, self.destination.port)
        encodedAddr = protocol.encodeHost(self.destination.host)
        self.local = all([
            protocol.checkIPAddress(encodedAddr, True),
            not protocol.checkSocksIP(self.destination.host)
        ])
        ObjectTracker.__init__(self)  # pylint: disable=non-parent-init-called
        self.bm_proto_reset()
        self.set_state("bm_header", expectBytes=protocol.Header.size)

    def antiIntersectionDelay(self, initial=False):
        """
        This is a defense against the so called intersection attacks.

        It is called when you notice peer is requesting non-existing
        objects, or right after the connection is established. It will
        estimate how long an object will take to propagate across the
        network, and skip processing "getdata" requests until then. This
        means an attacker only has one shot per IP to perform the attack.
        """
        # estimated time for a small object to propagate across the
        # whole network
        max_known_nodes = max(
            len(knownnodes.knownNodes[x]) for x in knownnodes.knownNodes)
        delay = math.ceil(math.log(max_known_nodes + 2, 20)) * (
            0.2 + invQueue.queueCount / 2.0)
        # take the stream with maximum amount of nodes
        # +2 is to avoid problems with log(0) and log(1)
        # 20 is avg connected nodes count
        # 0.2 is avg message transmission time
        if delay > 0:
            if initial:
                self.skipUntil = self.connectedAt + delay
                if self.skipUntil > time.time():
                    logger.debug(
                        'Initial skipping processing getdata for %.2fs',
                        self.skipUntil - time.time())
            else:
                logger.debug(
                    'Skipping processing getdata due to missing object'
                    ' for %.2fs', delay)
                self.skipUntil = time.time() + delay

    def state_connection_fully_established(self):
        """
        State after the bitmessage protocol handshake is completed
        (version/verack exchange, and if both side support TLS,
        the TLS handshake as well).
        """
        self.set_connection_fully_established()
        self.set_state("bm_header")
        self.bm_proto_reset()
        return True

    def set_connection_fully_established(self):
        """Initiate inventory synchronisation."""
        if not self.isOutbound and not self.local:
            shared.clientHasReceivedIncomingConnections = True
            UISignalQueue.put(('setStatusIcon', 'green'))
        UISignalQueue.put((
            'updateNetworkStatusTab',
            (self.isOutbound, True, self.destination)
        ))
        self.antiIntersectionDelay(True)
        self.fullyEstablished = True
        if self.isOutbound:
            knownnodes.increaseRating(self.destination)
            Dandelion().maybeAddStem(self)
        self.sendAddr()
        self.sendBigInv()

    def sendAddr(self):
        """Send a partial list of known addresses to peer."""
        # We are going to share a maximum number of 1000 addrs (per overlapping
        # stream) with our peer. 500 from overlapping streams, 250 from the
        # left child stream, and 250 from the right child stream.
        maxAddrCount = BMConfigParser().safeGetInt(
            "bitmessagesettings", "maxaddrperstreamsend", 500)

        templist = []
        addrs = {}
        for stream in self.streams:
            with knownnodes.knownNodesLock:
                for n, s in enumerate((stream, stream * 2, stream * 2 + 1)):
                    nodes = knownnodes.knownNodes.get(s)
                    if not nodes:
                        continue
                    # only if more recent than 3 hours
                    # and having positive or neutral rating
                    filtered = [
                        (k, v) for k, v in nodes.items()
                        if v["lastseen"] > int(time.time()) -
                        shared.maximumAgeOfNodesThatIAdvertiseToOthers and
                        v["rating"] >= 0 and len(k.host) <= 22
                    ]
                    # sent 250 only if the remote isn't interested in it
                    elemCount = min(
                        len(filtered),
                        old_div(maxAddrCount, 2) if n else maxAddrCount)
                    addrs[s] = helper_random.randomsample(filtered, elemCount)
        for substream in addrs:
            for peer, params in addrs[substream]:
                templist.append((substream, peer, params["lastseen"]))
        if templist:
            self.append_write_buf(BMProto.assembleAddr(templist))

    def sendBigInv(self):
        """
        Send hashes of all inventory objects, chunked as the protocol has
        a per-command limit.
        """
        def sendChunk():
            """Send one chunk of inv entries in one command"""
            if objectCount == 0:
                return
            logger.debug(
                'Sending huge inv message with %i objects to just this'
                ' one peer', objectCount)
            self.append_write_buf(protocol.CreatePacket(
                'inv', addresses.encodeVarint(objectCount) + payload))

        # Select all hashes for objects in this stream.
        bigInvList = {}
        for stream in self.streams:
            # may lock for a long time, but I think it's better than
            # thousands of small locks
            with self.objectsNewToThemLock:
                for objHash in Inventory().unexpired_hashes_by_stream(stream):
                    # don't advertise stem objects on bigInv
                    if Dandelion().hasHash(objHash):
                        continue
                    bigInvList[objHash] = 0
        objectCount = 0
        payload = b''
        # Now let us start appending all of these hashes together. They will be
        # sent out in a big inv message to our new peer.
        for obj_hash, _ in list(bigInvList.items()):
            payload += obj_hash
            objectCount += 1

            # Remove -1 below when sufficient time has passed for users to
            # upgrade to versions of PyBitmessage that accept inv with 50,000
            # items
            if objectCount >= BMProto.maxObjectCount - 1:
                sendChunk()
                payload = b''
                objectCount = 0

        # flush
        sendChunk()

    def handle_connect(self):
        """Callback for TCP connection being established."""
        try:
            AdvancedDispatcher.handle_connect(self)
        except socket.error as e:
            # pylint: disable=protected-access
            if e.errno in asyncore._DISCONNECTED:
                logger.debug(
                    '%s:%i: Connection failed: %s',
                    self.destination.host, self.destination.port, e)
                return
        self.nodeid = randomBytes(8)
        self.append_write_buf(
            protocol.assembleVersionMessage(
                self.destination.host, self.destination.port,
                BMConnectionPool().streams,
                False, nodeid=self.nodeid))
        self.connectedAt = time.time()
        receiveDataQueue.put(self.destination)

    def handle_read(self):
        """Callback for reading from a socket"""
        TLSDispatcher.handle_read(self)
        if self.isOutbound and self.fullyEstablished:
            for s in self.streams:
                try:
                    with knownnodes.knownNodesLock:
                        knownnodes.knownNodes[s][self.destination][
                            "lastseen"] = time.time()
                except KeyError:
                    pass
        receiveDataQueue.put(self.destination)

    def handle_write(self):
        """Callback for writing to a socket"""
        TLSDispatcher.handle_write(self)

    def handle_close(self):
        """Callback for connection being closed."""
        if self.isOutbound and not self.fullyEstablished:
            knownnodes.decreaseRating(self.destination)
        if self.fullyEstablished:
            UISignalQueue.put((
                'updateNetworkStatusTab',
                (self.isOutbound, False, self.destination)
            ))
            if self.isOutbound:
                Dandelion().maybeRemoveStem(self)
        BMProto.handle_close(self)


class Socks5BMConnection(Socks5Connection, TCPConnection):
    """SOCKS5 wrapper for TCP connections"""

    def __init__(self, address):
        Socks5Connection.__init__(self, address=address)
        TCPConnection.__init__(self, address=address, sock=self.socket)
        self.set_state("init")

    def state_proxy_handshake_done(self):
        """
        State when SOCKS5 connection succeeds, we need to send a
        Bitmessage handshake to peer.
        """
        Socks5Connection.state_proxy_handshake_done(self)
        self.nodeid = randomBytes(8)
        self.append_write_buf(
            protocol.assembleVersionMessage(
                self.destination.host, self.destination.port,
                BMConnectionPool().streams,
                False, nodeid=self.nodeid))
        self.set_state("bm_header", expectBytes=protocol.Header.size)
        return True


class Socks4aBMConnection(Socks4aConnection, TCPConnection):
    """SOCKS4a wrapper for TCP connections"""

    def __init__(self, address):
        Socks4aConnection.__init__(self, address=address)
        TCPConnection.__init__(self, address=address, sock=self.socket)
        self.set_state("init")

    def state_proxy_handshake_done(self):
        """
        State when SOCKS4a connection succeeds, we need to send a
        Bitmessage handshake to peer.
        """
        Socks4aConnection.state_proxy_handshake_done(self)
        self.nodeid = randomBytes(8)
        self.append_write_buf(
            protocol.assembleVersionMessage(
                self.destination.host, self.destination.port,
                BMConnectionPool().streams,
                False, nodeid=self.nodeid))
        self.set_state("bm_header", expectBytes=protocol.Header.size)
        return True


class TCPServer(AdvancedDispatcher):
    """TCP connection server for Bitmessage protocol"""

    def __init__(self, host='127.0.0.1', port=8444):
        if not hasattr(self, '_map'):
            AdvancedDispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        for attempt in range(50):
            try:
                if attempt > 0:
                    port = random.randint(32767, 65535)
                self.bind((host, port))
            except socket.error as e:
                if e.errno in (asyncore.EADDRINUSE, asyncore.WSAEADDRINUSE):
                    continue
            else:
                if attempt > 0:
                    BMConfigParser().set(
                        'bitmessagesettings', 'port', str(port))
                    BMConfigParser().save()
                break
        self.destination = state.Peer(host, port)
        self.bound = True
        self.listen(5)

    def is_bound(self):
        """Is the socket bound?"""
        try:
            return self.bound
        except AttributeError:
            return False

    def handle_accept(self):
        """Incoming connection callback"""
        try:
            sock = self.accept()[0]
        except (TypeError, IndexError):
            return

        state.ownAddresses[state.Peer(*sock.getsockname())] = True
        if (
            len(BMConnectionPool().inboundConnections) +
            len(BMConnectionPool().outboundConnections) >
            BMConfigParser().safeGetInt(
                'bitmessagesettings', 'maxtotalconnections') +
            BMConfigParser().safeGetInt(
                'bitmessagesettings', 'maxbootstrapconnections') + 10
        ):
            # 10 is a sort of buffer, in between it will go through
            # the version handshake and return an error to the peer
            logger.warning("Server full, dropping connection")
            sock.close()
            return
        try:
            BMConnectionPool().addConnection(
                TCPConnection(sock=sock))
        except socket.error:
            pass
