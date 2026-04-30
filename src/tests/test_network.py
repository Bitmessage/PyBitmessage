"""Test network module"""

import os
import select
import socket
import threading
import time
import unittest

from .partial import TestPartialRun


def _can_broadcast_loopback():
    """Check whether UDP broadcast loopback works.

    Some virtualised environments (e.g. Docker on colima) don't
    deliver broadcasts back to the sender.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
    try:
        s.bind(('0.0.0.0', 18444))
        s.setblocking(0)
        s.sendto(b'loopback-test', ('<broadcast>', 18444))
        r, _, _ = select.select([s], [], [], 2.0)
        return bool(r)
    finally:
        s.close()


skip_without_broadcast_loopback = unittest.skipUnless(
    _can_broadcast_loopback(),
    'UDP broadcast loopback not supported (e.g. Docker on colima)'
)


class TestNetwork(TestPartialRun):
    """A test case for running the network subsystem"""

    @classmethod
    def setUpClass(cls):
        super(TestNetwork, cls).setUpClass()

        cls.state.maximumNumberOfHalfOpenConnections = 4

        cls.config.set('bitmessagesettings', 'sendoutgoingconnections', 'True')
        cls.config.set('bitmessagesettings', 'udp', 'True')
        cls.config.add_section('bootstrap')
        cls.config.set('bootstrap', 'testnet', 'True')

        import network
        from network import connectionpool, stats
        cls.stats = stats

        # remove stale knownnodes from previous runs
        try:
            os.remove(os.path.join(cls.state.appdata, 'knownnodes.dat'))
        except OSError:
            pass

        network.start(cls.config, cls.state)

        # pool is created inside network.start(), read it after
        cls.pool = connectionpool.pool

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
        for _ in range(60):
            if pl == 0:
                pl = len(self.pool)
            if (
                    self.stats.receivedBytes() > 0
                    and self.stats.sentBytes() > 0
                    and pl > 0
                    # and len(self.stats.connectedHostsList()) > 0
            ):
                break
            time.sleep(1)
        else:
            from network import knownnodes
            peers = [
                '%s:%d' % (p.host, p.port)
                for p in knownnodes.knownNodes.get(1, {})]
            conns = [
                '%s:%d(e=%s)' % (
                    c.destination.host, c.destination.port,
                    c.fullyEstablished)
                for c in self.pool.connections()]
            self.fail(
                'Have not started any connection in 60 sec:'
                ' pl=%d sent=%d recv=%d outbound=%d inbound=%d'
                ' knownNodesActual=%s peers=%s conns=%s'
                % (
                    pl, self.stats.sentBytes(),
                    self.stats.receivedBytes(),
                    len(self.pool.outboundConnections),
                    len(self.pool.inboundConnections),
                    knownnodes.knownNodesActual,
                    peers, conns))

    @skip_without_broadcast_loopback
    def test_udp(self):
        """Invoke AnnounceThread.announceSelf() and check discovered peers"""

        for _ in range(20):
            if self.pool.udpSockets:
                break
            time.sleep(1)
        else:
            self.fail('No UDP sockets found in 20 sec')

        for _ in range(10):
            try:
                self.state.announceThread.announceSelf()
            except AttributeError:
                self.fail('state.announceThread is not set properly')
            time.sleep(1)
            try:
                peer = self.state.discoveredPeers.popitem()[0]
            except KeyError:
                continue
            else:
                self.assertEqual(peer.port, 8444)
                break
        else:
            self.fail('No self in discovered peers')

    @classmethod
    def tearDownClass(cls):
        super(TestNetwork, cls).tearDownClass()
        for thread in threading.enumerate():
            if thread.name == "Asyncore":
                thread.stopThread()
