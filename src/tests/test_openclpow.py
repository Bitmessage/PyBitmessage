"""
Tests for openclpow module
"""

import unittest
from binascii import hexlify

from pybitmessage import openclpow, proofofwork

from .samples import sample_pow_target, sample_pow_initial_hash


class TestOpenClPow(unittest.TestCase):
    """
    Main opencl test case
    """

    @classmethod
    def setUpClass(cls):
        openclpow.initCL()

    @unittest.skipUnless(openclpow.enabledGpus, "No GPUs found / enabled")
    def test_openclpow(self):
        """Check the working of openclpow module"""
        nonce = openclpow.do_opencl_pow(
            hexlify(sample_pow_initial_hash), sample_pow_target)
        self.assertLess(
            nonce - proofofwork.trial_value(nonce, sample_pow_initial_hash),
            sample_pow_target)
