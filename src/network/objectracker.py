"""
Module for tracking objects
"""
import time
from threading import RLock
from binascii import hexlify

import state
import network.connectionpool as connectionpool
from randomtrackingdict import RandomTrackingDict

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

# tracking pending downloads globally, for stats
missingObjects = {}


class ObjectTracker(object):
    """Object tracker mixin"""
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
        """Init bloom filter for tracking. WIP."""
        if haveBloom:
            # lock?
            self.invBloom = BloomFilter(
                capacity=ObjectTracker.invInitialCapacity,
                error_rate=ObjectTracker.invErrorRate)

    def initAddrBloom(self):
        """Init bloom filter for tracking addrs, WIP.
        This either needs to be moved to addrthread.py or removed."""
        if haveBloom:
            # lock?
            self.addrBloom = BloomFilter(
                capacity=ObjectTracker.invInitialCapacity,
                error_rate=ObjectTracker.invErrorRate)

    def clean(self):
        """Clean up tracking to prevent memory bloat"""
        if self.lastCleaned < time.time() - ObjectTracker.invCleanPeriod:
            if haveBloom:
                if missingObjects == 0:
                    self.initInvBloom()
                self.initAddrBloom()
            else:
                # release memory
                deadline = time.time() - ObjectTracker.trackingExpires
                with self.objectsNewToThemLock:
                    self.objectsNewToThem = {
                        k: v
                        for k, v in self.objectsNewToThem.items()
                        if v >= deadline}
            self.lastCleaned = time.time()

    def hasObj(self, hashid):
        """Do we already have object?"""
        if haveBloom:
            return hashid in self.invBloom
        return hashid in self.objectsNewToMe

    def handleReceivedInventory(self, hashId):
        """Handling received inventory"""
        hex_hash = hexlify(hashId).decode('ascii')
        if haveBloom:
            self.invBloom.add(hex_hash)
        try:
            with self.objectsNewToThemLock:
                del self.objectsNewToThem[hex_hash]
        except KeyError:
            pass
        if hex_hash not in missingObjects:
            missingObjects[hex_hash] = time.time()
        self.objectsNewToMe[hashId] = True

    def handleReceivedObject(self, streamNumber, hashid):
        """Handling received object"""
        hex_hash = hexlify(hashid).decode('ascii')
        for i in connectionpool.pool.connections():
            if not i.fullyEstablished:
                continue
            try:
                del i.objectsNewToMe[hashid]
            except KeyError:
                if streamNumber in i.streams and (
                        not state.Dandelion.hasHash(hashid)
                        or state.Dandelion.objectChildStem(hashid) == i):
                    with i.objectsNewToThemLock:
                        i.objectsNewToThem[hex_hash] = time.time()
                    # update stream number,
                    # which we didn't have when we just received the dinv
                    # also resets expiration of the stem mode
                    state.Dandelion.setHashStream(hashid, streamNumber)

            if i == self:
                try:
                    with i.objectsNewToThemLock:
                        del i.objectsNewToThem[hex_hash]
                except KeyError:
                    pass
        self.objectsNewToMe.setLastObject()

    def hasAddr(self, addr):
        """WIP, should be moved to addrthread.py or removed"""
        if haveBloom:
            return addr in self.invBloom
        return None

    def addAddr(self, hashid):
        """WIP, should be moved to addrthread.py or removed"""
        if haveBloom:
            self.addrBloom.add(hashid)
