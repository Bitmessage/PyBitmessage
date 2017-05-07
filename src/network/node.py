import time

from inventory import PendingDownloadQueue

try:
    # pybloomfiltermmap
    from pybloomfilter import BloomFilter
except ImportError:
    try:
        # pybloom
        from pybloom import BloomFilter
    except ImportError:
        # bundled pybloom
        from fallback.pybloom import BloomFilter


class Node(object):
    invCleanPeriod = 300
    invInitialCapacity = 50000
    invErrorRate = 0.03

    def __init__(self):
        self.initInvBloom()
        self.initAddrBloom()

    def initInvBloom(self):
        # lock?
        self.invBloom = BloomFilter(capacity=Node.invInitialCapacity,
                                    error_rate=Node.invErrorRate)

    def initAddrBloom(self):
        # lock?
        self.addrBloom = BloomFilter(capacity=Node.invInitialCapacity,
                                     error_rate=Node.invErrorRate)

    def cleanBloom(self):
        if self.lastcleaned < time.time() - Node.invCleanPeriod:
            if PendingDownloadQueue().size() == 0:
                self.initInvBloom()
            self.initAddrBloom()

    def hasInv(self, hashid):
        return hashid in self.invBloom

    def addInv(self, hashid):
        self.invBloom.add(hashid)

    def hasAddr(self, hashid):
        return hashid in self.invBloom

    def addInv(self, hashid):
        self.invBloom.add(hashid)

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

