#!/usr/bin/env python
"""
ECC blind signature functionality based on
"An Efficient Blind Signature Scheme
Based on the Elliptic CurveDiscrete Logarithm Problem" by Morteza Nikooghadama
<mnikooghadam@sbu.ac.ir> and Ali Zakerolhosseini <a-zaker@sbu.ac.ir>,
http://www.isecure-journal.com/article_39171_47f9ec605dd3918c2793565ec21fcd7a.pdf
"""

# variable names are based on the math in the paper, so they don't conform
# to PEP8

import time
from hashlib import sha256
from struct import pack, unpack

from .openssl import OpenSSL

# first byte in serialisation can contain data
Y_BIT = 0x01
COMPRESSED_BIT = 0x02

# formats
BIGNUM = '!32s'
EC = '!B32s'
PUBKEY = '!BB33s'


class Expiration(object):
    """Expiration of pubkey"""
    @staticmethod
    def deserialize(val):
        """Create an object out of int"""
        year = ((val & 0xF0) >> 4) + 2020
        month = val & 0x0F
        assert month < 12
        return Expiration(year, month)

    def __init__(self, year, month):
        assert isinstance(year, int)
        assert year > 2019 and year < 2036
        assert isinstance(month, int)
        assert month < 12
        self.year = year
        self.month = month
        self.exp = year + month / 12.0

    def serialize(self):
        """Make int out of object"""
        return ((self.year - 2020) << 4) + self.month

    def verify(self):
        """Check if the pubkey has expired"""
        now = time.gmtime()
        return self.exp >= now.tm_year + (now.tm_mon - 1) / 12.0


class Value(object):
    """Value of a pubkey"""
    @staticmethod
    def deserialize(val):
        """Make object out of int"""
        return Value(val)

    def __init__(self, value=0xFF):
        assert isinstance(value, int)
        self.value = value

    def serialize(self):
        """Make int out of object"""
        return self.value & 0xFF

    def verify(self, value):
        """Verify against supplied value"""
        return value <= self.value


class ECCBlind(object):  # pylint: disable=too-many-instance-attributes
    """
    Class for ECC blind signature functionality
    """

    # init
    k = None
    R = None
    F = None
    d = None
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
    exp = None
    val = None

    def ec_get_random(self):
        """
        Random integer within the EC order
        """
        randomnum = OpenSSL.BN_new()
        OpenSSL.BN_rand(randomnum, OpenSSL.BN_num_bits(self.n), 0, 0)
        return randomnum

    def ec_invert(self, a):
        """
        ECC inversion
        """
        inverse = OpenSSL.BN_mod_inverse(0, a, self.n, self.ctx)
        return inverse

    def ec_gen_keypair(self):
        """
        Generate an ECC keypair
        We're using compressed keys
        """
        d = self.ec_get_random()
        Q = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_mul(self.group, Q, d, 0, 0, 0)
        return (d, Q)

    def ec_Ftor(self, F):
        """
        x0 coordinate of F
        """
        # F = (x0, y0)
        x0 = OpenSSL.BN_new()
        y0 = OpenSSL.BN_new()
        OpenSSL.EC_POINT_get_affine_coordinates(self.group, F, x0, y0, self.ctx)
        OpenSSL.BN_free(y0)
        return x0

    def _ec_point_serialize(self, point):
        """Make an EC point into a string"""
        try:
            x = OpenSSL.BN_new()
            y = OpenSSL.BN_new()
            OpenSSL.EC_POINT_get_affine_coordinates(
                self.group, point, x, y, 0)
            y_byte = (OpenSSL.BN_is_odd(y) & Y_BIT) | COMPRESSED_BIT
            l_ = OpenSSL.BN_num_bytes(self.n)
            try:
                bx = OpenSSL.malloc(0, l_)
                OpenSSL.BN_bn2binpad(x, bx, l_)
                out = bx.raw
            except AttributeError:
                # padding manually
                bx = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(x))
                OpenSSL.BN_bn2bin(x, bx)
                out = bx.raw.rjust(l_, chr(0))
            return pack(EC, y_byte, out)

        finally:
            OpenSSL.BN_clear_free(x)
            OpenSSL.BN_clear_free(y)

    def _ec_point_deserialize(self, data):
        """Make a string into an EC point"""
        y_bit, x_raw = unpack(EC, data)
        x = OpenSSL.BN_bin2bn(x_raw, OpenSSL.BN_num_bytes(self.n), 0)
        y_bit &= Y_BIT
        retval = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_set_compressed_coordinates(self.group,
                                                    retval,
                                                    x,
                                                    y_bit,
                                                    self.ctx)
        return retval

    def _bn_serialize(self, bn):
        """Make a string out of BigNum"""
        l_ = OpenSSL.BN_num_bytes(self.n)
        try:
            o = OpenSSL.malloc(0, l_)
            OpenSSL.BN_bn2binpad(bn, o, l_)
            return o.raw
        except AttributeError:
            o = OpenSSL.malloc(0, OpenSSL.BN_num_bytes(bn))
            OpenSSL.BN_bn2bin(bn, o)
            return o.raw.rjust(l_, chr(0))

    def _bn_deserialize(self, data):
        """Make a BigNum out of string"""
        x = OpenSSL.BN_bin2bn(data, OpenSSL.BN_num_bytes(self.n), 0)
        return x

    def _init_privkey(self, privkey):
        """Initialise private key out of string/bytes"""
        self.d = self._bn_deserialize(privkey)

    def privkey(self):
        """Make a private key into a string"""
        return pack(BIGNUM, self.d)

    def _init_pubkey(self, pubkey):
        """Initialise pubkey out of string/bytes"""
        unpacked = unpack(PUBKEY, pubkey)
        self.expiration = Expiration.deserialize(unpacked[0])
        self.value = Value.deserialize(unpacked[1])
        self.Q = self._ec_point_deserialize(unpacked[2])

    def pubkey(self):
        """Make a pubkey into a string"""
        return pack(PUBKEY, self.expiration.serialize(),
                    self.value.serialize(),
                    self._ec_point_serialize(self.Q))

    def __init__(self, curve="secp256k1", pubkey=None, privkey=None,  # pylint: disable=too-many-arguments
                 year=2025, month=11, value=0xFF):
        self.ctx = OpenSSL.BN_CTX_new()

        # ECC group
        self.group = OpenSSL.EC_GROUP_new_by_curve_name(
            OpenSSL.get_curve(curve))

        # Order n
        self.n = OpenSSL.BN_new()
        OpenSSL.EC_GROUP_get_order(self.group, self.n, self.ctx)

        # Generator G
        self.G = OpenSSL.EC_GROUP_get0_generator(self.group)

        # Identity O (infinity)
        self.iO = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_set_to_infinity(self.group, self.iO)

        if privkey:
            assert pubkey
            # load both pubkey and privkey from bytes
            self._init_privkey(privkey)
            self._init_pubkey(pubkey)
        elif pubkey:
            # load pubkey from bytes
            self._init_pubkey(pubkey)
        else:
            # new keypair
            self.d, self.Q = self.ec_gen_keypair()
            if not year or not month:
                now = time.gmtime()
                if now.tm_mon == 12:
                    self.expiration = Expiration(now.tm_year + 1, 1)
                else:
                    self.expiration = Expiration(now.tm_year, now.tm_mon + 1)
            else:
                self.expiration = Expiration(year, month)
            self.value = Value(value)

    def __del__(self):
        OpenSSL.BN_free(self.n)
        OpenSSL.BN_CTX_free(self.ctx)

    def signer_init(self):
        """
        Init signer
        """
        # Signer: Random integer k
        self.k = self.ec_get_random()

        # R = kG
        self.R = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_mul(self.group, self.R, self.k, 0, 0, 0)

        return self._ec_point_serialize(self.R)

    def create_signing_request(self, R, msg):
        """
        Requester creates a new signing request
        """
        self.R = self._ec_point_deserialize(R)
        msghash = sha256(msg).digest()

        # Requester: 3 random blinding factors
        self.F = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_set_to_infinity(self.group, self.F)
        temp = OpenSSL.EC_POINT_new(self.group)
        abinv = OpenSSL.BN_new()

        # F != O
        while OpenSSL.EC_POINT_cmp(self.group, self.F, self.iO, self.ctx) == 0:
            self.a = self.ec_get_random()
            self.b = self.ec_get_random()
            self.c = self.ec_get_random()

            # F = b^-1 * R...
            self.binv = self.ec_invert(self.b)
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
        self.r = self.ec_Ftor(self.F)

        # Requester: Blinding (m' = br(m) + a)
        self.m = OpenSSL.BN_new()
        OpenSSL.BN_bin2bn(msghash, len(msghash), self.m)

        self.m_ = OpenSSL.BN_new()
        OpenSSL.BN_mod_mul(self.m_, self.b, self.r, self.n, self.ctx)
        OpenSSL.BN_mod_mul(self.m_, self.m_, self.m, self.n, self.ctx)
        OpenSSL.BN_mod_add(self.m_, self.m_, self.a, self.n, self.ctx)
        return self._bn_serialize(self.m_)

    def blind_sign(self, m_):
        """
        Signer blind-signs the request
        """
        self.m_ = self._bn_deserialize(m_)
        self.s_ = OpenSSL.BN_new()
        OpenSSL.BN_mod_mul(self.s_, self.d, self.m_, self.n, self.ctx)
        OpenSSL.BN_mod_add(self.s_, self.s_, self.k, self.n, self.ctx)
        OpenSSL.BN_free(self.k)
        return self._bn_serialize(self.s_)

    def unblind(self, s_):
        """
        Requester unblinds the signature
        """
        self.s_ = self._bn_deserialize(s_)
        s = OpenSSL.BN_new()
        OpenSSL.BN_mod_mul(s, self.binv, self.s_, self.n, self.ctx)
        OpenSSL.BN_mod_add(s, s, self.c, self.n, self.ctx)
        OpenSSL.BN_free(self.a)
        OpenSSL.BN_free(self.b)
        OpenSSL.BN_free(self.c)
        self.signature = (s, self.F)
        return self._bn_serialize(s) + self._ec_point_serialize(self.F)

    def verify(self, msg, signature, value=1):
        """
        Verify signature with certifier's pubkey
        """

        # convert msg to BIGNUM
        self.m = OpenSSL.BN_new()
        msghash = sha256(msg).digest()
        OpenSSL.BN_bin2bn(msghash, len(msghash), self.m)

        # init
        s, self.F = (self._bn_deserialize(signature[0:32]),
                     self._ec_point_deserialize(signature[32:]))
        if self.r is None:
            self.r = self.ec_Ftor(self.F)

        lhs = OpenSSL.EC_POINT_new(self.group)
        rhs = OpenSSL.EC_POINT_new(self.group)

        OpenSSL.EC_POINT_mul(self.group, lhs, s, 0, 0, 0)

        OpenSSL.EC_POINT_mul(self.group, rhs, 0, self.Q, self.m, 0)
        OpenSSL.EC_POINT_mul(self.group, rhs, 0, rhs, self.r, 0)
        OpenSSL.EC_POINT_add(self.group, rhs, rhs, self.F, self.ctx)

        retval = OpenSSL.EC_POINT_cmp(self.group, lhs, rhs, self.ctx)
        if retval == -1:
            raise RuntimeError("EC_POINT_cmp returned an error")
        elif not self.value.verify(value):
            return False
        elif not self.expiration.verify():
            return False
        elif retval != 0:
            return False
        return True
