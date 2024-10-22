"""
High level cryptographic functions based on `.pyelliptic` OpenSSL bindings.

.. note::
  Upstream pyelliptic was upgraded from SHA1 to SHA256 for signing. We must
  `upgrade PyBitmessage gracefully. <https://github.com/Bitmessage/PyBitmessage/issues/953>`_
  `More discussion. <https://github.com/yann2192/pyelliptic/issues/32>`_
"""

from unqstr import unic

import hashlib
import os
from binascii import hexlify

try:
    import pyelliptic
    from fallback import RIPEMD160Hash
    from pyelliptic import OpenSSL
    from pyelliptic import arithmetic as a
except ImportError:
    from pybitmessage import pyelliptic
    from pybitmessage.fallback import RIPEMD160Hash
    from pybitmessage.pyelliptic import OpenSSL
    from pybitmessage.pyelliptic import arithmetic as a


__all__ = [
    'decodeWalletImportFormat', 'deterministic_keys',
    'double_sha512', 'calculateInventoryHash', 'encodeWalletImportFormat',
    'encrypt', 'makeCryptor', 'pointMult', 'privToPub', 'randomBytes',
    'random_keys', 'sign', 'to_ripe', 'verify']


# WIF (uses arithmetic ):
def decodeWalletImportFormat(WIFstring):
    """
    Convert private key from base58 that's used in the config file to
    8-bit binary string.
    """
    fullString = a.changebase(WIFstring, 58, 256)
    privkey = fullString[:-4]
    if fullString[-4:] != \
       hashlib.sha256(hashlib.sha256(privkey).digest()).digest()[:4]:
        raise ValueError('Checksum failed')
    elif privkey[0:1] == b'\x80':  # checksum passed
        return privkey[1:]

    raise ValueError('No hex 80 prefix')


# An excellent way for us to store our keys
# is in Wallet Import Format. Let us convert now.
# https://en.bitcoin.it/wiki/Wallet_import_format
def encodeWalletImportFormat(privKey):
    """
    Convert private key from binary 8-bit string into base58check WIF string.
    """
    privKey = b'\x80' + privKey
    checksum = hashlib.sha256(hashlib.sha256(privKey).digest()).digest()[0:4]
    return a.changebase(privKey + checksum, 256, 58)


# Random

def randomBytes(n):
    """Get n random bytes"""
    try:
        return os.urandom(n)
    except NotImplementedError:
        return OpenSSL.rand(n)


# Hashes

def _bm160(data):
    """RIPEME160(SHA512(data)) -> bytes"""
    return RIPEMD160Hash(hashlib.sha512(data).digest()).digest()


def to_ripe(signing_key, encryption_key):
    """Convert two public keys to a ripe hash"""
    return _bm160(signing_key + encryption_key)


def double_sha512(data):
    """Binary double SHA512 digest"""
    return hashlib.sha512(hashlib.sha512(data).digest()).digest()


def calculateInventoryHash(data):
    """Calculate inventory hash from object data"""
    return double_sha512(data)[:32]


# Keys

def random_keys():
    """Return a pair of keys, private and public"""
    priv = randomBytes(32)
    pub = pointMult(priv)
    return priv, pub


def deterministic_keys(passphrase, nonce):
    """Generate keys from *passphrase* and *nonce* (encoded as varint)"""
    priv = hashlib.sha512(unic(passphrase).encode("utf-8", "replace") + nonce).digest()[:32]
    pub = pointMult(priv)
    return priv, pub


def hexToPubkey(pubkey):
    """Convert a pubkey from hex to binary"""
    pubkey_raw = a.changebase(pubkey[2:], 16, 256, minlen=64)
    pubkey_bin = b'\x02\xca\x00 ' + pubkey_raw[:32] + b'\x00 ' + pubkey_raw[32:]
    return pubkey_bin


def privToPub(privkey):
    """Converts hex private key into hex public key"""
    private_key = a.changebase(privkey, 16, 256, minlen=32)
    public_key = pointMult(private_key)
    return hexlify(public_key)


def pointMult(secret):
    """
    Does an EC point multiplication; turns a private key into a public key.

    Evidently, this type of error can occur very rarely:

    >>> File "highlevelcrypto.py", line 54, in pointMult
    >>>  group = OpenSSL.EC_KEY_get0_group(k)
    >>> WindowsError: exception: access violation reading 0x0000000000000008
    """
    while True:
        try:
            k = OpenSSL.EC_KEY_new_by_curve_name(
                OpenSSL.get_curve('secp256k1'))
            priv_key = OpenSSL.BN_bin2bn(secret, 32, None)
            group = OpenSSL.EC_KEY_get0_group(k)
            pub_key = OpenSSL.EC_POINT_new(group)

            OpenSSL.EC_POINT_mul(group, pub_key, priv_key, None, None, None)
            OpenSSL.EC_KEY_set_private_key(k, priv_key)
            OpenSSL.EC_KEY_set_public_key(k, pub_key)

            size = OpenSSL.i2o_ECPublicKey(k, None)
            mb = OpenSSL.create_string_buffer(size)
            OpenSSL.i2o_ECPublicKey(k, OpenSSL.byref(OpenSSL.pointer(mb)))

            return mb.raw

        except Exception:
            import traceback
            import time
            traceback.print_exc()
            time.sleep(0.2)
        finally:
            OpenSSL.EC_POINT_free(pub_key)
            OpenSSL.BN_free(priv_key)
            OpenSSL.EC_KEY_free(k)


# Encryption

def makeCryptor(privkey, curve='secp256k1'):
    """Return a private `.pyelliptic.ECC` instance"""
    private_key = a.changebase(privkey, 16, 256, minlen=32)
    public_key = pointMult(private_key)
    cryptor = pyelliptic.ECC(
        pubkey_x=public_key[1:-32], pubkey_y=public_key[-32:],
        raw_privkey=private_key, curve=curve)
    return cryptor


def makePubCryptor(pubkey):
    """Return a public `.pyelliptic.ECC` instance"""
    pubkey_bin = hexToPubkey(pubkey)
    return pyelliptic.ECC(curve='secp256k1', pubkey=pubkey_bin)


def encrypt(msg, hexPubkey):
    """Encrypts message with hex public key"""
    return pyelliptic.ECC(curve='secp256k1').encrypt(
        msg, hexToPubkey(hexPubkey))


def decrypt(msg, hexPrivkey):
    """Decrypts message with hex private key"""
    return makeCryptor(hexPrivkey).decrypt(msg)


def decryptFast(msg, cryptor):
    """Decrypts message with an existing `.pyelliptic.ECC` object"""
    return cryptor.decrypt(msg)


# Signatures

def _choose_digest_alg(name):
    """
    Choose openssl digest constant by name raises ValueError if not appropriate
    """
    if name not in ("sha1", "sha256"):
        raise ValueError("Unknown digest algorithm %s" % name)
    return (
        # SHA1, this will eventually be deprecated
        OpenSSL.digest_ecdsa_sha1 if name == "sha1" else OpenSSL.EVP_sha256)


def sign(msg, hexPrivkey, digestAlg="sha256"):
    """
    Signs with hex private key using SHA1 or SHA256 depending on
    *digestAlg* keyword.
    """
    return makeCryptor(hexPrivkey).sign(
        msg, digest_alg=_choose_digest_alg(digestAlg))


def verify(msg, sig, hexPubkey, digestAlg=None):
    """Verifies with hex public key using SHA1 or SHA256"""
    # As mentioned above, we must upgrade gracefully to use SHA256. So
    # let us check the signature using both SHA1 and SHA256 and if one
    # of them passes then we will be satisfied. Eventually this can
    # be simplified and we'll only check with SHA256.
    if digestAlg is None:
        # old SHA1 algorithm.
        sigVerifyPassed = verify(msg, sig, hexPubkey, "sha1")
        if sigVerifyPassed:
            # The signature check passed using SHA1
            return True
        # The signature check using SHA1 failed. Let us try it with SHA256.
        return verify(msg, sig, hexPubkey, "sha256")

    try:
        return makePubCryptor(hexPubkey).verify(
            sig, msg, digest_alg=_choose_digest_alg(digestAlg))
    except:
        return False
