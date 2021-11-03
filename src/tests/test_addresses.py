
import unittest
from binascii import unhexlify

from pybitmessage import addresses

from .samples import (
    sample_address, sample_daddr3_512, sample_daddr4_512,
    sample_deterministic_addr4, sample_deterministic_addr3,
    sample_deterministic_ripe, sample_ripe)

sample_addr3 = sample_deterministic_addr3.split('-')[1]
sample_addr4 = sample_deterministic_addr4.split('-')[1]


class TestAddresses(unittest.TestCase):
    """Test addresses manipulations"""

    def test_decode(self):
        """Decode some well known addresses and check the result"""
        self.assertEqual(
            addresses.decodeAddress(sample_address),
            ('success', 2, 1, unhexlify(sample_ripe)))

        status, version, stream, ripe1 = addresses.decodeAddress(
            sample_deterministic_addr4)
        self.assertEqual(status, 'success')
        self.assertEqual(stream, 1)
        self.assertEqual(version, 4)
        status, version, stream, ripe2 = addresses.decodeAddress(sample_addr3)
        self.assertEqual(status, 'success')
        self.assertEqual(stream, 1)
        self.assertEqual(version, 3)
        self.assertEqual(ripe1, ripe2)
        self.assertEqual(ripe1, unhexlify(sample_deterministic_ripe))

    def test_encode(self):
        """Encode sample ripe and compare the result to sample address"""
        self.assertEqual(
            sample_address,
            addresses.encodeAddress(2, 1, unhexlify(sample_ripe)))
        ripe = unhexlify(sample_deterministic_ripe)
        self.assertEqual(
            addresses.encodeAddress(3, 1, ripe),
            'BM-%s' % addresses.encodeBase58(sample_daddr3_512))

    def test_base58(self):
        """Check Base58 encoding and decoding"""
        self.assertEqual(addresses.decodeBase58('1'), 0)
        self.assertEqual(addresses.decodeBase58('!'), 0)
        self.assertEqual(
            addresses.decodeBase58(sample_addr4), sample_daddr4_512)
        self.assertEqual(
            addresses.decodeBase58(sample_addr3), sample_daddr3_512)

        self.assertEqual(addresses.encodeBase58(0), '1')
        self.assertEqual(addresses.encodeBase58(-1), None)
        self.assertEqual(
            sample_addr4, addresses.encodeBase58(sample_daddr4_512))
        self.assertEqual(
            sample_addr3, addresses.encodeBase58(sample_daddr3_512))
