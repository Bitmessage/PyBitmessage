import collections
from threading import current_thread, enumerate as threadingEnumerate, RLock
import Queue
import time

from helper_sql import *
from storage import InventoryStorage, InventoryItem

class SqliteInventory(InventoryStorage):
    def __init__(self):
        super(self.__class__, self).__init__()
        self._inventory = {} #of objects (like msg payloads and pubkey payloads) Does not include protocol headers (the first 24 bytes of each packet).
        self._streams = collections.defaultdict(set) # key = streamNumer, value = a set which holds the inventory object hashes that we are aware of. This is used whenever we receive an inv message from a peer to check to see what items are new to us. We don't delete things out of it; instead, the singleCleaner thread clears and refills it every couple hours.
        self.lock = RLock() # Guarantees that two receiveDataThreads don't receive and process the same message concurrently (probably sent by a malicious individual)

    def __contains__(self, hash):
        with self.lock:
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
            return InventoryItem(*rows[0])

    def __setitem__(self, hash, value):
        with self.lock:
            value = InventoryItem(*value)
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

    def by_type_and_tag(self, objectType, tag):
        with self.lock:
            values = [value for value in self._inventory.values() if value.type == objectType and value.tag == tag]
            values += (InventoryItem(*value) for value in sqlQuery('SELECT objecttype, streamnumber, payload, expirestime, tag FROM inventory WHERE objecttype=? AND tag=?', objectType, tag))
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

