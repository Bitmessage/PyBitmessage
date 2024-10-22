"""
Dandelion class definition, tracks stages
"""
import logging
from collections import namedtuple
from random import choice, expovariate, sample
from threading import RLock
from time import time
import six
from binascii import hexlify


# randomise routes after 600 seconds
REASSIGN_INTERVAL = 600

# trigger fluff due to expiration
FLUFF_TRIGGER_FIXED_DELAY = 10
FLUFF_TRIGGER_MEAN_DELAY = 30

MAX_STEMS = 2

Stem = namedtuple('Stem', ['child', 'stream', 'timeout'])

logger = logging.getLogger('default')


class Dandelion:  # pylint: disable=old-style-class
    """Dandelion class for tracking stem/fluff stages."""
    def __init__(self):
        # currently assignable child stems
        self.stem = []
        # currently assigned parent <-> child mappings
        self.nodeMap = {}
        # currently existing objects in stem mode
        self.hashMap = {}
        # when to rerandomise routes
        self.refresh = time() + REASSIGN_INTERVAL
        self.lock = RLock()
        self.enabled = None
        self.pool = None

    @staticmethod
    def poissonTimeout(start=None, average=0):
        """Generate deadline using Poisson distribution"""
        if start is None:
            start = time()
        if average == 0:
            average = FLUFF_TRIGGER_MEAN_DELAY
        return start + expovariate(1.0 / average) + FLUFF_TRIGGER_FIXED_DELAY

    def init_pool(self, pool):
        """pass pool instance"""
        self.pool = pool

    def init_dandelion_enabled(self, config):
        """Check if Dandelion is enabled and set value in enabled attribute"""
        dandelion_enabled = config.safeGetInt('network', 'dandelion')
        # dandelion requires outbound connections, without them,
        # stem objects will get stuck forever
        if not config.safeGetBoolean(
                'bitmessagesettings', 'sendoutgoingconnections'):
            dandelion_enabled = 0
        self.enabled = dandelion_enabled

    def addHash(self, hashId, source=None, stream=1):
        """Add inventory vector to dandelion stem return status of dandelion enabled"""
        assert self.enabled is not None
        with self.lock:
            self.hashMap[bytes(hashId)] = Stem(
                self.getNodeStem(source),
                stream,
                self.poissonTimeout())

    def setHashStream(self, hashId, stream=1):
        """
        Update stream for inventory vector (as inv/dinv commands don't
        include streams, we only learn this after receiving the object)
        """
        with self.lock:
            hashId_bytes = bytes(hashId)
            if hashId_bytes in self.hashMap:
                self.hashMap[hashId_bytes] = Stem(
                    self.hashMap[hashId_bytes].child,
                    stream,
                    self.poissonTimeout())

    def removeHash(self, hashId, reason="no reason specified"):
        """Switch inventory vector from stem to fluff mode"""
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                '%s entering fluff mode due to %s.',
                hexlify(hashId), reason)
        with self.lock:
            try:
                del self.hashMap[bytes(hashId)]
            except KeyError:
                pass

    def hasHash(self, hashId):
        """Is inventory vector in stem mode?"""
        return bytes(hashId) in self.hashMap

    def objectChildStem(self, hashId):
        """Child (i.e. next) node for an inventory vector during stem mode"""
        return self.hashMap[bytes(hashId)].child

    def maybeAddStem(self, connection, invQueue):
        """
        If we had too few outbound connections, add the current one to the
        current stem list. Dandelion as designed by the authors should
        always have two active stem child connections.
        """
        # fewer than MAX_STEMS outbound connections at last reshuffle?
        with self.lock:
            if len(self.stem) < MAX_STEMS:
                self.stem.append(connection)
                for k in (k for k, v in six.iteritems(self.nodeMap) if v is None):
                    self.nodeMap[k] = connection
                for k, v in six.iteritems({
                        k: v for k, v in six.iteritems(self.hashMap)
                        if v.child is None
                }):
                    self.hashMap[k] = Stem(
                        connection, v.stream, self.poissonTimeout())
                    invQueue.put((v.stream, k, v.child))

    def maybeRemoveStem(self, connection):
        """
        Remove current connection from the stem list (called e.g. when
        a connection is closed).
        """
        # is the stem active?
        with self.lock:
            if connection in self.stem:
                self.stem.remove(connection)
                # active mappings to pointing to the removed node
                for k in (
                        k for k, v in six.iteritems(self.nodeMap)
                        if v == connection
                ):
                    self.nodeMap[k] = None
                for k, v in six.iteritems({
                        k: v for k, v in six.iteritems(self.hashMap)
                        if v.child == connection
                }):
                    self.hashMap[k] = Stem(
                        None, v.stream, self.poissonTimeout())

    def pickStem(self, parent=None):
        """
        Pick a random active stem, but not the parent one
        (the one where an object came from)
        """
        try:
            # pick a random from available stems
            stem = choice(range(len(self.stem)))  # nosec B311
            if self.stem[stem] == parent:
                # one stem available and it's the parent
                if len(self.stem) == 1:
                    return None
                # else, pick the other one
                return self.stem[1 - stem]
            # all ok
            return self.stem[stem]
        except IndexError:
            # no stems available
            return None

    def getNodeStem(self, node=None):
        """
        Return child stem node for a given parent stem node
        (the mapping is static for about 10 minutes, then it reshuffles)
        """
        with self.lock:
            try:
                return self.nodeMap[node]
            except KeyError:
                self.nodeMap[node] = self.pickStem(node)
                return self.nodeMap[node]

    def expire(self, invQueue):
        """Switch expired objects from stem to fluff mode"""
        with self.lock:
            deadline = time()
            toDelete = [
                [v.stream, k, v.child] for k, v in six.iteritems(self.hashMap)
                if v.timeout < deadline
            ]

            for row in toDelete:
                self.removeHash(row[1], 'expiration')
                invQueue.put(row)
        return toDelete

    def reRandomiseStems(self):
        """Re-shuffle stem mapping (parent <-> child pairs)"""
        assert self.pool is not None
        if self.refresh > time():
            return

        with self.lock:
            try:
                # random two connections
                self.stem = sample(
                    sorted(self.pool.outboundConnections.values()), MAX_STEMS)
            # not enough stems available
            except ValueError:
                self.stem = list(self.pool.outboundConnections.values())
            self.nodeMap = {}
            # hashMap stays to cater for pending stems
        self.refresh = time() + REASSIGN_INTERVAL
