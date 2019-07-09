#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright (C) 2011 Yann GUIBET <yannguibet@gmail.com>
#  See LICENSE for details.

from pyelliptic.openssl import OpenSSL


class Cipher:
    """
    Symmetric encryption

        import pyelliptic
        iv = pyelliptic.Cipher.gen_IV('aes-256-cfb')
        ctx = pyelliptic.Cipher("secretkey", iv, 1, ciphername='aes-256-cfb')
        ciphertext = ctx.update('test1')
        ciphertext += ctx.update('test2')
        ciphertext += ctx.final()

        ctx2 = pyelliptic.Cipher("secretkey", iv, 0, ciphername='aes-256-cfb')
        print ctx2.ciphering(ciphertext)
    """
    def __init__(self, key, iv, do, cipher_name='aes-256-cbc'):
        """
        do == 1 => Encrypt; do == 0 => Decrypt
        """
        self.cipher = OpenSSL.get_cipher(cipher_name)
        self.ctx = OpenSSL.EVP_CIPHER_CTX_new()
        if do == 1 or do == 0:
            k = OpenSSL.malloc(key, len(key))
            iv1 = OpenSSL.malloc(iv, len(iv))
            OpenSSL.EVP_CipherInit_ex(
                self.ctx, self.cipher.get_pointer(), 0, k, iv1, do)
        else:
            raise Exception("RTFM ...")

    @staticmethod
    def get_all_cipher():
        """
        static method, returns all ciphers available
        """
        return OpenSSL.cipher_algo.keys()

    @staticmethod
    def get_blocksize(cipher_name):
        cipher = OpenSSL.get_cipher(cipher_name)
        return cipher.get_blocksize()

    @staticmethod
    def gen_IV(cipher_name):
        cipher = OpenSSL.get_cipher(cipher_name)
        return OpenSSL.rand(cipher.get_blocksize())

    def update(self, in_put):
        i = OpenSSL.c_int(0)
        buffer = OpenSSL.malloc(b"", len(in_put) + self.cipher.get_blocksize())
        inp = OpenSSL.malloc(in_put, len(in_put))
        if OpenSSL.EVP_CipherUpdate(self.ctx, OpenSSL.byref(buffer),
                                    OpenSSL.byref(i), inp, len(in_put)) == 0:
            raise Exception("[OpenSSL] EVP_CipherUpdate FAIL ...")
        return buffer.raw[0:i.value]

    def final(self):
        i = OpenSSL.c_int(0)
        buffer = OpenSSL.malloc(b"", self.cipher.get_blocksize())
        if (OpenSSL.EVP_CipherFinal_ex(self.ctx, OpenSSL.byref(buffer),
                                       OpenSSL.byref(i))) == 0:
            raise Exception("[OpenSSL] EVP_CipherFinal_ex FAIL ...")
        return buffer.raw[0:i.value]

    def ciphering(self, in_put):
        """
        Do update and final in one method
        """
        buff = self.update(in_put)
        return buff + self.final()

    def __del__(self):
        if OpenSSL._hexversion > 0x10100000 and not OpenSSL._libreSSL:
            OpenSSL.EVP_CIPHER_CTX_reset(self.ctx)
        else:
            OpenSSL.EVP_CIPHER_CTX_cleanup(self.ctx)
        OpenSSL.EVP_CIPHER_CTX_free(self.ctx)
