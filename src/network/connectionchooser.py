from queues import Queue
import random

from bmconfigparser import BMConfigParser
import knownnodes
from queues import portCheckerQueue, peerDiscoveryQueue
import state

def chooseConnection(stream):
    if state.trustedPeer:
        return state.trustedPeer
    else:
        try:
            return portCheckerQueue.get(False)
        except Queue.Empty:
            try:
                return peerDiscoveryQueue.get(False)
            except Queue.Empty:
                return random.choice(knownnodes.knownNodes[stream].keys())
