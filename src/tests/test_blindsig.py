"""
Tests using API.
"""

from datetime import datetime
from datetime import timedelta
from ctypes import cast, c_char_p
import sys
import os
import unittest
sys.path.insert(1, '/home/cis/ektarepo/PyBitmessage/src/pyelliptic')
from eccblindChain import ECCBlindChain
from eccblind import ECCBlind
from openssl import OpenSSL


EXP = datetime.now() + (timedelta(days=365))
SIGNER_OBJ_LIST = []
MSG_UNPACK_CHAIN = []


class TestBlindSig(unittest.TestCase):
    """
        Class to test blind signature mechanism
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

    def test_blind_sig_chain(self):
        """
        Method to test blind signature chain API
        """
        callchain = ECCBlindChain()
        level = 0
        while level <= 4:
            signer_obj = ECCBlind()
            SIGNER_OBJ_LIST.append(signer_obj)
            if level == 0:
                signer_obj = SIGNER_OBJ_LIST[0]
            else:
                signer_obj = SIGNER_OBJ_LIST[level - 1]
            point_r = signer_obj.signer_init()
            # Check to add metadata with pubkey at level 1
            if level == 1:
                pubkey_expiry_date = EXP
                val = "20"
            else:
                pubkey_expiry_date = ""
                val = ""

            msg = {"PubKEY": signer_obj.pubkey, "Expiry": pubkey_expiry_date, "val": val}
            requester_obj = ECCBlind(pubkey=signer_obj.pubkey)

            # API to serialize the msg using msgpack
            serialized_msg = callchain.ec_serialize(msg)

            # API to hash the data after serializing
            hashed_msg = callchain.encrypt_string(serialized_msg)
            msg_blinded = requester_obj.create_signing_request(point_r, hashed_msg)
            msg_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(msg_blinded))
            OpenSSL.BN_bn2bin(msg_blinded, msg_blinded_str)

            # Signature Generation
            signature_blinded = signer_obj.blind_sign(msg_blinded)

            # Signature extraction
            signature = requester_obj.unblind(signature_blinded)

            # Appending Signature with the msg
            chain = {"Msg": msg, "Sign": signature}
            signature_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature_blinded))
            signature_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature[0]))
            OpenSSL.BN_bn2bin(signature_blinded, signature_blinded_str)
            OpenSSL.BN_bn2bin(signature[0], signature_str)
            self.assertNotEqual(cast(signature_str, c_char_p).value, cast(signature_blinded_str, c_char_p).value)
            level = level + 1

            # Appending complete chain for verification
            MSG_UNPACK_CHAIN.append(chain)
        level = level - 1
        packed_msg_chain = callchain.ec_serialize(MSG_UNPACK_CHAIN)
        callchain.verify_Chain(packed_msg_chain)


OBJ = TestBlindSig('test_blind_sig_chain')
OBJ.test_blind_sig_chain()
