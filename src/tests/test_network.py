"""Test network module"""

import threading
import time

from .common import skip_python3
from .partial import TestPartialRun

skip_python3()


class TestNetwork(TestPartialRun):
    """A test case for running the network subsystem"""

    @classmethod
    def setUpClass(cls):
        super(TestNetwork, cls).setUpClass()

        cls.state.maximumNumberOfHalfOpenConnections = 4

        cls.config.set('bitmessagesettings', 'sendoutgoingconnections', 'True')
        cls.config.set('bitmessagesettings', 'udp', 'True')

        # config variable is still used inside of the network ):
        import network
        from network import connectionpool, stats

        # beware of singleton
        connectionpool.config = cls.config
        cls.pool = network.BMConnectionPool()
        cls.stats = stats

        network.start(cls.config, cls.state)

    def test_threads(self):
        """Ensure all the network threads started"""
        threads = {
            "AddrBroadcaster", "Announcer", "Asyncore", "Downloader",
            "InvBroadcaster", "Uploader"}
        extra = self.config.getint('threads', 'receive')
        for thread in threading.enumerate():
            try:
                threads.remove(thread.name)
            except KeyError:
                extra -= thread.name.startswith("ReceiveQueue_")

        self.assertEqual(len(threads), 0)
        self.assertEqual(extra, 0)

    def test_stats(self):
        """Check that network starts connections and updates stats"""
        pl = 0
        for _ in range(30):
            if pl == 0:
                pl = len(self.pool)
            if (
                self.stats.receivedBytes() > 0 and self.stats.sentBytes() > 0
                and pl > 0
                # and len(self.stats.connectedHostsList()) > 0
            ):
                break
            time.sleep(1)
        else:
            self.fail('Have not started any connection in 30 sec')

    @classmethod
    def tearDownClass(cls):
        super(TestNetwork, cls).tearDownClass()
        for thread in threading.enumerate():
            if thread.name == "Asyncore":
                thread.stopThread()
