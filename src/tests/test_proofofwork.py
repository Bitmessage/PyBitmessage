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


class TestProofofworkBase(unittest.TestCase):
    """Basic test case for proofofwork"""

    @classmethod
    def setUpClass(cls):
        proofofwork.init()

    @staticmethod
    def _make_sample_payload(TTL=7200):
        return pack('>Q', int(time.time() + TTL)) + os.urandom(166)

    def test_calculate(self):
        """Ensure a calculated nonce has sufficient work for the protocol"""
        payload = self._make_sample_payload()
        nonce = proofofwork.calculate(payload, 7200)[1]
        self.assertTrue(
            protocol.isProofOfWorkSufficient(pack('>Q', nonce) + payload))


@unittest.skipUnless(
    os.getenv('BITMESSAGE_TEST_POW'), "BITMESSAGE_TEST_POW is not set")
class TestProofofwork(TestProofofworkBase):
    """The main test case for proofofwork"""

    def test_calculate(self):
        """Extended test for the main proofofwork call"""
        # raise difficulty and TTL
        TTL = 24 * 60 * 60
        payload = self._make_sample_payload(TTL)
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
