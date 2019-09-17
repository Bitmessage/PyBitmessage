"""
Test for ECC blind signatures
"""
import os
import unittest
from ctypes import cast, c_char_p

from pybitmessage.pyelliptic.eccblind import ECCBlind
from pybitmessage.pyelliptic.openssl import OpenSSL


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

        # check
        msg_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(msg_blinded))
        OpenSSL.BN_bn2bin(msg_blinded, msg_blinded_str)
        self.assertNotEqual(msg, cast(msg_blinded_str, c_char_p).value)

        # (3) Signature Generation
        signature_blinded = signer_obj.blind_sign(msg_blinded)

        # (4) Extraction
        signature = requester_obj.unblind(signature_blinded)

        # check
        signature_blinded_str = OpenSSL.malloc(0,
                                               OpenSSL.BN_num_bytes(
                                                   signature_blinded))
        signature_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature[0]))
        OpenSSL.BN_bn2bin(signature_blinded, signature_blinded_str)
        OpenSSL.BN_bn2bin(signature[0], signature_str)
        self.assertNotEqual(cast(signature_str, c_char_p).value,
                            cast(signature_blinded_str, c_char_p).value)

        # (5) Verification
        verifier_obj = ECCBlind(pubkey=signer_obj.pubkey)
        self.assertTrue(verifier_obj.verify(msg, signature))
