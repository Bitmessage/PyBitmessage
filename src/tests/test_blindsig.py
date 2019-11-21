"""
Test for ECC blind signatures
"""
import os
import unittest
from ctypes import cast, c_char_p
import sys
sys.path.insert(1, '/home/cis/Peter_DebPackage/blindsig_Task/PyBitmessage/src/pyelliptic')
from eccblind import ECCBlind
from openssl import OpenSSL
import msgpack
from datetime import datetime  
from datetime import timedelta  
import timedelta
cur = datetime.now()
def encode_datetime(obj):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
#from .src.pyelliptic.eccblind import ECCBlind
#from .src.pyelliptic.openssl import OpenSSL


class TestBlindSig(unittest.TestCase):
    """
    Test case for ECC blind signature
    """
    def test_blind_sig(self):
        import pdb;pdb.set_trace()
        # Local varaible if verify method is called separately aftercomplete chain of signatures
        i = 0   #Loop variable to initiate signature in chain format
        signature_list = [] #Stores the signature as per the order of signing on the msg
        signer_obj_list = [] #Stores the signer as per the order of signing on the msg
        msg_list = [] #Stores the msg as per the order of signing on the msg
        keypair_list=[]
        signature_blinded_list=[]
        
        """Test full sequence using a random certifier key and a random message"""
        # See page 127 of the paper
        # (1) Initialization
        print("**********WELCOME*********************")
        # Metadata for msg as well as second signer pubkey
        
        cur = datetime.now()
        exp = datetime.now()+(timedelta.Timedelta(days = 360))
                
        msg = {"msg":"Hello from CIS","Name": "CIS", "created": cur , "expiry": exp, }
        keymetadata = {"PubKey_Name" :"PUBKEY_CIS","PubKey_create_Date": cur , "PubKey_expiry_Date": exp,}
       
        signer_obj = ECCBlind()#certify
        signer_obj_list.append(signer_obj)
        
        keypair_list.append(signer_obj_list[i].keypair[0]) #List of private keys of signers
        k = 1;

        while i <= 2:
            
            second_signer = ECCBlind()
            signer_obj_list.append(second_signer)
            point_r = signer_obj_list[i].signer_init()
            point_r_second = signer_obj_list[k].signer_init() #Random number as per the second signer
                  
            msg_key = {"pubkey":signer_obj_list[k].pubkey}
            msg = msgpack.packb([msg,msg_key], default=encode_datetime, use_bin_type=True) #Msg packed with second pubkey
            msg_list.append(msg)        
            requester_obj = ECCBlind(pubkey=signer_obj_list[i].pubkey) #Requestor with first signer pubkey
           
            msg_blinded = requester_obj.create_signing_request(point_r_second, msg) # Creating signing request with second signer random number
            msg_blinded_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(msg_blinded))
            OpenSSL.BN_bn2bin(msg_blinded, msg_blinded_str)
           
            signature_blinded = signer_obj_list[k].blind_sign(keypair_list[i],msg_blinded) # Submitting blind sign request with private key 0 
            
            
            signature = requester_obj.unblind(signature_blinded)
            signature_blinded_list.append(signature)
            signature_blinded_str = OpenSSL.malloc(0,
                                                   OpenSSL.BN_num_bytes(
                                                       signature_blinded))
            signature_str = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(signature[0]))
            OpenSSL.BN_bn2bin(signature_blinded, signature_blinded_str)
            OpenSSL.BN_bn2bin(signature[0], signature_str)
            self.assertNotEqual(cast(signature_str, c_char_p).value,
                                cast(signature_blinded_str, c_char_p).value)
           
            # verifier_obj = ECCBlind(pubkey=signer_obj_list[i].pubkey) # Verifier object initialised with certifier object
            
            # self.assertTrue(verifier_obj.verify(msg, signature))
            # msg = msgpack.unpackb(msg)
            # print("Msg at line 87 is ",msg)
            
            # Test level counters       
            i = i + 1 
            k = k + 1
            keypair_list.append(signer_obj_list[i].keypair[0]) # Assigned the next level keys for the next index
        
        print("KeyPair list at line 94 is",keypair_list)
        print("Signature blinded list at line 95 is ",signature_blinded_list)

        # Verify is can be called once all the signature  is performed. 
        k = 2
        while k >= 0:
            print("Value of msg variable at line 107 is ********",msg_list[k])
            verifier_obj = ECCBlind(pubkey=signer_obj_list[k].pubkey)
            self.assertTrue(verifier_obj.verify(msg_list[k], signature_blinded_list[k]))
            print("Msg verified at line 91 for ",k,"+th index")
            msg = msgpack.unpackb(msg_list[k])
            print("Unpacked data is ",msg)
            k = k - 1
            

obj = TestBlindSig('test_blind_sig')
obj.test_blind_sig()
