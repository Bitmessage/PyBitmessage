"""
Test the arithmetic functions
"""

from binascii import unhexlify
import unittest

try:
    from pyelliptic import arithmetic
except ImportError:
    from pybitmessage.pyelliptic import arithmetic

from .samples import (
    sample_deterministic_addr3, sample_deterministic_addr4,
    sample_daddr3_512, sample_daddr4_512,
    sample_factor, sample_point, sample_pubsigningkey, sample_pubencryptionkey,
    sample_privsigningkey, sample_privencryptionkey,
    sample_privsigningkey_wif, sample_privencryptionkey_wif,
    sample_wif_privsigningkey, sample_wif_privencryptionkey
)


class TestArithmetic(unittest.TestCase):
    """Test arithmetic functions"""
    def test_base10_multiply(self):
        """Test arithmetic.base10_multiply"""
        self.assertEqual(
            sample_point,
            arithmetic.base10_multiply(arithmetic.G, sample_factor))

    def test_base58(self):
        """Test encoding/decoding base58 using arithmetic functions"""
        self.assertEqual(
            arithmetic.decode(arithmetic.changebase(
                sample_deterministic_addr4, 58, 256), 256), sample_daddr4_512)
        self.assertEqual(
            arithmetic.decode(arithmetic.changebase(
                sample_deterministic_addr3, 58, 256), 256), sample_daddr3_512)
        self.assertEqual(
            arithmetic.changebase(
                arithmetic.encode(sample_daddr4_512, 256), 256, 58),
            sample_deterministic_addr4)
        self.assertEqual(
            arithmetic.changebase(
                arithmetic.encode(sample_daddr3_512, 256), 256, 58),
            sample_deterministic_addr3)

    def test_wif(self):
        """Decode WIFs of [chan] bitmessage and check the keys"""
        self.assertEqual(
            sample_wif_privsigningkey,
            arithmetic.changebase(arithmetic.changebase(
                sample_privsigningkey_wif, 58, 256)[1:-4], 256, 16))
        self.assertEqual(
            sample_wif_privencryptionkey,
            arithmetic.changebase(arithmetic.changebase(
                sample_privencryptionkey_wif, 58, 256)[1:-4], 256, 16))

    def test_decode(self):
        """Decode sample privsigningkey from hex to int and compare to factor"""
        self.assertEqual(
            arithmetic.decode(sample_privsigningkey, 16), sample_factor)

    def test_encode(self):
        """Encode sample factor into hex and compare to privsigningkey"""
        self.assertEqual(
            arithmetic.encode(sample_factor, 16), sample_privsigningkey)

    def test_changebase(self):
        """Check the results of changebase()"""
        self.assertEqual(
            arithmetic.changebase(sample_privsigningkey, 16, 256, minlen=32),
            unhexlify(sample_privsigningkey))
        self.assertEqual(
            arithmetic.changebase(sample_pubsigningkey, 16, 256, minlen=64),
            unhexlify(sample_pubsigningkey))
        self.assertEqual(
            32,  # padding
            len(arithmetic.changebase(sample_privsigningkey[:5], 16, 256, 32)))

    def test_hex_to_point(self):
        """Check that sample_pubsigningkey is sample_point encoded in hex"""
        self.assertEqual(
            arithmetic.hex_to_point(sample_pubsigningkey), sample_point)

    def test_point_to_hex(self):
        """Check that sample_point is sample_pubsigningkey decoded from hex"""
        self.assertEqual(
            arithmetic.point_to_hex(sample_point), sample_pubsigningkey)

    def test_privtopub(self):
        """Generate public keys and check the result"""
        self.assertEqual(
            arithmetic.privtopub(sample_privsigningkey),
            sample_pubsigningkey
        )
        self.assertEqual(
            arithmetic.privtopub(sample_privencryptionkey),
            sample_pubencryptionkey
        )
