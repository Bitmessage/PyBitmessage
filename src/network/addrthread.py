import queue as Queue

from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
from queues import addrQueue
import state


class AddrThread(StoppableThread):
    name = "AddrBroadcaster"

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                try:
                    data = addrQueue.get(False)
                    chunk.append((data[0], data[1]))
                    if len(data) > 2:
                        source = BMConnectionPool().getConnectionByAddr(data[2])
                except Queue.Empty:
                    break
                except KeyError:
                    continue

            # finish

            addrQueue.iterate()
            for i in range(len(chunk)):
                addrQueue.task_done()
            self.stop.wait(1)
