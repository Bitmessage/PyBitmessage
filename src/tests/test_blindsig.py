import os
import unittest
import hashlib
import hmac
from ctypes import cast, c_char_p
import sys
sys.path.insert(1, '/home/cis/ektarepo/PyBitmessage/src/pyelliptic')
from eccblind import ECCBlind
from openssl import OpenSSL
import msgpack
signer_obj_list = []
msgPubKey = []
msg_list = []
signature_list = []
hash_algo = "sha256"
import base64

class TestBlindSig(unittest.TestCase):
    def hash(message_Value):
        H = hashlib.new(hash_algo)
        H.update(message_Value)
        b_hash = H.digest()
        return b_hash

    def verifySerialize(self,level):
        level = level - 1
        i = level
        while i >= 0:
            if i is 0:
                verifier_obj = ECCBlind(pubkey=signer_obj_list[0].pubkey)
            else:
                verifier_obj = ECCBlind(pubkey=signer_obj_list[i - 1].pubkey)
            self.assertTrue(verifier_obj.verify(msg_list[i], signature_list[i]))
            msg = msgpack.unpackb(msg_list[i])
            print("Unpacked msg at level : ",i,"is ::",msg)
            i = i - 1
        print("Msg at line 62 is ",msg)
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
            msgPubKey.append(signer_obj.pubkey)
            hash_value = hash(msgPubKey[level])
            msg = msgpack.packb(hash_value)
            msg_list.append(msg)
            print("Msg at ",level, "ieration is",msg_list[level])
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
        self.verifySerialize(level)
obj = TestBlindSig('test_blind_sig')
obj.test_blind_sig()





