import random
from threading import RLock

import protocol
from singleton import Singleton

# randomise routes after 600 seconds
REASSIGN_INTERVAL = 600
FLUFF_TRIGGER_TIMEOUT = 300

@Singleton
class DandelionStems():
    def __init__(self):
        self.stem = {}
        self.timeouts = {}
        self.lock = RLock()

    def add(self, hashId, stems):
        with self.lock:
            self.stem[hashId] = stems
            self.timeouts[hashId] = time.time()

    def remove(self, hashId):
        with self.lock:
            try:
                del self.stem[hashId]
                del self.timeouts[hashId]
            except KeyError:
                pass
