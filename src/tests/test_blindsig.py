import unittest
from ctypes import cast, c_char_p
import sys
sys.path.insert(1, '/home/cis/ektarepo/PyBitmessage/src/pyelliptic')
#from eccblind import ECCBlind
from eccblindChain import ECCBlindChain
from openssl import OpenSSL
from datetime import datetime
from datetime import timedelta
exp = datetime.now()+(timedelta(days =365))
signer_obj_list = []
msg_unpack_Chain = []

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
            signer_obj = ECCBlindChain()
            signer_obj_list.append(signer_obj)
            if level == 0:
                signer_obj = signer_obj_list[0]              
            else:
                signer_obj = signer_obj_list[level - 1]               

            point_r = signer_obj.signer_init()
            if level is 1:
                PubKey_expiry_Date = exp
                val = 20
            else:
                PubKey_expiry_Date = ""
                val = ""

            msg = {"PubKEY":signer_obj.pubkey,"Expiry":PubKey_expiry_Date,"val":val}
            
            requester_obj = ECCBlindChain(pubkey=signer_obj.pubkey)
            msg_blinded = requester_obj.create_signing_request(point_r, msg )
            msg_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(msg_blinded))
            OpenSSL.BN_bn2bin(msg_blinded, msg_blinded_str)
            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            
            chain = {"Msg":msg,"Sign":signature}
            signature_blinded_str = OpenSSL.malloc(0,
                                                           OpenSSL.BN_num_bytes(
                                                               signature_blinded))
            signature_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature[0]))
            OpenSSL.BN_bn2bin(signature_blinded, signature_blinded_str)
            OpenSSL.BN_bn2bin(signature[0], signature_str)
            self.assertNotEqual(cast(signature_str, c_char_p).value,
                                        cast(signature_blinded_str, c_char_p).value)
            level = level + 1
            msg_unpack_Chain.append(chain)
        level = level - 1
        callChain = ECCBlindChain()
        packed_msg_chain = callChain.ec_serialize(msg_unpack_Chain)
        callChain.verify_Chain(packed_msg_chain)

obj = TestBlindSig('test_blind_sig')

obj.test_blind_sig()
