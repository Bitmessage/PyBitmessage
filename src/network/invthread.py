from binascii import hexlify
import collections
import Queue
import random
import threading
import time

import addresses
from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
from network.bmproto import BMProto
from network.connectionpool import BMConnectionPool
from queues import invQueue
import protocol
import state

class InvThread(threading.Thread, StoppableThread):
    size = 10

    def __init__(self):
        threading.Thread.__init__(self, name="InvThread")
        self.initStop()
        self.name = "InvThread"

        self.shutdown = False

        self.collectionOfInvs = []
        for i in range(InvThread.size):
            self.collectionOfInvs.append({})

    def run(self):
        iterator = 0
        while not state.shutdown:
            while True:
                try:
                    (stream, hash) = invQueue.get(False)
                    self.holdHash (stream, hash)
                    #print "Holding hash %i, %s" % (stream, hexlify(hash))
                except Queue.Empty:
                    break

            if len(self.collectionOfInvs[iterator]) > 0:
                for connection in BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values():
                    hashes = []
                    for stream in connection.streams:
                        try:
                            for hashId in self.collectionOfInvs[iterator][stream]:
                                if hashId in connection.objectsNewToThem:
                                    hashes.append(hashId)
                                    del connection.objectsNewToThem[hashId]
                        except KeyError:
                            continue
                    if len(hashes) > 0:
                        #print "sending inv of %i" % (len(hashes))
                        connection.writeQueue.put(protocol.CreatePacket('inv', addresses.encodeVarint(len(hashes)) + "".join(hashes)))
                self.collectionOfInvs[iterator] = {}
            iterator += 1
            iterator %= InvThread.size
            self.stop.wait(1)

    def holdHash(self, stream, hash):
        i = random.randrange(0, InvThread.size)
        if stream not in self.collectionOfInvs[i]:
            self.collectionOfInvs[i][stream] = []
        self.collectionOfInvs[i][stream].append(hash)

    def hasHash(self, hash):
        for streamlist in self.collectionOfInvs:
            for stream in streamlist:
                if hash in streamlist[stream]:
                    return True
        return False

    def hashCount(self):
        retval = 0
        for streamlist in self.collectionOfInvs:
            for stream in streamlist:
                retval += len(streamlist[stream])
        return retval

    def close(self):
        self.shutdown = True
