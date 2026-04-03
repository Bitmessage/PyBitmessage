"""
Announce myself (node address)
"""
import time

from bmconfigparser import config
from protocol import assembleAddrMessage

from .node import Peer
from .threads import StoppableThread


class AnnounceThread(StoppableThread):
    """A thread to manage regular announcing of this node"""
    name = "Announcer"
    announceInterval = 60

    def __init__(self, pool):
        super(AnnounceThread, self).__init__()
        self.pool = pool

    def run(self):
        lastSelfAnnounced = 0
        while not self._stopped:
            processed = 0
            if lastSelfAnnounced < time.time() - self.announceInterval:
                self.announceSelf()
                lastSelfAnnounced = time.time()
            if processed == 0:
                self.stop.wait(10)

    def announceSelf(self):
        """Announce our presence"""
        for connection in self.pool.udpSockets.values():
            if not connection.announcing:
                continue
            for stream in self.pool.streams:
                addr = (
                    stream,
                    Peer(
                        '127.0.0.1',
                        config.safeGetInt('bitmessagesettings', 'port')),
                    int(time.time()))
                connection.append_write_buf(assembleAddrMessage([addr]))
