from queues import Queue
import random

from bmconfigparser import BMConfigParser
import knownnodes
from queues import portCheckerQueue
import state

def getDiscoveredPeer():
    try:
        peer = random.choice(state.discoveredPeers.keys())
    except (IndexError, KeyError):
        raise ValueError
    try:
        del state.discoveredPeers[peer]
    except KeyError:
        pass
    return peer

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
    # with a probability of 0.5, connect to a discovered peer
    if random.choice((False, True)) and not haveOnion:
        # discovered peers are already filtered by allowed streams
        return getDiscoveredPeer()
    for _ in range(50):
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
