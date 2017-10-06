from random import choice
from threading import RLock
from time import time

from bmconfigparser import BMConfigParser
from singleton import Singleton

# randomise routes after 600 seconds
REASSIGN_INTERVAL = 600
FLUFF_TRIGGER_TIMEOUT = 300

@Singleton
class DandelionStems():
    def __init__(self):
        self.stem = {}
        self.source = {}
        self.timeouts = {}
        self.lock = RLock()

    def add(self, hashId, source, stems):
        if BMConfigParser().safeGetInt('network', 'dandelion') == 0:
            return
        with self.lock:
            try:
                self.stem[hashId] = choice(stems)
            except IndexError:
                self.stem = None
            self.source[hashId] = source
            self.timeouts[hashId] = time()

    def remove(self, hashId):
        with self.lock:
            try:
                del self.stem[hashId]
                del self.source[hashId]
                del self.timeouts[hashId]
            except KeyError:
                pass
