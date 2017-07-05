import Queue
import threading

import addresses
from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
from queues import addrQueue
import protocol
import state

class AddrThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="AddrThread")
        self.initStop()
        self.name = "AddrThread"

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                try:
                    data = addrQueue.get(False)
                    chunk.append((data[0], data[1]))
                except Queue.Empty:
                    break

            #finish

            addrQueue.iterate()
            self.stop.wait(1)
