"""Tests for ECC object"""

import os
import unittest
from hashlib import sha512

try:
    import pyelliptic
except ImportError:
    from pybitmessage import pyelliptic

from .samples import (
    sample_pubkey, sample_iv, sample_ephem_privkey, sample_ephem_pubkey,
    sample_enkey, sample_mackey, sample_data, sample_ciphertext, sample_mac)


sample_pubkey_x = sample_ephem_pubkey[1:-32]
sample_pubkey_y = sample_ephem_pubkey[-32:]
sample_pubkey_bin = (
    b'\x02\xca\x00\x20' + sample_pubkey_x + b'\x00\x20' + sample_pubkey_y)
sample_privkey_bin = b'\x02\xca\x00\x20' + sample_ephem_privkey


class TestECC(unittest.TestCase):
    """The test case for ECC"""

    def test_random_keys(self):
        """A dummy test for random keys in ECC object"""
        eccobj = pyelliptic.ECC(curve='secp256k1')
        self.assertTrue(len(eccobj.privkey) <= 32)
        pubkey = eccobj.get_pubkey()
        self.assertEqual(pubkey[:4], b'\x02\xca\x00\x20')

    def test_short_keys(self):
        """Check formatting of the keys with leading zeroes"""
        # pylint: disable=protected-access
        def sample_key(_):
            """Fake ECC keypair"""
            return os.urandom(32), os.urandom(31), os.urandom(30)

        try:
            gen_orig = pyelliptic.ECC._generate
            pyelliptic.ECC._generate = sample_key
            eccobj = pyelliptic.ECC(curve='secp256k1')
            pubkey = eccobj.get_pubkey()
            self.assertEqual(pubkey[:4], b'\x02\xca\x00\x20')
            self.assertEqual(pubkey[36:38], b'\x00\x20')
            self.assertEqual(len(pubkey[38:]), 32)
        finally:
            pyelliptic.ECC._generate = gen_orig

    def test_decode_keys(self):
        """Check keys decoding"""
        # pylint: disable=protected-access
        curve_secp256k1 = pyelliptic.OpenSSL.get_curve('secp256k1')
        curve, raw_privkey, _ = pyelliptic.ECC._decode_privkey(
            sample_privkey_bin)
        self.assertEqual(curve, curve_secp256k1)
        self.assertEqual(
            pyelliptic.OpenSSL.get_curve_by_id(curve), 'secp256k1')
        self.assertEqual(sample_ephem_privkey, raw_privkey)

        curve, pubkey_x, pubkey_y, _ = pyelliptic.ECC._decode_pubkey(
            sample_pubkey_bin)
        self.assertEqual(curve, curve_secp256k1)
        self.assertEqual(sample_pubkey_x, pubkey_x)
        self.assertEqual(sample_pubkey_y, pubkey_y)

    def test_encode_keys(self):
        """Check keys encoding"""
        cryptor = pyelliptic.ECC(
            pubkey_x=sample_pubkey_x,
            pubkey_y=sample_pubkey_y,
            raw_privkey=sample_ephem_privkey, curve='secp256k1')
        self.assertEqual(cryptor.get_privkey(), sample_privkey_bin)
        self.assertEqual(cryptor.get_pubkey(), sample_pubkey_bin)

    def test_encryption_parts(self):
        """Check results of the encryption steps against samples in the Spec"""
        ephem = pyelliptic.ECC(
            pubkey_x=sample_pubkey_x,
            pubkey_y=sample_pubkey_y,
            raw_privkey=sample_ephem_privkey, curve='secp256k1')
        key = sha512(ephem.raw_get_ecdh_key(
            sample_pubkey[1:-32], sample_pubkey[-32:])).digest()
        self.assertEqual(sample_enkey, key[:32])
        self.assertEqual(sample_mackey, key[32:])

        ctx = pyelliptic.Cipher(sample_enkey, sample_iv, 1)
        self.assertEqual(ctx.ciphering(sample_data), sample_ciphertext)
        self.assertEqual(
            sample_mac,
            pyelliptic.hash.hmac_sha256(
                sample_mackey,
                sample_iv + sample_pubkey_bin + sample_ciphertext))

    def test_decryption(self):
        """Check decription of a message by random cryptor"""
        random_recipient = pyelliptic.ECC(curve='secp256k1')
        payload = pyelliptic.ECC.encrypt(
            sample_data, random_recipient.get_pubkey())
        self.assertEqual(random_recipient.decrypt(payload), sample_data)
