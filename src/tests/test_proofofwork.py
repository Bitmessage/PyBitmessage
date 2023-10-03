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
from pybitmessage.defaults import (
    networkDefaultProofOfWorkNonceTrialsPerByte,
    networkDefaultPayloadLengthExtraBytes)

from .samples import sample_pow_target, sample_pow_initial_hash

default_ttl = 7200


class TestProofofworkBase(unittest.TestCase):
    """Basic test case for proofofwork"""

    @classmethod
    def setUpClass(cls):
        proofofwork.init()

    @staticmethod
    def _make_sample_payload(TTL=default_ttl):
        return pack('>Q', int(time.time() + TTL)) + os.urandom(166)

    def test_calculate(self):
        """Ensure a calculated nonce has sufficient work for the protocol"""
        payload = self._make_sample_payload()
        nonce = proofofwork.calculate(payload, default_ttl)[1]
        self.assertTrue(
            protocol.isProofOfWorkSufficient(pack('>Q', nonce) + payload))


@unittest.skipUnless(
    os.getenv('BITMESSAGE_TEST_POW'), "BITMESSAGE_TEST_POW is not set")
class TestProofofwork(TestProofofworkBase):
    """The main test case for proofofwork"""

    @classmethod
    def tearDownClass(cls):
        import state
        state.shutdown = 0

    def setUp(self):
        self.tearDownClass()

    def _make_sample_data(self):
        payload = self._make_sample_payload()
        return payload, proofofwork.getTarget(
            len(payload), default_ttl,
            networkDefaultProofOfWorkNonceTrialsPerByte,
            networkDefaultPayloadLengthExtraBytes
        ), hashlib.sha512(payload).digest()

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

        import state

        with self.assertRaises(StopIteration):
            state.shutdown = 1
            proofofwork.calculate(payload, TTL)

    def test_CPoW(self):
        """Do PoW with parameters from test_openclpow and check the result"""
        nonce = proofofwork._doCPoW(
            sample_pow_target, sample_pow_initial_hash)[0]
        trial_value, = unpack(
            '>Q', hashlib.sha512(hashlib.sha512(
                pack('>Q', nonce) + sample_pow_initial_hash
            ).digest()).digest()[0:8])
        self.assertLess((nonce - trial_value), sample_pow_target)

    def test_SafePoW(self):
        """Do python PoW for a sample payload and check by protocol"""
        payload, target, initial_hash = self._make_sample_data()
        nonce = proofofwork._doSafePoW(target, initial_hash)[1]
        self.assertTrue(
            protocol.isProofOfWorkSufficient(pack('>Q', nonce) + payload))

    def test_FastPoW(self):
        """Do python multiprocessing PoW for a sample payload and check"""
        payload, target, initial_hash = self._make_sample_data()
        nonce = proofofwork._doFastPoW(target, initial_hash)[1]
        self.assertTrue(
            protocol.isProofOfWorkSufficient(pack('>Q', nonce) + payload))
