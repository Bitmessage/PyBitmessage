"""
Test the alternatives for crypto primitives
"""

import hashlib
import ssl
import unittest
from abc import ABCMeta, abstractmethod
from binascii import hexlify

from pybitmessage import highlevelcrypto


try:
    from Crypto.Hash import RIPEMD160
except ImportError:
    RIPEMD160 = None

from .samples import (
    sample_double_sha512, sample_hash_data,
    sample_msg, sample_pubsigningkey, sample_pubencryptionkey,
    sample_privsigningkey, sample_privencryptionkey, sample_ripe,
    sample_sig, sample_sig_sha1
)


_sha = hashlib.new('sha512')
_sha.update(sample_pubsigningkey + sample_pubencryptionkey)

pubkey_sha = _sha.digest()


class RIPEMD160TestCase(object):
    """Base class for RIPEMD160 test case"""
    # pylint: disable=too-few-public-methods,no-member
    __metaclass__ = ABCMeta

    @abstractmethod
    def _hashdigest(self, data):
        """RIPEMD160 digest implementation"""
        pass

    def test_hash_string(self):
        """Check RIPEMD160 hash function on string"""
        self.assertEqual(hexlify(self._hashdigest(pubkey_sha)), sample_ripe)


@unittest.skipIf(
    ssl.OPENSSL_VERSION.startswith('OpenSSL 3'), 'no ripemd160 in openssl 3')
class TestHashlib(RIPEMD160TestCase, unittest.TestCase):
    """RIPEMD160 test case for hashlib"""
    @staticmethod
    def _hashdigest(data):
        hasher = hashlib.new('ripemd160')
        hasher.update(data)
        return hasher.digest()


@unittest.skipUnless(RIPEMD160, 'pycrypto package not found')
class TestCrypto(RIPEMD160TestCase, unittest.TestCase):
    """RIPEMD160 test case for Crypto"""
    @staticmethod
    def _hashdigest(data):
        return RIPEMD160.new(data).digest()


class TestHighlevelcrypto(unittest.TestCase):
    """Test highlevelcrypto public functions"""

    def test_double_sha512(self):
        """Reproduce the example on page 1 of the Specification"""
        self.assertEqual(
            highlevelcrypto.double_sha512(sample_hash_data),
            sample_double_sha512)

    def test_randomBytes(self):
        """Dummy checks for random bytes"""
        for n in (8, 32, 64):
            data = highlevelcrypto.randomBytes(n)
            self.assertEqual(len(data), n)
            self.assertNotEqual(len(set(data)), 1)
            self.assertNotEqual(data, highlevelcrypto.randomBytes(n))

    def test_signatures(self):
        """Verify sample signatures and newly generated ones"""
        pubkey_hex = hexlify(sample_pubsigningkey)
        # pregenerated signatures
        self.assertTrue(highlevelcrypto.verify(
            sample_msg, sample_sig, pubkey_hex, "sha256"))
        self.assertFalse(highlevelcrypto.verify(
            sample_msg, sample_sig, pubkey_hex, "sha1"))
        self.assertTrue(highlevelcrypto.verify(
            sample_msg, sample_sig_sha1, pubkey_hex, "sha1"))
        self.assertTrue(highlevelcrypto.verify(
            sample_msg, sample_sig_sha1, pubkey_hex))
        # new signatures
        sig256 = highlevelcrypto.sign(sample_msg, sample_privsigningkey)
        sig1 = highlevelcrypto.sign(sample_msg, sample_privsigningkey, "sha1")
        self.assertTrue(
            highlevelcrypto.verify(sample_msg, sig256, pubkey_hex))
        self.assertTrue(
            highlevelcrypto.verify(sample_msg, sig256, pubkey_hex, "sha256"))
        self.assertTrue(
            highlevelcrypto.verify(sample_msg, sig1, pubkey_hex))

    def test_privtopub(self):
        """Generate public keys and check the result"""
        self.assertEqual(
            highlevelcrypto.privToPub(sample_privsigningkey),
            hexlify(sample_pubsigningkey)
        )
        self.assertEqual(
            highlevelcrypto.privToPub(sample_privencryptionkey),
            hexlify(sample_pubencryptionkey)
        )

    def test_make_cryptor(self):
        """Test returning a private `.pyelliptic.ECC` instance"""
        result = highlevelcrypto.makeCryptor(privkey=sample_privencryptionkey)
        self.assertEqual(type(result), highlevelcrypto.pyelliptic.ECC)

    def test_hextopubkey(self):
        """Test converting a pubkey from hex to binary"""
        result = highlevelcrypto.hexToPubkey(pubkey=hexlify(sample_pubencryptionkey))
        self.assertEqual(type(result), bytes)

    def test_makepubcryptor(self):
        """Test returning a public `.pyelliptic.ECC` instance"""
        result = highlevelcrypto.makePubCryptor(pubkey=hexlify(sample_pubencryptionkey))
        self.assertEqual(type(result), highlevelcrypto.pyelliptic.ECC)

    def test_encrypt_decrypt(self):
        """Test Encrypting message with hex public key & Decrypting message with hex private key"""
        # encrypt
        ENCRYPTED_MSG = highlevelcrypto.encrypt(
            msg=sample_msg, hexPubkey=hexlify(sample_pubencryptionkey)
        )
        self.assertEqual(type(ENCRYPTED_MSG), bytes)

        # decrypt
        result = highlevelcrypto.decrypt(
            msg=ENCRYPTED_MSG, hexPrivkey=sample_privencryptionkey
        )
        self.assertEqual(sample_msg, result)
        self.assertEqual(type(result), bytes)

        # make `.pyelliptic.ECC` object & decryptfast
        cryptor_ = highlevelcrypto.makeCryptor(privkey=sample_privencryptionkey)

        result1 = highlevelcrypto.decryptFast(msg=ENCRYPTED_MSG, cryptor=cryptor_)
        self.assertEqual(sample_msg, result1)
