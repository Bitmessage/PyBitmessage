"""
`DownloadThread` class definition
"""
import time
import random
import state
import six
import addresses
import protocol
from network import connectionpool
from network import dandelion_ins
from .objectracker import missingObjects
from .threads import StoppableThread


class DownloadThread(StoppableThread):
    """Thread-based class for downloading from connections"""
    minPending = 200
    maxRequestChunk = 1000
    requestTimeout = 60
    cleanInterval = 60
    requestExpires = 3600

    def __init__(self):
        super(DownloadThread, self).__init__(name="Downloader")
        self.lastCleaned = time.time()

    def cleanPending(self):
        """Expire pending downloads eventually"""
        deadline = time.time() - self.requestExpires
        try:
            toDelete = [
                k for k, v in six.iteritems(missingObjects)
                if v < deadline]
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
            connections = connectionpool.pool.establishedConnections()
            random.shuffle(connections)
            requestChunk = max(int(
                min(self.maxRequestChunk, len(missingObjects))
                / len(connections)), 1) if connections else 1

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
                    if chunk in state.Inventory and not dandelion_ins.hasHash(chunk):
                        try:
                            del i.objectsNewToMe[chunk]
                        except KeyError:
                            pass
                        continue
                    payload.extend(chunk)
                    chunkCount += 1
                    missingObjects[bytes(chunk)] = now
                if not chunkCount:
                    continue
                payload[0:0] = addresses.encodeVarint(chunkCount)
                i.append_write_buf(protocol.CreatePacket(b'getdata', payload))
                self.logger.debug(
                    '%s:%i Requesting %i objects',
                    i.destination.host, i.destination.port, chunkCount)
                requested += chunkCount
            if time.time() >= self.lastCleaned + self.cleanInterval:
                self.cleanPending()
            if not requested:
                self.stop.wait(1)
