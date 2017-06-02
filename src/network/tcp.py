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
from network.bmproto import BMProtoError, BMProtoInsufficientDataError, BMProtoExcessiveDataError, BMProto
from network.bmobject import BMObject, BMObjectInsufficientPOWError, BMObjectInvalidDataError, BMObjectExpiredError, BMObjectUnwantedStreamError, BMObjectInvalidError, BMObjectAlreadyHaveError
import network.connectionpool
from network.downloadqueue import DownloadQueue
from network.node import Node
import network.asyncore_pollchoose as asyncore
from network.proxy import Proxy, ProxyError, GeneralProxyError
from network.objectracker import ObjectTracker
from network.socks5 import Socks5Connection, Socks5Resolver, Socks5AuthError, Socks5Error
from network.socks4a import Socks4aConnection, Socks4aResolver, Socks4aError
from network.uploadqueue import UploadQueue, UploadElem, AddrUploadQueue, ObjUploadQueue
from network.tls import TLSDispatcher

import addresses
from bmconfigparser import BMConfigParser
from queues import objectProcessorQueue, portCheckerQueue, UISignalQueue
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
        UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        self.bm_proto_reset()
        self.set_state("bm_header", expectBytes=protocol.Header.size)

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
                self.skipUntil = time.time() + delay

    def set_connection_fully_established(self):
        if not self.isOutbound and not self.local:
            shared.clientHasReceivedIncomingConnections = True
            UISignalQueue.put(('setStatusIcon', 'green'))
        UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        self.antiIntersectionDelay(True)
        self.fullyEstablished = True
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
                        if v > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount:
                        elemCount = maxAddrCount
                    # only if more recent than 3 hours
                    addrs[stream] = random.sample(filtered.items(), elemCount)
                # sent 250 only if the remote isn't interested in it
                if len(knownnodes.knownNodes[stream * 2]) > 0 and stream not in self.streams:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream*2].items()
                        if v > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount / 2:
                        elemCount = int(maxAddrCount / 2)
                    addrs[stream * 2] = random.sample(filtered.items(), elemCount)
                if len(knownnodes.knownNodes[(stream * 2) + 1]) > 0 and stream not in self.streams:
                    filtered = {k: v for k, v in knownnodes.knownNodes[stream*2+1].items()
                        if v > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers)}
                    elemCount = len(filtered)
                    if elemCount > maxAddrCount / 2:
                        elemCount = int(maxAddrCount / 2)
                    addrs[stream * 2 + 1] = random.sample(filtered.items(), elemCount)
        for substream in addrs.keys():
            for peer, timestamp in addrs[substream]:
                templist.append((substream, peer, timestamp))
                if len(templist) >= BMProto.maxAddrCount:
                    self.writeQueue.put(BMProto.assembleAddr(templist))
                    templist = []
        # flush
        if len(templist) > 0:
            self.writeQueue.put(BMProto.assembleAddr(templist))

    def sendBigInv(self):
        self.receiveQueue.put(("biginv", None))

    def handle_connect_event(self):
        try:
            AdvancedDispatcher.handle_connect_event(self)
        except socket.error as e:
            if e.errno in asyncore._DISCONNECTED:
                logger.debug("%s:%i: Connection failed: %s" % (self.destination.host, self.destination.port, str(e)))
                return
        self.writeQueue.put(protocol.assembleVersionMessage(self.destination.host, self.destination.port, network.connectionpool.BMConnectionPool().streams, False))
        #print "%s:%i: Sending version"  % (self.destination.host, self.destination.port)
        self.connectedAt = time.time()

    def handle_read(self):
        try:
            TLSDispatcher.handle_read(self)
        except socket.error as e:
            logger.debug("%s:%i: Handle read fail: %s" % (self.destination.host, self.destination.port, str(e)))

    def handle_write(self):
        try:
            TLSDispatcher.handle_write(self)
        except socket.error as e:
            logger.debug("%s:%i: Handle write fail: %s" % (self.destination.host, self.destination.port, str(e)))


class Socks5BMConnection(Socks5Connection, TCPConnection):
    def __init__(self, address):
        Socks5Connection.__init__(self, address=address)

    def state_socks_handshake_done(self):
        TCPConnection.state_init(self)
        return False


class Socks4aBMConnection(Socks4aConnection, TCPConnection):
    def __init__(self, address):
        Socks4aConnection.__init__(self, address=address)

    def state_socks_handshake_done(self):
        TCPConnection.state_init(self)
        return False


class TCPServer(AdvancedDispatcher):
    def __init__(self, host='127.0.0.1', port=8444):
        if not hasattr(self, '_map'):
            AdvancedDispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.destination = state.Peer(host, port)
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            state.ownAddresses[state.Peer(sock.getsockname()[0], sock.getsockname()[1])] = True
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
