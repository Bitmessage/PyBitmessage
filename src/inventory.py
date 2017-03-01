import collections
from threading import current_thread, enumerate as threadingEnumerate, RLock
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
        PendingDownload().delete(hash)

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


@Singleton
class PendingDownload(object):
# keep a track of objects that have been advertised to us but we haven't downloaded them yet
    def __init__(self):
        super(self.__class__, self).__init__()
        self.lock = RLock()
        self.hashes = {}
        self.stopped = False
        # don't request the same object more frequently than this
        self.frequency = 60
        # after requesting and not receiving an object more than this times, consider it expired
        self.maxRequestCount = 3
        self.pending = {}

    def add(self, objectHash):
        if self.stopped:
            return
        with self.lock:
            if objectHash not in self.hashes:
                self.hashes[objectHash] = {'peers':[], 'requested':0, 'requestedCount':0}
            self.hashes[objectHash]['peers'].append(current_thread().peer)

    def addPending(self, objectHash=None):
        if self.stopped:
            return
        if current_thread().peer not in self.pending:
            self.pending[current_thread().peer] = {'objects':[], 'requested':0, 'received':0}
        if objectHash not in self.pending[current_thread().peer]['objects'] and not objectHash is None:
            self.pending[current_thread().peer]['objects'].append(objectHash)
        self.pending[current_thread().peer]['requested'] = time.time()

    def len(self):
        with self.lock:
            return sum(1 for x in self.hashes.values() if len(x) > 0)

    def pull(self, count=1):
        if count < 1:
            raise ValueError("Must be at least one")
        objectHashes = []
        unreachableObjects = []
        if self.stopped:
            return objectHashes
        start = time.time()
        try:
            for objectHash in self.hashes.keys():
                with self.lock:
                    if len(objectHashes) >= count:
                        break
                    if current_thread().peer not in self.pending:
                        self.addPending()
                    if (self.pending[current_thread().peer]['requested'] >= time.time() - self.frequency or \
                        self.pending[current_thread().peer]['received'] >= time.time() - self.frequency) and \
                        len(self.pending[current_thread().peer]['objects']) >= count:
                        break
                    if len(self.hashes[objectHash]['peers']) == 0:
                        unreachableObjects.append(objectHash)
                        continue
                    # requested too long ago or not at all from any thread
                    if self.hashes[objectHash]['requested'] < time.time() - self.frequency:
                        # ready requested from this thread but haven't received yet
                        if objectHash in self.pending[current_thread().peer]['objects']:
                            # if still sending or receiving, request next
                            if self.pending[current_thread().peer]['received'] >= time.time() - self.frequency or \
                                self.pending[current_thread().peer]['requested'] >= time.time() - self.frequency:
                                continue
                            # haven't requested or received anything recently, re-request (i.e. continue)
                        # the current node doesn't have the object
                        elif current_thread().peer not in self.hashes[objectHash]['peers']:
                            continue
                        # already requested too many times, remove all signs of this object
                        if self.hashes[objectHash]['requestedCount'] >= self.maxRequestCount:
                            del self.hashes[objectHash]
                            for thread in self.pending.keys():
                                if objectHash in self.pending[thread]['objects']:
                                    self.pending[thread]['objects'].remove(objectHash)
                            continue
                        # all ok, request
                        objectHashes.append(objectHash)
                        self.hashes[objectHash]['requested'] = time.time()
                        self.hashes[objectHash]['requestedCount'] += 1
                        self.pending[current_thread().peer]['requested'] = time.time()
                        self.addPending(objectHash)
        except (RuntimeError, KeyError, ValueError):
            # the for cycle sometimes breaks if you remove elements
            pass
        for objectHash in unreachableObjects:
            with self.lock:
                if objectHash in self.hashes:
                    del self.hashes[objectHash]
#        logger.debug("Pull took %.3f seconds", time.time() - start)
        return objectHashes

    def delete(self, objectHash):
        with self.lock:
            if objectHash in self.hashes:
                del self.hashes[objectHash]
            if hasattr(current_thread(), 'peer') and current_thread().peer in self.pending:
                self.pending[current_thread().peer]['received'] = time.time()
        for thread in self.pending.keys():
            with self.lock:
                if thread in self.pending and objectHash in self.pending[thread]['objects']:
                    self.pending[thread]['objects'].remove(objectHash)

    def stop(self):
        with self.lock:
            self.hashes = {}
            self.pending = {}

    def threadEnd(self):
        while True:
            try:
                with self.lock:
                    if current_thread().peer in self.pending:
                        for objectHash in self.pending[current_thread().peer]['objects']:
                            if objectHash in self.hashes:
                                self.hashes[objectHash]['peers'].remove(current_thread().peer)
            except (KeyError):
                pass
            else:
                break
        with self.lock:
            try:
                del self.pending[current_thread().peer]
            except KeyError:
                pass


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
