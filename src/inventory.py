import collections
from importlib import import_module
from threading import current_thread, enumerate as threadingEnumerate, RLock
import Queue
import time
import sys

from bmconfigparser import BMConfigParser
from helper_sql import *
from singleton import Singleton

# TODO make this dynamic, and watch out for frozen, like with messagetypes
import storage.sqlite
import storage.filesystem

@Singleton
class Inventory():
    def __init__(self):
        #super(self.__class__, self).__init__()
        self._moduleName = BMConfigParser().safeGet("inventory", "storage")
        #import_module("." + self._moduleName, "storage")
        #import_module("storage." + self._moduleName)
        self._className = "storage." + self._moduleName + "." + self._moduleName.title() + "Inventory"
        self._inventoryClass = eval(self._className)
        self._realInventory = self._inventoryClass()
        self.numberOfInventoryLookupsPerformed = 0

    # cheap inheritance copied from asyncore
    def __getattr__(self, attr):
        try:
            if attr == "__contains__":
                self.numberOfInventoryLookupsPerformed += 1
            realRet = getattr(self._realInventory, attr)
        except AttributeError:
            raise AttributeError("%s instance has no attribute '%s'" %(self.__class__.__name__, attr))
        else:
            return realRet


class PendingDownloadQueue(Queue.Queue):
# keep a track of objects that have been advertised to us but we haven't downloaded them yet
    maxWait = 300

    def __init__(self, maxsize=0):
        Queue.Queue.__init__(self, maxsize)
        self.stopped = False
        self.pending = {}
        self.lock = RLock()

    def task_done(self, hashId):
        Queue.Queue.task_done(self)
        try:
            with self.lock:
                del self.pending[hashId]
        except KeyError:
            pass

    def get(self, block=True, timeout=None):
        retval = Queue.Queue.get(self, block, timeout)
        # no exception was raised
        if not self.stopped:
            with self.lock:
                self.pending[retval] = time.time()
        return retval

    def clear(self):
        with self.lock:
            newPending = {}
            for hashId in self.pending:
                if self.pending[hashId] + PendingDownloadQueue.maxWait > time.time():
                    newPending[hashId] = self.pending[hashId]
            self.pending = newPending

    @staticmethod
    def totalSize():
        size = 0
        for thread in threadingEnumerate():
            if thread.isAlive() and hasattr(thread, 'downloadQueue'):
                size += thread.downloadQueue.qsize() + len(thread.downloadQueue.pending)
        return size

    @staticmethod
    def stop():
        for thread in threadingEnumerate():
            if thread.isAlive() and hasattr(thread, 'downloadQueue'):
                thread.downloadQueue.stopped = True
                with thread.downloadQueue.lock:
                    thread.downloadQueue.pending = {}


class PendingUploadDeadlineException(Exception):
    pass


@Singleton
class PendingUpload(object):
# keep a track of objects that we have created but haven't distributed yet
    def __init__(self):
        super(self.__class__, self).__init__()
        self.lock = RLock()
        self.hashes = {}
        # end by this time in any case
        self.deadline = 0
        self.maxLen = 0
        # during shutdown, wait up to 20 seconds to finish uploading
        self.shutdownWait = 20
        # forget tracking objects after 60 seconds
        self.objectWait = 60
        # wait 10 seconds between clears
        self.clearDelay = 10
        self.lastCleared = time.time()

    def add(self, objectHash = None):
        with self.lock:
            # add a new object into existing thread lists
            if objectHash:
                if objectHash not in self.hashes:
                    self.hashes[objectHash] = {'created': time.time(), 'sendCount': 0, 'peers': []}
                for thread in threadingEnumerate():
                    if thread.isAlive() and hasattr(thread, 'peer') and \
                        thread.peer not in self.hashes[objectHash]['peers']:
                        self.hashes[objectHash]['peers'].append(thread.peer)
            # add all objects into the current thread
            else:
                for objectHash in self.hashes:
                    if current_thread().peer not in self.hashes[objectHash]['peers']:
                        self.hashes[objectHash]['peers'].append(current_thread().peer)

    def len(self):
        self.clearHashes()
        with self.lock:
            return sum(1
                for x in self.hashes if (self.hashes[x]['created'] + self.objectWait < time.time() or
                    self.hashes[x]['sendCount'] == 0))

    def _progress(self):
        with self.lock:
            return float(sum(len(self.hashes[x]['peers'])
                for x in self.hashes if (self.hashes[x]['created'] + self.objectWait < time.time()) or
                    self.hashes[x]['sendCount'] == 0))

    def progress(self, raiseDeadline=True):
        if self.maxLen < self._progress():
            self.maxLen = self._progress()
        if self.deadline < time.time():
            if self.deadline > 0 and raiseDeadline:
                raise PendingUploadDeadlineException
            self.deadline = time.time() + 20
        try:
            return 1.0 - self._progress() / self.maxLen
        except ZeroDivisionError:
            return 1.0

    def clearHashes(self, objectHash=None):
        if objectHash is None:
            if self.lastCleared > time.time() - self.clearDelay:
                return
            objects = self.hashes.keys()
        else:
            objects = objectHash, 
        with self.lock:
            for i in objects:
                try:
                    if self.hashes[i]['sendCount'] > 0 and (
                        len(self.hashes[i]['peers']) == 0 or 
                        self.hashes[i]['created'] + self.objectWait < time.time()):
                        del self.hashes[i]
                except KeyError:
                    pass
        self.lastCleared = time.time()
    
    def delete(self, objectHash=None):
        if not hasattr(current_thread(), 'peer'):
            return
        if objectHash is None:
            return
        with self.lock:
            try:
                if objectHash in self.hashes and current_thread().peer in self.hashes[objectHash]['peers']:
                    self.hashes[objectHash]['sendCount'] += 1
                    self.hashes[objectHash]['peers'].remove(current_thread().peer)
            except KeyError:
                pass
        self.clearHashes(objectHash)

    def stop(self):
        with self.lock:
            self.hashes = {}

    def threadEnd(self):
        with self.lock:
            for objectHash in self.hashes:
                try:
                    if current_thread().peer in self.hashes[objectHash]['peers']:
                        self.hashes[objectHash]['peers'].remove(current_thread().peer)
                except KeyError:
                    pass
        self.clearHashes()
