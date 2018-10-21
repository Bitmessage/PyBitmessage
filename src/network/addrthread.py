"""
src/network/addrthread.py
=========================
"""

import Queue
import threading

import state
from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
from queues import addrQueue


class AddrThread(threading.Thread, StoppableThread):
    """Process a queue of addresses to broadcast"""

    def __init__(self):
        threading.Thread.__init__(self, name="AddrBroadcaster")
        self.initStop()
        self.name = "AddrBroadcaster"

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                try:
                    data = addrQueue.get(False)
                    chunk.append((data[0], data[1]))
                    if len(data) > 2:
                        BMConnectionPool().getConnectionByAddr(data[2])
                except Queue.Empty:
                    break
                except KeyError:
                    continue

            # finish

            addrQueue.iterate()
            for _ in range(len(chunk)):
                addrQueue.task_done()
            self.stop.wait(1)
