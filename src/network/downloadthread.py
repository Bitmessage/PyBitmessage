import threading

import addresses
#from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
#from inventory import Inventory
from network.connectionpool import BMConnectionPool
import protocol

class DownloadThread(threading.Thread, StoppableThread):
    maxPending = 500
    requestChunk = 1000

    def __init__(self):
        threading.Thread.__init__(self, name="DownloadThread")
        self.initStop()
        self.name = "DownloadThread"
        logger.info("init download thread")

    def run(self):
        while not self._stopped:
            requested = 0
            for i in BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values():
                # this may take a while, but it needs a consistency so I think it's better
                with i.objectsNewToMeLock:
                    downloadPending = len(list((k for k, v in i.objectsNewToMe.iteritems() if not v)))
                    if downloadPending >= DownloadThread.maxPending:
                        continue
                    # keys with True values in the dict
                    request = list((k for k, v in i.objectsNewToMe.iteritems() if v))
                    if not request:
                        continue
                    if len(request) > DownloadThread.requestChunk - downloadPending:
                        request = request[:DownloadThread.requestChunk - downloadPending]
                    # mark them as pending
                    for k in request:
                        i.objectsNewToMe[k] = False

                payload = addresses.encodeVarint(len(request)) + ''.join(request)
                i.writeQueue.put(protocol.CreatePacket('getdata', payload))
                logger.debug("%s:%i Requesting %i objects", i.destination.host, i.destination.port, len(request))
                requested += len(request)
            self.stop.wait(1)
