import random

from bmconfigparser import BMConfigParser
import knownnodes
import state

def chooseConnection(stream):
    if state.trustedPeer:
        return state.trustedPeer
    else:
        return random.choice(knownnodes.knownNodes[stream].keys())
