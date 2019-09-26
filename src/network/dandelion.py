"""
src/network/dandelion.py
========================
"""
from collections import namedtuple
from random import choice, sample, expovariate
from threading import RLock
from time import time

import network.connectionpool
import state
from debug import logging
from queues import invQueue
from singleton import Singleton

# randomise routes after 600 seconds
REASSIGN_INTERVAL = 600

# trigger fluff due to expiration
FLUFF_TRIGGER_FIXED_DELAY = 10
FLUFF_TRIGGER_MEAN_DELAY = 30

MAX_STEMS = 2

Stem = namedtuple('Stem', ['child', 'stream', 'timeout'])


@Singleton
class Dandelion():      # pylint: disable=old-style-class
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

    @staticmethod
    def poissonTimeout(start=None, average=0):
        """Generate deadline using Poisson distribution"""
        if start is None:
            start = time()
        if average == 0:
            average = FLUFF_TRIGGER_MEAN_DELAY
        return start + expovariate(1.0 / average) + FLUFF_TRIGGER_FIXED_DELAY

    def addHash(self, hashId, source=None, stream=1):
        """Add inventory vector to dandelion stem"""
        if not state.dandelion:
            return
        with self.lock:
            self.hashMap[hashId] = Stem(
                self.getNodeStem(source),
                stream,
                self.poissonTimeout())

    def setHashStream(self, hashId, stream=1):
        """
        Update stream for inventory vector (as inv/dinv commands don't
        include streams, we only learn this after receiving the object)
        """
        with self.lock:
            if hashId in self.hashMap:
                self.hashMap[hashId] = Stem(
                    self.hashMap[hashId].child,
                    stream,
                    self.poissonTimeout())

    def removeHash(self, hashId, reason="no reason specified"):
        """Switch inventory vector from stem to fluff mode"""
        logging.debug(
            "%s entering fluff mode due to %s.",
            ''.join('%02x' % ord(i) for i in hashId), reason)
        with self.lock:
            try:
                del self.hashMap[hashId]
            except KeyError:
                pass

    def hasHash(self, hashId):
        """Is inventory vector in stem mode?"""
        return hashId in self.hashMap

    def objectChildStem(self, hashId):
        """Child (i.e. next) node for an inventory vector during stem mode"""
        return self.hashMap[hashId].child

    def maybeAddStem(self, connection):
        """
        If we had too few outbound connections, add the current one to the
        current stem list. Dandelion as designed by the authors should
        always have two active stem child connections.
        """
        # fewer than MAX_STEMS outbound connections at last reshuffle?
        with self.lock:
            if len(self.stem) < MAX_STEMS:
                self.stem.append(connection)
                for k in (k for k, v in self.nodeMap.iteritems() if v is None):
                    self.nodeMap[k] = connection
                for k, v in {
                        k: v for k, v in self.hashMap.iteritems()
                        if v.child is None
                }.iteritems():
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
                        k for k, v in self.nodeMap.iteritems() if v == connection
                ):
                    self.nodeMap[k] = None
                for k, v in {
                        k: v for k, v in self.hashMap.iteritems()
                        if v.child == connection
                }.iteritems():
                    self.hashMap[k] = Stem(
                        None, v.stream, self.poissonTimeout())

    def pickStem(self, parent=None):
        """
        Pick a random active stem, but not the parent one
        (the one where an object came from)
        """
        try:
            # pick a random from available stems
            stem = choice(range(len(self.stem)))
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

    def expire(self):
        """Switch expired objects from stem to fluff mode"""
        with self.lock:
            deadline = time()
            toDelete = [
                [v.stream, k, v.child] for k, v in self.hashMap.iteritems()
                if v.timeout < deadline
            ]

            for row in toDelete:
                self.removeHash(row[1], 'expiration')
                invQueue.put(row)
        return toDelete

    def reRandomiseStems(self):
        """Re-shuffle stem mapping (parent <-> child pairs)"""
        with self.lock:
            try:
                # random two connections
                self.stem = sample(
                    connectionpool.BMConnectionPool(
                    ).outboundConnections.values(), MAX_STEMS)
            # not enough stems available
            except ValueError:
                self.stem = connectionpool.BMConnectionPool(
                ).outboundConnections.values()
            self.nodeMap = {}
            # hashMap stays to cater for pending stems
        self.refresh = time() + REASSIGN_INTERVAL
