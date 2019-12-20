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

import hashlib as HashLib
import hash as Hash
import msgpack
import os
import sys
from openssl import OpenSSL
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
    # init
    k = None
    R = None
    keypair = None
    F = None
    Q = None
    a = None
    b = None
    c = None
    binv = None
    r = None
    m = None
    m_ = None
    s_ = None
    signature = None
    @staticmethod
    def ec_serialize(msg):
        """
        Serialize the data using msgpack
        """
        msg = msgpack.packb(msg, default=encode_datetime, use_bin_type=True)
        return msg

    @staticmethod
    def ec_deSerialize(msg):
        """
        Deserialize the data using msgpack
        """
        msg = msgpack.unpackb(msg)
        return msg

    @staticmethod
    def encrypt_string(hash_string):
        """
        Hashing the data using hashlib
        """
        sha_signature = HashLib.sha256(hash_string).hexdigest()
        return sha_signature

    @staticmethod
    def verify_Chain(msg):
        """
        Verify complete chain with its relevant signature
        """
        Unpacked_dict = ECCBlindChain.ec_deSerialize(msg)
        i = len(Unpacked_dict) - 1
        while i >= 0:
            signature = Unpacked_dict[i]['Sign']
            verifier_obj = ECCBlind(pubkey=Unpacked_dict[i]['Msg']['PubKEY'])
            ret = verifier_obj.verify(ECCBlindChain.ec_serialize(Unpacked_dict[i]['Msg']), signature)
            if ret is True:
                print("Message verified successfully")
            else:
                print("Message verification fails")
            i = i - 1
