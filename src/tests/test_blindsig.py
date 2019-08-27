"""
Test for ECC blind signatures
"""
import os
import unittest

from pybitmessage.pyelliptic.eccblind import ECCBlind


class TestBlindSig(unittest.TestCase):
    """
    Test case for ECC blind signature
    """
    def test_blind_sig(self):
        """Test full sequence using a random certifier key and a random message"""
        # See page 127 of the paper
        # (1) Initialization
        signer_obj = ECCBlind()
        point_r = signer_obj.signer_init()

        # (2) Request
        requester_obj = ECCBlind(pubkey=signer_obj.pubkey)
        # only 64 byte messages are planned to be used in Bitmessage
        msg = os.urandom(64)
        msg_blinded = requester_obj.create_signing_request(point_r, msg)

        # (3) Signature Generation
        signature_blinded = signer_obj.blind_sign(msg_blinded)

        # (4) Extraction
        signature = requester_obj.unblind(signature_blinded)

        # (5) Verification
        verifier_obj = ECCBlind(pubkey=signer_obj.pubkey)
        self.assertTrue(verifier_obj.verify(msg, signature))
