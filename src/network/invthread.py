from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import *
import queue
from random import randint, shuffle
import threading
from time import time

import addresses
from bmconfigparser import BMConfigParser
from helper_threading import StoppableThread
from .fix_circular_imports import BMConnectionPool, Dandelion
from queues import invQueue
import protocol
import state


def handleExpiredDandelion(expired):
    """For expired dandelion objects, mark all remotes as not having
       the object"""
    if not expired:
        return
    for i in \
        list(BMConnectionPool().inboundConnections.values()) + \
            list(BMConnectionPool().outboundConnections.values()):
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


class InvThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="InvBroadcaster")
        self.initStop()
        self.name = "InvBroadcaster"

    def handleLocallyGenerated(self, stream, hashId):
        Dandelion().addHash(hashId, stream=stream)
        for connection in \
                list(BMConnectionPool().inboundConnections.values()) + \
                list(BMConnectionPool().outboundConnections.values()):
                if state.dandelion and connection != Dandelion().objectChildStem(hashId):
                    continue
                connection.objectsNewToThem[hashId] = time()

    def run(self):
        while not state.shutdown:
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
                except queue.Empty:
                    break

            if chunk:
                for connection in list(BMConnectionPool().inboundConnections.values()) + \
                        list(BMConnectionPool().outboundConnections.values()):
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
                                if randint(1, 100) >= state.dandelion:
                                    fluffs.append(inv[1])
                                # send a dinv only if the stem node supports dandelion
                                elif connection.services & protocol.NODE_DANDELION > 0:
                                    stems.append(inv[1])
                                else:
                                    fluffs.append(inv[1])
                        except KeyError:
                            fluffs.append(inv[1])

                    if fluffs:
                        shuffle(fluffs)
                        connection.append_write_buf(protocol.CreatePacket('inv', \
                                addresses.encodeVarint(len(fluffs)) + "".join(fluffs)))
                    if stems:
                        shuffle(stems)
                        connection.append_write_buf(protocol.CreatePacket('dinv', \
                                addresses.encodeVarint(len(stems)) + "".join(stems)))

            invQueue.iterate()
            for i in range(len(chunk)):
                invQueue.task_done()

            if Dandelion().refresh < time():
                Dandelion().reRandomiseStems()

            self.stop.wait(1)
