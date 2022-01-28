"""
Class BMProto defines bitmessage's network protocol workflow.
"""

import base64
import hashlib
import logging
import re
import socket
import struct
import time
from binascii import hexlify

import addresses
import connectionpool
import knownnodes
import protocol
import state
from bmconfigparser import config
from inventory import Inventory
from network.advanceddispatcher import AdvancedDispatcher
from network.bmobject import (
    BMObject, BMObjectAlreadyHaveError, BMObjectExpiredError,
    BMObjectInsufficientPOWError, BMObjectInvalidDataError,
    BMObjectInvalidError, BMObjectUnwantedStreamError
)
from network.constants import (
    ADDRESS_ALIVE, MAX_MESSAGE_SIZE, MAX_OBJECT_COUNT,
    MAX_OBJECT_PAYLOAD_SIZE, MAX_TIME_OFFSET
)
from network.dandelion import Dandelion
from network.proxy import ProxyError
from node import Node, Peer
from objectracker import ObjectTracker, missingObjects
from queues import invQueue, objectProcessorQueue, portCheckerQueue
from randomtrackingdict import RandomTrackingDict

logger = logging.getLogger('default')


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
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    timeOffsetWrongCount = 0

    def __init__(self, address=None, sock=None):
        # pylint: disable=unused-argument, super-init-not-called
        AdvancedDispatcher.__init__(self, sock)
        self.isOutbound = False
        # packet/connection from a local IP
        self.local = False
        self.pendingUpload = RandomTrackingDict()
        # canonical identifier of network group
        self.network_group = None
        # userAgent initialization
        self.userAgent = ''

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
        if self.payloadLength > MAX_MESSAGE_SIZE:
            self.invalid = True
        self.set_state(
            "bm_command",
            length=protocol.Header.size, expectBytes=self.payloadLength)
        return True

    def state_bm_command(self):   # pylint: disable=too-many-branches
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
        value, offset = addresses.decodeVarint(
            self.payload[self.payloadOffset:])
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

    # pylint: disable=too-many-branches,too-many-statements
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
            return None

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
                    j = 0
                    for j in range(
                            parserStack[-1][4], len(parserStack[-1][3])):
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
                #        self.payloadOffset:self.payloadOffset
                #        + parserStack[-1][0]])
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
        err_values = self.decode_payload_content("vvlsls")
        fatalStatus = err_values[0]
        # banTime = err_values[1]
        # inventoryVector = err_values[2]
        errorText = err_values[3]
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
        """
        Common inv announce implementation:
        both inv and dinv depending on *dandelion* kwarg
        """
        items = self.decode_payload_content("l32s")

        if len(items) > MAX_OBJECT_COUNT:
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

        payload_len = len(self.payload) - self.payloadOffset
        if payload_len > MAX_OBJECT_PAYLOAD_SIZE:
            logger.info(
                'The payload length of this object is too large'
                ' (%d bytes). Ignoring it.', payload_len)
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
            acceptmismatch = config.get(
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

        if self.object.inventoryHash in Inventory() and Dandelion().hasHash(
                self.object.inventoryHash):
            Dandelion().removeHash(
                self.object.inventoryHash, "cycle detection")

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
        # not using services
        for seenTime, stream, _, ip, port in self._decode_addr():
            ip = str(ip)
            if (
                stream not in state.streamsInWhichIAmParticipating
                # FIXME: should check against complete list
                or ip.startswith('bootstrap')
            ):
                continue
            decodedIP = protocol.checkIPAddress(ip)
            if (
                decodedIP and time.time() - seenTime > 0
                and seenTime > time.time() - ADDRESS_ALIVE
                and port > 0
            ):
                peer = Peer(decodedIP, port)

                with knownnodes.knownNodesLock:
                    # isnew =
                    knownnodes.addKnownNode(stream, peer, seenTime)

                # since we don't track peers outside of knownnodes,
                # only spread if in knownnodes to prevent flood
                # DISABLED TO WORKAROUND FLOOD/LEAK
                # if isnew:
                #     addrQueue.put((
                #         stream, peer, seenTime, self.destination))
        return True

    def bm_command_portcheck(self):
        """Incoming port check request, queue it."""
        portCheckerQueue.put(Peer(self.destination, self.peerNode.port))
        return True

    def bm_command_ping(self):
        """Incoming ping, respond to it."""
        self.append_write_buf(protocol.CreatePacket('pong'))
        return True

    @staticmethod
    def bm_command_pong():
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
        decoded = self.decode_payload_content("IQQiiQlslv")
        (self.remoteProtocolVersion, self.services, self.timestamp,
         self.sockNode, self.peerNode, self.nonce, self.userAgent
         ) = decoded[:7]
        self.streams = decoded[7:]
        self.nonce = struct.pack('>Q', self.nonce)
        self.timeOffset = self.timestamp - int(time.time())
        logger.debug('remoteProtocolVersion: %i', self.remoteProtocolVersion)
        logger.debug('services: 0x%08X', self.services)
        logger.debug('time offset: %i', self.timeOffset)
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
        ua_valid = re.match(
            r'^/[a-zA-Z]+:[0-9]+\.?[\w\s\(\)\./:;-]*/$', self.userAgent)
        if not ua_valid:
            self.userAgent = '/INVALID:0/'
        if not self.isOutbound:
            self.append_write_buf(protocol.assembleVersionMessage(
                self.destination.host, self.destination.port,
                connectionpool.BMConnectionPool().streams, True,
                nodeid=self.nodeid))
            logger.debug(
                '%(host)s:%(port)i sending version',
                self.destination._asdict())
        if ((self.services & protocol.NODE_SSL == protocol.NODE_SSL)
           and protocol.haveSSL(not self.isOutbound)):
            self.isSSL = True
        if not self.verackReceived:
            return True
        self.set_state(
            "tls_init" if self.isSSL else "connection_fully_established",
            length=self.payloadLength, expectBytes=0)
        return False

    # pylint: disable=too-many-return-statements
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
        if self.timeOffset > MAX_TIME_OFFSET:
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="Your time is too far in the future"
                " compared to mine. Closing connection.", fatal=2))
            logger.info(
                "%s's time is too far in the future (%s seconds)."
                " Closing connection to it.",
                self.destination, self.timeOffset)
            BMProto.timeOffsetWrongCount += 1
            return False
        elif self.timeOffset < -MAX_TIME_OFFSET:
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="Your time is too far in the past compared to mine."
                " Closing connection.", fatal=2))
            logger.info(
                "%s's time is too far in the past"
                " (timeOffset %s seconds). Closing connection to it.",
                self.destination, self.timeOffset)
            BMProto.timeOffsetWrongCount += 1
            return False
        else:
            BMProto.timeOffsetWrongCount = 0
        if not self.streams:
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="We don't have shared stream interests."
                " Closing connection.", fatal=2))
            logger.debug(
                'Closed connection to %s because there is no overlapping'
                ' interest in streams.', self.destination)
            return False
        if connectionpool.BMConnectionPool().inboundConnections.get(
                self.destination):
            try:
                if not protocol.checkSocksIP(self.destination.host):
                    self.append_write_buf(protocol.assembleErrorMessage(
                        errorText="Too many connections from your IP."
                        " Closing connection.", fatal=2))
                    logger.debug(
                        'Closed connection to %s because we are already'
                        ' connected to that IP.', self.destination)
                    return False
            except Exception:  # TODO: exception types
                pass
        if not self.isOutbound:
            # incoming from a peer we're connected to as outbound,
            # or server full report the same error to counter deanonymisation
            if (
                Peer(self.destination.host, self.peerNode.port)
                in connectionpool.BMConnectionPool().inboundConnections
                or len(connectionpool.BMConnectionPool())
                > config.safeGetInt(
                    'bitmessagesettings', 'maxtotalconnections')
                + config.safeGetInt(
                    'bitmessagesettings', 'maxbootstrapconnections')
            ):
                self.append_write_buf(protocol.assembleErrorMessage(
                    errorText="Server full, please try again later.", fatal=2))
                logger.debug(
                    'Closed connection to %s due to server full'
                    ' or duplicate inbound/outbound.', self.destination)
                return False
        if connectionpool.BMConnectionPool().isAlreadyConnected(self.nonce):
            self.append_write_buf(protocol.assembleErrorMessage(
                errorText="I'm connected to myself. Closing connection.",
                fatal=2))
            logger.debug(
                "Closed connection to %s because I'm connected to myself.",
                self.destination)
            return False

        return True

    @staticmethod
    def stopDownloadingObject(hashId, forwardAnyway=False):
        """Stop downloading object *hashId*"""
        for connection in connectionpool.BMConnectionPool().connections():
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
                    '%s:%i: closing',
                    self.destination.host, self.destination.port)
            except AttributeError:
                logger.debug('Disconnected socket closing')
        AdvancedDispatcher.handle_close(self)


class BMStringParser(BMProto):
    """
    A special case of BMProto used by objectProcessor to send ACK
    """
    def __init__(self):
        super(BMStringParser, self).__init__()
        self.destination = Peer('127.0.0.1', 8444)
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
