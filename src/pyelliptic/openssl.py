#  Copyright (C) 2011 Yann GUIBET <yannguibet@gmail.com>
#  See LICENSE for details.
#
#  Software slightly changed by Jonathan Warren <bitmessage at-symbol jonwarren.org>
"""
This module loads openssl libs with ctypes and incapsulates
needed openssl functionality in class _OpenSSL.
"""
import ctypes
import sys

# pylint: disable=protected-access

OpenSSL = None


class CipherName(object):
    """Class returns cipher name, pointer and blocksize"""

    def __init__(self, name, pointer, blocksize):
        self._name = name
        self._pointer = pointer
        self._blocksize = blocksize

    def __str__(self):
        return "Cipher : " + self._name + \
               " | Blocksize : " + str(self._blocksize) + \
               " | Function pointer : " + str(self._pointer)

    def get_pointer(self):
        """This method returns cipher pointer"""
        return self._pointer()

    def get_name(self):
        """This method returns cipher name"""
        return self._name

    def get_blocksize(self):
        """This method returns cipher blocksize"""
        return self._blocksize


def get_version(library):
    """This function return version, hexversion and cflages"""
    version = None
    hexversion = None
    cflags = None
    try:
        # OpenSSL 1.1
        OPENSSL_VERSION = 0
        OPENSSL_CFLAGS = 1
        library.OpenSSL_version.argtypes = [ctypes.c_int]
        library.OpenSSL_version.restype = ctypes.c_char_p
        version = library.OpenSSL_version(OPENSSL_VERSION)
        cflags = library.OpenSSL_version(OPENSSL_CFLAGS)
        library.OpenSSL_version_num.restype = ctypes.c_long
        hexversion = library.OpenSSL_version_num()
    except AttributeError:
        try:
            # OpenSSL 1.0
            SSLEAY_VERSION = 0
            SSLEAY_CFLAGS = 2
            library.SSLeay.restype = ctypes.c_long
            library.SSLeay_version.restype = ctypes.c_char_p
            library.SSLeay_version.argtypes = [ctypes.c_int]
            version = library.SSLeay_version(SSLEAY_VERSION)
            cflags = library.SSLeay_version(SSLEAY_CFLAGS)
            hexversion = library.SSLeay()
        except AttributeError:
            # raise NotImplementedError('Cannot determine version of this OpenSSL library.')
            pass
    return (version, hexversion, cflags)


class _OpenSSL(object):
    """
    Wrapper for OpenSSL using ctypes
    """
    # pylint: disable=too-many-statements, too-many-instance-attributes
    def __init__(self, library):
        """
        Build the wrapper
        """
        self._lib = ctypes.CDLL(library)
        self._version, self._hexversion, self._cflags = get_version(self._lib)
        self._libreSSL = self._version.startswith("LibreSSL")

        self.pointer = ctypes.pointer
        self.c_int = ctypes.c_int
        self.byref = ctypes.byref
        self.create_string_buffer = ctypes.create_string_buffer

        self.BN_new = self._lib.BN_new
        self.BN_new.restype = ctypes.c_void_p
        self.BN_new.argtypes = []

        self.BN_free = self._lib.BN_free
        self.BN_free.restype = None
        self.BN_free.argtypes = [ctypes.c_void_p]

        self.BN_clear_free = self._lib.BN_clear_free
        self.BN_clear_free.restype = None
        self.BN_clear_free.argtypes = [ctypes.c_void_p]

        self.BN_num_bits = self._lib.BN_num_bits
        self.BN_num_bits.restype = ctypes.c_int
        self.BN_num_bits.argtypes = [ctypes.c_void_p]

        self.BN_bn2bin = self._lib.BN_bn2bin
        self.BN_bn2bin.restype = ctypes.c_int
        self.BN_bn2bin.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        try:
            self.BN_bn2binpad = self._lib.BN_bn2binpad
            self.BN_bn2binpad.restype = ctypes.c_int
            self.BN_bn2binpad.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                          ctypes.c_int]
        except AttributeError:
            # optional, we have a workaround
            pass

        self.BN_bin2bn = self._lib.BN_bin2bn
        self.BN_bin2bn.restype = ctypes.c_void_p
        self.BN_bin2bn.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                   ctypes.c_void_p]

        self.EC_KEY_free = self._lib.EC_KEY_free
        self.EC_KEY_free.restype = None
        self.EC_KEY_free.argtypes = [ctypes.c_void_p]

        self.EC_KEY_new_by_curve_name = self._lib.EC_KEY_new_by_curve_name
        self.EC_KEY_new_by_curve_name.restype = ctypes.c_void_p
        self.EC_KEY_new_by_curve_name.argtypes = [ctypes.c_int]

        self.EC_KEY_generate_key = self._lib.EC_KEY_generate_key
        self.EC_KEY_generate_key.restype = ctypes.c_int
        self.EC_KEY_generate_key.argtypes = [ctypes.c_void_p]

        self.EC_KEY_check_key = self._lib.EC_KEY_check_key
        self.EC_KEY_check_key.restype = ctypes.c_int
        self.EC_KEY_check_key.argtypes = [ctypes.c_void_p]

        self.EC_KEY_get0_private_key = self._lib.EC_KEY_get0_private_key
        self.EC_KEY_get0_private_key.restype = ctypes.c_void_p
        self.EC_KEY_get0_private_key.argtypes = [ctypes.c_void_p]

        self.EC_KEY_get0_public_key = self._lib.EC_KEY_get0_public_key
        self.EC_KEY_get0_public_key.restype = ctypes.c_void_p
        self.EC_KEY_get0_public_key.argtypes = [ctypes.c_void_p]

        self.EC_KEY_get0_group = self._lib.EC_KEY_get0_group
        self.EC_KEY_get0_group.restype = ctypes.c_void_p
        self.EC_KEY_get0_group.argtypes = [ctypes.c_void_p]

        self.EC_POINT_get_affine_coordinates_GFp = \
            self._lib.EC_POINT_get_affine_coordinates_GFp
        self.EC_POINT_get_affine_coordinates_GFp.restype = ctypes.c_int
        self.EC_POINT_get_affine_coordinates_GFp.argtypes = [ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_void_p]

        try:
            self.EC_POINT_get_affine_coordinates = \
                self._lib.EC_POINT_get_affine_coordinates
        except AttributeError:
            # OpenSSL docs say only use this for backwards compatibility
            self.EC_POINT_get_affine_coordinates = \
                self._lib.EC_POINT_get_affine_coordinates_GF2m
        self.EC_POINT_get_affine_coordinates.restype = ctypes.c_int
        self.EC_POINT_get_affine_coordinates.argtypes = [ctypes.c_void_p,
                                                         ctypes.c_void_p,
                                                         ctypes.c_void_p,
                                                         ctypes.c_void_p,
                                                         ctypes.c_void_p]

        self.EC_KEY_set_private_key = self._lib.EC_KEY_set_private_key
        self.EC_KEY_set_private_key.restype = ctypes.c_int
        self.EC_KEY_set_private_key.argtypes = [ctypes.c_void_p,
                                                ctypes.c_void_p]

        self.EC_KEY_set_public_key = self._lib.EC_KEY_set_public_key
        self.EC_KEY_set_public_key.restype = ctypes.c_int
        self.EC_KEY_set_public_key.argtypes = [ctypes.c_void_p,
                                               ctypes.c_void_p]

        self.EC_KEY_set_group = self._lib.EC_KEY_set_group
        self.EC_KEY_set_group.restype = ctypes.c_int
        self.EC_KEY_set_group.argtypes = [ctypes.c_void_p,
                                          ctypes.c_void_p]

        self.EC_POINT_set_affine_coordinates_GFp = \
            self._lib.EC_POINT_set_affine_coordinates_GFp
        self.EC_POINT_set_affine_coordinates_GFp.restype = ctypes.c_int
        self.EC_POINT_set_affine_coordinates_GFp.argtypes = [ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_void_p]

        try:
            self.EC_POINT_set_affine_coordinates = \
                self._lib.EC_POINT_set_affine_coordinates
        except AttributeError:
            # OpenSSL docs say only use this for backwards compatibility
            self.EC_POINT_set_affine_coordinates = \
                self._lib.EC_POINT_set_affine_coordinates_GF2m
        self.EC_POINT_set_affine_coordinates.restype = ctypes.c_int
        self.EC_POINT_set_affine_coordinates.argtypes = [ctypes.c_void_p,
                                                         ctypes.c_void_p,
                                                         ctypes.c_void_p,
                                                         ctypes.c_void_p,
                                                         ctypes.c_void_p]

        try:
            self.EC_POINT_set_compressed_coordinates = \
                self._lib.EC_POINT_set_compressed_coordinates
        except AttributeError:
            # OpenSSL docs say only use this for backwards compatibility
            self.EC_POINT_set_compressed_coordinates = \
                self._lib.EC_POINT_set_compressed_coordinates_GF2m
        self.EC_POINT_set_compressed_coordinates.restype = ctypes.c_int
        self.EC_POINT_set_compressed_coordinates.argtypes = [ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_void_p,
                                                             ctypes.c_int,
                                                             ctypes.c_void_p]

        self.EC_POINT_new = self._lib.EC_POINT_new
        self.EC_POINT_new.restype = ctypes.c_void_p
        self.EC_POINT_new.argtypes = [ctypes.c_void_p]

        self.EC_POINT_free = self._lib.EC_POINT_free
        self.EC_POINT_free.restype = None
        self.EC_POINT_free.argtypes = [ctypes.c_void_p]

        self.BN_CTX_free = self._lib.BN_CTX_free
        self.BN_CTX_free.restype = None
        self.BN_CTX_free.argtypes = [ctypes.c_void_p]

        self.EC_POINT_mul = self._lib.EC_POINT_mul
        self.EC_POINT_mul.restype = None
        self.EC_POINT_mul.argtypes = [ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p]

        self.EC_KEY_set_private_key = self._lib.EC_KEY_set_private_key
        self.EC_KEY_set_private_key.restype = ctypes.c_int
        self.EC_KEY_set_private_key.argtypes = [ctypes.c_void_p,
                                                ctypes.c_void_p]

        if self._hexversion >= 0x10100000 and not self._libreSSL:
            self.EC_KEY_OpenSSL = self._lib.EC_KEY_OpenSSL
            self._lib.EC_KEY_OpenSSL.restype = ctypes.c_void_p
            self._lib.EC_KEY_OpenSSL.argtypes = []

            self.EC_KEY_set_method = self._lib.EC_KEY_set_method
            self._lib.EC_KEY_set_method.restype = ctypes.c_int
            self._lib.EC_KEY_set_method.argtypes = [ctypes.c_void_p,
                                                    ctypes.c_void_p]
        else:
            self.ECDH_OpenSSL = self._lib.ECDH_OpenSSL
            self._lib.ECDH_OpenSSL.restype = ctypes.c_void_p
            self._lib.ECDH_OpenSSL.argtypes = []

            self.ECDH_set_method = self._lib.ECDH_set_method
            self._lib.ECDH_set_method.restype = ctypes.c_int
            self._lib.ECDH_set_method.argtypes = [ctypes.c_void_p,
                                                  ctypes.c_void_p]

        self.ECDH_compute_key = self._lib.ECDH_compute_key
        self.ECDH_compute_key.restype = ctypes.c_int
        self.ECDH_compute_key.argtypes = [ctypes.c_void_p,
                                          ctypes.c_int,
                                          ctypes.c_void_p,
                                          ctypes.c_void_p]

        self.EVP_CipherInit_ex = self._lib.EVP_CipherInit_ex
        self.EVP_CipherInit_ex.restype = ctypes.c_int
        self.EVP_CipherInit_ex.argtypes = [ctypes.c_void_p,
                                           ctypes.c_void_p,
                                           ctypes.c_void_p]

        self.EVP_CIPHER_CTX_new = self._lib.EVP_CIPHER_CTX_new
        self.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
        self.EVP_CIPHER_CTX_new.argtypes = []

        # Cipher
        self.EVP_aes_128_cfb128 = self._lib.EVP_aes_128_cfb128
        self.EVP_aes_128_cfb128.restype = ctypes.c_void_p
        self.EVP_aes_128_cfb128.argtypes = []

        self.EVP_aes_256_cfb128 = self._lib.EVP_aes_256_cfb128
        self.EVP_aes_256_cfb128.restype = ctypes.c_void_p
        self.EVP_aes_256_cfb128.argtypes = []

        self.EVP_aes_128_cbc = self._lib.EVP_aes_128_cbc
        self.EVP_aes_128_cbc.restype = ctypes.c_void_p
        self.EVP_aes_128_cbc.argtypes = []

        self.EVP_aes_256_cbc = self._lib.EVP_aes_256_cbc
        self.EVP_aes_256_cbc.restype = ctypes.c_void_p
        self.EVP_aes_256_cbc.argtypes = []

        # self.EVP_aes_128_ctr = self._lib.EVP_aes_128_ctr
        # self.EVP_aes_128_ctr.restype = ctypes.c_void_p
        # self.EVP_aes_128_ctr.argtypes = []

        # self.EVP_aes_256_ctr = self._lib.EVP_aes_256_ctr
        # self.EVP_aes_256_ctr.restype = ctypes.c_void_p
        # self.EVP_aes_256_ctr.argtypes = []

        self.EVP_aes_128_ofb = self._lib.EVP_aes_128_ofb
        self.EVP_aes_128_ofb.restype = ctypes.c_void_p
        self.EVP_aes_128_ofb.argtypes = []

        self.EVP_aes_256_ofb = self._lib.EVP_aes_256_ofb
        self.EVP_aes_256_ofb.restype = ctypes.c_void_p
        self.EVP_aes_256_ofb.argtypes = []

        self.EVP_bf_cbc = self._lib.EVP_bf_cbc
        self.EVP_bf_cbc.restype = ctypes.c_void_p
        self.EVP_bf_cbc.argtypes = []

        self.EVP_bf_cfb64 = self._lib.EVP_bf_cfb64
        self.EVP_bf_cfb64.restype = ctypes.c_void_p
        self.EVP_bf_cfb64.argtypes = []

        self.EVP_rc4 = self._lib.EVP_rc4
        self.EVP_rc4.restype = ctypes.c_void_p
        self.EVP_rc4.argtypes = []

        if self._hexversion >= 0x10100000 and not self._libreSSL:
            self.EVP_CIPHER_CTX_reset = self._lib.EVP_CIPHER_CTX_reset
            self.EVP_CIPHER_CTX_reset.restype = ctypes.c_int
            self.EVP_CIPHER_CTX_reset.argtypes = [ctypes.c_void_p]
        else:
            self.EVP_CIPHER_CTX_cleanup = self._lib.EVP_CIPHER_CTX_cleanup
            self.EVP_CIPHER_CTX_cleanup.restype = ctypes.c_int
            self.EVP_CIPHER_CTX_cleanup.argtypes = [ctypes.c_void_p]

        self.EVP_CIPHER_CTX_free = self._lib.EVP_CIPHER_CTX_free
        self.EVP_CIPHER_CTX_free.restype = None
        self.EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]

        self.EVP_CipherUpdate = self._lib.EVP_CipherUpdate
        self.EVP_CipherUpdate.restype = ctypes.c_int
        self.EVP_CipherUpdate.argtypes = [ctypes.c_void_p,
                                          ctypes.c_void_p, ctypes.c_void_p,
                                          ctypes.c_void_p, ctypes.c_int]

        self.EVP_CipherFinal_ex = self._lib.EVP_CipherFinal_ex
        self.EVP_CipherFinal_ex.restype = ctypes.c_int
        self.EVP_CipherFinal_ex.argtypes = [ctypes.c_void_p,
                                            ctypes.c_void_p, ctypes.c_void_p]

        self.EVP_DigestInit = self._lib.EVP_DigestInit
        self.EVP_DigestInit.restype = ctypes.c_int
        self._lib.EVP_DigestInit.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.EVP_DigestInit_ex = self._lib.EVP_DigestInit_ex
        self.EVP_DigestInit_ex.restype = ctypes.c_int
        self._lib.EVP_DigestInit_ex.argtypes = 3 * [ctypes.c_void_p]

        self.EVP_DigestUpdate = self._lib.EVP_DigestUpdate
        self.EVP_DigestUpdate.restype = ctypes.c_int
        self.EVP_DigestUpdate.argtypes = [ctypes.c_void_p,
                                          ctypes.c_void_p, ctypes.c_int]

        self.EVP_DigestFinal = self._lib.EVP_DigestFinal
        self.EVP_DigestFinal.restype = ctypes.c_int
        self.EVP_DigestFinal.argtypes = [ctypes.c_void_p,
                                         ctypes.c_void_p, ctypes.c_void_p]

        self.EVP_DigestFinal_ex = self._lib.EVP_DigestFinal_ex
        self.EVP_DigestFinal_ex.restype = ctypes.c_int
        self.EVP_DigestFinal_ex.argtypes = [ctypes.c_void_p,
                                            ctypes.c_void_p, ctypes.c_void_p]

        self.ECDSA_sign = self._lib.ECDSA_sign
        self.ECDSA_sign.restype = ctypes.c_int
        self.ECDSA_sign.argtypes = [ctypes.c_int, ctypes.c_void_p,
                                    ctypes.c_int, ctypes.c_void_p,
                                    ctypes.c_void_p, ctypes.c_void_p]

        self.ECDSA_verify = self._lib.ECDSA_verify
        self.ECDSA_verify.restype = ctypes.c_int
        self.ECDSA_verify.argtypes = [ctypes.c_int, ctypes.c_void_p,
                                      ctypes.c_int, ctypes.c_void_p,
                                      ctypes.c_int, ctypes.c_void_p]

        if self._hexversion >= 0x10100000 and not self._libreSSL:
            self.EVP_MD_CTX_new = self._lib.EVP_MD_CTX_new
            self.EVP_MD_CTX_new.restype = ctypes.c_void_p
            self.EVP_MD_CTX_new.argtypes = []

            self.EVP_MD_CTX_reset = self._lib.EVP_MD_CTX_reset
            self.EVP_MD_CTX_reset.restype = None
            self.EVP_MD_CTX_reset.argtypes = [ctypes.c_void_p]

            self.EVP_MD_CTX_free = self._lib.EVP_MD_CTX_free
            self.EVP_MD_CTX_free.restype = None
            self.EVP_MD_CTX_free.argtypes = [ctypes.c_void_p]

            self.EVP_sha1 = self._lib.EVP_sha1
            self.EVP_sha1.restype = ctypes.c_void_p
            self.EVP_sha1.argtypes = []

            self.digest_ecdsa_sha1 = self.EVP_sha1
        else:
            self.EVP_MD_CTX_create = self._lib.EVP_MD_CTX_create
            self.EVP_MD_CTX_create.restype = ctypes.c_void_p
            self.EVP_MD_CTX_create.argtypes = []

            self.EVP_MD_CTX_init = self._lib.EVP_MD_CTX_init
            self.EVP_MD_CTX_init.restype = None
            self.EVP_MD_CTX_init.argtypes = [ctypes.c_void_p]

            self.EVP_MD_CTX_destroy = self._lib.EVP_MD_CTX_destroy
            self.EVP_MD_CTX_destroy.restype = None
            self.EVP_MD_CTX_destroy.argtypes = [ctypes.c_void_p]

            self.EVP_ecdsa = self._lib.EVP_ecdsa
            self._lib.EVP_ecdsa.restype = ctypes.c_void_p
            self._lib.EVP_ecdsa.argtypes = []

            self.digest_ecdsa_sha1 = self.EVP_ecdsa

        self.RAND_bytes = self._lib.RAND_bytes
        self.RAND_bytes.restype = ctypes.c_int
        self.RAND_bytes.argtypes = [ctypes.c_void_p, ctypes.c_int]

        self.EVP_sha256 = self._lib.EVP_sha256
        self.EVP_sha256.restype = ctypes.c_void_p
        self.EVP_sha256.argtypes = []

        self.i2o_ECPublicKey = self._lib.i2o_ECPublicKey
        self.i2o_ECPublicKey.restype = ctypes.c_void_p
        self.i2o_ECPublicKey.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.EVP_sha512 = self._lib.EVP_sha512
        self.EVP_sha512.restype = ctypes.c_void_p
        self.EVP_sha512.argtypes = []

        self.HMAC = self._lib.HMAC
        self.HMAC.restype = ctypes.c_void_p
        self.HMAC.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                              ctypes.c_void_p, ctypes.c_int,
                              ctypes.c_void_p, ctypes.c_void_p]

        try:
            self.PKCS5_PBKDF2_HMAC = self._lib.PKCS5_PBKDF2_HMAC
        except Exception:
            # The above is not compatible with all versions of OSX.
            self.PKCS5_PBKDF2_HMAC = self._lib.PKCS5_PBKDF2_HMAC_SHA1

        self.PKCS5_PBKDF2_HMAC.restype = ctypes.c_int
        self.PKCS5_PBKDF2_HMAC.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                           ctypes.c_void_p, ctypes.c_int,
                                           ctypes.c_int, ctypes.c_void_p,
                                           ctypes.c_int, ctypes.c_void_p]

        # Blind signature requirements
        self.BN_CTX_new = self._lib.BN_CTX_new
        self.BN_CTX_new.restype = ctypes.c_void_p
        self.BN_CTX_new.argtypes = []

        self.BN_dup = self._lib.BN_dup
        self.BN_dup.restype = ctypes.c_void_p
        self.BN_dup.argtypes = [ctypes.c_void_p]

        self.BN_rand = self._lib.BN_rand
        self.BN_rand.restype = ctypes.c_int
        self.BN_rand.argtypes = [ctypes.c_void_p,
                                 ctypes.c_int,
                                 ctypes.c_int]

        self.BN_set_word = self._lib.BN_set_word
        self.BN_set_word.restype = ctypes.c_int
        self.BN_set_word.argtypes = [ctypes.c_void_p,
                                     ctypes.c_ulong]

        self.BN_mul = self._lib.BN_mul
        self.BN_mul.restype = ctypes.c_int
        self.BN_mul.argtypes = [ctypes.c_void_p,
                                ctypes.c_void_p,
                                ctypes.c_void_p,
                                ctypes.c_void_p]

        self.BN_mod_add = self._lib.BN_mod_add
        self.BN_mod_add.restype = ctypes.c_int
        self.BN_mod_add.argtypes = [ctypes.c_void_p,
                                    ctypes.c_void_p,
                                    ctypes.c_void_p,
                                    ctypes.c_void_p,
                                    ctypes.c_void_p]

        self.BN_mod_inverse = self._lib.BN_mod_inverse
        self.BN_mod_inverse.restype = ctypes.c_void_p
        self.BN_mod_inverse.argtypes = [ctypes.c_void_p,
                                        ctypes.c_void_p,
                                        ctypes.c_void_p,
                                        ctypes.c_void_p]

        self.BN_mod_mul = self._lib.BN_mod_mul
        self.BN_mod_mul.restype = ctypes.c_int
        self.BN_mod_mul.argtypes = [ctypes.c_void_p,
                                    ctypes.c_void_p,
                                    ctypes.c_void_p,
                                    ctypes.c_void_p,
                                    ctypes.c_void_p]

        self.BN_lshift = self._lib.BN_lshift
        self.BN_lshift.restype = ctypes.c_int
        self.BN_lshift.argtypes = [ctypes.c_void_p,
                                   ctypes.c_void_p,
                                   ctypes.c_int]

        self.BN_sub_word = self._lib.BN_sub_word
        self.BN_sub_word.restype = ctypes.c_int
        self.BN_sub_word.argtypes = [ctypes.c_void_p,
                                     ctypes.c_ulong]

        self.BN_cmp = self._lib.BN_cmp
        self.BN_cmp.restype = ctypes.c_int
        self.BN_cmp.argtypes = [ctypes.c_void_p,
                                ctypes.c_void_p]

        try:
            self.BN_is_odd = self._lib.BN_is_odd
            self.BN_is_odd.restype = ctypes.c_int
            self.BN_is_odd.argtypes = [ctypes.c_void_p]
        except AttributeError:
            # OpenSSL 1.1.0 implements this as a function, but earlier
            # versions as macro, so we need to workaround
            self.BN_is_odd = self.BN_is_odd_compatible

        self.BN_bn2dec = self._lib.BN_bn2dec
        self.BN_bn2dec.restype = ctypes.c_char_p
        self.BN_bn2dec.argtypes = [ctypes.c_void_p]

        self.EC_GROUP_new_by_curve_name = self._lib.EC_GROUP_new_by_curve_name
        self.EC_GROUP_new_by_curve_name.restype = ctypes.c_void_p
        self.EC_GROUP_new_by_curve_name.argtypes = [ctypes.c_int]

        self.EC_GROUP_get_order = self._lib.EC_GROUP_get_order
        self.EC_GROUP_get_order.restype = ctypes.c_int
        self.EC_GROUP_get_order.argtypes = [ctypes.c_void_p,
                                            ctypes.c_void_p,
                                            ctypes.c_void_p]

        self.EC_GROUP_get_cofactor = self._lib.EC_GROUP_get_cofactor
        self.EC_GROUP_get_cofactor.restype = ctypes.c_int
        self.EC_GROUP_get_cofactor.argtypes = [ctypes.c_void_p,
                                               ctypes.c_void_p,
                                               ctypes.c_void_p]

        self.EC_GROUP_get0_generator = self._lib.EC_GROUP_get0_generator
        self.EC_GROUP_get0_generator.restype = ctypes.c_void_p
        self.EC_GROUP_get0_generator.argtypes = [ctypes.c_void_p]

        self.EC_POINT_copy = self._lib.EC_POINT_copy
        self.EC_POINT_copy.restype = ctypes.c_int
        self.EC_POINT_copy.argtypes = [ctypes.c_void_p,
                                       ctypes.c_void_p]

        self.EC_POINT_add = self._lib.EC_POINT_add
        self.EC_POINT_add.restype = ctypes.c_int
        self.EC_POINT_add.argtypes = [ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p]

        self.EC_POINT_cmp = self._lib.EC_POINT_cmp
        self.EC_POINT_cmp.restype = ctypes.c_int
        self.EC_POINT_cmp.argtypes = [ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p,
                                      ctypes.c_void_p]

        self.EC_POINT_set_to_infinity = self._lib.EC_POINT_set_to_infinity
        self.EC_POINT_set_to_infinity.restype = ctypes.c_int
        self.EC_POINT_set_to_infinity.argtypes = [ctypes.c_void_p,
                                                  ctypes.c_void_p]

        self._set_ciphers()
        self._set_curves()

    def _set_ciphers(self):
        self.cipher_algo = {
            'aes-128-cbc': CipherName(
                'aes-128-cbc', self.EVP_aes_128_cbc, 16),
            'aes-256-cbc': CipherName(
                'aes-256-cbc', self.EVP_aes_256_cbc, 16),
            'aes-128-cfb': CipherName(
                'aes-128-cfb', self.EVP_aes_128_cfb128, 16),
            'aes-256-cfb': CipherName(
                'aes-256-cfb', self.EVP_aes_256_cfb128, 16),
            'aes-128-ofb': CipherName(
                'aes-128-ofb', self._lib.EVP_aes_128_ofb, 16),
            'aes-256-ofb': CipherName(
                'aes-256-ofb', self._lib.EVP_aes_256_ofb, 16),
            # 'aes-128-ctr': CipherName(
            #      'aes-128-ctr', self._lib.EVP_aes_128_ctr, 16),
            # 'aes-256-ctr': CipherName(
            #      'aes-256-ctr', self._lib.EVP_aes_256_ctr, 16),
            'bf-cfb': CipherName(
                'bf-cfb', self.EVP_bf_cfb64, 8),
            'bf-cbc': CipherName(
                'bf-cbc', self.EVP_bf_cbc, 8),
            # 128 is the initialisation size not block size
            'rc4': CipherName(
                'rc4', self.EVP_rc4, 128),
        }

    def _set_curves(self):
        self.curves = {
            'secp112r1': 704,
            'secp112r2': 705,
            'secp128r1': 706,
            'secp128r2': 707,
            'secp160k1': 708,
            'secp160r1': 709,
            'secp160r2': 710,
            'secp192k1': 711,
            'secp224k1': 712,
            'secp224r1': 713,
            'secp256k1': 714,
            'secp384r1': 715,
            'secp521r1': 716,
            'sect113r1': 717,
            'sect113r2': 718,
            'sect131r1': 719,
            'sect131r2': 720,
            'sect163k1': 721,
            'sect163r1': 722,
            'sect163r2': 723,
            'sect193r1': 724,
            'sect193r2': 725,
            'sect233k1': 726,
            'sect233r1': 727,
            'sect239k1': 728,
            'sect283k1': 729,
            'sect283r1': 730,
            'sect409k1': 731,
            'sect409r1': 732,
            'sect571k1': 733,
            'sect571r1': 734,
        }

    def BN_num_bytes(self, x):
        """
        returns the length of a BN (OpenSSl API)
        """
        return int((self.BN_num_bits(x) + 7) / 8)

    def BN_is_odd_compatible(self, x):
        """
        returns if BN is odd
        we assume big endianness, and that BN is initialised
        """
        length = self.BN_num_bytes(x)
        data = self.malloc(0, length)
        OpenSSL.BN_bn2bin(x, data)
        return ord(data[length - 1]) & 1

    def get_cipher(self, name):
        """
        returns the OpenSSL cipher instance
        """
        if name not in self.cipher_algo:
            raise Exception("Unknown cipher")
        return self.cipher_algo[name]

    def get_curve(self, name):
        """
        returns the id of a elliptic curve
        """
        if name not in self.curves:
            raise Exception("Unknown curve")
        return self.curves[name]

    def get_curve_by_id(self, id_):
        """
        returns the name of a elliptic curve with his id
        """
        res = None
        for i in self.curves:
            if self.curves[i] == id_:
                res = i
                break
        if res is None:
            raise Exception("Unknown curve")
        return res

    def rand(self, size):
        """
        OpenSSL random function
        """
        buffer_ = self.malloc(0, size)
        # This pyelliptic library, by default, didn't check the return value
        # of RAND_bytes. It is evidently possible that it returned an error
        # and not-actually-random data. However, in tests on various
        # operating systems, while generating hundreds of gigabytes of random
        # strings of various sizes I could not get an error to occur.
        # Also Bitcoin doesn't check the return value of RAND_bytes either.
        # Fixed in Bitmessage version 0.4.2 (in source code on 2013-10-13)
        while self.RAND_bytes(buffer_, size) != 1:
            import time
            time.sleep(1)
        return buffer_.raw

    def malloc(self, data, size):
        """
        returns a create_string_buffer (ctypes)
        """
        buffer_ = None
        if data != 0:
            if sys.version_info.major == 3 and isinstance(data, type('')):
                data = data.encode()
            buffer_ = self.create_string_buffer(data, size)
        else:
            buffer_ = self.create_string_buffer(size)
        return buffer_


def loadOpenSSL():
    """This function finds and load the OpenSSL library"""
    # pylint: disable=global-statement
    global OpenSSL
    from os import path, environ
    from ctypes.util import find_library

    libdir = []
    if getattr(sys, 'frozen', None):
        if 'darwin' in sys.platform:
            libdir.extend([
                path.join(
                    environ['RESOURCEPATH'], '..',
                    'Frameworks', 'libcrypto.dylib'),
                path.join(
                    environ['RESOURCEPATH'], '..',
                    'Frameworks', 'libcrypto.1.1.0.dylib'),
                path.join(
                    environ['RESOURCEPATH'], '..',
                    'Frameworks', 'libcrypto.1.0.2.dylib'),
                path.join(
                    environ['RESOURCEPATH'], '..',
                    'Frameworks', 'libcrypto.1.0.1.dylib'),
                path.join(
                    environ['RESOURCEPATH'], '..',
                    'Frameworks', 'libcrypto.1.0.0.dylib'),
                path.join(
                    environ['RESOURCEPATH'], '..',
                    'Frameworks', 'libcrypto.0.9.8.dylib'),
            ])
        elif 'win32' in sys.platform or 'win64' in sys.platform:
            libdir.append(path.join(sys._MEIPASS, 'libeay32.dll'))
        else:
            libdir.extend([
                path.join(sys._MEIPASS, 'libcrypto.so'),
                path.join(sys._MEIPASS, 'libssl.so'),
                path.join(sys._MEIPASS, 'libcrypto.so.1.1.0'),
                path.join(sys._MEIPASS, 'libssl.so.1.1.0'),
                path.join(sys._MEIPASS, 'libcrypto.so.1.0.2'),
                path.join(sys._MEIPASS, 'libssl.so.1.0.2'),
                path.join(sys._MEIPASS, 'libcrypto.so.1.0.1'),
                path.join(sys._MEIPASS, 'libssl.so.1.0.1'),
                path.join(sys._MEIPASS, 'libcrypto.so.1.0.0'),
                path.join(sys._MEIPASS, 'libssl.so.1.0.0'),
                path.join(sys._MEIPASS, 'libcrypto.so.0.9.8'),
                path.join(sys._MEIPASS, 'libssl.so.0.9.8'),
            ])
    if 'darwin' in sys.platform:
        libdir.extend([
            'libcrypto.dylib', '/usr/local/opt/openssl/lib/libcrypto.dylib'])
    elif 'win32' in sys.platform or 'win64' in sys.platform:
        libdir.append('libeay32.dll')
    else:
        libdir.append('libcrypto.so')
        libdir.append('libssl.so')
        libdir.append('libcrypto.so.1.0.0')
        libdir.append('libssl.so.1.0.0')
    if 'linux' in sys.platform or 'darwin' in sys.platform \
            or 'bsd' in sys.platform:
        libdir.append(find_library('ssl'))
    elif 'win32' in sys.platform or 'win64' in sys.platform:
        libdir.append(find_library('libeay32'))
    for library in libdir:
        try:
            OpenSSL = _OpenSSL(library)
            return
        except Exception:
            pass
    raise Exception(
        "Couldn't find and load the OpenSSL library. You must install it.")


loadOpenSSL()
