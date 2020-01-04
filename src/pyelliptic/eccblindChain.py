#!/usr/bin/env python
"""
ECC blind signature functionality based on "An Efficient Blind Signature Scheme
Based on the Elliptic CurveDiscrete Logarithm Problem" by Morteza Nikooghadama
<mnikooghadam@sbu.ac.ir> and Ali Zakerolhosseini <a-zaker@sbu.ac.ir>,
http://www.isecure-journal.com/article_39171_47f9ec605dd3918c2793565ec21fcd7a.pdf
"""

# variable names are based on the math in the paper, so they don't conform
# to PEP8
# pylint: disable=invalid-name

import sys
import hash as Hash
sys.path.insert(1, '/home/cis/ektarepo/PyBitmessage/src/pyelliptic')
from eccblind import ECCBlind

try:
    import msgpack
except ImportError:
    try:
        import umsgpack as msgpack
    except ImportError:
        import fallback.umsgpack.umsgpack as msgpack

from eccblind import ECCBlind

def encode_datetime(obj):
    """
    Method to format time
    """
    return {'Time': int(obj.strftime("%s"))}


class ECCBlindChain(object):  # pylint: disable=too-many-instance-attributes
    """
    # Class for ECC Blind Chain signature functionality
    """
    chain = []
    ca = []

    def __init__(self, chain=None):
        if chain is not None:
            self.chain = chain

    def serialize(self):
        data = msgpack.packb(self.chain)
        return data

    @staticmethod
    def deserialize(chain):
        """
        Deserialize the data using msgpack
        """
        data = msgpack.unpackb(chain)
        return ECCBlindChain(data)

    def add_level(self, pubkey, metadata, signature):
        self.chain.append((pubkey, metadata, signature))

    def add_ca(self, ca):
        pubkey = ca.pubkey
        metadata = ca.metadata
        self.ca.append(pubkey)

    def verify(self, msg, value):
        lastpubkey = None
        retval = False
        for level in reversed(self.chain):
            pubkey, metadata, signature = level
            verifier_obj = ECCBlind(pubkey=pubkey, metadata=metadata)

            # As msg is being seriaized so no need of using lastpubkey it will be the msg which is being signed
            retval = verifier_obj.verify(msgpack.packb([pubkey,metadata]), signature, value)
            if not retval:
                break
        if retval:
            retval = False
            for ca in self.ca:
                match = True
                for i in range(4):
                    if pubkey[i] != ca[i]:
                        match = False
                        break
                if match:
                    return True
        return retval
