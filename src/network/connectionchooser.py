from queues import Queue
import random

from bmconfigparser import BMConfigParser
import knownnodes
from queues import portCheckerQueue, peerDiscoveryQueue
import state

def chooseConnection(stream):
    haveOnion = BMConfigParser().safeGet("bitmessagesettings", "socksproxytype")[0:5] == 'SOCKS'
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
    return retval
