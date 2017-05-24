from collections import namedtuple
import Queue
import random
from threading import current_thread, enumerate as threadingEnumerate, RLock
import time

#from helper_sql import *
from singleton import Singleton

UploadElem = namedtuple("UploadElem", "stream identifier")

class UploadQueueDeadlineException(Exception):
    pass


class UploadQueue(object):
    queueCount = 10

    def __init__(self):
        self.queue = []
        self.lastGet = 0
        self.getIterator = 0
        for i in range(UploadQueue.queueCount):
            self.queue.append([])

    def put(self, item):
        self.queue[random.randrange(0, UploadQueue.queueCount)].append(item)

    def get(self):
        i = UploadQueue.queueCount
        retval = []
        while self.lastGet < time.time() - 1 and i > 0:
            if len(self.queue) > 0:
                retval.extend(self.queue[self.getIterator])
                self.queue[self.getIterator] = []
            self.lastGet += 1
            # only process each queue once
            i -= 1
            self.getIterator = (self.getIterator + 1) % UploadQueue.queueCount
        if self.lastGet < time.time() - 1:
            self.lastGet = time.time()
        return retval

    def streamElems(self, stream):
        retval = {}
        for q in self.queue:
            for elem in q:
                if elem.stream == stream:
                    retval[elem.identifier] = True
        return retval

    def len(self):
        retval = 0
        for i in range(UploadQueue.queueCount):
            retval += len(self.queue[i])
        return retval

    def stop(self):
        for i in range(UploadQueue.queueCount):
            self.queue[i] = []


@Singleton
class AddrUploadQueue(UploadQueue):
    pass


@Singleton
class ObjUploadQueue(UploadQueue):
    pass
