from queues import Queue
import random

from bmconfigparser import BMConfigParser
import knownnodes
from queues import portCheckerQueue, peerDiscoveryQueue
import state

def chooseConnection(stream):
    if state.trustedPeer:
        return state.trustedPeer
    try:
        retval = portCheckerQueue.get(False)
        portCheckerQueue.task_done()
    except Queue.Empty:
        try:
            retval = peerDiscoveryQueue.get(False)
            peerDiscoveryQueue.task_done()
        except Queue.Empty:
            return random.choice(knownnodes.knownNodes[stream].keys())
    return retval
