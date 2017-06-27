import Queue
import threading

import addresses
from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
from queues import invQueue
import protocol
import state

class InvThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="InvThread")
        self.initStop()
        self.name = "InvThread"

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                try:
                    data = invQueue.get(False)
                    if len(data) == 2:
                        BMConnectionPool().handleReceivedObject(data[0], data[1])
                    else:
                        BMConnectionPool().handleReceivedObject(data[0], data[1], data[2])
                    chunk.append((data[0], data[1]))
                except Queue.Empty:
                    break

            if chunk:
                for connection in BMConnectionPool().inboundConnections.values() + \
                        BMConnectionPool().outboundConnections.values():
                    hashes = []
                    for inv in chunk:
                        if inv[0] not in connection.streams:
                            continue
                        try:
                            with connection.objectsNewToThemLock:
                                del connection.objectsNewToThem[inv[1]]
                            hashes.append(inv[1])
                        except KeyError:
                            continue
                    if hashes:
                        connection.writeQueue.put(protocol.CreatePacket('inv', \
                                addresses.encodeVarint(len(hashes)) + "".join(hashes)))
            invQueue.iterate()
            self.stop.wait(1)
