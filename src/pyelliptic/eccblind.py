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

from .openssl import OpenSSL


class ECCBlind(object):  # pylint: disable=too-many-instance-attributes
    """
    Class for ECC blind signature functionality
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
    def ec_get_random(group, ctx):
        """
        Random point from finite field
        """
        order = OpenSSL.BN_new()
        OpenSSL.EC_GROUP_get_order(group, order, ctx)
        OpenSSL.BN_rand(order, OpenSSL.BN_num_bits(order), 0, 0)
        return order

    @staticmethod
    def ec_invert(group, a, ctx):
        """
        ECC inversion
        """
        order = OpenSSL.BN_new()
        OpenSSL.EC_GROUP_get_order(group, order, ctx)
        inverse = OpenSSL.BN_mod_inverse(0, a, order, ctx)
        return inverse

    @staticmethod
    def ec_gen_keypair(group, ctx):
        """
        Generate an ECC keypair
        """
        d = ECCBlind.ec_get_random(group, ctx)
        Q = OpenSSL.EC_POINT_new(group)
        OpenSSL.EC_POINT_mul(group, Q, d, 0, 0, 0)
        return (d, Q)

    @staticmethod
    def ec_Ftor(F, group, ctx):
        """
        x0 coordinate of F
        """
        # F = (x0, y0)
        x0 = OpenSSL.BN_new()
        y0 = OpenSSL.BN_new()
        OpenSSL.EC_POINT_get_affine_coordinates_GFp(group, F, x0, y0, ctx)
        return x0

    def __init__(self, curve="secp256k1", pubkey=None):
        self.ctx = OpenSSL.BN_CTX_new()

        if pubkey:
            self.group, self.G, self.n, self.Q = pubkey
        else:
            self.group = OpenSSL.EC_GROUP_new_by_curve_name(
                OpenSSL.get_curve(curve))
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

    def signer_init(self):
        """
        Init signer
        """
        # Signer: Random integer k
        self.k = ECCBlind.ec_get_random(self.group, self.ctx)

        # R = kG
        self.R = OpenSSL.EC_POINT_new(self.group)
        OpenSSL.EC_POINT_mul(self.group, self.R, self.k, 0, 0, 0)

        return self.R

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
        OpenSSL.BN_bin2bn(msg, len(msg), self.m)

        self.m_ = OpenSSL.BN_new()
        OpenSSL.BN_mod_mul(self.m_, self.b, self.r, self.n, self.ctx)
        OpenSSL.BN_mod_mul(self.m_, self.m_, self.m, self.n, self.ctx)
        OpenSSL.BN_mod_add(self.m_, self.m_, self.a, self.n, self.ctx)
        return self.m_

    def blind_sign(self, m_):
        """
        Signer blind-signs the request
        """
        self.m_ = m_
        self.s_ = OpenSSL.BN_new()
        OpenSSL.BN_mod_mul(self.s_, self.keypair[0], self.m_, self.n, self.ctx)
        OpenSSL.BN_mod_add(self.s_, self.s_, self.k, self.n, self.ctx)
        return self.s_

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

    def verify(self, msg, signature):
        """
        Verify signature with certifier's pubkey
        """

        # convert msg to BIGNUM
        self.m = OpenSSL.BN_new()
        OpenSSL.BN_bin2bn(msg, len(msg), self.m)

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
