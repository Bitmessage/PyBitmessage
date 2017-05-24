import errno
import socket
import time
import random

from bmconfigparser import BMConfigParser
from debug import logger
import helper_bootstrap
import network.bmproto
from network.connectionchooser import chooseConnection
import network.asyncore_pollchoose as asyncore
import protocol
from singleton import Singleton
import shared
import state

@Singleton
class BMConnectionPool(object):
    def __init__(self):
        asyncore.set_rates(
                BMConfigParser().safeGetInt("bitmessagesettings", "maxdownloadrate"),
                BMConfigParser().safeGetInt("bitmessagesettings", "maxuploadrate"))
        self.outboundConnections = {}
        self.inboundConnections = {}
        self.listeningSockets = {}
        self.streams = []
            
        self.bootstrapped = False

    def handleReceivedObject(self, connection, streamNumber, hashid):
        for i in self.inboundConnections.values() + self.outboundConnections.values():
            if not isinstance(i, network.bmproto.BMConnection):
                continue
            if i == connection:
                try:
                    del i.objectsNewToThem[hashid]
                except KeyError:
                    pass
            else:
                try:
                    del i.objectsNewToThem[hashid]
                except KeyError:
                    i.objectsNewToThem[hashid] = True
            try:
                del i.objectsNewToMe[hashid]
            except KeyError:
                pass

    def connectToStream(self, streamNumber):
        self.streams.append(streamNumber)

    def addConnection(self, connection):
        if connection.isOutbound:
            self.outboundConnections[connection.destination] = connection
        else:
            if connection.destination.host in self.inboundConnections:
                self.inboundConnections[connection.destination] = connection
            else:
                self.inboundConnections[connection.destination.host] = connection

    def removeConnection(self, connection):
        if connection.isOutbound:
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

    def startListening(self):
        port = BMConfigParser().safeGetInt("bitmessagesettings", "port")
        if BMConfigParser().safeGet("bitmessagesettings", "onionhostname").endswith(".onion"):
            host = BMConfigParser().safeGet("bitmessagesettigns", "onionbindip")
        else:
            host = '127.0.0.1'
        if BMConfigParser().safeGetBoolean("bitmessagesettings", "sockslisten") or \
                BMConfigParser().get("bitmessagesettings", "socksproxytype") == "none":
            host = ''
        self.listeningSockets[state.Peer(host, port)] = network.bmproto.BMServer(host=host, port=port)

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
                print "bootstrapping dns"
                helper_bootstrap.dns()
                self.bootstrapped = True
            for i in range(len(self.outboundConnections), BMConfigParser().safeGetInt("bitmessagesettings", "maxoutboundconnections")):
                chosen = chooseConnection(random.choice(self.streams))
                if chosen in self.outboundConnections:
                    continue
                if chosen.host in self.inboundConnections:
                    continue

                #for c in self.outboundConnections:
                #    if chosen == c.destination:
                #        continue
                #for c in self.inboundConnections:
                #    if chosen.host == c.destination.host:
                #        continue
                try:
                    if (BMConfigParser().safeGet("bitmessagesettings", "socksproxytype") == "SOCKS5"):
                        self.addConnection(network.bmproto.Socks5BMConnection(chosen))
                    elif (BMConfigParser().safeGet("bitmessagesettings", "socksproxytype") == "SOCKS4a"):
                        self.addConnection(network.bmproto.Socks4aBMConnection(chosen))
                    elif not chosen.host.endswith(".onion"):
                        self.addConnection(network.bmproto.BMConnection(chosen))
                except socket.error as e:
                    if e.errno == errno.ENETUNREACH:
                        continue

        if acceptConnections and len(self.listeningSockets) == 0:
            self.startListening()
            logger.info('Listening for incoming connections.')
        if len(self.listeningSockets) > 0 and not acceptConnections:
            for i in self.listeningSockets:
                i.close()
            logger.info('Stopped listening for incoming connections.')

#        while len(asyncore.socket_map) > 0 and state.shutdown == 0:
#            print "loop, state = %s" % (proxy.state)
        asyncore.loop(timeout=2.0, count=1)

        for i in self.inboundConnections.values() + self.outboundConnections.values():
            minTx = time.time() - 20
            if i.connectionFullyEstablished:
                minTx -= 300 - 20
            if i.lastTx < minTx:
                i.close("Timeout (%is)" % (time.time() - i.lastTx))
