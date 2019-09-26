"""
src/network/downloadthread.py
=============================
"""
import time

import addresses
import helper_random
import protocol
from network.dandelion import Dandelion
from debug import logger
from helper_threading import StoppableThread
from inventory import Inventory
from network.connectionpool import BMConnectionPool
from network.objectracker import missingObjects


class DownloadThread(StoppableThread):
    """Thread-based class for downloading from connections"""
    minPending = 200
    maxRequestChunk = 1000
    requestTimeout = 60
    cleanInterval = 60
    requestExpires = 3600

    def __init__(self):
        super(DownloadThread, self).__init__(name="Downloader")
        logger.info("init download thread")
        self.lastCleaned = time.time()

    def cleanPending(self):
        """Expire pending downloads eventually"""
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
            connections = [
                x for x in
                BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values()
                if x.fullyEstablished]
            helper_random.randomshuffle(connections)
            try:
                requestChunk = max(int(min(DownloadThread.maxRequestChunk, len(missingObjects)) / len(connections)), 1)
            except ZeroDivisionError:
                requestChunk = 1
            for i in connections:
                now = time.time()
                # avoid unnecessary delay
                if i.skipUntil >= now:
                    continue
                try:
                    request = i.objectsNewToMe.randomKeys(requestChunk)
                except KeyError:
                    continue
                payload = bytearray()
                chunkCount = 0
                for chunk in request:
                    if chunk in Inventory() and not Dandelion().hasHash(chunk):
                        try:
                            del i.objectsNewToMe[chunk]
                        except KeyError:
                            pass
                        continue
                    payload.extend(chunk)
                    chunkCount += 1
                    missingObjects[chunk] = now
                if not chunkCount:
                    continue
                payload[0:0] = addresses.encodeVarint(chunkCount)
                i.append_write_buf(protocol.CreatePacket('getdata', payload))
                logger.debug("%s:%i Requesting %i objects", i.destination.host, i.destination.port, chunkCount)
                requested += chunkCount
            if time.time() >= self.lastCleaned + DownloadThread.cleanInterval:
                self.cleanPending()
            if not requested:
                self.stop.wait(1)
