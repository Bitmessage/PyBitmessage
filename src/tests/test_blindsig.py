"""
Test for ECC blind signatures
"""
import os
import time
import unittest
from ctypes import cast, c_char_p

from pybitmessage.pyelliptic.eccblind import ECCBlind, Metadata
from pybitmessage.pyelliptic.eccblindchain import ECCBlindChain
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

        # Serialization and deserialisation
        pk = signer_obj.serialize()
        pko = ECCBlind.deserialize(pk)
        self.assertTrue(pko.verify(msg, signature))

    def test_blind_sig_chain(self):
        """Test blind signature chain using a random certifier key and a random message"""

        test_levels = 5
        value = 1
        msg = os.urandom(1024)

        chain = ECCBlindChain()
        ca = ECCBlind()
        signer_obj = ca
        signer_pubkey = signer_obj.serialize()

        for level in range(test_levels):
            if level == 0:
                metadata = Metadata(exp=int(time.time()) + 100,
                                    value=value).serialize()
                requester_obj = ECCBlind(pubkey=signer_obj.pubkey,
                                         metadata=metadata)
            else:
                requester_obj = ECCBlind(pubkey=signer_obj.pubkey)
            point_r = signer_obj.signer_init()

            if level == test_levels - 1:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   msg)
            else:
                msg_blinded = requester.obj.create_signing_request(point_r,
                                                                   signer_pubkey)
            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            chain.add_level(signer_obj.pubkey,
                            signer_obj.metadata.serialize,
                            signature)
            signer_obj = requester_obj
            signer_pubkey = requester_obj.serialize()
        sigchain = chain.serialize()
        verifychain = ECCBlindChain.deserialize(sigchain)
        self.assertTrue(verifychain.verify(msg, value))
