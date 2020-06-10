"""
Test if OpenSSL is working correctly
"""
import unittest

from pybitmessage.pyelliptic.openssl import OpenSSL

try:
    OpenSSL.BN_bn2binpad
    have_pad = True
except AttributeError:
    have_pad = None


class TestOpenSSL(unittest.TestCase):
    """
    Test cases for OpenSSL
    """
    def test_is_odd(self):
        """Test BN_is_odd implementation"""
        ctx = OpenSSL.BN_CTX_new()
        a = OpenSSL.BN_new()
        group = OpenSSL.EC_GROUP_new_by_curve_name(
            OpenSSL.get_curve("secp256k1"))
        OpenSSL.EC_GROUP_get_order(group, a, ctx)

        bad = 0
        for _ in range(1024):
            OpenSSL.BN_rand(a, OpenSSL.BN_num_bits(a), 0, 0)
            if not OpenSSL.BN_is_odd(a) == OpenSSL.BN_is_odd_compatible(a):
                bad += 1
        self.assertEqual(bad, 0)

    @unittest.skipUnless(have_pad, 'Skipping OpenSSL pad test')
    def test_padding(self):
        """Test an alternatie implementation of bn2binpad"""

        ctx = OpenSSL.BN_CTX_new()
        a = OpenSSL.BN_new()
        n = OpenSSL.BN_new()
        group = OpenSSL.EC_GROUP_new_by_curve_name(
            OpenSSL.get_curve("secp256k1"))
        OpenSSL.EC_GROUP_get_order(group, n, ctx)

        bad = 0
        for _ in range(1024):
            OpenSSL.BN_rand(a, OpenSSL.BN_num_bits(n), 0, 0)
            b = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(n))
            c = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(a))
            OpenSSL.BN_bn2binpad(a, b, OpenSSL.BN_num_bytes(n))
            OpenSSL.BN_bn2bin(a, c)
            if b.raw != c.raw.rjust(OpenSSL.BN_num_bytes(n), chr(0)):
                bad += 1
        self.assertEqual(bad, 0)
