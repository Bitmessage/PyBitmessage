"""
Tests for proofofwork module
"""
# pylint: disable=protected-access

import hashlib
import os
import time
import unittest
from struct import pack, unpack

from pybitmessage import proofofwork, protocol

from .samples import sample_pow_target, sample_pow_initial_hash


class TestProofofwork(unittest.TestCase):
    """The main test case for proofofwork"""

    @classmethod
    def setUpClass(cls):
        proofofwork.init()

    def test_calculate(self):
        """Ensure a calculated nonce has sufficient work for the protocol"""
        TTL = 24 * 60 * 60
        payload = pack('>Q', int(time.time() + TTL)) + os.urandom(166)
        nonce = proofofwork.calculate(payload, TTL)[1]
        self.assertTrue(
            protocol.isProofOfWorkSufficient(pack('>Q', nonce) + payload))
        # raise difficulty
        nonce = proofofwork.calculate(payload, TTL, 2000, 2000)[1]
        self.assertTrue(
            protocol.isProofOfWorkSufficient(
                pack('>Q', nonce) + payload, 2000, 2000,
                int(time.time()) + TTL - 3600))

    def test_with_target(self):
        """Do PoW with parameters from test_openclpow and check the result"""
        nonce = proofofwork._doCPoW(
            sample_pow_target, sample_pow_initial_hash)[0]
        trial_value, = unpack(
            '>Q', hashlib.sha512(hashlib.sha512(
                pack('>Q', nonce) + sample_pow_initial_hash
            ).digest()).digest()[0:8])
        self.assertLess((nonce - trial_value), sample_pow_target)
