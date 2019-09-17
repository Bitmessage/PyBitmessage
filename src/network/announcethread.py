"""
src/network/announcethread.py
=================================
"""
import time

from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
from network.bmproto import BMProto
from network.connectionpool import BMConnectionPool
from network.udp import UDPSocket
import state


class AnnounceThread(StoppableThread):
    """A thread to manage regular announcing of this node"""
    def __init__(self):
        super(AnnounceThread, self).__init__(name="Announcer")
        logger.info("init announce thread")

    def run(self):
        lastSelfAnnounced = 0
        while not self._stopped and state.shutdown == 0:
            processed = 0
            if lastSelfAnnounced < time.time() - UDPSocket.announceInterval:
                self.announceSelf()
                lastSelfAnnounced = time.time()
            if processed == 0:
                self.stop.wait(10)

    @staticmethod
    def announceSelf():
        """Announce our presence"""
        for connection in BMConnectionPool().udpSockets.values():
            if not connection.announcing:
                continue
            for stream in state.streamsInWhichIAmParticipating:
                addr = (
                    stream,
                    state.Peer('127.0.0.1', BMConfigParser().safeGetInt("bitmessagesettings", "port")),
                    time.time())
                connection.append_write_buf(BMProto.assembleAddr([addr]))
