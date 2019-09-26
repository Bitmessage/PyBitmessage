"""
src/network/uploadthread.py
"""
# pylint: disable=unsubscriptable-object
import time

import helper_random
import protocol
from debug import logger
from helper_threading import StoppableThread
from inventory import Inventory
from network.connectionpool import BMConnectionPool
from network.dandelion import Dandelion
from network.randomtrackingdict import RandomTrackingDict


class UploadThread(StoppableThread):
    """This is a thread that uploads the objects that the peers requested from me """
    maxBufSize = 2097152  # 2MB

    def __init__(self):
        super(UploadThread, self).__init__(name="Uploader")
        logger.info("init upload thread")

    def run(self):
        while not self._stopped:
            uploaded = 0
            # Choose downloading peers randomly
            connections = [x for x in BMConnectionPool().inboundConnections.values() +
                           BMConnectionPool().outboundConnections.values() if x.fullyEstablished]
            helper_random.randomshuffle(connections)
            for i in connections:
                now = time.time()
                # avoid unnecessary delay
                if i.skipUntil >= now:
                    continue
                if len(i.write_buf) > UploadThread.maxBufSize:
                    continue
                try:
                    request = i.pendingUpload.randomKeys(RandomTrackingDict.maxPending)
                except KeyError:
                    continue
                payload = bytearray()
                chunk_count = 0
                for chunk in request:
                    del i.pendingUpload[chunk]
                    if Dandelion().hasHash(chunk) and \
                       i != Dandelion().objectChildStem(chunk):
                        i.antiIntersectionDelay()
                        logger.info('%s asked for a stem object we didn\'t offer to it.',
                                    i.destination)
                        break
                    try:
                        payload.extend(protocol.CreatePacket('object',
                                                             Inventory()[chunk].payload))
                        chunk_count += 1
                    except KeyError:
                        i.antiIntersectionDelay()
                        logger.info('%s asked for an object we don\'t have.', i.destination)
                        break
                if not chunk_count:
                    continue
                i.append_write_buf(payload)
                logger.debug("%s:%i Uploading %i objects",
                             i.destination.host, i.destination.port, chunk_count)
                uploaded += chunk_count
            if not uploaded:
                self.stop.wait(1)
