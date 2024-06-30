"""
`UploadThread` class definition
"""
import time

import random
import protocol
import state
from network import connectionpool
from randomtrackingdict import RandomTrackingDict
from network import dandelion_ins
from .threads import StoppableThread


class UploadThread(StoppableThread):
    """
    This is a thread that uploads the objects that the peers requested from me
    """
    maxBufSize = 2097152  # 2MB
    name = "Uploader"

    def run(self):
        while not self._stopped:
            uploaded = 0
            # Choose uploading peers randomly
            connections = connectionpool.pool.establishedConnections()
            random.shuffle(connections)
            for i in connections:
                now = time.time()
                # avoid unnecessary delay
                if i.skipUntil >= now:
                    continue
                if len(i.write_buf) > self.maxBufSize:
                    continue
                try:
                    request = i.pendingUpload.randomKeys(
                        RandomTrackingDict.maxPending)
                except KeyError:
                    continue
                payload = bytearray()
                chunk_count = 0
                for chunk in request:
                    del i.pendingUpload[chunk]
                    if dandelion_ins.hasHash(chunk) and \
                       i != dandelion_ins.objectChildStem(chunk):
                        i.antiIntersectionDelay()
                        self.logger.info(
                            '%s asked for a stem object we didn\'t offer to it.',
                            i.destination)
                        break
                    try:
                        payload.extend(protocol.CreatePacket(
                            b'object', state.Inventory[chunk].payload))
                        chunk_count += 1
                    except KeyError:
                        i.antiIntersectionDelay()
                        self.logger.info(
                            '%s asked for an object we don\'t have.',
                            i.destination)
                        break
                if not chunk_count:
                    continue
                i.append_write_buf(payload)
                self.logger.debug(
                    '%s:%i Uploading %i objects',
                    i.destination.host, i.destination.port, chunk_count)
                uploaded += chunk_count
            if not uploaded:
                self.stop.wait(1)
