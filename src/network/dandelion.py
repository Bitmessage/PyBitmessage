from collections import namedtuple
from random import choice, sample, expovariate
from threading import RLock
from time import time

from bmconfigparser import BMConfigParser
import network.connectionpool
from debug import logging
from queues import invQueue
from singleton import Singleton
import state

# randomise routes after 600 seconds
REASSIGN_INTERVAL = 600

# trigger fluff due to expiration
FLUFF_TRIGGER_FIXED_DELAY = 10
FLUFF_TRIGGER_MEAN_DELAY = 30

MAX_STEMS = 2

Stem = namedtuple('Stem', ['child', 'stream', 'timeout'])

@Singleton
class Dandelion():
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

    def poissonTimeout(self, start=None, average=0):
        if start is None:
            start = time()
        if average == 0:
            average = FLUFF_TRIGGER_MEAN_DELAY
        return start + expovariate(1.0/average) + FLUFF_TRIGGER_FIXED_DELAY

    def addHash(self, hashId, source=None, stream=1):
        if not state.dandelion:
            return
        with self.lock:
            self.hashMap[hashId] = Stem(
                    self.getNodeStem(source),
                    stream,
                    self.poissonTimeout())

    def setHashStream(self, hashId, stream=1):
        with self.lock:
            if hashId in self.hashMap:
                self.hashMap[hashId] = Stem(
                        self.hashMap[hashId].child,
                        stream,
                        self.poissonTimeout())

    def removeHash(self, hashId, reason="no reason specified"):
        logging.debug("%s entering fluff mode due to %s.", ''.join('%02x'%ord(i) for i in hashId), reason)
        with self.lock:
            try:
                del self.hashMap[hashId]
            except KeyError:
                pass

    def hasHash(self, hashId):
        return hashId in self.hashMap

    def objectChildStem(self, hashId):
        return self.hashMap[hashId].child

    def maybeAddStem(self, connection):
        # fewer than MAX_STEMS outbound connections at last reshuffle?
        with self.lock:
            if len(self.stem) < MAX_STEMS:
                self.stem.append(connection)
                for k in (k for k, v in self.nodeMap.iteritems() if v is None):
                    self.nodeMap[k] = connection
                for k, v in {k: v for k, v in self.hashMap.iteritems() if v.child is None}.iteritems():
                    self.hashMap[k] = Stem(connection, v.stream, self.poissonTimeout())
                    invQueue.put((v.stream, k, v.child))


    def maybeRemoveStem(self, connection):
        # is the stem active?
        with self.lock:
            if connection in self.stem:
                self.stem.remove(connection)
                # active mappings to pointing to the removed node
                for k in (k for k, v in self.nodeMap.iteritems() if v == connection):
                    self.nodeMap[k] = None
                for k, v in {k: v for k, v in self.hashMap.iteritems() if v.child == connection}.iteritems():
                    self.hashMap[k] = Stem(None, v.stream, self.poissonTimeout())

    def pickStem(self, parent=None):
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
        with self.lock:
            try:
                return self.nodeMap[node]
            except KeyError:
                self.nodeMap[node] = self.pickStem(node)
                return self.nodeMap[node]

    def expire(self):
        with self.lock:
            deadline = time()
            # only expire those that have a child node, i.e. those without a child not will stick around
            toDelete = [[v.stream, k, v.child] for k, v in self.hashMap.iteritems() if v.timeout < deadline and v.child]
            for row in toDelete:
                self.removeHash(row[1], 'expiration')
                invQueue.put((row[0], row[1], row[2]))

    def reRandomiseStems(self):
        with self.lock:
            try:
                # random two connections
                self.stem = sample(network.connectionpool.BMConnectionPool().outboundConnections.values(), MAX_STEMS)
            # not enough stems available
            except ValueError:
                self.stem = network.connectionpool.BMConnectionPool().outboundConnections.values()
            self.nodeMap = {}
            # hashMap stays to cater for pending stems
        self.refresh = time() + REASSIGN_INTERVAL
