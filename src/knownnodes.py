import pickle
import threading

import state

knownNodesLock = threading.Lock()
knownNodes = {}

def saveKnownNodes(dirName = None):
    if dirName is None:
        dirName = state.appdata
    with knownNodesLock:
        with open(dirName + 'knownnodes.dat', 'wb') as output:
            pickle.dump(knownNodes, output)
