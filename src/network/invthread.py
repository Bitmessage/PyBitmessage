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
        threading.Thread.__init__(self, name="InvBroadcaster")
        self.initStop()
        self.name = "InvBroadcaster"

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                try:
                    data = invQueue.get(False)
                    if len(data) == 2:
                        BMConnectionPool().handleReceivedObject(data[0], data[1])
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
                        connection.append_write_buf(protocol.CreatePacket('inv', \
                                addresses.encodeVarint(len(hashes)) + "".join(hashes)))
            invQueue.iterate()
            self.stop.wait(1)
