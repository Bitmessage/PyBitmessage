"""
Manipulations with knownNodes dictionary.
"""

import json
import os
import pickle
import threading
import time

import state
from bmconfigparser import BMConfigParser
from debug import logger
from helper_bootstrap import dns

knownNodesLock = threading.Lock()
knownNodes = {stream: {} for stream in range(1, 4)}

knownNodesTrimAmount = 2000

# forget a node after rating is this low
knownNodesForgetRating = -0.5

knownNodesActual = False

DEFAULT_NODES = (
    state.Peer('5.45.99.75', 8444),
    state.Peer('75.167.159.54', 8444),
    state.Peer('95.165.168.168', 8444),
    state.Peer('85.180.139.241', 8444),
    state.Peer('158.222.217.190', 8080),
    state.Peer('178.62.12.187', 8448),
    state.Peer('24.188.198.204', 8111),
    state.Peer('109.147.204.113', 1195),
    state.Peer('178.11.46.221', 8444)
)

DEFAULT_NODES_ONION = (
    state.Peer('quzwelsuziwqgpt2.onion', 8444),
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
    global knownNodesActual  # pylint: disable=global-statement
    for node in json.load(source):
        peer = node['peer']
        info = node['info']
        peer = state.Peer(str(peer['host']), peer.get('port', 8444))
        knownNodes[node['stream']][peer] = info

        if (
            not (knownNodesActual or info.get('is_self')) and
            peer not in DEFAULT_NODES and
            peer not in DEFAULT_NODES_ONION
        ):
            knownNodesActual = True


def pickle_deserialize_old_knownnodes(source):
    """
    Unpickle source and reorganize knownnodes dict if it's in old format
    the old format was {Peer:lastseen, ...}
    the new format is {Peer:{"lastseen":i, "rating":f}}
    """
    global knownNodes  # pylint: disable=global-statement
    knownNodes = pickle.load(source)
    for stream in knownNodes.keys():
        for node, params in knownNodes[stream].iteritems():
            if isinstance(params, (float, int)):
                addKnownNode(stream, node, params)


def saveKnownNodes(dirName=None):
    if dirName is None:
        dirName = state.appdata
    with knownNodesLock:
        with open(os.path.join(dirName, 'knownnodes.dat'), 'wb') as output:
            json_serialize_knownnodes(output)


def addKnownNode(stream, peer, lastseen=None, is_self=False):
    knownNodes[stream][peer] = {
        "lastseen": lastseen or time.time(),
        "rating": 0,
        "self": is_self,
    }


def createDefaultKnownNodes(onion=False):
    past = time.time() - 2418600  # 28 days - 10 min
    for peer in DEFAULT_NODES_ONION if onion else DEFAULT_NODES:
        addKnownNode(1, peer, past)
    saveKnownNodes()


def readKnownNodes():
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
            self_peer = state.Peer(onionhostname, onionport)
            addKnownNode(1, self_peer, is_self=True)
            state.ownAddresses[self_peer] = True


def increaseRating(peer):
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


def cleanupKnownNodes():
    """
    Cleanup knownnodes: remove old nodes and nodes with low rating
    """
    now = int(time.time())
    needToWriteKnownNodesToDisk = False
    dns_done = False
    spawnConnections = not BMConfigParser().safeGetBoolean(
        'bitmessagesettings', 'dontconnect'
    ) and BMConfigParser().safeGetBoolean(
        'bitmessagesettings', 'sendoutgoingconnections')

    with knownNodesLock:
        for stream in knownNodes:
            if stream not in state.streamsInWhichIAmParticipating:
                continue
            keys = knownNodes[stream].keys()
            if len(keys) <= 1:  # leave at least one node
                if not dns_done and spawnConnections:
                    dns()
                    dns_done = True
                continue
            for node in keys:
                try:
                    # scrap old nodes
                    if (now - knownNodes[stream][node]["lastseen"] >
                            2419200):  # 28 days
                        needToWriteKnownNodesToDisk = True
                        del knownNodes[stream][node]
                        continue
                    # scrap old nodes with low rating
                    if (now - knownNodes[stream][node]["lastseen"] > 10800 and
                        knownNodes[stream][node]["rating"] <=
                            knownNodesForgetRating):
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
