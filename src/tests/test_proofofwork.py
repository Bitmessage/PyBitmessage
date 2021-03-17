"""
Tests for proofofwork module
"""

import hashlib
import unittest
from binascii import unhexlify
from struct import pack, unpack

from pybitmessage import proofofwork


class TestProofofwork(unittest.TestCase):
    """The main test case for proofofwork"""

    @classmethod
    def setUpClass(cls):
        proofofwork.init()

    def test_empty(self):
        """just reproducing the empty test from proofofwork.init()"""
        self.assertEqual(
            proofofwork._doCPoW(2**63, ""), [6485065370652060397, 4])

    def test_with_target(self):
        """Do PoW with parameters from test_openclpow and check the result"""
        target = 54227212183
        initialHash = unhexlify(
            '3758f55b5a8d902fd3597e4ce6a2d3f23daff735f65d9698c270987f4e67ad590'
            'b93f3ffeba0ef2fd08a8dc2f87b68ae5a0dc819ab57f22ad2c4c9c8618a43b3'
        )
        nonce = proofofwork._doCPoW(target, initialHash)[0]
        trialValue, = unpack(
            '>Q', hashlib.sha512(hashlib.sha512(
                pack('>Q', nonce) + initialHash).digest()).digest()[0:8])
        self.assertLess((nonce - trialValue), target)
