"""
Tests for openclpow module
"""
import hashlib
import unittest

import pybitmessage.openclpow as openclpow

from struct import pack, unpack

from test_process import TestProcessProto


class TestOpenClPow(TestProcessProto):
    """
    Main opencl test case
    """

    @classmethod
    def setUpClass(cls):
        openclpow.initCL()
        super(TestOpenClPow, cls).setUpClass()

    @unittest.skipIf(not openclpow.enabledGpus,
                     "No GPUs found / enabled")
    def test_openclpow(self):
        """Check the working of openclpow module"""
        target_ = 54227212183
        initialHash = ("3758f55b5a8d902fd3597e4ce6a2d3f23daff735f65d9698c270987f4e67ad590"
                       "b93f3ffeba0ef2fd08a8dc2f87b68ae5a0dc819ab57f22ad2c4c9c8618a43b3").decode("hex")
        nonce = openclpow.do_opencl_pow(initialHash.encode("hex"), target_)
        trialValue, = unpack(
            '>Q', hashlib.sha512(hashlib.sha512(pack('>Q', nonce) + initialHash).digest()).digest()[0:8])
        self.assertLess((nonce - trialValue), target_)
