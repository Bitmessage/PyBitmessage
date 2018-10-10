"""
src/network/connectionpool.py
=============================
"""

import errno
import re
import socket
import time
from ConfigParser import NoOptionError, NoSectionError

import helper_bootstrap
import helper_random
import knownnodes
import protocol
import state
from bmconfigparser import BMConfigParser
from debug import logger
import network.asyncore_pollchoose as asyncore
from network.connectionchooser import chooseConnection
from network.proxy import Proxy
from network.tcp import Socks4aBMConnection, Socks5BMConnection, TCPConnection, TCPServer
from network.udp import UDPSocket
from singleton import Singleton


@Singleton
class BMConnectionPool(object):
    """Pool of all existing connections"""
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        asyncore.set_rates(
            BMConfigParser().safeGetInt("bitmessagesettings", "maxdownloadrate"),
            BMConfigParser().safeGetInt("bitmessagesettings", "maxuploadrate"))
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
        """Return an (existing) connection object based on a `Peer` object (IP and port)"""
        if addr in self.inboundConnections:
            return self.inboundConnections[addr]
        try:
            if addr.host in self.inboundConnections:
                return self.inboundConnections[addr.host]
        except AttributeError:
            pass
        if addr in self.outboundConnections:
            return self.outboundConnections[addr]
        try:
            if addr.host in self.udpSockets:
                return self.udpSockets[addr.host]
        except AttributeError:
            pass
        raise KeyError

    def isAlreadyConnected(self, nodeid):
        """Check if we're already connected to this peer"""
        for i in self.inboundConnections.values() + self.outboundConnections.values():
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
                self.inboundConnections[connection.destination.host] = connection

    def removeConnection(self, connection):
        """Remove a connection from our internal dict"""
        if isinstance(connection, UDPSocket):
            del self.udpSockets[connection.listening.host]
        elif isinstance(connection, TCPServer):
            del self.listeningSockets[state.Peer(connection.destination.host, connection.destination.port)]
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
        connection.close()

    def getListeningIP(self):
        """What IP are we supposed to be listening on?"""
        # pylint: disable=no-self-use
        if BMConfigParser().safeGet("bitmessagesettings", "onionhostname").endswith(".onion"):
            host = BMConfigParser().safeGet("bitmessagesettings", "onionbindip")
        else:
            host = '127.0.0.1'
        if BMConfigParser().safeGetBoolean("bitmessagesettings", "sockslisten") or \
                BMConfigParser().get("bitmessagesettings", "socksproxytype") == "none":
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
        Open an UDP socket. Depending on settings, it can either only accept incoming UDP packets, or also be able to
        send them.
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
        """defaults to empty loop if outbound connections are maxed"""
        # pylint: disable=too-many-statements,too-many-branches,too-many-nested-blocks
        spawnConnections = False
        acceptConnections = True
        if BMConfigParser().safeGetBoolean('bitmessagesettings', 'dontconnect'):
            acceptConnections = False
        elif BMConfigParser().safeGetBoolean('bitmessagesettings', 'sendoutgoingconnections'):
            spawnConnections = True
        if BMConfigParser().get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and \
            (not BMConfigParser().getboolean('bitmessagesettings', 'sockslisten') and
             ".onion" not in BMConfigParser().get('bitmessagesettings', 'onionhostname')):
            acceptConnections = False

        if spawnConnections:
            if not knownnodes.knownNodesActual:
                helper_bootstrap.dns()
            if not self.bootstrapped:
                self.bootstrapped = True
                Proxy.proxy = (BMConfigParser().safeGet("bitmessagesettings", "sockshostname"),
                               BMConfigParser().safeGetInt("bitmessagesettings", "socksport"))
                # .. todo:: AUTH
                # .. todo:: reset based on GUI settings changes
                try:
                    if not BMConfigParser().get("network", "onionsocksproxytype").startswith("SOCKS"):
                        raise NoOptionError
                    Proxy.onionproxy = (BMConfigParser().get("network", "onionsockshostname"),
                                        BMConfigParser().getint("network", "onionsocksport"))
                except (NoOptionError, NoSectionError):
                    Proxy.onionproxy = None
            established = sum(1 for c in self.outboundConnections.values() if (c.connected and c.fullyEstablished))
            pending = len(self.outboundConnections) - established
            if established < BMConfigParser().safeGetInt("bitmessagesettings", "maxoutboundconnections"):
                for i in range(state.maximumNumberOfHalfOpenConnections - pending):
                    try:
                        chosen = chooseConnection(helper_random.randomchoice(self.streams))
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
                        if chosen.host.endswith(".onion") and Proxy.onionproxy is not None:
                            if BMConfigParser().get("network", "onionsocksproxytype") == "SOCKS5":
                                self.addConnection(Socks5BMConnection(chosen))
                            elif BMConfigParser().get("network", "onionsocksproxytype") == "SOCKS4a":
                                self.addConnection(Socks4aBMConnection(chosen))
                        elif BMConfigParser().safeGet("bitmessagesettings", "socksproxytype") == "SOCKS5":
                            self.addConnection(Socks5BMConnection(chosen))
                        elif BMConfigParser().safeGet("bitmessagesettings", "socksproxytype") == "SOCKS4a":
                            self.addConnection(Socks4aBMConnection(chosen))
                        else:
                            self.addConnection(TCPConnection(chosen))
                    except socket.error as e:
                        if e.errno == errno.ENETUNREACH:
                            continue
                    except (NoSectionError, NoOptionError):
                        # shouldn't happen
                        pass

                    self.lastSpawned = time.time()
        else:
            for i in (
                    self.inboundConnections.values() +
                    self.outboundConnections.values()
            ):
                i.set_state("close")
                # .. todo:: FIXME: rating will be increased after next connection
                i.handle_close()

        if acceptConnections:
            if not self.listeningSockets:
                if BMConfigParser().safeGet("network", "bind") == '':
                    self.startListening()
                else:
                    for bind in re.sub(r"[^\w.]+", " ", BMConfigParser().safeGet("network", "bind")).split():
                        self.startListening(bind)
                logger.info('Listening for incoming connections.')
            if not self.udpSockets:
                if BMConfigParser().safeGet("network", "bind") == '':
                    self.startUDPSocket()
                else:
                    for bind in re.sub(r"[^\w.]+", " ", BMConfigParser().safeGet("network", "bind")).split():
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

        loopTime = float(self.spawnWait)
        if self.lastSpawned < time.time() - self.spawnWait:
            loopTime = 2.0
        asyncore.loop(timeout=loopTime, count=1000)

        for i in self.inboundConnections.values() + self.outboundConnections.values():
            minTx = time.time() - 20
            if i.fullyEstablished:
                minTx -= 300 - 20
            if i.lastTx < minTx:
                if i.fullyEstablished:
                    i.append_write_buf(protocol.CreatePacket('ping'))
                else:
                    i.close_reason = "Timeout (%is)" % (time.time() - i.lastTx)
                    i.set_state("close")

        all_connections = list()
        all_connections.extend(self.inboundConnections.values())
        all_connections.extend(self.outboundConnections.values())
        all_connections.extend(self.listeningSockets.values())
        all_connections.extend(self.udpSockets.values())
        for i in all_connections:
            if not (i.accepting or i.connecting or i.connected):
                self.removeConnection(i)
            else:
                try:
                    if i.state == "close":
                        self.removeConnection(i)
                except AttributeError:
                    pass
