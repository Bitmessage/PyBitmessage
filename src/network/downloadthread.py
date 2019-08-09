from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import *
from past.utils import old_div
import threading
import time

import addresses
import helper_random
import protocol
from .fix_circular_imports import BMConnectionPool, Dandelion, missingObjects
from debug import logger
from helper_threading import StoppableThread
from inventory import Inventory


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
            toDelete = [k for k, v in missingObjects.items() if v < deadline]
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
            connections = [x for x in list(BMConnectionPool().inboundConnections.values()) + list(BMConnectionPool().outboundConnections.values()) if x.fullyEstablished]
            helper_random.randomshuffle(connections)
            try:
                requestChunk =  max(int(old_div(min(DownloadThread.maxRequestChunk, len(missingObjects)), len(connections))), 1)
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
