import time
from threading import RLock

from inventory import Inventory
import network.connectionpool
from network.dandelion import Dandelion
from randomtrackingdict import RandomTrackingDict
from state import missingObjects

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
    initialTimeOffset = 60

    def __init__(self):
        self.objectsNewToMe = RandomTrackingDict()
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
                if len(missingObjects) == 0:
                    self.initInvBloom()
                self.initAddrBloom()
            else:
                # release memory
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
        if hashId not in missingObjects:
            missingObjects[hashId] = time.time()
        self.objectsNewToMe[hashId] = True

    def handleReceivedObject(self, streamNumber, hashid):
        for i in network.connectionpool.BMConnectionPool().inboundConnections.values() + network.connectionpool.BMConnectionPool().outboundConnections.values():
            if not i.fullyEstablished:
                continue
            try:
                del i.objectsNewToMe[hashid]
            except KeyError:
                if streamNumber in i.streams and \
                    (not Dandelion().hasHash(hashid) or \
                    Dandelion().objectChildStem(hashid) == i):
                    with i.objectsNewToThemLock:
                        i.objectsNewToThem[hashid] = time.time()
                    # update stream number, which we didn't have when we just received the dinv
                    # also resets expiration of the stem mode
                    Dandelion().setHashStream(hashid, streamNumber)

            if i == self:
                try:
                    with i.objectsNewToThemLock:
                        del i.objectsNewToThem[hashid]
                except KeyError:
                    pass

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
