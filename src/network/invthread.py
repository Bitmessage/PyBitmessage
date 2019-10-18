"""
src/network/invthread.py
========================
"""
import queue as Queue
import random
from time import time

import addresses
import protocol
import state
from helper_threading import StoppableThread
from network.connectionpool import BMConnectionPool
from network.dandelion import Dandelion
from queues import invQueue


def handleExpiredDandelion(expired):
    """For expired dandelion objects, mark all remotes as not having
       the object"""
    if not expired:
        return
    for i in \
        BMConnectionPool().inboundConnections.values() + \
            BMConnectionPool().outboundConnections.values():
        if not i.fullyEstablished:
            continue
        for x in expired:
            streamNumber, hashid, _ = x
            try:
                del i.objectsNewToMe[hashid]
            except KeyError:
                if streamNumber in i.streams:
                    with i.objectsNewToThemLock:
                        i.objectsNewToThem[hashid] = time()


class InvThread(StoppableThread):
    """A thread to send inv annoucements."""

    name = "InvBroadcaster"

    @staticmethod
    def handleLocallyGenerated(stream, hashId):
        """Locally generated inventory items require special handling"""
        Dandelion().addHash(hashId, stream=stream)
        for connection in \
            BMConnectionPool().inboundConnections.values() + \
                BMConnectionPool().outboundConnections.values():
            if state.dandelion and connection != Dandelion().objectChildStem(hashId):
                continue
            connection.objectsNewToThem[hashId] = time()

    def run(self):      # pylint: disable=too-many-branches
        while not state.shutdown:       # pylint: disable=too-many-nested-blocks
            chunk = []
            while True:
                # Dandelion fluff trigger by expiration
                handleExpiredDandelion(Dandelion().expire())
                try:
                    data = invQueue.get(False)
                    chunk.append((data[0], data[1]))
                    # locally generated
                    if len(data) == 2 or data[2] is None:
                        self.handleLocallyGenerated(data[0], data[1])
                except Queue.Empty:
                    break

            if chunk:
                for connection in BMConnectionPool().inboundConnections.values() + \
                        BMConnectionPool().outboundConnections.values():
                    fluffs = []
                    stems = []
                    for inv in chunk:
                        if inv[0] not in connection.streams:
                            continue
                        try:
                            with connection.objectsNewToThemLock:
                                del connection.objectsNewToThem[inv[1]]
                        except KeyError:
                            continue
                        try:
                            if connection == Dandelion().objectChildStem(inv[1]):
                                # Fluff trigger by RNG
                                # auto-ignore if config set to 0, i.e. dandelion is off
                                if random.randint(1, 100) >= state.dandelion:
                                    fluffs.append(inv[1])
                                # send a dinv only if the stem node supports dandelion
                                elif connection.services & protocol.NODE_DANDELION > 0:
                                    stems.append(inv[1])
                                else:
                                    fluffs.append(inv[1])
                        except KeyError:
                            fluffs.append(inv[1])

                    if fluffs:
                        random.shuffle(fluffs)
                        connection.append_write_buf(protocol.CreatePacket(
                            'inv', addresses.encodeVarint(len(fluffs)) +
                            "".join(fluffs)))
                    if stems:
                        random.shuffle(stems)
                        connection.append_write_buf(protocol.CreatePacket(
                            'dinv', addresses.encodeVarint(len(stems)) +
                            "".join(stems)))

            invQueue.iterate()
            for i in range(len(chunk)):
                invQueue.task_done()

            if Dandelion().refresh < time():
                Dandelion().reRandomiseStems()

            self.stop.wait(1)
