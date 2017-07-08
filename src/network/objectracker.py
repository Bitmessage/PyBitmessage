from Queue import Queue
import time
from threading import RLock

from debug import logger
from inventory import Inventory

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

class ObjectTracker(object):
    invCleanPeriod = 300
    invInitialCapacity = 50000
    invErrorRate = 0.03
    trackingExpires = 3600

    def __init__(self):
        self.objectsNewToMe = {}
        self.objectsNewToMeLock = RLock()
        self.objectsNewToThem = {}
        self.objectsNewToThemLock = RLock()
        self.initInvBloom()
        self.initAddrBloom()
        self.lastCleaned = time.time()

    def initInvBloom(self):
        if haveBloom:
            # lock?
            self.invBloom = BloomFilter(capacity=ObjectTracker.invInitialCapacity,
                                        error_rate=ObjectTracker.invErrorRate)

    def initAddrBloom(self):
        if haveBloom:
            # lock?
            self.addrBloom = BloomFilter(capacity=ObjectTracker.invInitialCapacity,
                                         error_rate=ObjectTracker.invErrorRate)

    def clean(self):
        if self.lastCleaned < time.time() - ObjectTracker.invCleanPeriod:
            if haveBloom:
                # FIXME
                if PendingDownloadQueue().size() == 0:
                    self.initInvBloom()
                self.initAddrBloom()
            else:
                # release memory
                with self.objectsNewToMeLock:
                    tmp = self.objectsNewToMe.copy()
                    self.objectsNewToMe = tmp
                deadline = time.time() - ObjectTracker.trackingExpires
                with self.objectsNewToThemLock:
                    self.objectsNewToThem = {k: v for k, v in self.objectsNewToThem.iteritems() if v >= deadline}
            self.lastCleaned = time.time()

    def hasObj(self, hashid):
        if haveBloom:
            return hashid in self.invBloom
        else:
            return hashid in self.objectsNewToMe

    def handleReceivedInventory(self, hashId):
        if haveBloom:
            self.invBloom.add(hashId)
        try:
            with self.objectsNewToThemLock:
                del self.objectsNewToThem[hashId]
        except KeyError:
            pass
        if hashId not in Inventory():
            with self.objectsNewToMeLock:
                self.objectsNewToMe[hashId] = True

    def hasAddr(self, addr):
        if haveBloom:
            return addr in self.invBloom

    def addAddr(self, hashid):
        if haveBloom:
            self.addrBloom.add(hashid)

# addr sending -> per node upload queue, and flush every minute or so
# inv sending -> if not in bloom, inv immediately, otherwise put into a per node upload queue and flush every minute or so
# data sending -> a simple queue

# no bloom
# - if inv arrives
#   - if we don't have it, add tracking and download queue
#   - if we do have it, remove from tracking
# tracking downloads
# - per node hash of items the node has but we don't
# tracking inv
# - per node hash of items that neither the remote node nor we have
#

