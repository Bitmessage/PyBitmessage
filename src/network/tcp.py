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
from helper_random import randomBytes
import helper_random
from inventory import Inventory
import knownnodes
from network.advanceddispatcher import AdvancedDispatcher
from network.bmproto import BMProtoError, BMProtoInsufficientDataError, BMProtoExcessiveDataError, BMProto
from network.bmobject import BMObject, BMObjectInsufficientPOWError, BMObjectInvalidDataError, BMObjectExpiredError, BMObjectUnwantedStreamError, BMObjectInvalidError, BMObjectAlreadyHaveError
import network.connectionpool
from network.dandelion import Dandelion
from network.node import Node
import network.asyncore_pollchoose as asyncore
from network.proxy import Proxy, ProxyError, GeneralProxyError
from network.objectracker import ObjectTracker
from network.socks5 import Socks5Connection, Socks5Resolver, Socks5AuthError, Socks5Error
from network.socks4a import Socks4aConnection, Socks4aResolver, Socks4aError
from network.tls import TLSDispatcher

import addresses
from bmconfigparser import BMConfigParser
from queues import invQueue, objectProcessorQueue, portCheckerQueue, UISignalQueue, receiveDataQueue
import shared
import state
import protocol

class TCPConnection(BMProto, TLSDispatcher):
    def __init__(self, address=None, sock=None):
        BMProto.__init__(self, address=address, sock=sock)
        self.verackReceived = False
        self.verackSent = False
        self.streams = [0]
        self.fullyEstablished = False
        self.connectedAt = 0
        self.skipUntil = 0
        if address is None and sock is not None:
            self.destination = state.Peer(sock.getpeername()[0], sock.getpeername()[1])
            self.isOutbound = False
            TLSDispatcher.__init__(self, sock, server_side=True)
            self.connectedAt = time.time()
            logger.debug("Received connection from %s:%i", self.destination.host, self.destination.port)
            self.nodeid = randomBytes(8)
        elif address is not None and sock is not None:
            TLSDispatcher.__init__(self, sock, server_side=False)
            self.isOutbound = True
            logger.debug("Outbound proxy connection to %s:%i", self.destination.host, self.destination.port)
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
            logger.debug("Connecting to %s:%i", self.destination.host, self.destination.port)
        encodedAddr = protocol.encodeHost(self.destination.host)
        if protocol.checkIPAddress(encodedAddr, True) and not protocol.checkSocksIP(self.destination.host):
            self.local = True
        else:
            self.local = False
        #shared.connectedHostsList[self.destination] = 0
        ObjectTracker.__init__(self)
        self.bm_proto_reset()
        self.set_state("bm_header", expectBytes=protocol.Header.size)

    def antiIntersectionDelay(self, initial = False):
        # estimated time for a small object to propagate across the whole network
        delay = math.ceil(math.log(max(len(knownnodes.knownNodes[x]) for x in knownnodes.knownNodes) + 2, 20)) * (0.2 + invQueue.queueCount/2.0)
        # take the stream with maximum amount of nodes
        # +2 is to avoid problems with log(0) and log(1)
        # 20 is avg connected nodes count
        # 0.2 is avg message transmission time
        if delay > 0:
            if initial:
                self.skipUntil = self.connectedAt + delay
                if self.skipUntil > time.time():
                    logger.debug("Initial skipping processing getdata for %.2fs", self.skipUntil - time.time())
            else:
                logger.debug("Skipping processing getdata due to missing object for %.2fs", delay)
                self.skipUntil = time.time() + delay

    def state_connection_fully_established(self):
        self.set_connection_fully_established()
        self.set_state("bm_header")
        self.bm_proto_reset()
        return True

    def set_connection_fully_established(self):
        if not self.isOutbound and not self.local:
            shared.clientHasReceivedIncomingConnections = True
            UISignalQueue.put(('setStatusIcon', 'green'))
        UISignalQueue.put(('updateNetworkStatusTab', (self.isOutbound, True, self.destination)))
        self.antiIntersectionDelay(True)
        self.fullyEstablished = True
        if self.isOutbound:
            knownnodes.increaseRating(self.destination)
        if self.isOutbound:
            Dandelion().maybeAddStem(self)
        self.sendAddr()
        self.sendBigInv()

    def sendAddr(self):
        # We are going to share a maximum number of 1000 addrs (per overlapping
        # stream) with our peer. 500 from overlapping streams, 250 from the
        # left child stream, and 250 from the right child stream.
        maxAddrCount = BMConfigParser().safeGetInt("bitmessagesettings", "maxaddrperstreamsend", 500)

        # init
        addressCount = 0
        payload = b''

        templist = []
        addrs = {}
        for stream in self.streams:
            with knownnodes.knownNodesLock:
                if len(knownnodes.knownNodes[stream]) > 0:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream].items()
                        if v["lastseen"] > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount:
                        elemCount = maxAddrCount
                    # only if more recent than 3 hours
                    addrs[stream] = helper_random.randomsample(filtered.items(), elemCount)
                # sent 250 only if the remote isn't interested in it
                if len(knownnodes.knownNodes[stream * 2]) > 0 and stream not in self.streams:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream*2].items()
                        if v["lastseen"] > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount / 2:
                        elemCount = int(maxAddrCount / 2)
                    addrs[stream * 2] = helper_random.randomsample(filtered.items(), elemCount)
                if len(knownnodes.knownNodes[(stream * 2) + 1]) > 0 and stream not in self.streams:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream*2+1].items()
                        if v["lastseen"] > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount / 2:
                        elemCount = int(maxAddrCount / 2)
                    addrs[stream * 2 + 1] = helper_random.randomsample(filtered.items(), elemCount)
        for substream in addrs.keys():
            for peer, params in addrs[substream]:
                templist.append((substream, peer, params["lastseen"]))
        if len(templist) > 0:
            self.append_write_buf(BMProto.assembleAddr(templist))

    def sendBigInv(self):
        def sendChunk():
            if objectCount == 0:
                return
            logger.debug('Sending huge inv message with %i objects to just this one peer', objectCount)
            self.append_write_buf(protocol.CreatePacket('inv', addresses.encodeVarint(objectCount) + payload))

        # Select all hashes for objects in this stream.
        bigInvList = {}
        for stream in self.streams:
            # may lock for a long time, but I think it's better than thousands of small locks
            with self.objectsNewToThemLock:
                for objHash in Inventory().unexpired_hashes_by_stream(stream):
                    # don't advertise stem objects on bigInv
                    if Dandelion().hasHash(objHash):
                        continue
                    bigInvList[objHash] = 0
                    self.objectsNewToThem[objHash] = time.time()
        objectCount = 0
        payload = b''
        # Now let us start appending all of these hashes together. They will be
        # sent out in a big inv message to our new peer.
        for hash, storedValue in bigInvList.items():
            payload += hash
            objectCount += 1
            if objectCount >= BMProto.maxObjectCount:
                sendChunk()
                payload = b''
                objectCount = 0

        # flush
        sendChunk()

    def handle_connect(self):
        try:
            AdvancedDispatcher.handle_connect(self)
        except socket.error as e:
            if e.errno in asyncore._DISCONNECTED:
                logger.debug("%s:%i: Connection failed: %s" % (self.destination.host, self.destination.port, str(e)))
                return
        self.nodeid = randomBytes(8)
        self.append_write_buf(protocol.assembleVersionMessage(self.destination.host, self.destination.port, \
                network.connectionpool.BMConnectionPool().streams, False, nodeid=self.nodeid))
        #print "%s:%i: Sending version"  % (self.destination.host, self.destination.port)
        self.connectedAt = time.time()
        receiveDataQueue.put(self.destination)

    def handle_read(self):
        TLSDispatcher.handle_read(self)
        if self.isOutbound and self.fullyEstablished:
            for s in self.streams:
                try:
                    with knownnodes.knownNodesLock:
                        knownnodes.knownNodes[s][self.destination]["lastseen"] = time.time()
                except KeyError:
                    pass
        receiveDataQueue.put(self.destination)

    def handle_write(self):
        TLSDispatcher.handle_write(self)

    def handle_close(self):
        if self.isOutbound and not self.fullyEstablished:
            knownnodes.decreaseRating(self.destination)
        if self.fullyEstablished:
            UISignalQueue.put(('updateNetworkStatusTab', (self.isOutbound, False, self.destination)))
            if self.isOutbound:
                Dandelion().maybeRemoveStem(self)
        BMProto.handle_close(self)


class Socks5BMConnection(Socks5Connection, TCPConnection):
    def __init__(self, address):
        Socks5Connection.__init__(self, address=address)
        TCPConnection.__init__(self, address=address, sock=self.socket)
        self.set_state("init")

    def state_proxy_handshake_done(self):
        Socks5Connection.state_proxy_handshake_done(self)
        self.nodeid = randomBytes(8)
        self.append_write_buf(protocol.assembleVersionMessage(self.destination.host, self.destination.port, \
                network.connectionpool.BMConnectionPool().streams, False, nodeid=self.nodeid))
        self.set_state("bm_header", expectBytes=protocol.Header.size)
        return True


class Socks4aBMConnection(Socks4aConnection, TCPConnection):
    def __init__(self, address):
        Socks4aConnection.__init__(self, address=address)
        TCPConnection.__init__(self, address=address, sock=self.socket)
        self.set_state("init")

    def state_proxy_handshake_done(self):
        Socks4aConnection.state_proxy_handshake_done(self)
        self.nodeid = randomBytes(8)
        self.append_write_buf(protocol.assembleVersionMessage(self.destination.host, self.destination.port, \
                network.connectionpool.BMConnectionPool().streams, False, nodeid=self.nodeid))
        self.set_state("bm_header", expectBytes=protocol.Header.size)
        return True


class TCPServer(AdvancedDispatcher):
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
                    BMConfigParser().set("bitmessagesettings", "port", str(port))
                    BMConfigParser().save()
                break
        self.destination = state.Peer(host, port)
        self.bound = True
        self.listen(5)

    def is_bound(self):
        try:
            return self.bound
        except AttributeError:
            return False

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            state.ownAddresses[state.Peer(sock.getsockname()[0], sock.getsockname()[1])] = True
            if len(network.connectionpool.BMConnectionPool().inboundConnections) + \
                len(network.connectionpool.BMConnectionPool().outboundConnections) > \
                BMConfigParser().safeGetInt("bitmessagesettings", "maxtotalconnections") + \
                BMConfigParser().safeGetInt("bitmessagesettings", "maxbootstrapconnections") + 10:
                # 10 is a sort of buffer, in between it will go through the version handshake
                # and return an error to the peer
                logger.warning("Server full, dropping connection")
                sock.close()
                return
            try:
                network.connectionpool.BMConnectionPool().addConnection(TCPConnection(sock=sock))
            except socket.error:
                pass


if __name__ == "__main__":
    # initial fill

    for host in (("127.0.0.1", 8448),):
        direct = TCPConnection(host)
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
