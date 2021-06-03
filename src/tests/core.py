"""
Tests for core and those that do not work outside
(because of import error for example)
"""

import atexit
import os
import pickle  # nosec
import Queue
import random  # nosec
import shutil
import socket
import string
import sys
import threading
import time
import unittest

import protocol
import state
import helper_sent
import helper_addressbook

from bmconfigparser import config
from helper_msgcoding import MsgEncode, MsgDecode
from helper_sql import sqlQuery, sqlExecute
from network import asyncore_pollchoose as asyncore, knownnodes
from network.bmproto import BMProto
from network.connectionpool import BMConnectionPool
from network.node import Node, Peer
from network.tcp import Socks4aBMConnection, Socks5BMConnection, TCPConnection
from queues import excQueue
from version import softwareVersion

from common import cleanup

try:
    socket.socket().bind(('127.0.0.1', 9050))
    tor_port_free = True
except (OSError, socket.error):
    tor_port_free = False

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
    addr = 'BM-2cVvkzJuQDsQHLqxRXc6HZGPLZnkBLzEZY'

    def tearDown(self):
        """Reset possible unexpected settings after test"""
        knownnodes.addKnownNode(1, Peer('127.0.0.1', 8444), is_self=True)
        config.remove_option('bitmessagesettings', 'dontconnect')
        config.remove_option('bitmessagesettings', 'onionservicesonly')
        config.set('bitmessagesettings', 'socksproxytype', 'none')

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
        config.set('bitmessagesettings', 'dontconnect', 'true')
        try:
            for peer in (Peer("127.0.0.1", 8448),):
                direct = TCPConnection(peer)
                while asyncore.socket_map:
                    print("loop, state = %s" % direct.state)
                    asyncore.loop(timeout=10, count=1)
        except:  # noqa:E722
            self.fail('Exception in test loop')

    def _load_knownnodes(self, filepath):
        with knownnodes.knownNodesLock:
            shutil.copyfile(filepath, knownnodes_file)
        try:
            knownnodes.readKnownNodes()
        except AttributeError as e:
            self.fail('Failed to load knownnodes: %s' % e)

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
        config.set('bitmessagesettings', 'dontconnect', 'true')
        self._wipe_knownnodes()
        knownnodes.addKnownNode(1, Peer('127.0.0.1', 8444), is_self=True)
        knownnodes.cleanupKnownNodes()
        time.sleep(5)

    def _check_connection(self, full=False):
        """
        Check if there is at least one outbound connection to remote host
        with name not starting with "bootstrap" in 6 minutes at most,
        fail otherwise.
        """
        _started = time.time()
        config.remove_option('bitmessagesettings', 'dontconnect')
        proxy_type = config.safeGet(
            'bitmessagesettings', 'socksproxytype')
        if proxy_type == 'SOCKS5':
            connection_base = Socks5BMConnection
        elif proxy_type == 'SOCKS4a':
            connection_base = Socks4aBMConnection
        else:
            connection_base = TCPConnection
        c = 360
        while c > 0:
            time.sleep(1)
            c -= 2
            for peer, con in BMConnectionPool().outboundConnections.iteritems():
                if (
                    peer.host.startswith('bootstrap')
                    or peer.host == 'quzwelsuziwqgpt2.onion'
                ):
                    if c < 60:
                        self.fail(
                            'Still connected to bootstrap node %s after % seconds' %
                            (peer, time.time() - _started))
                    c += 1
                    break
                else:
                    self.assertIsInstance(con, connection_base)
                    self.assertNotEqual(peer.host, '127.0.0.1')
                    if full and not con.fullyEstablished:
                        continue
                    return
        self.fail(
            'Failed to connect during %s sec' % (time.time() - _started))

    def _check_knownnodes(self):
        for stream in knownnodes.knownNodes.itervalues():
            for peer in stream:
                if peer.host.startswith('bootstrap'):
                    self.fail(
                        'Bootstrap server in knownnodes: %s' % peer.host)

    def test_dontconnect(self):
        """all connections are closed 5 seconds after setting dontconnect"""
        self._initiate_bootstrap()
        self.assertEqual(len(BMConnectionPool().connections()), 0)

    def test_connection(self):
        """test connection to bootstrap servers"""
        self._initiate_bootstrap()
        for port in [8080, 8444]:
            for item in socket.getaddrinfo(
                    'bootstrap%s.bitmessage.org' % port, 80):
                try:
                    addr = item[4][0]
                    socket.inet_aton(item[4][0])
                except (TypeError, socket.error):
                    continue
                else:
                    knownnodes.addKnownNode(1, Peer(addr, port))
        self._check_connection(True)

    def test_bootstrap(self):
        """test bootstrapping"""
        config.set('bitmessagesettings', 'socksproxytype', 'none')
        self._initiate_bootstrap()
        self._check_connection()
        self._check_knownnodes()
        # backup potentially enough knownnodes
        knownnodes.saveKnownNodes()
        with knownnodes.knownNodesLock:
            shutil.copyfile(knownnodes_file, knownnodes_file + '.bak')

    @unittest.skipIf(tor_port_free, 'no running tor detected')
    def test_bootstrap_tor(self):
        """test bootstrapping with tor"""
        config.set('bitmessagesettings', 'socksproxytype', 'SOCKS5')
        self._initiate_bootstrap()
        self._check_connection()
        self._check_knownnodes()

    @unittest.skipIf(tor_port_free, 'no running tor detected')
    def test_onionservicesonly(self):
        """ensure bitmessage doesn't try to connect to non-onion nodes
        if onionservicesonly set, wait at least 3 onion nodes
        """
        config.set('bitmessagesettings', 'socksproxytype', 'SOCKS5')
        config.set('bitmessagesettings', 'onionservicesonly', 'true')
        self._load_knownnodes(knownnodes_file + '.bak')
        if len([
            node for node in knownnodes.knownNodes[1]
            if node.host.endswith('.onion')
        ]) < 3:  # generate fake onion nodes if have not enough
            with knownnodes.knownNodesLock:
                for f in ('a', 'b', 'c', 'd'):
                    knownnodes.addKnownNode(1, Peer(f * 16 + '.onion', 8444))
        config.remove_option('bitmessagesettings', 'dontconnect')
        tried_hosts = set()
        for _ in range(360):
            time.sleep(1)
            for peer in BMConnectionPool().outboundConnections:
                if peer.host.endswith('.onion'):
                    tried_hosts.add(peer.host)
                else:
                    if not peer.host.startswith('bootstrap'):
                        self.fail(
                            'Found non onion hostname %s in outbound'
                            'connections!' % peer.host)
                if len(tried_hosts) > 2:
                    return
        self.fail('Failed to find at least 3 nodes to connect within 360 sec')

    def test_udp(self):
        """check default udp setting and presence of Announcer thread"""
        self.assertTrue(
            config.safeGetBoolean('bitmessagesettings', 'udp'))
        for thread in threading.enumerate():
            if thread.name == 'Announcer':  # find Announcer thread
                break
        else:
            return self.fail('No Announcer thread found')

        for _ in range(20):  # wait for UDP socket
            for sock in BMConnectionPool().udpSockets.values():
                thread.announceSelf()
                break
            else:
                time.sleep(1)
                continue
            break
        else:
            self.fail('UDP socket is not started')

        for _ in range(20):
            if state.discoveredPeers:
                peer = state.discoveredPeers.keys()[0]
                self.assertEqual(peer.port, 8444)
                break
            time.sleep(1)
        else:
            self.fail('No self in discovered peers')

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
            subject=subject, message=message
        )
        queryreturn = sqlQuery(
            '''select msgid from sent where ackdata=?''', result)
        self.assertNotEqual(queryreturn[0][0] if queryreturn else '', '')

        column_type = sqlQuery(
            '''select typeof(msgid) from sent where ackdata=?''', result)
        self.assertEqual(column_type[0][0] if column_type else '', 'text')

    def test_old_knownnodes_pickle(self):
        """Testing old (v0.6.2) version knownnodes.dat file"""
        try:
            self._load_knownnodes(
                os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    'test_pattern', 'knownnodes.dat'))
        except self.failureException:
            raise
        finally:
            cleanup(files=('knownnodes.dat',))

    @staticmethod
    def delete_address_from_addressbook(address):
        """Clean up addressbook"""
        sqlQuery('''delete from addressbook where address=?''', address)

    def test_add_same_address_twice_in_addressbook(self):
        """checking same address is added twice in addressbook"""
        self.assertTrue(helper_addressbook.insert(label='test1', address=self.addr))
        self.assertFalse(helper_addressbook.insert(label='test1', address=self.addr))
        self.delete_address_from_addressbook(self.addr)

    def test_is_address_present_in_addressbook(self):
        """checking is address added in addressbook or not"""
        helper_addressbook.insert(label='test1', address=self.addr)
        queryreturn = sqlQuery('''select count(*) from addressbook where address=?''', self.addr)
        self.assertEqual(queryreturn[0][0], 1)
        self.delete_address_from_addressbook(self.addr)

    def test_adding_two_same_case_sensitive_addresses(self):
        """Testing same case sensitive address store in addressbook"""
        address1 = 'BM-2cVWtdUzPwF7UNGDrZftWuHWiJ6xxBpiSP'
        address2 = 'BM-2CvwTDuZpWf7ungdRzFTwUhwIj6XXbPIsp'
        self.assertTrue(helper_addressbook.insert(label='test1', address=address1))
        self.assertTrue(helper_addressbook.insert(label='test2', address=address2))
        self.delete_address_from_addressbook(address1)
        self.delete_address_from_addressbook(address2)

    def test_sqlscripts(self):
        """ Test sql statements"""

        sqlExecute('create table if not exists testtbl (id integer)')
        tables = list(sqlQuery("select name from sqlite_master where type is 'table'"))
        res = [item for item in tables if 'testtbl' in item]
        self.assertEqual(res[0][0], 'testtbl')

        queryreturn = sqlExecute("INSERT INTO testtbl VALUES(101);")
        self.assertEqual(queryreturn, 1)

        queryreturn = sqlQuery('''SELECT * FROM testtbl''')
        self.assertEqual(queryreturn[0][0], 101)

        sqlQuery("DROP TABLE testtbl")


def run():
    """Starts all tests defined in this module"""
    loader = unittest.defaultTestLoader
    loader.sortTestMethodsUsing = None
    suite = loader.loadTestsFromTestCase(TestCore)
    try:
        import bitmessageqt.tests
        from xvfbwrapper import Xvfb
    except ImportError:
        Xvfb = None
    else:
        qt_tests = loader.loadTestsFromModule(bitmessageqt.tests)
        suite.addTests(qt_tests)

    def keep_exc(ex_cls, exc, tb):  # pylint: disable=unused-argument
        """Own exception hook for test cases"""
        excQueue.put(('tests', exc))

    sys.excepthook = keep_exc

    if Xvfb:
        vdisplay = Xvfb(width=1024, height=768)
        vdisplay.start()
        atexit.register(vdisplay.stop)
    return unittest.TextTestRunner(verbosity=2).run(suite)
