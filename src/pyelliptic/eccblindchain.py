"""
Blind signature chain with a top level CA
"""

from .eccblind import ECCBlind


class ECCBlindChain(object):  # pylint: disable=too-few-public-methods
    """
    # Class for ECC Blind Chain signature functionality
    """
    chain = []
    ca = []

    def __init__(self, ca=None, chain=None):
        if ca:
            for i in range(0, len(ca), 35):
                self.ca.append(ca[i:i + 35])
        if chain:
            self.chain.append(chain[0:35])
            for i in range(35, len(chain), 100):
                if len(chain[i:]) == 65:
                    self.chain.append(chain[i:i + 65])
                else:
                    self.chain.append(chain[i:i + 100])

    def verify(self, msg, value):
        """Verify a chain provides supplied message and value"""
        parent = None
        for level in self.chain:
            pubkey = None
            signature = None
            if len(level) == 100:
                pubkey, signature = (level[0:35], level[35:])
            elif len(level) == 35:
                if level not in self.ca:
                    return False
                parent = level
                continue
            else:
                signature = level
            verifier_obj = ECCBlind(pubkey=parent)
            if pubkey:
                if not verifier_obj.verify(pubkey, signature, value):
                    return False
                parent = pubkey
            else:
                return verifier_obj.verify(msg, signature, value)
        return None
