import os
import unittest
from ctypes import cast, c_char_p
import sys
sys.path.insert(1, '/home/cis/ektarepo/PyBitmessage/src/pyelliptic')
from eccblind import ECCBlind
from openssl import OpenSSL
import msgpack
from datetime import datetime
from datetime import timedelta
import timedelta
cur = datetime.now()
exp = datetime.now()+(timedelta.Timedelta(days = 365))
def encode_datetime(obj):
        return {'Time': int(exp.strftime("%s"))}
signer_obj_list = []
signature_list = []
msg_Chain = []

class TestBlindSig(unittest.TestCase):
    keymetadata = {"PubKey_expiry_Date": "", "Value" : "",}
    def test_blind_sig(self):
        level = 0
        while level <= 4:
            signer_obj = ECCBlind()
            signer_obj_list.append(signer_obj)
            if level == 0:
                signer_obj = signer_obj_list[0]              
            else:
                signer_obj = signer_obj_list[level - 1]               

            point_r = signer_obj.signer_init()
            PubKey = {"Public_Key":signer_obj.pubkey }
                        
            if level is 1:
                keymetadata = {"PubKey_expiry_Date": exp, "Value" : 20,}
                msg = msgpack.packb([PubKey,keymetadata], default=encode_datetime, use_bin_type=True)
            else:
                msg = msgpack.packb([PubKey,self.keymetadata], default=encode_datetime, use_bin_type=True)  
            msg_Chain.append(msg)
            
            requester_obj = ECCBlind(pubkey=signer_obj.pubkey)
            msg_blinded = requester_obj.create_signing_request(point_r, msg)
            msg_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(msg_blinded))
            OpenSSL.BN_bn2bin(msg_blinded, msg_blinded_str)

            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            signature_list.append(signature)

            signature_blinded_str = OpenSSL.malloc(0,
                                                           OpenSSL.BN_num_bytes(
                                                               signature_blinded))
            signature_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature[0]))
            OpenSSL.BN_bn2bin(signature_blinded, signature_blinded_str)
            OpenSSL.BN_bn2bin(signature[0], signature_str)
            self.assertNotEqual(cast(signature_str, c_char_p).value,
                                        cast(signature_blinded_str, c_char_p).value)
            level = level + 1
        level = level - 1
        callChain = ECCBlind()
        callChain.verify_Chain(msg_Chain,signature_list,signer_obj_list)

obj = TestBlindSig('test_blind_sig')

obj.test_blind_sig()