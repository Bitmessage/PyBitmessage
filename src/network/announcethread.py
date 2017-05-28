import Queue
import threading
import time

from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
from network.bmproto import BMProto
from network.connectionpool import BMConnectionPool
from network.udp import UDPSocket
import protocol
import state

class AnnounceThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="AnnounceThread")
        self.initStop()
        self.name = "AnnounceThread"
        BMConnectionPool()
        logger.info("init announce thread")

    def run(self):
        lastSelfAnnounced = 0
        while not self._stopped:
            processed = 0
            if lastSelfAnnounced < time.time() - UDPSocket.announceInterval:
                self.announceSelf()
                lastSelfAnnounced = time.time()
            if processed == 0:
                self.stop.wait(10)

    def announceSelf(self):
        for connection in BMConnectionPool().udpSockets.values():
            for stream in state.streamsInWhichIAmParticipating:
                addr = (stream, state.Peer('127.0.0.1', BMConfigParser().safeGetInt("bitmessagesettings", "port")), time.time())
                connection.writeQueue.put(BMProto.assembleAddr([addr]))

    def stopThread(self):
        super(AnnounceThread, self).stopThread()
