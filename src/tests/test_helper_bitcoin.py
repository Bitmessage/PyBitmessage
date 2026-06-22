"""Test for helperbitcoin"""
import unittest
from pybitmessage.helper_bitcoin import (
    calculateBitcoinAddressFromPubkey,
    calculateTestnetAddressFromPubkey
)
from .samples import sample_pubsigningkey

PUB_SIGNING_KEY = sample_pubsigningkey
# CORRESPONDING BITCONADDRESS AND TESTNET ADDRESS
BITCOINADDRESS = b'1CJQzhGb1Lh4DwDoxbTSZbTkSq2zJ7LAK7'
TESTNETADDRESS = b'mrpNHkMZpN8K13hRgARpPWg5JpdhDVUVGA'


class TestHelperBitcoin(unittest.TestCase):
    """Test class for ObjectProcessor"""

    def test_calculateBitcoinAddressFromPubkey(self):
        """Test calculateBitcoinAddressFromPubkey"""
        bitcoinAddress = calculateBitcoinAddressFromPubkey(PUB_SIGNING_KEY)
        self.assertEqual(bitcoinAddress, BITCOINADDRESS)

    def test_calculateTestnetAddressFromPubkey(self):
        """Test calculateTestnetAddressFromPubkey"""
        testnetAddress = calculateTestnetAddressFromPubkey(PUB_SIGNING_KEY)
        self.assertEqual(testnetAddress, TESTNETADDRESS)
