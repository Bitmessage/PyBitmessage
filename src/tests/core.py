"""
Tests for core and those that do not work outside
(because of import error for example)
"""

import random  # nosec
import string
import unittest

from helper_msgcoding import MsgEncode, MsgDecode


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


def run():
    """Starts all tests defined in this module"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCore)
    return unittest.TextTestRunner(verbosity=2).run(suite)
