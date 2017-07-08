import Queue
import sys
import threading
import time

import addresses
from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
from inventory import Inventory
from network.connectionpool import BMConnectionPool
from network.bmproto import BMProto
from queues import receiveDataQueue
import protocol
import state

class ReceiveQueueThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="ReceiveQueueThread")
        self.initStop()
        self.name = "ReceiveQueueThread"
        logger.info("init receive queue thread")

    def run(self):
        while not self._stopped and state.shutdown == 0:
            try:
                dest = receiveDataQueue.get(block=True, timeout=1)
                receiveDataQueue.task_done()
            except Queue.Empty:
                continue

            if self._stopped:
                break

            # cycle as long as there is data
            # methods should return False if there isn't enough data, or the connection is to be aborted

            # state_* methods should return False if there isn't enough data,
            # or the connection is to be aborted

            try:
                BMConnectionPool().inboundConnections[dest].process()
            except KeyError:
                try:
                    BMConnectionPool().inboundConnections[dest.host].process()
                except KeyError:
                    pass
            except AttributeError:
                pass

            try:
                BMConnectionPool().outboundConnections[dest].process()
            except (KeyError, AttributeError):
                pass

            try:
                BMConnectionPool().udpSockets[dest].process()
            except (KeyError, AttributeError):
                pass
