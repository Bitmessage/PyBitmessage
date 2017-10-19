import Queue
from random import randint, shuffle
import threading
from time import time

import addresses
from bmconfigparser import BMConfigParser
from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
from network.dandelion import Dandelion
from queues import invQueue
import protocol
import state

class InvThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="InvBroadcaster")
        self.initStop()
        self.name = "InvBroadcaster"

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                try:
                    data = invQueue.get(False)
                    chunk.append((data[0], data[1]))
                    # locally generated
                    if len(data) == 2:
                        Dandelion().addHash(data[1], None)
                        BMConnectionPool().handleReceivedObject(data[0], data[1])
                    # came over the network
                    else:
                        source = BMConnectionPool().getConnectionByAddr(data[2])
                        BMConnectionPool().handleReceivedObject(data[0], data[1], source)
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
                        try:
                            with connection.objectsNewToThemLock:
                                del connection.objectsNewToThem[inv[1]]
                        except KeyError:
                            continue
                        try:
                            if connection == Dandelion().hashMap[inv[1]]:
                                # Fluff trigger by RNG
                                # auto-ignore if config set to 0, i.e. dandelion is off
                                # send a normal inv if stem node doesn't support dandelion
                                if randint(1, 100) < BMConfigParser().safeGetBoolean("network", "dandelion") and \
                                        connection.services | protocol.NODE_DANDELION > 0:
                                    stems.append(inv[1])
                                else:
                                    fluffs.append(inv[1])
                        except KeyError:
                            fluffs.append(inv[1])

                    if fluffs:
                        shuffle(fluffs)
                        connection.append_write_buf(protocol.CreatePacket('inv', \
                                addresses.encodeVarint(len(fluffs)) + "".join(fluffs)))
                    if stems:
                        shuffle(stems)
                        connection.append_write_buf(protocol.CreatePacket('dinv', \
                                addresses.encodeVarint(len(stems)) + "".join(stems)))

            invQueue.iterate()
            for i in range(len(chunk)):
                invQueue.task_done()

            if Dandelion().refresh < time():
                BMConnectionPool().reRandomiseDandelionStems()

            self.stop.wait(1)
