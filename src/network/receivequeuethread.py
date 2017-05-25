import Queue
import threading

from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
from inventory import Inventory
from network.connectionpool import BMConnectionPool
import protocol

class ReceiveQueueThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="ReceiveQueueThread")
        self.initStop()
        self.name = "ReceiveQueueThread"
        BMConnectionPool()
        logger.error("init asyncore thread")

    def run(self):
        while not self._stopped:
            processed = 0
            for i in BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values():
                try:
                    command, args = i.receiveQueue.get(False)
                except Queue.Empty:
                    continue
                processed += 1
                try:
                    getattr(self, "command_" + str(command))(i, args)
                except AttributeError:
                    # missing command
                    raise
            if processed == 0:
                self.stop.wait(0.2)

    def command_object(self, connection, objHash):
        try:
            connection.writeQueue.put(protocol.CreatePacket('object', Inventory()[objHash].payload))
        except KeyError:
            connection.antiIntersectionDelay()
            logger.warning('%s asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. We probably cleaned it out after advertising it but before they got around to asking for it.' % (connection.destination,))

    def stopThread(self):
        super(ReceiveQueueThread, self).stopThread()
