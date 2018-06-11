import json
import os
import pickle
# import sys
import threading
import time

import state
from bmconfigparser import BMConfigParser
from debug import logger

knownNodesLock = threading.Lock()
knownNodes = {stream: {} for stream in range(1, 4)}

knownNodesTrimAmount = 2000

# forget a node after rating is this low
knownNodesForgetRating = -0.5

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


def json_serialize_knownnodes(output):
    """
    Reorganize knownnodes dict and write it as JSON to output
    """
    _serialized = []
    for stream, peers in knownNodes.iteritems():
        for peer, info in peers.iteritems():
            _serialized.append({
                'stream': stream, 'peer': peer._asdict(), 'info': info
            })
    json.dump(_serialized, output, indent=4)


def json_deserialize_knownnodes(source):
    """
    Read JSON from source and make knownnodes dict
    """
    for node in json.load(source):
        peer = node['peer']
        peer['host'] = str(peer['host'])
        knownNodes[node['stream']][state.Peer(**peer)] = node['info']


def pickle_deserialize_old_knownnodes(source):
    """
    Unpickle source and reorganize knownnodes dict if it's in old format
    the old format was {Peer:lastseen, ...}
    the new format is {Peer:{"lastseen":i, "rating":f}}
    """
    knownNodes = pickle.load(source)
    for stream in knownNodes.keys():
        for node, params in knownNodes[stream].items():
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


def createDefaultKnownNodes():
    for peer in DEFAULT_NODES:
        addKnownNode(1, peer)
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
    except (IOError, OSError, KeyError):
        logger.debug(
            'Failed to read nodes from knownnodes.dat', exc_info=True)
        createDefaultKnownNodes()

    config = BMConfigParser()
    # if config.safeGetInt('bitmessagesettings', 'settingsversion') > 10:
    #     sys.exit(
    #         'Bitmessage cannot read future versions of the keys file'
    #         ' (keys.dat). Run the newer version of Bitmessage.')

    # your own onion address, if setup
    onionhostname = config.safeGet('bitmessagesettings', 'onionhostname')
    if onionhostname and ".onion" in onionhostname:
        onionport = config.safeGetInt('bitmessagesettings', 'onionport')
        if onionport:
            addKnownNode(1, state.Peer(onionhostname, onionport), is_self=True)


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
