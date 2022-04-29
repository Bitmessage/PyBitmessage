"""
Select which node to connect to
"""
# pylint: disable=too-many-branches
import logging
import random

import knownnodes
import protocol
import state
from bmconfigparser import config
from queues import queue, portCheckerQueue

logger = logging.getLogger('default')


def getDiscoveredPeer():
    """Get a peer from the local peer discovery list"""
    try:
        peer = random.choice(state.discoveredPeers.keys())  # nosec B311
    except (IndexError, KeyError):
        raise ValueError
    try:
        del state.discoveredPeers[peer]
    except KeyError:
        pass
    return peer


def chooseConnection(stream):
    """Returns an appropriate connection"""
    haveOnion = config.safeGet(
        "bitmessagesettings", "socksproxytype")[0:5] == 'SOCKS'
    onionOnly = config.safeGetBoolean(
        "bitmessagesettings", "onionservicesonly")
    try:
        retval = portCheckerQueue.get(False)
        portCheckerQueue.task_done()
        return retval
    except queue.Empty:
        pass
    # with a probability of 0.5, connect to a discovered peer
    if random.choice((False, True)) and not haveOnion:  # nosec B311
        # discovered peers are already filtered by allowed streams
        return getDiscoveredPeer()
    for _ in range(50):
        peer = random.choice(  # nosec B311
            knownnodes.knownNodes[stream].keys())
        try:
            peer_info = knownnodes.knownNodes[stream][peer]
            if peer_info.get('self'):
                continue
            rating = peer_info["rating"]
        except TypeError:
            logger.warning('Error in %s', peer)
            rating = 0
        if haveOnion:
            # do not connect to raw IP addresses
            # --keep all traffic within Tor overlay
            if onionOnly and not peer.host.endswith('.onion'):
                continue
            # onion addresses have a higher priority when SOCKS
            if peer.host.endswith('.onion') and rating > 0:
                rating = 1
            # TODO: need better check
            elif not peer.host.startswith('bootstrap'):
                encodedAddr = protocol.encodeHost(peer.host)
                # don't connect to local IPs when using SOCKS
                if not protocol.checkIPAddress(encodedAddr, False):
                    continue
        if rating > 1:
            rating = 1
        try:
            if 0.05 / (1.0 - rating) > random.random():  # nosec B311
                return peer
        except ZeroDivisionError:
            return peer
    raise ValueError
