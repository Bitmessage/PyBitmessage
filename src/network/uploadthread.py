"""
src/network/uploadthread.py
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint: disable=unsubscriptable-object
from future import standard_library
standard_library.install_aliases()
from builtins import *
import threading
import time

import helper_random
import protocol
from debug import logger
from helper_threading import StoppableThread
from inventory import Inventory
from .fix_circular_imports import BMConnectionPool, Dandelion
from randomtrackingdict import RandomTrackingDict


class UploadThread(threading.Thread, StoppableThread):
    """This is a thread that uploads the objects that the peers requested from me """
    maxBufSize = 2097152  # 2MB

    def __init__(self):
        threading.Thread.__init__(self, name="Uploader")
        self.initStop()
        self.name = "Uploader"
        logger.info("init upload thread")

    def run(self):
        while not self._stopped:
            uploaded = 0
            # Choose downloading peers randomly
            connections = [x for x in list(BMConnectionPool().inboundConnections.values()) +
                           list(BMConnectionPool().outboundConnections.values()) if x.fullyEstablished]
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
