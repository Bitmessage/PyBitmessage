"""
Blind signature chain with a top level CA
"""

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
    def deserialize(self, chain):
        """
        Deserialize the data using msgpack
        """
        data = msgpack.unpackb(chain)
        return ECCBlindChain(data)

    def add_level(self, pubkey, metadata, signature):
        self.chain.append((pubkey, metadata, signature))

    def add_ca(self, ca):
        pubkey, metadata = ECCBlind.deserialize(ca)
        self.ca.append(pubkey)

    def verify(self, msg, value):
        lastpubkey = None
        retval = False
        for level in reversed(self.chain):
            pubkey, metadata, signature = level
            verifier_obj = ECCBlind(pubkey=pubkey, metadata)
            if not lastpubkey:
                retval = verifier_obj.verify(msg, signature, value)
            else:
                retval = verifier_obj.verify(lastpubkey, signature, value)
            if not reval:
                break
            lastpubkey = pubkey
        if retval:
            retval = False
            for ca in self.ca:
                match = True
                for i in range(4):
                    if lastpubkey[i] != ca[i]:
                        match = False
                        break
                if match:
                    return True
        return retval
