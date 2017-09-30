import hashlib
import highlevelcrypto
import random
import helper_random
from binascii import hexlify, unhexlify
from struct import pack, unpack
from addresses import encodeVarint

# This function generates payload objects for message acknowledgements
# Several stealth levels are available depending on the privacy needs; 
# a higher level means better stealth, but also higher cost (size+POW)
#   - level 0: a random 32-byte sequence with a message header appended
#   - level 1: a getpubkey request for a (random) dummy key hash
#   - level 2: a standard message, encrypted to a random pubkey

def genAckPayload(streamNumber=1, stealthLevel=0):
    if (stealthLevel==2):      # Generate privacy-enhanced payload
        # Generate a dummy privkey and derive the pubkey
        dummyPubKeyHex = highlevelcrypto.privToPub(hexlify(helper_random.randomBytes(32)))
        # Generate a dummy message of random length
        # (the smallest possible standard-formatted message is 234 bytes)
        dummyMessage = helper_random.randomBytes(random.randint(234, 800))
        # Encrypt the message using standard BM encryption (ECIES)
        ackdata = highlevelcrypto.encrypt(dummyMessage, dummyPubKeyHex)
        acktype = 2  # message
        version = 1

    elif (stealthLevel==1):    # Basic privacy payload (random getpubkey)
        ackdata = helper_random.randomBytes(32)
        acktype = 0  # getpubkey
        version = 4

    else:            # Minimum viable payload (non stealth)
        ackdata = helper_random.randomBytes(32)
        acktype = 2  # message
        version = 1

    ackobject = pack('>I', acktype) + encodeVarint(version) + encodeVarint(streamNumber) + ackdata

    return ackobject
