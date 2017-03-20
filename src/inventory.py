import collections
from threading import current_thread, enumerate as threadingEnumerate, RLock
import Queue
import time

from helper_sql import *
from singleton import Singleton


@Singleton
class Inventory(collections.MutableMapping):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._inventory = {} #of objects (like msg payloads and pubkey payloads) Does not include protocol headers (the first 24 bytes of each packet).
        self.numberOfInventoryLookupsPerformed = 0
        self._streams = collections.defaultdict(set) # key = streamNumer, value = a set which holds the inventory object hashes that we are aware of. This is used whenever we receive an inv message from a peer to check to see what items are new to us. We don't delete things out of it; instead, the singleCleaner thread clears and refills it every couple hours.
        self.lock = RLock() # Guarantees that two receiveDataThreads don't receive and process the same message concurrently (probably sent by a malicious individual)
        self.InventoryItem = collections.namedtuple('InventoryItem', 'type stream payload expires tag')

    def __contains__(self, hash):
        with self.lock:
            self.numberOfInventoryLookupsPerformed += 1
            if hash in self._inventory:
                return True
            return bool(sqlQuery('SELECT 1 FROM inventory WHERE hash=?', hash))

    def __getitem__(self, hash):
        with self.lock:
            if hash in self._inventory:
                return self._inventory[hash]
            rows = sqlQuery('SELECT objecttype, streamnumber, payload, expirestime, tag FROM inventory WHERE hash=?', hash)
            if not rows:
                raise KeyError(hash)
            return self.InventoryItem(*rows[0])

    def __setitem__(self, hash, value):
        with self.lock:
            value = self.InventoryItem(*value)
            self._inventory[hash] = value
            self._streams[value.stream].add(hash)

    def __delitem__(self, hash):
        raise NotImplementedError

    def __iter__(self):
        with self.lock:
            hashes = self._inventory.keys()[:]
            hashes += (x for x, in sqlQuery('SELECT hash FROM inventory'))
            return hashes.__iter__()

    def __len__(self):
        with self.lock:
            return len(self._inventory) + sqlQuery('SELECT count(*) FROM inventory')[0][0]

    def by_type_and_tag(self, type, tag):
        with self.lock:
            values = [value for value in self._inventory.values() if value.type == type and value.tag == tag]
            values += (self.InventoryItem(*value) for value in sqlQuery('SELECT objecttype, streamnumber, payload, expirestime, tag FROM inventory WHERE objecttype=? AND tag=?', type, tag))
            return values

    def hashes_by_stream(self, stream):
        with self.lock:
            return self._streams[stream]

    def unexpired_hashes_by_stream(self, stream):
        with self.lock:
            t = int(time.time())
            hashes = [x for x, value in self._inventory.items() if value.stream == stream and value.expires > t]
            hashes += (payload for payload, in sqlQuery('SELECT hash FROM inventory WHERE streamnumber=? AND expirestime>?', stream, t))
            return hashes

    def flush(self):
        with self.lock: # If you use both the inventoryLock and the sqlLock, always use the inventoryLock OUTSIDE of the sqlLock.
            with SqlBulkExecute() as sql:
                for objectHash, value in self._inventory.items():
                    sql.execute('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)', objectHash, *value)
                self._inventory.clear()

    def clean(self):
        with self.lock:
            sqlExecute('DELETE FROM inventory WHERE expirestime<?',int(time.time()) - (60 * 60 * 3))
            self._streams.clear()
            for objectHash, value in self.items():
                self._streams[value.stream].add(objectHash)


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
