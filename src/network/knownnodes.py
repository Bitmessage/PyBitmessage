"""
Manipulations with knownNodes dictionary.
"""
# TODO: knownnodes object maybe?
# pylint: disable=global-statement

import json
import logging
import os
import pickle
import threading
import time
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

import state
from bmconfigparser import BMConfigParser
from network.node import Peer

state.Peer = Peer

knownNodesLock = threading.RLock()
"""Thread lock for knownnodes modification"""
knownNodes = {stream: {} for stream in range(1, 4)}
"""The dict of known nodes for each stream"""

knownNodesTrimAmount = 2000
"""trim stream knownnodes dict to this length"""

knownNodesForgetRating = -0.5
"""forget a node after rating is this low"""

knownNodesActual = False

logger = logging.getLogger('default')

DEFAULT_NODES = (
    Peer('5.45.99.75', 8444),
    Peer('75.167.159.54', 8444),
    Peer('95.165.168.168', 8444),
    Peer('85.180.139.241', 8444),
    Peer('158.222.217.190', 8080),
    Peer('178.62.12.187', 8448),
    Peer('24.188.198.204', 8111),
    Peer('109.147.204.113', 1195),
    Peer('178.11.46.221', 8444)
)


def json_serialize_knownnodes(output):
    """
    Reorganize knownnodes dict and write it as JSON to output
    """
    _serialized = []
    for stream, peers in knownNodes.iteritems():
        for peer, info in peers.iteritems():
            info.update(rating=round(info.get('rating', 0), 2))
            _serialized.append({
                'stream': stream, 'peer': peer._asdict(), 'info': info
            })
    json.dump(_serialized, output, indent=4)


def json_deserialize_knownnodes(source):
    """
    Read JSON from source and make knownnodes dict
    """
    global knownNodesActual
    for node in json.load(source):
        peer = node['peer']
        info = node['info']
        peer = Peer(str(peer['host']), peer.get('port', 8444))
        knownNodes[node['stream']][peer] = info
        if not (knownNodesActual
                or info.get('self')) and peer not in DEFAULT_NODES:
            knownNodesActual = True


def pickle_deserialize_old_knownnodes(source):
    """
    Unpickle source and reorganize knownnodes dict if it has old format
    the old format was {Peer:lastseen, ...}
    the new format is {Peer:{"lastseen":i, "rating":f}}
    """
    global knownNodes
    knownNodes = pickle.load(source)
    for stream in knownNodes.keys():
        for node, params in knownNodes[stream].iteritems():
            if isinstance(params, (float, int)):
                addKnownNode(stream, node, params)


def saveKnownNodes(dirName=None):
    """Save knownnodes to filesystem"""
    if dirName is None:
        dirName = state.appdata
    with knownNodesLock:
        with open(os.path.join(dirName, 'knownnodes.dat'), 'wb') as output:
            json_serialize_knownnodes(output)


def addKnownNode(stream, peer, lastseen=None, is_self=False):
    """
    Add a new node to the dict or update lastseen if it already exists.
    Do it for each stream number if *stream* is `Iterable`.
    Returns True if added a new node.
    """
    # pylint: disable=too-many-branches
    if isinstance(stream, Iterable):
        with knownNodesLock:
            for s in stream:
                addKnownNode(s, peer, lastseen, is_self)
        return

    rating = 0.0
    if not lastseen:
        # FIXME: maybe about 28 days?
        lastseen = int(time.time())
    else:
        lastseen = int(lastseen)
        try:
            info = knownNodes[stream].get(peer)
            if lastseen > info['lastseen']:
                info['lastseen'] = lastseen
        except (KeyError, TypeError):
            pass
        else:
            return

    if not is_self:
        if len(knownNodes[stream]) > BMConfigParser().safeGetInt(
                "knownnodes", "maxnodes"):
            return

    knownNodes[stream][peer] = {
        'lastseen': lastseen,
        'rating': rating or 1 if is_self else 0,
        'self': is_self,
    }
    return True


def createDefaultKnownNodes():
    """Creating default Knownnodes"""
    past = time.time() - 2418600  # 28 days - 10 min
    for peer in DEFAULT_NODES:
        addKnownNode(1, peer, past)
    saveKnownNodes()


def readKnownNodes():
    """Load knownnodes from filesystem"""
    try:
        with open(state.appdata + 'knownnodes.dat', 'rb') as source:
            with knownNodesLock:
                try:
                    json_deserialize_knownnodes(source)
                except ValueError:
                    source.seek(0)
                    pickle_deserialize_old_knownnodes(source)
    except (IOError, OSError, KeyError, EOFError):
        logger.debug(
            'Failed to read nodes from knownnodes.dat', exc_info=True)
        createDefaultKnownNodes()

    config = BMConfigParser()

    # your own onion address, if setup
    onionhostname = config.safeGet('bitmessagesettings', 'onionhostname')
    if onionhostname and ".onion" in onionhostname:
        onionport = config.safeGetInt('bitmessagesettings', 'onionport')
        if onionport:
            self_peer = Peer(onionhostname, onionport)
            addKnownNode(1, self_peer, is_self=True)
            state.ownAddresses[self_peer] = True


def increaseRating(peer):
    """Increase rating of a peer node"""
    increaseAmount = 0.1
    maxRating = 1
    with knownNodesLock:
        for stream in knownNodes.keys():
            try:
                knownNodes[stream][peer]["rating"] = min(
                    knownNodes[stream][peer]["rating"] + increaseAmount,
                    maxRating
                )
            except KeyError:
                pass


def decreaseRating(peer):
    """Decrease rating of a peer node"""
    decreaseAmount = 0.1
    minRating = -1
    with knownNodesLock:
        for stream in knownNodes.keys():
            try:
                knownNodes[stream][peer]["rating"] = max(
                    knownNodes[stream][peer]["rating"] - decreaseAmount,
                    minRating
                )
            except KeyError:
                pass


def trimKnownNodes(recAddrStream=1):
    """Triming Knownnodes"""
    if len(knownNodes[recAddrStream]) < \
            BMConfigParser().safeGetInt("knownnodes", "maxnodes"):
        return
    with knownNodesLock:
        oldestList = sorted(
            knownNodes[recAddrStream],
            key=lambda x: x['lastseen']
        )[:knownNodesTrimAmount]
        for oldest in oldestList:
            del knownNodes[recAddrStream][oldest]


def dns():
    """Add DNS names to knownnodes"""
    for port in [8080, 8444]:
        addKnownNode(
            1, Peer('bootstrap%s.bitmessage.org' % port, port))


def cleanupKnownNodes():
    """
    Cleanup knownnodes: remove old nodes and nodes with low rating
    """
    global knownNodesActual
    now = int(time.time())
    needToWriteKnownNodesToDisk = False

    with knownNodesLock:
        for stream in knownNodes:
            if stream not in state.streamsInWhichIAmParticipating:
                continue
            keys = knownNodes[stream].keys()
            for node in keys:
                if len(knownNodes[stream]) <= 1:  # leave at least one node
                    if stream == 1:
                        knownNodesActual = False
                    break
                try:
                    age = now - knownNodes[stream][node]["lastseen"]
                    # scrap old nodes (age > 28 days)
                    if age > 2419200:
                        needToWriteKnownNodesToDisk = True
                        del knownNodes[stream][node]
                        continue
                    # scrap old nodes (age > 3 hours) with low rating
                    if (age > 10800 and knownNodes[stream][node]["rating"]
                            <= knownNodesForgetRating):
                        needToWriteKnownNodesToDisk = True
                        del knownNodes[stream][node]
                        continue
                except TypeError:
                    logger.warning('Error in %s', node)
            keys = []

    # Let us write out the knowNodes to disk
    # if there is anything new to write out.
    if needToWriteKnownNodesToDisk:
        saveKnownNodes()
