"""
Test for ECC blind signatures
"""
import os
import unittest

from src.pyelliptic.eccblind import ECCBlind


class TestBlindSig(unittest.TestCase):
    """
    Test case for ECC blind signature
    """
    def test_blind_sig(self):
        """Test full sequence using a random certifier key and a random message"""
        blind_sig = ECCBlind()
        blind_sig.signer_init()
        msg = os.urandom(64)
        blind_sig.create_signing_request(msg)
        blind_sig.blind_sign()
        blind_sig.unblind()
        self.assertTrue(blind_sig.verify())
