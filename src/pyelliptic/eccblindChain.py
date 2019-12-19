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
from openssl import OpenSSL
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

    def __init__(self, curve="secp256k1", pubkey=None):
        self.ctx = OpenSSL.BN_CTX_new()

        if pubkey:
            self.group, self.G, self.n, self.Q = pubkey
        else:
            self.group = OpenSSL.EC_GROUP_new_by_curve_name(OpenSSL.get_curve(curve))
            # Order n
            self.n = OpenSSL.BN_new()
            OpenSSL.EC_GROUP_get_order(self.group, self.n, self.ctx)

            # Generator G
            self.G = OpenSSL.EC_GROUP_get0_generator(self.group)

            # new keypair
            self.keypair = ECCBlind.ec_gen_keypair(self.group, self.ctx)

            self.Q = self.keypair[1]

        self.pubkey = (self.group, self.G, self.n, self.Q)

        # Identity O (infinity)
        self.iO = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_set_to_infinity(self.group, self.iO)

    def unblind(self, s_):
        """
        Requester unblinds the signature
        """
        self.s_ = s_
        s = OpenSSL.BN_new()
        OpenSSL.BN_mod_mul(s, self.binv, self.s_, self.n, self.ctx)
        OpenSSL.BN_mod_add(s, s, self.c, self.n, self.ctx)
        self.signature = (s, self.F)
        return self.signature

    def create_signing_request(self, R, msg):
        """
        Requester creates a new signing request
        """
        self.R = R

        # Requester: 3 random blinding factors
        self.F = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_set_to_infinity(self.group, self.F)
        temp = OpenSSL.EC_POINT_new(self.group)
        abinv = OpenSSL.BN_new()

        # F != O
        while OpenSSL.EC_POINT_cmp(self.group, self.F, self.iO, self.ctx) == 0:
            self.a = ECCBlind.ec_get_random(self.group, self.ctx)
            self.b = ECCBlind.ec_get_random(self.group, self.ctx)
            self.c = ECCBlind.ec_get_random(self.group, self.ctx)

            # F = b^-1 * R...
            self.binv = ECCBlind.ec_invert(self.group, self.b, self.ctx)
            OpenSSL.EC_POINT_mul(self.group, temp, 0, self.R, self.binv, 0)
            OpenSSL.EC_POINT_copy(self.F, temp)

            # ... + a*b^-1 * Q...
            OpenSSL.BN_mul(abinv, self.a, self.binv, self.ctx)
            OpenSSL.EC_POINT_mul(self.group, temp, 0, self.Q, abinv, 0)
            OpenSSL.EC_POINT_add(self.group, self.F, self.F, temp, 0)

            # ... + c*G
            OpenSSL.EC_POINT_mul(self.group, temp, 0, self.G, self.c, 0)
            OpenSSL.EC_POINT_add(self.group, self.F, self.F, temp, 0)

        # F = (x0, y0)
        self.r = ECCBlind.ec_Ftor(self.F, self.group, self.ctx)

        # Requester: Blinding (m' = br(m) + a)
        self.m = OpenSSL.BN_new()
        msg = ECCBlindChain.ec_serialize(msg)
        # Here key is only the msg as we are passing pubkeys in msg
        hashed_msg = Hash.hmac_sha256(msg, msg)
        OpenSSL.BN_bin2bn(hashed_msg, len(hashed_msg), self.m)

        self.m_ = OpenSSL.BN_new()
        OpenSSL.BN_mod_mul(self.m_, self.b, self.r, self.n, self.ctx)
        OpenSSL.BN_mod_mul(self.m_, self.m_, self.m, self.n, self.ctx)
        OpenSSL.BN_mod_add(self.m_, self.m_, self.a, self.n, self.ctx)
        return self.m_

    def verify(self, msg, signature):
        """
        Verify signature with certifier's pubkey
        """
        # convert msg to BIGNUM
        self.m = OpenSSL.BN_new()
        msg = ECCBlindChain.ec_serialize(msg)
        hashed_msg = Hash.hmac_sha256(msg, msg)
        OpenSSL.BN_bin2bn(hashed_msg, len(hashed_msg), self.m)

        # init
        s, self.F = signature
        if self.r is None:
            self.r = ECCBlind.ec_Ftor(self.F, self.group, self.ctx)

        lhs = OpenSSL.EC_POINT_new(self.group)
        rhs = OpenSSL.EC_POINT_new(self.group)

        OpenSSL.EC_POINT_mul(self.group, lhs, s, 0, 0, 0)

        OpenSSL.EC_POINT_mul(self.group, rhs, 0, self.Q, self.m, 0)
        OpenSSL.EC_POINT_mul(self.group, rhs, 0, rhs, self.r, 0)
        OpenSSL.EC_POINT_add(self.group, rhs, rhs, self.F, self.ctx)

        retval = OpenSSL.EC_POINT_cmp(self.group, lhs, rhs, self.ctx)
        if retval == -1:
            raise RuntimeError("EC_POINT_cmp returned an error")
        else:
            return retval == 0

    @staticmethod
    def verify_Chain(msg):
        """
        Verify complete chain with its relevant signature
        """
        Unpacked_dict = ECCBlindChain.ec_deSerialize(msg)
        i = len(Unpacked_dict) - 1
        while i >= 0:
            signature = Unpacked_dict[i]['Sign']
            verifier_obj = ECCBlindChain(pubkey=Unpacked_dict[i]['Msg']['PubKEY'])
            ret = verifier_obj.verify(Unpacked_dict[i]['Msg'], signature)
            if ret is True:
                print("Message verified successfully")
            else:
                print("Message verification fails")
            i = i - 1
