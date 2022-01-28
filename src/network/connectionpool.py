"""
`BMConnectionPool` class definition
"""
import errno
import logging
import re
import socket
import sys
import time

import asyncore_pollchoose as asyncore
import helper_random
import knownnodes
import protocol
import state
from bmconfigparser import config
from connectionchooser import chooseConnection
from node import Peer
from proxy import Proxy
from singleton import Singleton
from tcp import (
    bootstrap, Socks4aBMConnection, Socks5BMConnection,
    TCPConnection, TCPServer)
from udp import UDPSocket

logger = logging.getLogger('default')


@Singleton
class BMConnectionPool(object):
    """Pool of all existing connections"""
    # pylint: disable=too-many-instance-attributes

    trustedPeer = None
    """
    If the trustedpeer option is specified in keys.dat then this will
    contain a Peer which will be connected to instead of using the
    addresses advertised by other peers.

    The expected use case is where the user has a trusted server where
    they run a Bitmessage daemon permanently. If they then run a second
    instance of the client on a local machine periodically when they want
    to check for messages it will sync with the network a lot faster
    without compromising security.
    """

    def __init__(self):
        asyncore.set_rates(
            config.safeGetInt(
                "bitmessagesettings", "maxdownloadrate"),
            config.safeGetInt(
                "bitmessagesettings", "maxuploadrate")
        )
        self.outboundConnections = {}
        self.inboundConnections = {}
        self.listeningSockets = {}
        self.udpSockets = {}
        self.streams = []
        self._lastSpawned = 0
        self._spawnWait = 2
        self._bootstrapped = False

        trustedPeer = config.safeGet(
            'bitmessagesettings', 'trustedpeer')
        try:
            if trustedPeer:
                host, port = trustedPeer.split(':')
                self.trustedPeer = Peer(host, int(port))
        except ValueError:
            sys.exit(
                'Bad trustedpeer config setting! It should be set as'
                ' trustedpeer=<hostname>:<portnumber>'
            )

    def __len__(self):
        return len(self.outboundConnections) + len(self.inboundConnections)

    def connections(self):
        """
        Shortcut for combined list of connections from
        `inboundConnections` and `outboundConnections` dicts
        """
        return self.inboundConnections.values() + self.outboundConnections.values()

    def establishedConnections(self):
        """Shortcut for list of connections having fullyEstablished == True"""
        return [
            x for x in self.connections() if x.fullyEstablished]

    def connectToStream(self, streamNumber):
        """Connect to a bitmessage stream"""
        self.streams.append(streamNumber)
        state.streamsInWhichIAmParticipating.append(streamNumber)

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
        for i in self.connections():
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
            del self.listeningSockets[Peer(
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

    @staticmethod
    def getListeningIP():
        """What IP are we supposed to be listening on?"""
        if config.safeGet(
                "bitmessagesettings", "onionhostname").endswith(".onion"):
            host = config.safeGet(
                "bitmessagesettings", "onionbindip")
        else:
            host = '127.0.0.1'
        if (
            config.safeGetBoolean("bitmessagesettings", "sockslisten")
            or config.safeGet("bitmessagesettings", "socksproxytype")
            == "none"
        ):
            # python doesn't like bind + INADDR_ANY?
            # host = socket.INADDR_ANY
            host = config.get("network", "bind")
        return host

    def startListening(self, bind=None):
        """Open a listening socket and start accepting connections on it"""
        if bind is None:
            bind = self.getListeningIP()
        port = config.safeGetInt("bitmessagesettings", "port")
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

    def startBootstrappers(self):
        """Run the process of resolving bootstrap hostnames"""
        proxy_type = config.safeGet(
            'bitmessagesettings', 'socksproxytype')
        # A plugins may be added here
        hostname = None
        if not proxy_type or proxy_type == 'none':
            connection_base = TCPConnection
        elif proxy_type == 'SOCKS5':
            connection_base = Socks5BMConnection
            hostname = helper_random.randomchoice([
                'quzwelsuziwqgpt2.onion', None
            ])
        elif proxy_type == 'SOCKS4a':
            connection_base = Socks4aBMConnection  # FIXME: I cannot test
        else:
            # This should never happen because socksproxytype setting
            # is handled in bitmessagemain before starting the connectionpool
            return

        bootstrapper = bootstrap(connection_base)
        if not hostname:
            port = helper_random.randomchoice([8080, 8444])
            hostname = 'bootstrap%s.bitmessage.org' % port
        else:
            port = 8444
        self.addConnection(bootstrapper(hostname, port))

    def loop(self):  # pylint: disable=too-many-branches,too-many-statements
        """Main Connectionpool's loop"""
        # pylint: disable=too-many-locals
        # defaults to empty loop if outbound connections are maxed
        spawnConnections = False
        acceptConnections = True
        if config.safeGetBoolean(
                'bitmessagesettings', 'dontconnect'):
            acceptConnections = False
        elif config.safeGetBoolean(
                'bitmessagesettings', 'sendoutgoingconnections'):
            spawnConnections = True
        socksproxytype = config.safeGet(
            'bitmessagesettings', 'socksproxytype', '')
        onionsocksproxytype = config.safeGet(
            'bitmessagesettings', 'onionsocksproxytype', '')
        if (
            socksproxytype[:5] == 'SOCKS'
            and not config.safeGetBoolean(
                'bitmessagesettings', 'sockslisten')
            and '.onion' not in config.safeGet(
                'bitmessagesettings', 'onionhostname', '')
        ):
            acceptConnections = False

        # pylint: disable=too-many-nested-blocks
        if spawnConnections:
            if not knownnodes.knownNodesActual:
                self.startBootstrappers()
                knownnodes.knownNodesActual = True
            if not self._bootstrapped:
                self._bootstrapped = True
                Proxy.proxy = (
                    config.safeGet(
                        'bitmessagesettings', 'sockshostname'),
                    config.safeGetInt(
                        'bitmessagesettings', 'socksport')
                )
                # TODO AUTH
                # TODO reset based on GUI settings changes
                try:
                    if not onionsocksproxytype.startswith("SOCKS"):
                        raise ValueError
                    Proxy.onion_proxy = (
                        config.safeGet(
                            'network', 'onionsockshostname', None),
                        config.safeGet(
                            'network', 'onionsocksport', None)
                    )
                except ValueError:
                    Proxy.onion_proxy = None
            established = sum(
                1 for c in self.outboundConnections.values()
                if (c.connected and c.fullyEstablished))
            pending = len(self.outboundConnections) - established
            if established < config.safeGetInt(
                    'bitmessagesettings', 'maxoutboundconnections'):
                for i in range(
                        state.maximumNumberOfHalfOpenConnections - pending):
                    try:
                        chosen = self.trustedPeer or chooseConnection(
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
                    # don't connect to the hosts from the same
                    # network group, defense against sibyl attacks
                    host_network_group = protocol.network_group(
                        chosen.host)
                    same_group = False
                    for j in self.outboundConnections.values():
                        if host_network_group == j.network_group:
                            same_group = True
                            if chosen.host == j.destination.host:
                                knownnodes.decreaseRating(chosen)
                            break
                    if same_group:
                        continue

                    try:
                        if chosen.host.endswith(".onion") and Proxy.onion_proxy:
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

                    self._lastSpawned = time.time()
        else:
            for i in self.connections():
                # FIXME: rating will be increased after next connection
                i.handle_close()

        if acceptConnections:
            if not self.listeningSockets:
                if config.safeGet('network', 'bind') == '':
                    self.startListening()
                else:
                    for bind in re.sub(
                        r'[^\w.]+', ' ',
                        config.safeGet('network', 'bind')
                    ).split():
                        self.startListening(bind)
                logger.info('Listening for incoming connections.')
            if not self.udpSockets:
                if config.safeGet('network', 'bind') == '':
                    self.startUDPSocket()
                else:
                    for bind in re.sub(
                        r'[^\w.]+', ' ',
                        config.safeGet('network', 'bind')
                    ).split():
                        self.startUDPSocket(bind)
                    self.startUDPSocket(False)
                logger.info('Starting UDP socket(s).')
        else:
            if self.listeningSockets:
                for i in self.listeningSockets.values():
                    i.close_reason = "Stopping listening"
                    i.accepting = i.connecting = i.connected = False
                logger.info('Stopped listening for incoming connections.')
            if self.udpSockets:
                for i in self.udpSockets.values():
                    i.close_reason = "Stopping UDP socket"
                    i.accepting = i.connecting = i.connected = False
                logger.info('Stopped udp sockets.')

        loopTime = float(self._spawnWait)
        if self._lastSpawned < time.time() - self._spawnWait:
            loopTime = 2.0
        asyncore.loop(timeout=loopTime, count=1000)

        reaper = []
        for i in self.connections():
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
            self.connections()
            + self.listeningSockets.values() + self.udpSockets.values()
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
