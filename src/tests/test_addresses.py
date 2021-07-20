
import unittest
from binascii import unhexlify

from pybitmessage import addresses


sample_ripe = unhexlify('003cd097eb7f35c87b5dc8b4538c22cb55312a9f')
# stream: 1, version: 2
sample_address = 'BM-onkVu1KKL2UaUss5Upg9vXmqd3esTmV79'


class TestAddresses(unittest.TestCase):
    """Test addresses manipulations"""

    def test_decode(self):
        """Decode some well known addresses and check the result"""
        self.assertEqual(
            addresses.decodeAddress(sample_address),
            ('success', 2, 1, sample_ripe))
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
            addresses.encodeAddress(2, 1, sample_ripe), sample_address)
