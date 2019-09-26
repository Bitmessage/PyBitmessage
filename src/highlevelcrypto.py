"""
src/highlevelcrypto.py
======================
"""

from binascii import hexlify

import pyelliptic
from bmconfigparser import BMConfigParser
from pyelliptic import OpenSSL
from pyelliptic import arithmetic as a


def makeCryptor(privkey):
    """Return a private pyelliptic.ECC() instance"""
    # import pdb;pdb.set_trace()
    private_key = a.changebase(privkey, 16, 256, minlen=32)
    public_key = pointMult(private_key)
    privkey_bin = '\x02\xca\x00\x20' + private_key
    pubkey_bin = '\x02\xca\x00\x20' + public_key[1:-32].decode() + '\x00\x20' + public_key[-32:].decode()
    cryptor = pyelliptic.ECC(curve='secp256k1', privkey=privkey_bin, pubkey=pubkey_bin)
    return cryptor


def hexToPubkey(pubkey):
    """Convert a pubkey from hex to binary"""
    pubkey_raw = a.changebase(pubkey[2:], 16, 256, minlen=64)
    pubkey_bin = '\x02\xca\x00 ' + pubkey_raw[:32] + '\x00 ' + pubkey_raw[32:]
    return pubkey_bin


def makePubCryptor(pubkey):
    """Return a public pyelliptic.ECC() instance"""
    pubkey_bin = hexToPubkey(pubkey)
    return pyelliptic.ECC(curve='secp256k1', pubkey=pubkey_bin)


def privToPub(privkey):
    """Converts hex private key into hex public key"""
    private_key = a.changebase(privkey, 16, 256, minlen=32)
    public_key = pointMult(private_key)
    return hexlify(public_key)


def encrypt(msg, hexPubkey):
    """Encrypts message with hex public key"""
    return pyelliptic.ECC(curve='secp256k1').encrypt(msg, hexToPubkey(hexPubkey))


def decrypt(msg, hexPrivkey):
    """Decrypts message with hex private key"""
    return makeCryptor(hexPrivkey).decrypt(msg)


def decryptFast(msg, cryptor):
    """Decrypts message with an existing pyelliptic.ECC.ECC object"""
    return cryptor.decrypt(msg)


def sign(msg, hexPrivkey):
    """Signs with hex private key"""
    # pyelliptic is upgrading from SHA1 to SHA256 for signing. We must
    # upgrade PyBitmessage gracefully.
    # https://github.com/yann2192/pyelliptic/pull/33
    # More discussion: https://github.com/yann2192/pyelliptic/issues/32
    digestAlg = BMConfigParser().safeGet('bitmessagesettings', 'digestalg', 'sha1')
    if digestAlg == "sha1":
        # SHA1, this will eventually be deprecated
        return makeCryptor(hexPrivkey).sign(msg, digest_alg=OpenSSL.digest_ecdsa_sha1)
    elif digestAlg == "sha256":
        # SHA256. Eventually this will become the default
        return makeCryptor(hexPrivkey).sign(msg, digest_alg=OpenSSL.EVP_sha256)
    else:
        raise ValueError("Unknown digest algorithm %s" % (digestAlg))


def verify(msg, sig, hexPubkey):
    """Verifies with hex public key"""
    # As mentioned above, we must upgrade gracefully to use SHA256. So
    # let us check the signature using both SHA1 and SHA256 and if one
    # of them passes then we will be satisfied. Eventually this can
    # be simplified and we'll only check with SHA256.
    try:
        # old SHA1 algorithm.
        sigVerifyPassed = makePubCryptor(hexPubkey).verify(sig, msg, digest_alg=OpenSSL.digest_ecdsa_sha1)
    except:
        sigVerifyPassed = False
    if sigVerifyPassed:
        # The signature check passed using SHA1
        return True
    # The signature check using SHA1 failed. Let us try it with SHA256.
    try:
        return makePubCryptor(hexPubkey).verify(sig, msg, digest_alg=OpenSSL.EVP_sha256)
    except:
        return False


def pointMult(secret):
    """
    Does an EC point multiplication; turns a private key into a public key.

    Evidently, this type of error can occur very rarely:

        File "highlevelcrypto.py", line 54, in pointMult
          group = OpenSSL.EC_KEY_get0_group(k)
        WindowsError: exception: access violation reading 0x0000000000000008
    """
    while True:
        try:
            k = OpenSSL.EC_KEY_new_by_curve_name(OpenSSL.get_curve('secp256k1'))
            priv_key = OpenSSL.BN_bin2bn(secret, 32, None)
            group = OpenSSL.EC_KEY_get0_group(k)
            pub_key = OpenSSL.EC_POINT_new(group)

            OpenSSL.EC_POINT_mul(group, pub_key, priv_key, None, None, None)
            OpenSSL.EC_KEY_set_private_key(k, priv_key)
            OpenSSL.EC_KEY_set_public_key(k, pub_key)

            size = OpenSSL.i2o_ECPublicKey(k, None)
            mb = OpenSSL.create_string_buffer(size)
            OpenSSL.i2o_ECPublicKey(k, OpenSSL.byref(OpenSSL.pointer(mb)))

            OpenSSL.EC_POINT_free(pub_key)
            OpenSSL.BN_free(priv_key)
            OpenSSL.EC_KEY_free(k)
            return mb.raw

        except Exception:
            import traceback
            import time
            traceback.print_exc()
            time.sleep(0.2)
