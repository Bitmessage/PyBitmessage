from random import choice, shuffle
from threading import RLock
from time import time

from bmconfigparser import BMConfigParser
from singleton import Singleton

# randomise routes after 600 seconds
REASSIGN_INTERVAL = 600
FLUFF_TRIGGER_TIMEOUT = 300
MAX_STEMS = 2

@Singleton
class Dandelion():
    def __init__(self):
        self.stem = []
        self.nodeMap = {}
        self.hashMap = {}
        self.fluff = {}
        self.timeout = {}
        self.refresh = time() + REASSIGN_INTERVAL
        self.lock = RLock()

    def addHash(self, hashId, source):
        if BMConfigParser().safeGetInt('network', 'dandelion') == 0:
            return
        with self.lock:
            self.hashMap[hashId] = self.getNodeStem(source)
            self.timeout[hashId] = time() + FLUFF_TRIGGER_TIMEOUT

    def removeHash(self, hashId):
        with self.lock:
            try:
                del self.hashMap[hashId]
            except KeyError:
                pass
            try:
                del self.timeout[hashId]
            except KeyError:
                pass
            try:
                del self.fluff[hashId]
            except KeyError:
                pass

    def fluffTrigger(self, hashId):
        with self.lock:
            self.fluff[hashId] = None

    def maybeAddStem(self, connection):
        # fewer than MAX_STEMS outbound connections at last reshuffle?
        with self.lock:
            if len(self.stem) < MAX_STEMS:
                self.stem.append(connection)
                # active mappings pointing nowhere
                for k in (k for k, v in self.nodeMap.iteritems() if self.nodeMap[k] is None):
                    self.nodeMap[k] = connection
                for k in (k for k, v in self.hashMap.iteritems() if self.hashMap[k] is None):
                    self.hashMap[k] = connection

    def maybeRemoveStem(self, connection):
        # is the stem active?
        with self.lock:
            if connection in self.stem:
                self.stem.remove(connection)
                # active mappings to pointing to the removed node
                for k in (k for k, v in self.nodeMap.iteritems() if self.nodeMap[k] == connection):
                    self.nodeMap[k] = None
                for k in (k for k, v in self.hashMap.iteritems() if self.hashMap[k] == connection):
                    self.hashMap[k] = None
            if len(self.stem) < MAX_STEMS:
                self.stem.append(connection)

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
                self.nodeMap[node] = self.pickStem()
                return self.nodeMap[node]

    def getHashStem(self, hashId):
        with self.lock:
            return self.hashMap[hashId]

    def expire(self):
        with self.lock:
            deadline = time()
            toDelete = [k for k, v in self.hashMap.iteritems() if self.timeout[k] < deadline]
            for k in toDelete:
                del self.timeout[k]
                del self.hashMap[k]

    def reRandomiseStems(self, connections):
        shuffle(connections)
        with self.lock:
            # random two connections
            self.stem = connections[:MAX_STEMS]
            self.nodeMap = {}
            # hashMap stays to cater for pending stems
        self.refresh = time() + REASSIGN_INTERVAL
