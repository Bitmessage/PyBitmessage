"""
Module for using filesystem (directory with files) for inventory storage
"""
import logging
import os
import time
from binascii import hexlify, unhexlify
from threading import RLock

from paths import lookupAppdataFolder
from .storage import InventoryItem, InventoryStorage

logger = logging.getLogger('default')


class FilesystemInventory(InventoryStorage):
    """Filesystem for inventory storage"""
    topDir = "inventory"
    objectDir = "objects"
    metadataFilename = "metadata"
    dataFilename = "data"

    def __init__(self):
        super(FilesystemInventory, self).__init__()
        self.baseDir = os.path.join(
            lookupAppdataFolder(), FilesystemInventory.topDir)
        for createDir in [self.baseDir, os.path.join(self.baseDir, "objects")]:
            if os.path.exists(createDir):
                if not os.path.isdir(createDir):
                    raise IOError(
                        "%s exists but it's not a directory" % createDir)
            else:
                os.makedirs(createDir)
        # Guarantees that two receiveDataThreads
        # don't receive and process the same message
        # concurrently (probably sent by a malicious individual)
        self.lock = RLock()
        self._inventory = {}
        self._load()

    def __contains__(self, hashval):
        for streamDict in self._inventory.values():
            if hashval in streamDict:
                return True
        return False

    def __delitem__(self, hash_):
        raise NotImplementedError

    def __getitem__(self, hashval):
        for streamDict in self._inventory.values():
            try:
                retval = streamDict[hashval]
            except KeyError:
                continue
            if retval.payload is None:
                retval = InventoryItem(
                    retval.type,
                    retval.stream,
                    self.getData(hashval),
                    retval.expires,
                    retval.tag)
            return retval
        raise KeyError(hashval)

    def __setitem__(self, hashval, value):
        with self.lock:
            value = InventoryItem(*value)
            try:
                os.makedirs(os.path.join(
                    self.baseDir,
                    FilesystemInventory.objectDir,
                    hexlify(hashval).decode()))
            except OSError:
                pass
            try:
                with open(
                    os.path.join(
                        self.baseDir,
                        FilesystemInventory.objectDir,
                        hexlify(hashval).decode(),
                        FilesystemInventory.metadataFilename,
                    ),
                    "w",
                ) as f:
                    f.write("%s,%s,%s,%s," % (
                        value.type,
                        value.stream,
                        value.expires,
                        hexlify(value.tag).decode()))
                with open(
                    os.path.join(
                        self.baseDir,
                        FilesystemInventory.objectDir,
                        hexlify(hashval).decode(),
                        FilesystemInventory.dataFilename,
                    ),
                    "wb",
                ) as f:
                    f.write(value.payload)
            except IOError:
                raise KeyError
            try:
                self._inventory[value.stream][hashval] = value
            except KeyError:
                self._inventory[value.stream] = {}
                self._inventory[value.stream][hashval] = value

    def delHashId(self, hashval):
        """Remove object from inventory"""
        for stream in self._inventory:
            try:
                del self._inventory[stream][hashval]
            except KeyError:
                pass
        with self.lock:
            try:
                os.remove(
                    os.path.join(
                        self.baseDir,
                        FilesystemInventory.objectDir,
                        hexlify(hashval).decode(),
                        FilesystemInventory.metadataFilename))
            except IOError:
                pass
            try:
                os.remove(
                    os.path.join(
                        self.baseDir,
                        FilesystemInventory.objectDir,
                        hexlify(hashval).decode(),
                        FilesystemInventory.dataFilename))
            except IOError:
                pass
            try:
                os.rmdir(os.path.join(
                    self.baseDir,
                    FilesystemInventory.objectDir,
                    hexlify(hashval).decode()))
            except IOError:
                pass

    def __iter__(self):
        elems = []
        for streamDict in self._inventory.values():
            elems.extend(streamDict.keys())
        return elems.__iter__()

    def __len__(self):
        retval = 0
        for streamDict in self._inventory.values():
            retval += len(streamDict)
        return retval

    def _load(self):
        newInventory = {}
        for hashId in self.object_list():
            try:
                objectType, streamNumber, expiresTime, tag = self.getMetadata(
                    hashId)
                try:
                    newInventory[streamNumber][hashId] = InventoryItem(
                        objectType, streamNumber, None, expiresTime, tag)
                except KeyError:
                    newInventory[streamNumber] = {}
                    newInventory[streamNumber][hashId] = InventoryItem(
                        objectType, streamNumber, None, expiresTime, tag)
            except KeyError:
                logger.debug(
                    'error loading %s', hexlify(hashId), exc_info=True)
        self._inventory = newInventory

    def stream_list(self):
        """Return list of streams"""
        return self._inventory.keys()

    def object_list(self):
        """Return inventory vectors (hashes) from a directory"""
        return [unhexlify(x) for x in os.listdir(os.path.join(
            self.baseDir, FilesystemInventory.objectDir))]

    def getData(self, hashId):
        """Get object data"""
        try:
            with open(
                os.path.join(
                    self.baseDir,
                    FilesystemInventory.objectDir,
                    hexlify(hashId).decode(),
                    FilesystemInventory.dataFilename,
                ),
                "r",
            ) as f:
                return f.read()
        except IOError:
            raise AttributeError

    def getMetadata(self, hashId):
        """Get object metadata"""
        try:
            with open(
                os.path.join(
                    self.baseDir,
                    FilesystemInventory.objectDir,
                    hexlify(hashId).decode(),
                    FilesystemInventory.metadataFilename,
                ),
                "r",
            ) as f:
                objectType, streamNumber, expiresTime, tag = f.read().split(
                    ",", 4)[:4]
                return [
                    int(objectType),
                    int(streamNumber),
                    int(expiresTime),
                    unhexlify(tag)]
        except IOError:
            raise KeyError

    def by_type_and_tag(self, objectType, tag):
        """Get a list of objects filtered by object type and tag"""
        retval = []
        for streamDict in self._inventory.values():
            for hashId, item in streamDict:
                if item.type == objectType and item.tag == tag:
                    try:
                        if item.payload is None:
                            item.payload = self.getData(hashId)
                    except IOError:
                        continue
                    retval.append(InventoryItem(
                        item.type,
                        item.stream,
                        item.payload,
                        item.expires,
                        item.tag))
        return retval

    def hashes_by_stream(self, stream):
        """Return inventory vectors (hashes) for a stream"""
        try:
            return self._inventory[stream].keys()
        except KeyError:
            return []

    def unexpired_hashes_by_stream(self, stream):
        """Return unexpired hashes in the inventory for a particular stream"""
        try:
            return [
                x for x, value in self._inventory[stream].items()
                if value.expires > int(time.time())]
        except KeyError:
            return []

    def flush(self):
        """Flush the inventory and create a new, empty one"""
        self._load()

    def clean(self):
        """Clean out old items from the inventory"""
        minTime = int(time.time()) - 60 * 60 * 30
        deletes = []
        for streamDict in self._inventory.values():
            for hashId, item in streamDict.items():
                if item.expires < minTime:
                    deletes.append(hashId)
        for hashId in deletes:
            self.delHashId(hashId)
