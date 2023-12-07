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

from .partial import TestPartialRun
from .samples import sample_pow_target, sample_pow_initial_hash

default_ttl = 7200


class TestProofofworkBase(TestPartialRun):
    """Basic test case for proofofwork"""

    @classmethod
    def setUpClass(cls):
        proofofwork.init()
        super(TestProofofworkBase, cls).setUpClass()

    def setUp(self):
        self.state.shutdown = 0

    @staticmethod
    def _make_sample_payload(TTL=default_ttl):
        return pack('>Q', int(time.time() + TTL)) + os.urandom(166)

    def test_calculate(self):
        """Ensure a calculated nonce has sufficient work for the protocol"""
        payload = self._make_sample_payload()
        nonce = proofofwork.calculate(payload, default_ttl)[1]
        self.assertTrue(
            protocol.isProofOfWorkSufficient(pack('>Q', nonce) + payload))

        # pylint: disable=import-outside-toplevel
        from class_singleWorker import singleWorker

        self.assertTrue(protocol.isProofOfWorkSufficient(
            singleWorker._doPOWDefaults(payload, default_ttl)))


@unittest.skipUnless(
    os.getenv('BITMESSAGE_TEST_POW'), "BITMESSAGE_TEST_POW is not set")
class TestProofofwork(TestProofofworkBase):
    """The main test case for proofofwork"""

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

        # pylint: disable=import-outside-toplevel
        from class_singleWorker import singleWorker

        with self.assertLogs('default') as cm:
            self.assertTrue(protocol.isProofOfWorkSufficient(
                singleWorker._doPOWDefaults(payload, TTL, log_prefix='+')))
        self.assertEqual(
            cm.output[0],
            'INFO:default:+ Doing proof of work... TTL set to %s' % TTL)
        self.assertEqual(
            cm.output[1][:34], 'INFO:default:+ Found proof of work')

        with self.assertLogs('default') as cm:
            self.assertTrue(protocol.isProofOfWorkSufficient(
                singleWorker._doPOWDefaults(payload, TTL, log_time=True)))
        self.assertEqual(cm.output[2][:22], 'INFO:default:PoW took ')

        with self.assertRaises(StopIteration):
            self.state.shutdown = 1
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
