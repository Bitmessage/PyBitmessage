import os

from pyelliptic.openssl import OpenSSL


def randomBytes(n):
    """Method randomBytes."""
    try:
        return os.urandom(n)
    except NotImplementedError:
        return OpenSSL.rand(n)
