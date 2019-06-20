"""
.. todo:: hello world
"""

import hashlib

# We need to check hashlib for RIPEMD-160, as it won't be available
# if OpenSSL is not linked against or the linked OpenSSL has RIPEMD
# disabled.

try:
    hashlib.new('ripemd160')
except ValueError:
    try:
        from Crypto.Hash import RIPEMD
    except ImportError:
        RIPEMD160Hash = None
    else:
        RIPEMD160Hash = RIPEMD.RIPEMD160Hash
else:
    def RIPEMD160Hash(data=None):
        """hashlib based RIPEMD160Hash"""
        hasher = hashlib.new('ripemd160')
        if data:
            hasher.update(data)
        return hasher
