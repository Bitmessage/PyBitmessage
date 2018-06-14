import pickle
import os
import threading

from bmconfigparser import BMConfigParser
import state

knownNodesLock = threading.Lock()
knownNodes = {}

knownNodesTrimAmount = 2000

# forget a node after rating is this low
knownNodesForgetRating = -0.5


def saveKnownNodes(dirname=None):
    if dirname is None:
        dirname = state.appdata
    with knownNodesLock:
        with open(os.path.join(dirname, 'knownnodes.dat'), 'wb') as output:
            pickle.dump(knownNodes, output)


def increaseRating(peer):
    increaseAmount = 0.1
    maxRating = 1
    with knownNodesLock:
        for stream in knownNodes.keys():
            try:
                knownNodes[stream][peer]["rating"] = min(knownNodes[stream][peer]["rating"] + increaseAmount, maxRating)
            except KeyError:
                pass


def decreaseRating(peer):
    decreaseAmount = 0.1
    minRating = -1
    with knownNodesLock:
        for stream in knownNodes.keys():
            try:
                knownNodes[stream][peer]["rating"] = max(knownNodes[stream][peer]["rating"] - decreaseAmount, minRating)
            except KeyError:
                pass


def trimKnownNodes(rec_addr_stream=1):
    if len(knownNodes[rec_addr_stream]) < int(BMConfigParser().get("knownnodes", "maxnodes")):
        return
    with knownNodesLock:
        oldestList = sorted(knownNodes[rec_addr_stream], key=lambda x: x['lastseen'])[:knownNodesTrimAmount]
        for oldest in oldestList:
            del knownNodes[rec_addr_stream][oldest]
