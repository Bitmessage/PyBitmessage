"""
Tests using API.
"""

import unittest
from ctypes import cast, c_char_p
import sys
from datetime import datetime
from datetime import timedelta
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
        """
        Method to test blind signature API
        """
        level = 0
        while level <= 4:
            signer_obj = ECCBlind()
            SIGNER_OBJ_LIST.append(signer_obj)
            if level == 0:
                signer_obj = SIGNER_OBJ_LIST[0]
            else:
                signer_obj = SIGNER_OBJ_LIST[level - 1]
            point_r = signer_obj.signer_init()
            if level == 1:
                pubkey_expiry_date = EXP
                val = 20
            else:
                pubkey_expiry_date = ""
                val = ""

            msg = {"PubKEY": signer_obj.pubkey, "Expiry": pubkey_expiry_date, "val": val}
            requester_obj = ECCBlindChain(pubkey=signer_obj.pubkey)
            msg_blinded = requester_obj.create_signing_request(point_r, msg)
            msg_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(msg_blinded))
            OpenSSL.BN_bn2bin(msg_blinded, msg_blinded_str)
            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            chain = {"Msg": msg, "Sign": signature}
            signature_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature_blinded))
            signature_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature[0]))
            OpenSSL.BN_bn2bin(signature_blinded, signature_blinded_str)
            OpenSSL.BN_bn2bin(signature[0], signature_str)
            self.assertNotEqual(cast(signature_str, c_char_p).value, 
                                                                cast(signature_blinded_str, c_char_p).value)
            level = level + 1
            MSG_UNPACK_CHAIN.append(chain)
        level = level - 1
        callchain = ECCBlindChain()
        packed_msg_chain = callchain.ec_serialize(MSG_UNPACK_CHAIN)
        callchain.verify_Chain(packed_msg_chain)


OBJ = TestBlindSig('test_blind_sig')
OBJ.test_blind_sig()
