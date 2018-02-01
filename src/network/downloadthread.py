import random
import threading
import time

import addresses
from debug import logger
from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
import protocol
from state import missingObjects

class DownloadThread(threading.Thread, StoppableThread):
    minPending = 200
    maxRequestChunk = 1000
    requestTimeout = 60
    cleanInterval = 60
    requestExpires = 3600

    def __init__(self):
        threading.Thread.__init__(self, name="Downloader")
        self.initStop()
        self.name = "Downloader"
        logger.info("init download thread")
        self.lastCleaned = time.time()

    def cleanPending(self):
        deadline = time.time() - DownloadThread.requestExpires
        try:
            toDelete = [k for k, v in missingObjects.iteritems() if v < deadline]
        except RuntimeError:
            pass
        else:
            for i in toDelete:
                del missingObjects[i]
            self.lastCleaned = time.time()

    def run(self):
        while not self._stopped:
            requested = 0
            # Choose downloading peers randomly
            connections = BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values()
            random.shuffle(connections)
            try:
                requestChunk =  max(int(min(DownloadThread.maxRequestChunk, len(missingObjects)) / len(connections)), 1)
            except ZeroDivisionError:
                requestChunk = 1
            for i in connections:
                now = time.time()
                timedOut = now - DownloadThread.requestTimeout
                try:
                    request = i.objectsNewToMe.randomKeys(requestChunk)
                except KeyError:
                    continue
                payload = bytearray()
                payload.extend(addresses.encodeVarint(len(request)))
                for chunk in request:
                    payload.extend(chunk)
                    missingObjects[k] = now
                i.append_write_buf(protocol.CreatePacket('getdata', payload))
                logger.debug("%s:%i Requesting %i objects", i.destination.host, i.destination.port, len(request))
                requested += len(request)
            if time.time() >= self.lastCleaned + DownloadThread.cleanInterval:
                self.cleanPending()
            if not requested:
                self.stop.wait(5)
