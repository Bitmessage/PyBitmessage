#!/usr/bin/env python
"""
ECC blind signature functionality based on "An Efficient Blind Signature Scheme
Based on the Elliptic CurveDiscrete Logarithm Problem" by Morteza Nikooghadama
<mnikooghadam@sbu.ac.ir> and Ali Zakerolhosseini <a-zaker@sbu.ac.ir>,
http://www.isecure-journal.com/article_39171_47f9ec605dd3918c2793565ec21fcd7a.pdf
"""

# variable names are based on the math in the paper, so they don't conform
# to PEP8
# pylint: disable=invalid-name

import sys
import msgpack
import hash as Hash
sys.path.insert(1, '/home/cis/ektarepo/PyBitmessage/src/pyelliptic')
from eccblind import ECCBlind


def encode_datetime(obj):
    """
    Method to format time
    """
    return {'Time': int(obj.strftime("%s"))}


class ECCBlindChain(object):  # pylint: disable=too-many-instance-attributes
    """
    # Class for ECC Blind Chain signature functionality
    """
    signature = None

    def ec_serialize(self, msg):
        """
        Serialize the data using msgpack
        """
        msg = msgpack.packb(msg, default=encode_datetime, use_bin_type=True)
        return msg

    def ec_deSerialize(self, msg):
        """
        Deserialize the data using msgpack
        """
        msg = msgpack.unpackb(msg)
        return msg

    def encrypt_string(self, hash_string):
        """
        Hashing the data using hashlib
        """
        sha_signature = Hash.hmac_sha256(hash_string, hash_string)
        return sha_signature

    def verify_Chain(self, msg):
        """
        Verify complete chain with its relevant signature
        """
        call = ECCBlindChain()
        Unpacked_dict = call.ec_deSerialize(msg)
        i = len(Unpacked_dict) - 1
        while i >= 0:
            signature = Unpacked_dict[i]['Sign']
            verifier_obj = ECCBlind(pubkey=Unpacked_dict[i]['Msg']['PubKEY'])
            msgtoverify = call.ec_serialize(Unpacked_dict[i]['Msg'])
            hashedmsg = call.encrypt_string(msgtoverify)
            ret = verifier_obj.verify(hashedmsg, signature)
            if ret is True:
                print("Message verified successfully")
            else:
                print("Message verification fails")
            i = i - 1
