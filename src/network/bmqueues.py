import time

from inventory import Inventory
from network.downloadqueue import DownloadQueue
from network.uploadqueue import UploadQueue

haveBloom = False

try:
    # pybloomfiltermmap
    from pybloomfilter import BloomFilter
    haveBloom = True
except ImportError:
    try:
        # pybloom
        from pybloom import BloomFilter
        haveBloom = True
    except ImportError:
        pass

# it isn't actually implemented yet so no point in turning it on
haveBloom = False

class BMQueues(object):
    invCleanPeriod = 300
    invInitialCapacity = 50000
    invErrorRate = 0.03

    def __init__(self):
        self.objectsNewToMe = {}
        self.objectsNewToThem = {}
        self.initInvBloom()
        self.initAddrBloom()

    def initInvBloom(self):
        if haveBloom:
            # lock?
            self.invBloom = BloomFilter(capacity=BMQueues.invInitialCapacity,
                                        error_rate=BMQueues.invErrorRate)

    def initAddrBloom(self):
        if haveBloom:
            # lock?
            self.addrBloom = BloomFilter(capacity=BMQueues.invInitialCapacity,
                                         error_rate=BMQueues.invErrorRate)

    def clean(self):
        if self.lastcleaned < time.time() - BMQueues.invCleanPeriod:
            if haveBloom:
                if PendingDownloadQueue().size() == 0:
                    self.initInvBloom()
                self.initAddrBloom()
        else:
            # release memory
            self.objectsNewToMe = self.objectsNewToMe.copy()
            self.objectsNewToThem = self.objectsNewToThem.copy()

    def hasObj(self, hashid):
        if haveBloom:
            return hashid in self.invBloom
        else:
            return hashid in self.objectsNewToMe

    def handleReceivedObj(self, hashid):
        if haveBloom:
            self.invBloom.add(hashid)
        elif hashid in Inventory():
            try:
                del self.objectsNewToThem[hashid]
            except KeyError:
                pass
        else:
            self.objectsNewToMe[hashid] = True

    def hasAddr(self, addr):
        if haveBloom:
            return addr in self.invBloom

    def addAddr(self, hashid):
        if haveBloom:
            self.addrBloom.add(hashid)

# addr sending -> per node upload queue, and flush every minute or so
# inv sending -> if not in bloom, inv immediately, otherwise put into a per node upload queue and flush every minute or so

# no bloom
# - if inv arrives
#   - if we don't have it, add tracking and download queue
#   - if we do have it, remove from tracking
# tracking downloads
# - per node hash of items the node has but we don't
# tracking inv
# - per node hash of items that neither the remote node nor we have
#

