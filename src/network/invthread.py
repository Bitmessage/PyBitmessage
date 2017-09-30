import Queue
from random import randint
import threading
from time import time

import addresses
from bmconfigparser import BMConfigParser
from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
from network.dandelion import DandelionStems, REASSIGN_INTERVAL
from queues import invQueue
import protocol
import state

class InvThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="InvBroadcaster")
        self.initStop()
        self.name = "InvBroadcaster"
        # for locally generated objects
        self.dandelionRoutes = []
        self.dandelionRefresh = 0

    def dandelionLocalRouteRefresh(self):
        if self.dandelionRefresh < time():
            self.dandelionRoutes = BMConnectionPool().dandelionRouteSelector(None)
            self.dandelionRefresh = time() + REASSIGN_INTERVAL

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                self.dandelionLocalRouteRefresh()
                try:
                    data = invQueue.get(False)
                    # locally generated
                    if len(data) == 2:
                        BMConnectionPool().handleReceivedObject(data[0], data[1])
                        # Fluff trigger by RNG
                        # auto-ignore if config set to 0, i.e. dandelion is off
                        if randint(1, 100) < BMConfigParser().safeGetBoolean("network", "dandelion"):
                            DandelionStems.add(data[1], self.dandelionRoutes)
                    # came over the network
                    else:
                        source = BMConnectionPool().getConnectionByAddr(data[2])
                        BMConnectionPool().handleReceivedObject(data[0], data[1], source)
                    chunk.append((data[0], data[1]))
                except Queue.Empty:
                    break
                # connection not found, handle it as if generated locally
                except KeyError:
                    BMConnectionPool().handleReceivedObject(data[0], data[1])

            if chunk:
                for connection in BMConnectionPool().inboundConnections.values() + \
                        BMConnectionPool().outboundConnections.values():
                    fluffs = []
                    stems = []
                    for inv in chunk:
                        if inv[0] not in connection.streams:
                            continue
                        if inv[1] in DandelionStems().stem:
                            if connection in DandelionStems().stem[inv[1]]:
                                stems.append(inv[1])
                            continue
                        # else
                        try:
                            with connection.objectsNewToThemLock:
                                del connection.objectsNewToThem[inv[1]]
                            fluffs.append(inv[1])
                        except KeyError:
                            continue
                    if fluffs:
                        connection.append_write_buf(protocol.CreatePacket('inv', \
                                addresses.encodeVarint(len(fluffs)) + "".join(fluffs)))
                    if stems:
                        connection.append_write_buf(protocol.CreatePacket('dinv', \
                                addresses.encodeVarint(len(stems)) + "".join(stems)))
            invQueue.iterate()
            self.stop.wait(1)
