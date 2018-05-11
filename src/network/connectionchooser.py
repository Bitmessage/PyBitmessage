from queues import Queue
import random

from bmconfigparser import BMConfigParser
import knownnodes
import protocol
from queues import portCheckerQueue
import state
import helper_random

def getDiscoveredPeer():
    try:
        peer = helper_random.randomchoice(state.discoveredPeers.keys())
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
    if helper_random.randomchoice((False, True)) and not haveOnion:
        # discovered peers are already filtered by allowed streams
        return getDiscoveredPeer()
    for _ in range(50):
        peer = helper_random.randomchoice(knownnodes.knownNodes[stream].keys())
        try:
            rating = knownnodes.knownNodes[stream][peer]["rating"]
        except TypeError:
            print "Error in %s" % (peer)
            rating = 0
        if haveOnion:
            # onion addresses have a higher priority when SOCKS
            if peer.host.endswith('.onion') and rating > 0:
                rating = 1
            else:
                encodedAddr = protocol.encodeHost(peer.host)
                # don't connect to local IPs when using SOCKS
                if not protocol.checkIPAddress(encodedAddr, False):
                    continue
        if rating > 1:
            rating = 1
        try:
            if 0.05/(1.0-rating) > random.random():
                return peer
        except ZeroDivisionError:
            return peer
    raise ValueError
