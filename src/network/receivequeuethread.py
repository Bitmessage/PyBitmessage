import Queue
import threading
import time

import addresses
from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
from inventory import Inventory
from network.connectionpool import BMConnectionPool
from network.bmproto import BMProto
import protocol
import state

class ReceiveQueueThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="ReceiveQueueThread")
        self.initStop()
        self.name = "ReceiveQueueThread"
        BMConnectionPool()
        logger.info("init receive queue thread")

    def run(self):
        lastprinted = int(time.time())
        while not self._stopped and state.shutdown == 0:
            if lastprinted < int(time.time()):
                lastprinted = int(time.time())
            processed = 0
            for i in BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values():
                if self._stopped:
                    break
                try:
                    command, args = i.receiveQueue.get(False)
                except Queue.Empty:
                    continue
                processed += 1
                try:
                    getattr(self, "command_" + str(command))(i, args)
                    i.receiveQueue.task_done()
                except AttributeError:
                    i.receiveQueue.task_done()
                    # missing command
                    raise
            if processed == 0:
                self.stop.wait(2)

    def command_object(self, connection, objHash):
        try:
            connection.writeQueue.put(protocol.CreatePacket('object', Inventory()[objHash].payload))
        except KeyError:
            connection.antiIntersectionDelay()
            logger.warning('%s asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. We probably cleaned it out after advertising it but before they got around to asking for it.' % (connection.destination,))

    def command_biginv(self, connection, dummy):
        def sendChunk():
            if objectCount == 0:
                return
            logger.debug('Sending huge inv message with %i objects to just this one peer', objectCount)
            connection.writeQueue.put(protocol.CreatePacket('inv', addresses.encodeVarint(objectCount) + payload))

        # Select all hashes for objects in this stream.
        bigInvList = {}
        for stream in connection.streams:
            for objHash in Inventory().unexpired_hashes_by_stream(stream):
                bigInvList[objHash] = 0
                connection.objectsNewToThem[objHash] = True
        objectCount = 0
        payload = b''
        # Now let us start appending all of these hashes together. They will be
        # sent out in a big inv message to our new peer.
        for hash, storedValue in bigInvList.items():
            payload += hash
            objectCount += 1
            if objectCount >= BMProto.maxObjectCount:
                self.sendChunk()
                payload = b''
                objectCount = 0

        # flush
        sendChunk()

    def command_inv(self, connection, hashId):
        connection.handleReceivedInventory(hashId)

    def stopThread(self):
        super(ReceiveQueueThread, self).stopThread()
