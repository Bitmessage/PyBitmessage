# pylint: disable=too-many-ancestors
"""
src/network/tcp.py
==================
"""

import math
import random
import socket
import time

import addresses
import network.asyncore_pollchoose as asyncore
import network.connectionpool
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
from network.bmproto import BMProto
from network.dandelion import Dandelion
from network.objectracker import ObjectTracker
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
        try:
            self.local = (
                protocol.checkIPAddress(
                    protocol.encodeHost(self.destination.host), True) and
                not protocol.checkSocksIP(self.destination.host)
            )
        except socket.error:
            pass  # it's probably a hostname
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
                        (k, v) for k, v in nodes.iteritems()
                        if v["lastseen"] > int(time.time()) -
                        shared.maximumAgeOfNodesThatIAdvertiseToOthers and
                        v["rating"] >= 0 and len(k.host) <= 22
                    ]
                    # sent 250 only if the remote isn't interested in it
                    elemCount = min(
                        len(filtered),
                        maxAddrCount / 2 if n else maxAddrCount)
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
        for obj_hash, _ in bigInvList.items():
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
                connectionpool.BMConnectionPool().streams,
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
                connectionpool.BMConnectionPool().streams,
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
                connectionpool.BMConnectionPool().streams,
                False, nodeid=self.nodeid))
        self.set_state("bm_header", expectBytes=protocol.Header.size)
        return True


def bootstrap(connection_class):
    """Make bootstrapper class for connection type (connection_class)"""
    class Bootstrapper(connection_class):
        """Base class for bootstrappers"""
        _connection_base = connection_class

        def __init__(self, host, port):
            self._connection_base.__init__(self, state.Peer(host, port))
            self.close_reason = self._succeed = False

        def bm_command_addr(self):
            """
            Got addr message - the bootstrap succeed.
            Let BMProto process the addr message and switch state to 'close'
            """
            BMProto.bm_command_addr(self)
            self._succeed = True
            # pylint: disable=attribute-defined-outside-init
            self.close_reason = "Thanks for bootstrapping!"
            self.set_state("close")

        def handle_close(self):
            """
            After closing the connection switch knownnodes.knownNodesActual
            back to False if the bootstrapper failed.
            """
            self._connection_base.handle_close(self)
            if not self._succeed:
                knownnodes.knownNodesActual = False

    return Bootstrapper


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
            len(connectionpool.BMConnectionPool().inboundConnections) +
            len(connectionpool.BMConnectionPool().outboundConnections) >
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
            connectionpool.BMConnectionPool().addConnection(
                TCPConnection(sock=sock))
        except socket.error:
            pass
