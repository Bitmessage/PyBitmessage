"""
Tests for core and those that do not work outside
(because of import error for example)
"""

import os
import pickle  # nosec
import Queue
import random  # nosec
import shutil
import string
import sys
import time
import unittest

import protocol
import state
import helper_sent

from bmconfigparser import BMConfigParser
from helper_msgcoding import MsgEncode, MsgDecode
from helper_startup import start_proxyconfig
from helper_sql import sqlQuery
from network import asyncore_pollchoose as asyncore, knownnodes
from network.bmproto import BMProto
from network.connectionpool import BMConnectionPool
from network.node import Node, Peer
from network.tcp import Socks4aBMConnection, Socks5BMConnection, TCPConnection
from queues import excQueue
from version import softwareVersion

from common import cleanup

try:
    import stem.version as stem_version
except ImportError:
    stem_version = None

knownnodes_file = os.path.join(state.appdata, 'knownnodes.dat')


def pickle_knownnodes():
    """Generate old style pickled knownnodes.dat"""
    now = time.time()
    with open(knownnodes_file, 'wb') as dst:
        pickle.dump({
            stream: {
                Peer(
                    '%i.%i.%i.%i' % tuple([
                        random.randint(1, 255) for i in range(4)]),
                    8444): {'lastseen': now, 'rating': 0.1}
                for i in range(1, 4)  # 3 test nodes
            }
            for stream in range(1, 4)  # 3 test streams
        }, dst)


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
            for peer in (Peer("127.0.0.1", 8448),):
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
        cleanup(files=('knownnodes.dat',))
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
        knownnodes.addKnownNode(1, Peer('127.0.0.1', 8444), is_self=True)
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
        self.fail(
            'Failed to connect during %s sec' % (time.time() - _started))

    def test_bootstrap(self):
        """test bootstrapping"""
        self._initiate_bootstrap()
        self._check_bootstrap()

    @unittest.skipUnless(stem_version, 'No stem, skipping tor dependent test')
    def test_bootstrap_tor(self):
        """test bootstrapping with tor"""
        self._initiate_bootstrap()
        BMConfigParser().set('bitmessagesettings', 'socksproxytype', 'stem')
        start_proxyconfig()
        self._check_bootstrap()

    @unittest.skipUnless(stem_version, 'No stem, skipping tor dependent test')
    def test_onionservicesonly(self):  # this should start after bootstrap
        """
        set onionservicesonly, wait for 3 connections and check them all
        are onions
        """
        BMConfigParser().set('bitmessagesettings', 'socksproxytype', 'SOCKS5')
        BMConfigParser().set('bitmessagesettings', 'onionservicesonly', 'true')
        self._initiate_bootstrap()
        BMConfigParser().remove_option('bitmessagesettings', 'dontconnect')
        for _ in range(360):
            time.sleep(1)
            for n, peer in enumerate(BMConnectionPool().outboundConnections):
                if n > 2:
                    return
                if (
                    not peer.host.endswith('.onion')
                    and not peer.host.startswith('bootstrap')
                ):
                    self.fail(
                        'Found non onion hostname %s in outbound connections!'
                        % peer.host)
        self.fail('Failed to connect to at least 3 nodes within 360 sec')

    @staticmethod
    def _decode_msg(data, pattern):
        proto = BMProto()
        proto.bm_proto_reset()
        proto.payload = data[protocol.Header.size:]
        return proto.decode_payload_content(pattern)

    def test_version(self):
        """check encoding/decoding of the version message"""
        # with single stream
        msg = protocol.assembleVersionMessage('127.0.0.1', 8444, [1])
        decoded = self._decode_msg(msg, "IQQiiQlsLv")
        peer, _, ua, streams = self._decode_msg(msg, "IQQiiQlsLv")[4:]
        self.assertEqual(
            peer, Node(11 if state.dandelion else 3, '127.0.0.1', 8444))
        self.assertEqual(ua, '/PyBitmessage:' + softwareVersion + '/')
        self.assertEqual(streams, [1])
        # with multiple streams
        msg = protocol.assembleVersionMessage('127.0.0.1', 8444, [1, 2, 3])
        decoded = self._decode_msg(msg, "IQQiiQlslv")
        peer, _, ua = decoded[4:7]
        streams = decoded[7:]
        self.assertEqual(streams, [1, 2, 3])

    def test_insert_method_msgid(self):
        """Test insert method of helper_sent module with message sending"""
        fromAddress = 'BM-2cTrmD22fLRrumi3pPLg1ELJ6PdAaTRTdfg'
        toAddress = 'BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEgU9U'
        message = 'test message'
        subject = 'test subject'
        result = helper_sent.insert(
            toAddress=toAddress, fromAddress=fromAddress,
            subject=subject, message=message,
        )
        queryreturn = sqlQuery(
            '''select msgid from sent where ackdata=?''', result)
        self.assertNotEqual(queryreturn[0][0] if queryreturn else '', '')

        column_type = sqlQuery(
            '''select typeof(msgid) from sent where ackdata=?''', result)
        self.assertEqual(column_type[0][0] if column_type else '', 'text')

    def test_old_knownnodes_pickle(self):
        """Testing old(v.0.6.2) version knownnodes.dat file"""
        try:
            old_source_file = os.path.join(
                os.path.abspath(os.path.dirname(__file__)), 'test_pattern', 'knownnodes.dat')
            new_destination_file = os.path.join(state.appdata, 'knownnodes.dat')
            shutil.copyfile(old_source_file, new_destination_file)
            knownnodes.readKnownNodes()
        except AttributeError as e:
            self.fail('Failed to load knownnodes: %s' % e)
        finally:
            cleanup(files=('knownnodes.dat',))


def run():
    """Starts all tests defined in this module"""
    loader = unittest.defaultTestLoader
    loader.sortTestMethodsUsing = None
    suite = loader.loadTestsFromTestCase(TestCore)
    try:
        import bitmessageqt.tests
    except ImportError:
        pass
    else:
        qt_tests = loader.loadTestsFromModule(bitmessageqt.tests)
        suite.addTests(qt_tests)

    def keep_exc(ex_cls, exc, tb):  # pylint: disable=unused-argument
        """Own exception hook for test cases"""
        excQueue.put(('tests', exc))

    sys.excepthook = keep_exc

    return unittest.TextTestRunner(verbosity=2).run(suite)
