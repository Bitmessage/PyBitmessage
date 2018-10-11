"""
Tests for core and those that do not work outside
(because of import error for example)
"""

import os
import pickle  # nosec
import Queue
import random  # nosec
import string
import time
import unittest

import knownnodes
import state
from helper_msgcoding import MsgEncode, MsgDecode
from queues import excQueue

knownnodes_file = os.path.join(state.appdata, 'knownnodes.dat')


def pickle_knownnodes():
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

    def _wipe_knownnodes(self):
        with knownnodes.knownNodesLock:
            knownnodes.knownNodes = {stream: {} for stream in range(1, 4)}

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
        for nodes in knownnodes.knownNodes.itervalues():
            for node in nodes.itervalues():
                node['lastseen'] -= 2419205  # older than 28 days
        # time.sleep(303)  # singleCleaner wakes up every 5 min
        knownnodes.cleanupKnownNodes()
        while True:
            try:
                thread, exc = excQueue.get(block=False)
            except Queue.Empty:
                return
            if thread == 'Asyncore' and isinstance(exc, IndexError):
                self.fail("IndexError because of empty knownNodes!")


def run():
    """Starts all tests defined in this module"""
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None
    suite = loader.loadTestsFromTestCase(TestCore)
    return unittest.TextTestRunner(verbosity=2).run(suite)
