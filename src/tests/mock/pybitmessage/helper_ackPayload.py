"""
This module is for generating ack payload
"""

from binascii import hexlify
from struct import pack

import helper_random
import highlevelcrypto
from addresses import encodeVarint


def genAckPayload(streamNumber=1, stealthLevel=0):
    """
    Generate and return payload obj.

    This function generates payload objects for message acknowledgements
    Several stealth levels are available depending on the privacy needs;
    a higher level means better stealth, but also higher cost (size+POW)

       - level 0: a random 32-byte sequence with a message header appended
       - level 1: a getpubkey request for a (random) dummy key hash
       - level 2: a standard message, encrypted to a random pubkey
    """
    if stealthLevel == 2:      # Generate privacy-enhanced payload
        # Generate a dummy privkey and derive the pubkey
        dummyPubKeyHex = highlevelcrypto.privToPub(
            hexlify(helper_random.randomBytes(32)))
        # Generate a dummy message of random length
        # (the smallest possible standard-formatted message is 234 bytes)
        dummyMessage = helper_random.randomBytes(
            helper_random.randomrandrange(234, 801))
        # Encrypt the message using standard BM encryption (ECIES)
        ackdata = highlevelcrypto.encrypt(dummyMessage, dummyPubKeyHex)
        acktype = 2  # message
        version = 1

    elif stealthLevel == 1:    # Basic privacy payload (random getpubkey)
        ackdata = helper_random.randomBytes(32)
        acktype = 0  # getpubkey
        version = 4

    else:            # Minimum viable payload (non stealth)
        ackdata = helper_random.randomBytes(32)
        acktype = 2  # message
        version = 1

    ackobject = pack('>I', acktype) + encodeVarint(
        version) + encodeVarint(streamNumber) + ackdata

    return ackobject
