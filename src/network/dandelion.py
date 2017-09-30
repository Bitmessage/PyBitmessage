from random import choice
from threading import RLock

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
        with self.lock:
            self.stem[hashId] = choice(stems)
            self.source[hashId] = source
            self.timeouts[hashId] = time.time()

    def remove(self, hashId):
        with self.lock:
            try:
                del self.stem[hashId]
                del self.source[hashId]
                del self.timeouts[hashId]
            except KeyError:
                pass
