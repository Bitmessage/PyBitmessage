import os
import unittest

from ctypes import cast, c_char_p
import sys
sys.path.insert(1, '/home/cis/ektarepo/PyBitmessage/src/pyelliptic')
from eccblind import ECCBlind
from openssl import OpenSSL
import msgpack
signer_obj_list = []
msgPubKey = []

class TestBlindSig(unittest.TestCase):
    def test_blind_sig(self):
        level = 0
        while level < 5:
            signer_obj = ECCBlind()
            signer_obj_list.append(signer_obj)
            
            if level == 0:
                signer_obj = signer_obj_list[0]              
            else:
                signer_obj = signer_obj_list[level - 1]               

            point_r = signer_obj.signer_init()
            msgPubKey.append(signer_obj.pubkey)
            msg = msgpack.packb(msgPubKey)
           
            requester_obj = ECCBlind(pubkey=signer_obj.pubkey)
            msg_blinded = requester_obj.create_signing_request(point_r, msg)

            msg_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(msg_blinded))
            OpenSSL.BN_bn2bin(msg_blinded, msg_blinded_str)

            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)

            signature_blinded_str = OpenSSL.malloc(0,
                                                           OpenSSL.BN_num_bytes(
                                                               signature_blinded))
            signature_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature[0]))
            OpenSSL.BN_bn2bin(signature_blinded, signature_blinded_str)
            OpenSSL.BN_bn2bin(signature[0], signature_str)
            self.assertNotEqual(cast(signature_str, c_char_p).value,
                                        cast(signature_blinded_str, c_char_p).value)

            verifier_obj = ECCBlind(pubkey=signer_obj.pubkey)
                
            self.assertTrue(verifier_obj.verify(msg, signature))
            msg = msgpack.unpackb(msg)
            

            level = level + 1

        print("Msg at line 62 is ",msg)
obj = TestBlindSig('test_blind_sig')
obj.test_blind_sig()





