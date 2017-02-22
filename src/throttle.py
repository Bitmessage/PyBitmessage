import math
import threading
import time

from bmconfigparser import BMConfigParser
from singleton import Singleton
import state

class Throttle(object):
    minChunkSize = 4096
    maxChunkSize = 131072

    def __init__(self, limit=0):
        self.limit = limit
        self.speed = 0
        self.chunkSize = Throttle.maxChunkSize
        self.txTime = int(time.time())
        self.txLen = 0
        self.total = 0
        self.timer = threading.Event()
        self.lock = threading.RLock()
        self.resetChunkSize()

    def recalculate(self):
        with self.lock:
            now = int(time.time())
            if now > self.txTime:
                self.speed = self.txLen / (now - self.txTime)
                self.txLen -= self.limit * (now - self.txTime)
                self.txTime = now
                if self.txLen < 0 or self.limit == 0:
                    self.txLen = 0

    def wait(self, dataLen):
        with self.lock:
            self.txLen += dataLen
            self.total += dataLen
        while state.shutdown == 0:
            self.recalculate()
            if self.limit == 0:
                break
            if self.txLen < self.limit:
                break
            self.timer.wait(0.2)

    def getSpeed(self):
        self.recalculate()
        return self.speed

    def resetChunkSize(self):
        with self.lock:
            # power of two smaller or equal to speed limit
            try:
                self.chunkSize = int(math.pow(2, int(math.log(self.limit,2))))
            except ValueError:
                self.chunkSize = Throttle.maxChunkSize
            # range check
            if self.chunkSize < Throttle.minChunkSize:
                self.chunkSize = Throttle.minChunkSize
            elif self.chunkSize > Throttle.maxChunkSize:
                self.chunkSize = Throttle.maxChunkSize

@Singleton
class SendThrottle(Throttle):
    def __init__(self):
        Throttle.__init__(self, BMConfigParser().safeGetInt('bitmessagesettings', 'maxuploadrate')*1024)
    
    def resetLimit(self):
        with self.lock:
            self.limit = BMConfigParser().safeGetInt('bitmessagesettings', 'maxuploadrate')*1024
        Throttle.resetChunkSize(self)

@Singleton
class ReceiveThrottle(Throttle):
    def __init__(self):
        Throttle.__init__(self, BMConfigParser().safeGetInt('bitmessagesettings', 'maxdownloadrate')*1024)

    def resetLimit(self):
        with self.lock:
            self.limit = BMConfigParser().safeGetInt('bitmessagesettings', 'maxdownloadrate')*1024
        Throttle.resetChunkSize(self)
