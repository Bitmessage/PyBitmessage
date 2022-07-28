import sys

if getattr(sys, 'frozen', None):
    from test_arithmetic import TestArithmetic
    from test_ecc import TestECC
    from test_blindsig import TestBlindSig
    from test_openssl import TestOpenSSL

    __all__ = ["TestArithmetic", "TestBlindSig", "TestECC", "TestOpenSSL"]
