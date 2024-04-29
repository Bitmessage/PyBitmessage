"""
Announce myself (node address)
"""
import time

# magic imports!
import state
from bmconfigparser import config
from protocol import assembleAddrMessage

from node import Peer
from threads import StoppableThread


class AnnounceThread(StoppableThread):
    """A thread to manage regular announcing of this node"""
    name = "Announcer"
    announceInterval = 60

    def run(self):
        lastSelfAnnounced = 0
        while not self._stopped and state.shutdown == 0:
            processed = 0
            if lastSelfAnnounced < time.time() - self.announceInterval:
                self.announceSelf()
                lastSelfAnnounced = time.time()
            if processed == 0:
                self.stop.wait(10)

    @staticmethod
    def announceSelf():
        """Announce our presence"""
        for connection in state.BMConnectionPool.udpSockets.values():
            if not connection.announcing:
                continue
            for stream in state.streamsInWhichIAmParticipating:
                addr = (
                    stream,
                    Peer(
                        '127.0.0.1',
                        config.safeGetInt('bitmessagesettings', 'port')),
                    int(time.time()))
                connection.append_write_buf(assembleAddrMessage([addr]))
