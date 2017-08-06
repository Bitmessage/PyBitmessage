from queues import Queue
import random

from bmconfigparser import BMConfigParser
import knownnodes
from queues import portCheckerQueue
import state

def getDiscoveredPeer(stream):
    try:
        return random.choice(state.discoveredPeers.keys())
    except (IndexError, KeyError):
        raise ValueError

def chooseConnection(stream):
    haveOnion = BMConfigParser().safeGet("bitmessagesettings", "socksproxytype")[0:5] == 'SOCKS'
    if state.trustedPeer:
        return state.trustedPeer
    try:
        retval = portCheckerQueue.get(False)
        portCheckerQueue.task_done()
        return retval
    except Queue.Empty:
        pass
    if random.choice((False, True)):
        return getDiscoveredPeer(stream)
    for i in range(50):
        peer = random.choice(knownnodes.knownNodes[stream].keys())
        try:
            rating = knownnodes.knownNodes[stream][peer]["rating"]
        except TypeError:
            print "Error in %s" % (peer)
            rating = 0
        if haveOnion and peer.host.endswith('.onion') and rating > 0:
            rating *= 10
        if rating > 1:
            rating = 1
        try:
            if 0.05/(1.0-rating) > random.random():
                return peer
        except ZeroDivisionError:
            return peer
    raise ValueError
