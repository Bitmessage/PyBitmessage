import random
import threading
import time

import addresses
#from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
#from inventory import Inventory
from network.connectionpool import BMConnectionPool
import protocol

class DownloadThread(threading.Thread, StoppableThread):
    maxPending = 200
    requestChunk = 1000
    requestTimeout = 60
    cleanInterval = 60
    requestExpires = 600

    def __init__(self):
        threading.Thread.__init__(self, name="Downloader")
        self.initStop()
        self.name = "Downloader"
        logger.info("init download thread")
        self.pending = {}
        self.lastCleaned = time.time()

    def cleanPending(self):
        deadline = time.time() - DownloadThread.requestExpires
        self.pending = {k: v for k, v in self.pending.iteritems() if v >= deadline}
        self.lastCleaned = time.time()

    def run(self):
        while not self._stopped:
            requested = 0
            # Choose downloading peers randomly
            connections = BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values()
            random.shuffle(connections)
            for i in connections:
                now = time.time()
                timedOut = now - DownloadThread.requestTimeout
                # this may take a while, but it needs a consistency so I think it's better to lock a bigger chunk
                with i.objectsNewToMeLock:
                    downloadPending = len(list((k for k, v in i.objectsNewToMe.iteritems() if k in self.pending and self.pending[k] > timedOut)))
                    if downloadPending >= DownloadThread.maxPending:
                        continue
                    # keys with True values in the dict
                    request = list((k for k, v in i.objectsNewToMe.iteritems() if k not in self.pending or self.pending[k] < timedOut))
                    if not request:
                        continue
                    if len(request) > DownloadThread.requestChunk - downloadPending:
                        request = request[:DownloadThread.requestChunk - downloadPending]
                    # mark them as pending
                    for k in request:
                        i.objectsNewToMe[k] = False
                        self.pending[k] = now

                payload = addresses.encodeVarint(len(request)) + ''.join(request)
                i.append_write_buf(protocol.CreatePacket('getdata', payload))
                logger.debug("%s:%i Requesting %i objects", i.destination.host, i.destination.port, len(request))
                requested += len(request)
            if time.time() >= self.lastCleaned + DownloadThread.cleanInterval:
                self.cleanPending()
            if not requested:
                self.stop.wait(1)
