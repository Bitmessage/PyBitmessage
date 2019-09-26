"""
Tests for core and those that do not work outside
(because of import error for example)
"""

import os
import pickle  # nosec
import queue as Queue
import random  # nosec
import string
import time
import unittest

import knownnodes
import state
from bmconfigparser import BMConfigParser
from helper_msgcoding import MsgEncode, MsgDecode
from network import asyncore_pollchoose as asyncore
from network.connectionpool import BMConnectionPool
from network.tcp import Socks4aBMConnection, Socks5BMConnection, TCPConnection
from queues import excQueue

knownnodes_file = os.path.join(state.appdata, 'knownnodes.dat')
program = None


def pickle_knownnodes():
    """Generate old style pickled knownnodes.dat"""
    now = time.time()
    with open(knownnodes_file, 'wb') as dst:
        pickle.dump({
            stream: {
                state.Peer(
                    '%i.%i.%i.%i' % tuple([
                        random.randint(1, 255) for i in range(4)]),
                    8444): {'lastseen': now, 'rating': 0.1}
                for i in range(1, 4)  # 3 test nodes
            }
            for stream in range(1, 4)  # 3 test streams
        }, dst)


def cleanup():
    """Cleanup application files"""
    os.remove(knownnodes_file)


class TestCore(unittest.TestCase):
    """Test case, which runs in main pybitmessage thread"""

    def test_msgcoding(self):
        """test encoding and decoding (originally from helper_msgcoding)"""
        msg_data = {
            'subject': ''.join(
                random.choice(string.ascii_lowercase + string.digits)  # nosec
                for _ in range(40)),
            'body': ''.join(
                random.choice(string.ascii_lowercase + string.digits)  # nosec
                for _ in range(10000))
        }

        obj1 = MsgEncode(msg_data, 1)
        obj2 = MsgEncode(msg_data, 2)
        obj3 = MsgEncode(msg_data, 3)
        # print "1: %i 2: %i 3: %i" % (
        # len(obj1.data), len(obj2.data), len(obj3.data))

        obj1e = MsgDecode(1, obj1.data)
        # no subject in trivial encoding
        self.assertEqual(msg_data['body'], obj1e.body)

        obj2e = MsgDecode(2, obj2.data)
        self.assertEqual(msg_data['subject'], obj2e.subject)
        self.assertEqual(msg_data['body'], obj2e.body)

        obj3e = MsgDecode(3, obj3.data)
        self.assertEqual(msg_data['subject'], obj3e.subject)
        self.assertEqual(msg_data['body'], obj3e.body)

        try:
            MsgEncode({'body': 'A msg with no subject'}, 3)
        except Exception as e:
            self.fail(
                'Exception %s while trying to encode message'
                ' with no subject!' % e
            )

    @unittest.skip('Bad environment for asyncore.loop')
    def test_tcpconnection(self):
        """initial fill script from network.tcp"""
        BMConfigParser().set('bitmessagesettings', 'dontconnect', 'true')
        try:
            for peer in (state.Peer("127.0.0.1", 8448),):
                direct = TCPConnection(peer)
                while asyncore.socket_map:
                    print("loop, state = %s" % direct.state)
                    asyncore.loop(timeout=10, count=1)
        except:
            self.fail('Exception in test loop')

    @staticmethod
    def _wipe_knownnodes():
        with knownnodes.knownNodesLock:
            knownnodes.knownNodes = {stream: {} for stream in range(1, 4)}

    @staticmethod
    def _outdate_knownnodes():
        with knownnodes.knownNodesLock:
            for nodes in knownnodes.knownNodes.itervalues():
                for node in nodes.itervalues():
                    node['lastseen'] -= 2419205  # older than 28 days

    def test_knownnodes_pickle(self):
        """ensure that 3 nodes was imported for each stream"""
        pickle_knownnodes()
        self._wipe_knownnodes()
        knownnodes.readKnownNodes()
        for nodes in knownnodes.knownNodes.itervalues():
            self_count = n = 0
            for n, node in enumerate(nodes.itervalues()):
                if node.get('self'):
                    self_count += 1
            self.assertEqual(n - self_count, 2)

    def test_knownnodes_default(self):
        """test adding default knownnodes if nothing loaded"""
        cleanup()
        self._wipe_knownnodes()
        knownnodes.readKnownNodes()
        self.assertGreaterEqual(
            len(knownnodes.knownNodes[1]), len(knownnodes.DEFAULT_NODES))

    def test_0_cleaner(self):
        """test knownnodes starvation leading to IndexError in Asyncore"""
        self._outdate_knownnodes()
        # time.sleep(303)  # singleCleaner wakes up every 5 min
        knownnodes.cleanupKnownNodes()
        self.assertTrue(knownnodes.knownNodes[1])
        while True:
            try:
                thread, exc = excQueue.get(block=False)
            except Queue.Empty:
                return
            if thread == 'Asyncore' and isinstance(exc, IndexError):
                self.fail("IndexError because of empty knownNodes!")

    def _initiate_bootstrap(self):
        BMConfigParser().set('bitmessagesettings', 'dontconnect', 'true')
        self._outdate_knownnodes()
        knownnodes.addKnownNode(1, state.Peer('127.0.0.1', 8444), is_self=True)
        knownnodes.cleanupKnownNodes()
        time.sleep(2)

    def _check_bootstrap(self):
        _started = time.time()
        BMConfigParser().remove_option('bitmessagesettings', 'dontconnect')
        proxy_type = BMConfigParser().safeGet(
            'bitmessagesettings', 'socksproxytype')
        if proxy_type == 'SOCKS5':
            connection_base = Socks5BMConnection
        elif proxy_type == 'SOCKS4a':
            connection_base = Socks4aBMConnection
        else:
            connection_base = TCPConnection
        for _ in range(180):
            time.sleep(1)
            for peer, con in BMConnectionPool().outboundConnections.iteritems():
                if not peer.host.startswith('bootstrap'):
                    self.assertIsInstance(con, connection_base)
                    self.assertNotEqual(peer.host, '127.0.0.1')
                    return
        else:  # pylint: disable=useless-else-on-loop
            self.fail(
                'Failed to connect during %s sec' % (time.time() - _started))

    def test_bootstrap(self):
        """test bootstrapping"""
        self._initiate_bootstrap()
        self._check_bootstrap()
        self._initiate_bootstrap()
        BMConfigParser().set('bitmessagesettings', 'socksproxytype', 'stem')
        program.start_proxyconfig(BMConfigParser())
        self._check_bootstrap()


def run(prog):
    """Starts all tests defined in this module"""
    global program  # pylint: disable=global-statement
    program = prog
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None
    suite = loader.loadTestsFromTestCase(TestCore)
    return unittest.TextTestRunner(verbosity=2).run(suite)
