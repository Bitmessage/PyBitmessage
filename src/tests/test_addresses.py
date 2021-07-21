
import unittest
from binascii import unhexlify

from pybitmessage import addresses

from .samples import sample_address, sample_ripe


class TestAddresses(unittest.TestCase):
    """Test addresses manipulations"""

    def test_decode(self):
        """Decode some well known addresses and check the result"""
        self.assertEqual(
            addresses.decodeAddress(sample_address),
            ('success', 2, 1, unhexlify(sample_ripe)))
        status, version, stream, ripe1 = addresses.decodeAddress(
            '2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK')
        self.assertEqual(status, 'success')
        self.assertEqual(stream, 1)
        self.assertEqual(version, 4)
        status, version, stream, ripe2 = addresses.decodeAddress(
            '2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN')
        self.assertEqual(status, 'success')
        self.assertEqual(stream, 1)
        self.assertEqual(version, 3)
        self.assertEqual(ripe1, ripe2)

    def test_encode(self):
        """Encode sample ripe and compare the result to sample address"""
        self.assertEqual(
            sample_address,
            addresses.encodeAddress(2, 1, unhexlify(sample_ripe)))
