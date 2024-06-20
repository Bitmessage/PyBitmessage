"""
Thread to send inv annoucements
"""
import Queue
import random
from time import time

import connectionpool
from network import dandelion_ins
from threads import StoppableThread


def handleExpiredDandelion(expired):
    """For expired dandelion objects, mark all remotes as not having
       the object"""
    if not expired:
        return
    for i in connectionpool.pool.connections():
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
    """Main thread that sends inv annoucements"""

    name = "InvBroadcaster"

    def __init__(self, protocol, state, queues, addresses):
        self.protocol = protocol
        self.state = state
        self.queues = queues
        self.addresses = addresses
        StoppableThread.__init__(self)

    @staticmethod
    def handleLocallyGenerated(stream, hashId):
        """Locally generated inventory items require special handling"""
        dandelion_ins.addHash(hashId, stream=stream)
        for connection in connectionpool.pool.connections():
            if dandelion_ins.enabled and connection != \
                    dandelion_ins.objectChildStem(hashId):
                continue
            connection.objectsNewToThem[hashId] = time()

    def run(self):  # pylint: disable=too-many-branches
        while not self.state.shutdown:  # pylint: disable=too-many-nested-blocks
            chunk = []
            while True:
                # Dandelion fluff trigger by expiration
                handleExpiredDandelion(dandelion_ins.expire(self.queues.invQueue))
                try:
                    data = self.queues.invQueue.get(False)
                    chunk.append((data[0], data[1]))
                    # locally generated
                    if len(data) == 2 or data[2] is None:
                        self.handleLocallyGenerated(data[0], data[1])
                except Queue.Empty:
                    break

            if chunk:
                for connection in connectionpool.pool.connections():
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
                            if connection == dandelion_ins.objectChildStem(inv[1]):
                                # Fluff trigger by RNG
                                # auto-ignore if config set to 0, i.e. dandelion is off
                                if random.randint(1, 100) >= dandelion_ins.enabled:  # nosec B311
                                    fluffs.append(inv[1])
                                # send a dinv only if the stem node supports dandelion
                                elif connection.services & self.protocol.NODE_DANDELION > 0:
                                    stems.append(inv[1])
                                else:
                                    fluffs.append(inv[1])
                        except KeyError:
                            fluffs.append(inv[1])

                    if fluffs:
                        random.shuffle(fluffs)
                        connection.append_write_buf(self.protocol.CreatePacket(
                            'inv',
                            self.addresses.encodeVarint(
                                len(fluffs)) + ''.join(fluffs)))
                    if stems:
                        random.shuffle(stems)
                        connection.append_write_buf(self.protocol.CreatePacket(
                            'dinv',
                            self.addresses.encodeVarint(
                                len(stems)) + ''.join(stems)))

            self.queues.invQueue.iterate()
            for _ in range(len(chunk)):
                self.queues.invQueue.task_done()

            dandelion_ins.reRandomiseStems()

            self.stop.wait(1)
