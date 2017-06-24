import pickle
import threading

from bmconfigparser import BMConfigParser
import state

knownNodesLock = threading.Lock()
knownNodes = {}

knownNodesTrimAmount = 2000

def saveKnownNodes(dirName = None):
    if dirName is None:
        dirName = state.appdata
    with knownNodesLock:
        with open(dirName + 'knownnodes.dat', 'wb') as output:
            pickle.dump(knownNodes, output)

def trimKnownNodes(recAddrStream = 1):
    if len(knownNodes[recAddrStream]) < BMConfigParser().get("knownnodes", "maxnodes"):
        return
    with knownNodesLock:
        oldestList = sorted(knownNodes[recAddrStream], key=knownNodes[recAddrStream].get)[:knownNodesTrimAmount]
        for oldest in oldestList:
            del knownNodes[recAddrStream][oldest]
