"""
Announce myself (node address)
"""
import time

from assemble import assemble_addr
from connectionpool import BMConnectionPool
from node import Peer
from pybitmessage import state
from pybitmessage.bmconfigparser import BMConfigParser
from threads import StoppableThread
from udp import UDPSocket


class AnnounceThread(StoppableThread):
    """A thread to manage regular announcing of this node"""
    name = "Announcer"

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
                    Peer(
                        '127.0.0.1',
                        BMConfigParser().safeGetInt(
                            'bitmessagesettings', 'port')),
                    time.time())
                connection.append_write_buf(assemble_addr([addr]))
