import errno
import socket
import time
import random
import re

from bmconfigparser import BMConfigParser
from debug import logger
import helper_bootstrap
from network.proxy import Proxy
import network.bmproto
import network.tcp
import network.udp
from network.connectionchooser import chooseConnection
import network.asyncore_pollchoose as asyncore
import protocol
from singleton import Singleton
import state

@Singleton
class BMConnectionPool(object):
    def __init__(self):
        asyncore.set_rates(
                BMConfigParser().safeGetInt("bitmessagesettings", "maxdownloadrate") * 1024,
                BMConfigParser().safeGetInt("bitmessagesettings", "maxuploadrate") * 1024)
        self.outboundConnections = {}
        self.inboundConnections = {}
        self.listeningSockets = {}
        self.udpSockets = {}
        self.streams = []
        self.lastSpawned = 0
        self.spawnWait = 2 
        self.bootstrapped = False

    def handleReceivedObject(self, streamNumber, hashid, connection = None):
        for i in self.inboundConnections.values() + self.outboundConnections.values():
            if not isinstance(i, network.bmproto.BMProto):
                continue
            if not i.fullyEstablished:
                continue
            try:
                with i.objectsNewToMeLock:
                    del i.objectsNewToMe[hashid]
            except KeyError:
                with i.objectsNewToThemLock:
                    i.objectsNewToThem[hashid] = time.time()
            if i == connection:
                try:
                    with i.objectsNewToThemLock:
                        del i.objectsNewToThem[hashid]
                except KeyError:
                    pass

    def connectToStream(self, streamNumber):
        self.streams.append(streamNumber)

    def getConnectionByAddr(self, addr):
        if addr in self.inboundConnections:
            return self.inboundConnections[addr]
        if addr.host in self.inboundConnections:
            return self.inboundConnections[addr.host]
        if addr in self.outboundConnections:
            return self.outboundConnections[addr]
        if addr in self.udpSockets:
            return self.udpSockets[addr]
        raise KeyError

    def isAlreadyConnected(self, nodeid):
        for i in self.inboundConnections.values() + self.outboundConnections.values():
            try:
                if nodeid == i.nodeid:
                    return True
            except AttributeError:
                pass
        return False

    def addConnection(self, connection):
        if isinstance(connection, network.udp.UDPSocket):
            return
        if connection.isOutbound:
            self.outboundConnections[connection.destination] = connection
        else:
            if connection.destination.host in self.inboundConnections:
                self.inboundConnections[connection.destination] = connection
            else:
                self.inboundConnections[connection.destination.host] = connection

    def removeConnection(self, connection):
        if isinstance(connection, network.udp.UDPSocket):
            del self.udpSockets[connection.listening.host]
        elif isinstance(connection, network.tcp.TCPServer):
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

    def getListeningIP(self):
        if BMConfigParser().safeGet("bitmessagesettings", "onionhostname").endswith(".onion"):
            host = BMConfigParser().safeGet("bitmessagesettigns", "onionbindip")
        else:
            host = '127.0.0.1'
        if BMConfigParser().safeGetBoolean("bitmessagesettings", "sockslisten") or \
                BMConfigParser().get("bitmessagesettings", "socksproxytype") == "none":
            # python doesn't like bind + INADDR_ANY?
            #host = socket.INADDR_ANY
            host = ''
        return host

    def startListening(self):
        host = self.getListeningIP()
        port = BMConfigParser().safeGetInt("bitmessagesettings", "port")
        self.listeningSockets[state.Peer(host, port)] = network.tcp.TCPServer(host=host, port=port)

    def startUDPSocket(self, bind=None):
        if bind is None:
            host = self.getListeningIP()
            udpSocket = network.udp.UDPSocket(host=host)
        else:
            udpSocket = network.udp.UDPSocket(host=bind)
        self.udpSockets[udpSocket.listening.host] = udpSocket

    def loop(self):
        # defaults to empty loop if outbound connections are maxed
        spawnConnections = False
        acceptConnections = True
        if BMConfigParser().safeGetBoolean('bitmessagesettings', 'dontconnect'):
            acceptConnections = False
        else:
            spawnConnections = True
        if BMConfigParser().safeGetBoolean('bitmessagesettings', 'sendoutgoingconnections'):
            spawnConnections = True
        if BMConfigParser().get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and \
            (not BMConfigParser().getboolean('bitmessagesettings', 'sockslisten') and \
            ".onion" not in BMConfigParser().get('bitmessagesettings', 'onionhostname')):
            acceptConnections = False

        if spawnConnections:
            if not self.bootstrapped:
                helper_bootstrap.dns()
                self.bootstrapped = True
                Proxy.proxy = (BMConfigParser().safeGet("bitmessagesettings", "sockshostname"),
                        BMConfigParser().safeGetInt("bitmessagesettings", "socksport"))
            established = sum(1 for c in self.outboundConnections.values() if (c.connected and c.fullyEstablished))
            pending = len(self.outboundConnections) - established
            if established < BMConfigParser().safeGetInt("bitmessagesettings", "maxoutboundconnections"):
                for i in range(state.maximumNumberOfHalfOpenConnections - pending):
                    try:
                        chosen = chooseConnection(random.choice(self.streams))
                    except ValueError:
                        continue
                    if chosen in self.outboundConnections:
                        continue
                    if chosen.host in self.inboundConnections:
                        continue
                    # don't connect to self
                    if chosen in state.ownAddresses:
                        continue
    
                    #for c in self.outboundConnections:
                    #    if chosen == c.destination:
                    #        continue
                    #for c in self.inboundConnections:
                    #    if chosen.host == c.destination.host:
                    #        continue
                    try:
                        if (BMConfigParser().safeGet("bitmessagesettings", "socksproxytype") == "SOCKS5"):
                            self.addConnection(network.tcp.Socks5BMConnection(chosen))
                        elif (BMConfigParser().safeGet("bitmessagesettings", "socksproxytype") == "SOCKS4a"):
                            self.addConnection(network.tcp.Socks4aBMConnection(chosen))
                        elif not chosen.host.endswith(".onion"):
                            self.addConnection(network.tcp.TCPConnection(chosen))
                    except socket.error as e:
                        if e.errno == errno.ENETUNREACH:
                            continue

                    self.lastSpawned = time.time()

        if acceptConnections:
            if not self.listeningSockets:
                self.startListening()
                logger.info('Listening for incoming connections.')
            if not self.udpSockets:
                if BMConfigParser().safeGet("network", "bind") is None:
                    self.startUDPSocket()
                else:
                    for bind in re.sub("[^\w.]+", " ", BMConfigParser().safeGet("network", "bind")).split():
                        self.startUDPSocket(bind)
                logger.info('Starting UDP socket(s).')
        else:
            if self.listeningSockets:
                for i in self.listeningSockets:
                    i.handle_close()
                logger.info('Stopped listening for incoming connections.')
            if self.udpSockets:
                for i in self.udpSockets:
                    i.handle_close()
                logger.info('Stopped udp sockets.')

        loopTime = float(self.spawnWait)
        if self.lastSpawned < time.time() - self.spawnWait:
            loopTime = 2.0
        asyncore.loop(timeout=loopTime, count=1000)

        reaper = []
        for i in self.inboundConnections.values() + self.outboundConnections.values():
            minTx = time.time() - 20
            if i.fullyEstablished:
                minTx -= 300 - 20
            if i.lastTx < minTx:
                if i.fullyEstablished:
                    i.append_write_buf(protocol.CreatePacket('ping'))
                else:
                    i.handle_close("Timeout (%is)" % (time.time() - i.lastTx))
        for i in self.inboundConnections.values() + self.outboundConnections.values() + self.listeningSockets.values() + self.udpSockets.values():
            if not (i.accepting or i.connecting or i.connected):
                reaper.append(i)
        for i in reaper:
            self.removeConnection(i)
