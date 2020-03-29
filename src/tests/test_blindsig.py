"""
Test for ECC blind signatures
"""
import os
import unittest
from hashlib import sha256

from pybitmessage.pyelliptic.eccblind import ECCBlind
from pybitmessage.pyelliptic.eccblindchain import ECCBlindChain
from pybitmessage.pyelliptic.openssl import OpenSSL

# pylint: disable=protected-access


class TestBlindSig(unittest.TestCase):
    """
    Test case for ECC blind signature
    """
    def test_blind_sig(self):
        """Test full sequence using a random certifier key and a random message"""
        # See page 127 of the paper
        # (1) Initialization
        signer_obj = ECCBlind()
        point_r = signer_obj.signer_init()
        self.assertEqual(len(signer_obj.pubkey()), 35)

        # (2) Request
        requester_obj = ECCBlind(pubkey=signer_obj.pubkey())
        # only 64 byte messages are planned to be used in Bitmessage
        msg = os.urandom(64)
        msg_blinded = requester_obj.create_signing_request(point_r, msg)
        self.assertEqual(len(msg_blinded), 32)

        # check
        self.assertNotEqual(sha256(msg).digest(), msg_blinded)

        # (3) Signature Generation
        signature_blinded = signer_obj.blind_sign(msg_blinded)
        assert isinstance(signature_blinded, str)
        self.assertEqual(len(signature_blinded), 32)

        # (4) Extraction
        signature = requester_obj.unblind(signature_blinded)
        assert isinstance(signature, str)
        self.assertEqual(len(signature), 65)

        self.assertNotEqual(signature, signature_blinded)

        # (5) Verification
        verifier_obj = ECCBlind(pubkey=signer_obj.pubkey())
        self.assertTrue(verifier_obj.verify(msg, signature))

    def test_is_odd(self):
        """Test our implementation of BN_is_odd"""
        for _ in range(1024):
            obj = ECCBlind()
            x = OpenSSL.BN_new()
            y = OpenSSL.BN_new()
            OpenSSL.EC_POINT_get_affine_coordinates(
                obj.group, obj.Q, x, y, 0)
            self.assertEqual(OpenSSL.BN_is_odd(y),
                             OpenSSL.BN_is_odd_compatible(y))

    def test_serialize_ec_point(self):
        """Test EC point serialization/deserialization"""
        for _ in range(1024):
            try:
                obj = ECCBlind()
                obj2 = ECCBlind()
                randompoint = obj.Q
                serialized = obj._ec_point_serialize(randompoint)
                secondpoint = obj2._ec_point_deserialize(serialized)
                x0 = OpenSSL.BN_new()
                y0 = OpenSSL.BN_new()
                OpenSSL.EC_POINT_get_affine_coordinates(obj.group,
                                                        randompoint, x0,
                                                        y0, obj.ctx)
                x1 = OpenSSL.BN_new()
                y1 = OpenSSL.BN_new()
                OpenSSL.EC_POINT_get_affine_coordinates(obj2.group,
                                                        secondpoint, x1,
                                                        y1, obj2.ctx)

                self.assertEqual(OpenSSL.BN_cmp(y0, y1), 0)
                self.assertEqual(OpenSSL.BN_cmp(x0, x1), 0)
                self.assertEqual(OpenSSL.EC_POINT_cmp(obj.group, randompoint,
                                                      secondpoint, 0), 0)
            finally:
                OpenSSL.BN_free(x0)
                OpenSSL.BN_free(x1)
                OpenSSL.BN_free(y0)
                OpenSSL.BN_free(y1)
                del obj
                del obj2

    def test_serialize_bn(self):
        """Test Bignum serialization/deserialization"""
        for _ in range(1024):
            obj = ECCBlind()
            obj2 = ECCBlind()
            randomnum = obj.d
            serialized = obj._bn_serialize(randomnum)
            secondnum = obj2._bn_deserialize(serialized)
            self.assertEqual(OpenSSL.BN_cmp(randomnum, secondnum), 0)

    def test_blind_sig_many(self):
        """Test a lot of blind signatures"""
        for _ in range(1024):
            self.test_blind_sig()

    def test_blind_sig_value(self):
        """Test blind signature value checking"""
        signer_obj = ECCBlind(value=5)
        point_r = signer_obj.signer_init()
        requester_obj = ECCBlind(pubkey=signer_obj.pubkey())
        msg = os.urandom(64)
        msg_blinded = requester_obj.create_signing_request(point_r, msg)
        signature_blinded = signer_obj.blind_sign(msg_blinded)
        signature = requester_obj.unblind(signature_blinded)
        verifier_obj = ECCBlind(pubkey=signer_obj.pubkey())
        self.assertFalse(verifier_obj.verify(msg, signature, value=8))

    def test_blind_sig_expiration(self):
        """Test blind signature expiration checking"""
        signer_obj = ECCBlind(year=2020, month=1)
        point_r = signer_obj.signer_init()
        requester_obj = ECCBlind(pubkey=signer_obj.pubkey())
        msg = os.urandom(64)
        msg_blinded = requester_obj.create_signing_request(point_r, msg)
        signature_blinded = signer_obj.blind_sign(msg_blinded)
        signature = requester_obj.unblind(signature_blinded)
        verifier_obj = ECCBlind(pubkey=signer_obj.pubkey())
        self.assertFalse(verifier_obj.verify(msg, signature))

    def test_blind_sig_chain(self):  # pylint: disable=too-many-locals
        """Test blind signature chain using a random certifier key and a random message"""

        test_levels = 4
        msg = os.urandom(1024)

        ca = ECCBlind()
        signer_obj = ca

        output = bytearray()

        for level in range(test_levels):
            if not level:
                output.extend(ca.pubkey())
            requester_obj = ECCBlind(pubkey=signer_obj.pubkey())
            child_obj = ECCBlind()
            point_r = signer_obj.signer_init()
            pubkey = child_obj.pubkey()

            if level == test_levels - 1:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   msg)
            else:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   pubkey)
            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            if level != test_levels - 1:
                output.extend(pubkey)
            output.extend(signature)
            signer_obj = child_obj
        verifychain = ECCBlindChain(ca=ca.pubkey(), chain=str(output))
        self.assertTrue(verifychain.verify(msg=msg, value=1))

    def test_blind_sig_chain_wrong_ca(self):  # pylint: disable=too-many-locals
        """Test blind signature chain with an unlisted ca"""

        test_levels = 4
        msg = os.urandom(1024)

        ca = ECCBlind()
        fake_ca = ECCBlind()
        signer_obj = fake_ca

        output = bytearray()

        for level in range(test_levels):
            requester_obj = ECCBlind(pubkey=signer_obj.pubkey())
            child_obj = ECCBlind()
            if not level:
                # unlisted CA, but a syntactically valid pubkey
                output.extend(fake_ca.pubkey())
            point_r = signer_obj.signer_init()
            pubkey = child_obj.pubkey()

            if level == test_levels - 1:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   msg)
            else:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   pubkey)
            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            if level != test_levels - 1:
                output.extend(pubkey)
            output.extend(signature)
            signer_obj = child_obj
        verifychain = ECCBlindChain(ca=ca.pubkey(), chain=str(output))
        self.assertFalse(verifychain.verify(msg, 1))

    def test_blind_sig_chain_wrong_msg(self):  # pylint: disable=too-many-locals
        """Test blind signature chain with a fake message"""

        test_levels = 4
        msg = os.urandom(1024)
        fake_msg = os.urandom(1024)

        ca = ECCBlind()
        signer_obj = ca

        output = bytearray()

        for level in range(test_levels):
            if not level:
                output.extend(ca.pubkey())
            requester_obj = ECCBlind(pubkey=signer_obj.pubkey())
            child_obj = ECCBlind()
            point_r = signer_obj.signer_init()
            pubkey = child_obj.pubkey()

            if level == test_levels - 1:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   msg)
            else:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   pubkey)
            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            if level != test_levels - 1:
                output.extend(pubkey)
            output.extend(signature)
            signer_obj = child_obj
        verifychain = ECCBlindChain(ca=ca.pubkey(), chain=str(output))
        self.assertFalse(verifychain.verify(fake_msg, 1))

    def test_blind_sig_chain_wrong_intermediary(self):  # pylint: disable=too-many-locals
        """Test blind signature chain using a fake intermediary pubkey"""

        test_levels = 4
        msg = os.urandom(1024)
        wrong_level = 2

        ca = ECCBlind()
        signer_obj = ca
        fake_intermediary = ECCBlind()

        output = bytearray()

        for level in range(test_levels):
            if not level:
                output.extend(ca.pubkey())
            requester_obj = ECCBlind(pubkey=signer_obj.pubkey())
            child_obj = ECCBlind()
            point_r = signer_obj.signer_init()
            pubkey = child_obj.pubkey()

            if level == test_levels - 1:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   msg)
            else:
                msg_blinded = requester_obj.create_signing_request(point_r,
                                                                   pubkey)
            signature_blinded = signer_obj.blind_sign(msg_blinded)
            signature = requester_obj.unblind(signature_blinded)
            if level == wrong_level:
                output.extend(fake_intermediary.pubkey())
            elif level != test_levels - 1:
                output.extend(pubkey)
            output.extend(signature)
            signer_obj = child_obj
        verifychain = ECCBlindChain(ca=ca.pubkey(), chain=str(output))
        self.assertFalse(verifychain.verify(msg, 1))
