"""Tests for ECC object"""

import unittest

try:
    from pyelliptic.ecc import ECC
except ImportError:
    from pybitmessage.pyelliptic import ECC


class TestECC(unittest.TestCase):
    """The test case for ECC"""

    def test_random_keys(self):
        """A dummy test for random keys in ECC object"""
        eccobj = ECC(curve='secp256k1')
        self.assertEqual(len(eccobj.privkey), 32)
        pubkey = eccobj.get_pubkey()
        self.assertEqual(pubkey[:4], b'\x02\xca\x00\x20')
