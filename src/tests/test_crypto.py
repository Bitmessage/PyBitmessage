"""
Test the alternatives for crypto primitives
"""

import hashlib
import unittest
from abc import ABCMeta, abstractmethod
from binascii import hexlify, unhexlify

try:
    from Crypto.Hash import RIPEMD
except ImportError:
    RIPEMD = None


# These keys are from addresses test script
sample_pubsigningkey = unhexlify(
    '044a367f049ec16cb6b6118eb734a9962d10b8db59c890cd08f210c43ff08bdf09d'
    '16f502ca26cd0713f38988a1237f1fc8fa07b15653c996dc4013af6d15505ce')
sample_pubencryptionkey = unhexlify(
    '044597d59177fc1d89555d38915f581b5ff2286b39d022ca0283d2bdd5c36be5d3c'
    'e7b9b97792327851a562752e4b79475d1f51f5a71352482b241227f45ed36a9')

sample_ripe = '003cd097eb7f35c87b5dc8b4538c22cb55312a9f'

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


class TestHashlib(RIPEMD160TestCase, unittest.TestCase):
    """RIPEMD160 test case for hashlib"""
    @staticmethod
    def _hashdigest(data):
        hasher = hashlib.new('ripemd160')
        hasher.update(data)
        return hasher.digest()


@unittest.skipUnless(RIPEMD, 'pycrypto package not found')
class TestCrypto(RIPEMD160TestCase, unittest.TestCase):
    """RIPEMD160 test case for Crypto"""
    @staticmethod
    def _hashdigest(data):
        return RIPEMD.RIPEMD160Hash(data).digest()
