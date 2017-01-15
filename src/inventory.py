import collections
from threading import current_thread, RLock
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
        Missing().delete(hash)

    def __delitem__(self, hash):
        raise NotImplementedError

    def __iter__(self):
        with self.lock:
            hashes = self._inventory.keys()[:]
            hashes += (hash for hash, in sqlQuery('SELECT hash FROM inventory'))
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
            hashes = [hash for hash, value in self._inventory.items() if value.stream == stream and value.expires > t]
            hashes += (payload for payload, in sqlQuery('SELECT hash FROM inventory WHERE streamnumber=? AND expirestime>?', stream, t))
            return hashes

    def flush(self):
        with self.lock: # If you use both the inventoryLock and the sqlLock, always use the inventoryLock OUTSIDE of the sqlLock.
            with SqlBulkExecute() as sql:
                for hash, value in self._inventory.items():
                    sql.execute('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)', hash, *value)
                self._inventory.clear()

    def clean(self):
        with self.lock:
            sqlExecute('DELETE FROM inventory WHERE expirestime<?',int(time.time()) - (60 * 60 * 3))
            self._streams.clear()
            for hash, value in self.items():
                self._streams[value.stream].add(hash)


@Singleton
class Missing(object):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.lock = RLock()
        self.hashes = {}
        self.stopped = False
        self.frequency = 60

    def add(self, objectHash):
        if self.stopped:
            return
        with self.lock:
            if not objectHash in self.hashes:
                self.hashes[objectHash] = {'peers':[], 'requested':0}
            self.hashes[objectHash]['peers'].append(current_thread().peer)

    def len(self):
        with self.lock:
            return len(self.hashes)

    def removeObjectFromCurrentThread(self, objectHash):
        with self.lock:
            try:
                self.hashes[objectHash]['peers'].remove(current_thread().peer)
            except KeyError:
                return
            except ValueError:
                pass
            if len(self.hashes[objectHash]['peers']) == 0 and self.hashes[objectHash]['requested'] < time.time() - self.frequency:
                self.delete(objectHash)
            else:
                self.hashes[objectHash]['requested'] = time.time()

    def pull(self, count=1):
        if count < 1:
            raise ValueError("Must be at least one")
        with self.lock:
            objectHashes = []
            try:
                for objectHash in self.hashes.keys():
                    if self.hashes[objectHash]['requested'] < time.time() - self.frequency:
                        if len(self.hashes[objectHash]['peers']) == 0:
                            self.removeObjectFromCurrentThread(objectHash)
                            continue
                        if current_thread().peer in self.hashes[objectHash]['peers']:
                            objectHashes.append(objectHash)
                            self.removeObjectFromCurrentThread(objectHash)
                            if len(objectHashes) >= count:
                                break
            except RuntimeError:
                # the for cycle sometimes breaks if you remove elements
                pass
            return objectHashes

    def delete(self, objectHash):
        with self.lock:
            if objectHash in self.hashes:
                del self.hashes[objectHash]

    def stop(self):
        with self.lock:
            self.hashes = {}

    def threadEnd(self):
        with self.lock:
            for objectHash in self.hashes:
                self.removeObjectFromCurrentThread(objectHash)
