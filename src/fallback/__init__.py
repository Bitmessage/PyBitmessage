"""
Fallback expressions help PyBitmessage modules to run without some external
dependencies.


RIPEMD160Hash
-------------

We need to check :mod:`hashlib` for RIPEMD-160, as it won't be available
if OpenSSL is not linked against or the linked OpenSSL has RIPEMD disabled.
Try to use `pycryptodome <https://pypi.org/project/pycryptodome/>`_
in that case.
"""

import hashlib

try:
    hashlib.new('ripemd160')
except ValueError:
    try:
        from Crypto.Hash import RIPEMD160
    except ImportError:
        RIPEMD160Hash = None
    else:
        RIPEMD160Hash = RIPEMD160.new
else:
    def RIPEMD160Hash(data=None):
        """hashlib based RIPEMD160Hash"""
        hasher = hashlib.new('ripemd160')
        if data:
            hasher.update(data)
        return hasher
