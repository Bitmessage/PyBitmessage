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
    print("Now I am entering into chooseConnection zone line 23..........................................................")
    haveOnion = BMConfigParser().safeGet("bitmessagesettings", "socksproxytype")[0:5] == 'SOCKS'
    print("Now I am entering into chooseConnection zone line 25..........................................................")
    if state.trustedPeer:
        return state.trustedPeer
    try:
        retval = portCheckerQueue.get(False)
        portCheckerQueue.task_done()
        return retval
    except Queue.Empty:
        pass
    # with a probability of 0.5, connect to a discovered peer
    print("Now I am entering into chooseConnection zone line 35..........................................................")
    if helper_random.randomchoice((False, True)) and not haveOnion:
        # discovered peers are already filtered by allowed streams
        return getDiscoveredPeer()
    print("Now I am entering into chooseConnection zone line 39..........................................................")
    for _ in range(50):
        print(_, "for In Zone for finding issue behind failure..........................................................")
        print(knownnodes.knownNodes[stream].keys(), "knowwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        print("knownnodesfinding.....................................................................................")
        peer = helper_random.randomchoice(knownnodes.knownNodes[stream].keys())
        print("for In Zone 43 ........................................................... ")
        try:
            print("for In Zone 45 ........................................................... ")
            rating = knownnodes.knownNodes[stream][peer]["rating"]
            print("for In Zone 47 ........................................................... ")
        except TypeError:
            print("for In Zone 49 ........................................................... ")
            print "Error in %s" % (peer)
            rating = 0
        print("for In Zone 52 ........................................................... ")
        if haveOnion:
            print("for In Zone 54 ........................................................... ")
            # onion addresses have a higher priority when SOCKS
            if peer.host.endswith('.onion') and rating > 0:
                print("for In Zone 57 ........................................................... ")
                rating = 1
                print("for In Zone 59 ........................................................... ")
            else:
                print("for In Zone 61 ........................................................... ")
                encodedAddr = protocol.encodeHost(peer.host)
                print("for In Zone 63 ........................................................... ")
                # don't connect to local IPs when using SOCKS
                if not protocol.checkIPAddress(encodedAddr, False):
                    print("for In Zone 66 ........................................................... ")
                    continue
        print("for In Zone 68 ........................................................... ")
        if rating > 1:
            print("for In Zone 70 ........................................................... ")
            rating = 1
        try:
            print("for In Zone 73 ........................................................... ")
            if 0.05/(1.0-rating) > random.random():
                print("for In Zone 75 ........................................................... ")
                return peer
        except ZeroDivisionError:
            return peer
        print("for In Zone 79 ........................................................... ")
    raise ValueError
