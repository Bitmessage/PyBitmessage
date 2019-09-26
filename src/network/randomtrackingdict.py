"""
src/randomtrackingdict.py
=========================
"""

import random
from threading import RLock
from time import time

import helper_random


class RandomTrackingDict(object):
    """
    Dict with randomised order and tracking.

    Keeps a track of how many items have been requested from the dict, and timeouts. Resets after all objects have been
    retrieved and timed out. The main purpose of this isn't as much putting related code together as performance
    optimisation and anonymisation of downloading of objects from other peers. If done using a standard dict or array,
    it takes too much CPU (and looks convoluted). Randomisation helps with anonymity.
    """
    # pylint: disable=too-many-instance-attributes
    maxPending = 10
    pendingTimeout = 60

    def __init__(self):
        self.dictionary = {}
        self.indexDict = []
        self.len = 0
        self.pendingLen = 0
        self.lastPoll = 0
        self.lastObject = 0
        self.lock = RLock()

    def __len__(self):
        return self.len

    def __contains__(self, key):
        return key in self.dictionary

    def __getitem__(self, key):
        return self.dictionary[key][1]

    def _swap(self, i1, i2):
        with self.lock:
            key1 = self.indexDict[i1]
            key2 = self.indexDict[i2]
            self.indexDict[i1] = key2
            self.indexDict[i2] = key1
            self.dictionary[key1][0] = i2
            self.dictionary[key2][0] = i1
        # for quick reassignment
        return i2

    def __setitem__(self, key, value):
        with self.lock:
            if key in self.dictionary:
                self.dictionary[key][1] = value
            else:
                self.indexDict.append(key)
                self.dictionary[key] = [self.len, value]
                self._swap(self.len, self.len - self.pendingLen)
                self.len += 1

    def __delitem__(self, key):
        if key not in self.dictionary:
            raise KeyError
        with self.lock:
            index = self.dictionary[key][0]
            # not pending
            if index < self.len - self.pendingLen:
                # left of pending part
                index = self._swap(index, self.len - self.pendingLen - 1)
            # pending
            else:
                self.pendingLen -= 1
            # end
            self._swap(index, self.len - 1)
            # if the following del is batched, performance of this single
            # operation can improve 4x, but it's already very fast so we'll
            # ignore it for the time being
            del self.indexDict[-1]
            del self.dictionary[key]
            self.len -= 1

    def setMaxPending(self, maxPending):
        """
        Sets maximum number of objects that can be retrieved from the class simultaneously as long as there is no
        timeout
        """
        self.maxPending = maxPending

    def setPendingTimeout(self, pendingTimeout):
        """Sets how long to wait for a timeout if max pending is reached (or all objects have been retrieved)"""
        self.pendingTimeout = pendingTimeout

    def setLastObject(self):
        """Update timestamp for tracking of received objects"""
        self.lastObject = time()

    def randomKeys(self, count=1):
        """Retrieve count random keys from the dict that haven't already been retrieved"""
        if self.len == 0 or ((self.pendingLen >= self.maxPending or
                              self.pendingLen == self.len) and self.lastPoll +
                             self.pendingTimeout > time()):
            raise KeyError

        # pylint: disable=redefined-outer-name
        with self.lock:
            # reset if we've requested all
            # and if last object received too long time ago
            if self.pendingLen == self.len and self.lastObject + self.pendingTimeout < time():
                self.pendingLen = 0
                self.setLastObject()
            available = self.len - self.pendingLen
            if count > available:
                count = available
            randomIndex = helper_random.randomsample(range(self.len - self.pendingLen), count)
            retval = [self.indexDict[i] for i in randomIndex]

            for i in sorted(randomIndex, reverse=True):
                # swap with one below lowest pending
                self._swap(i, self.len - self.pendingLen - 1)
                self.pendingLen += 1
            self.lastPoll = time()
            return retval


if __name__ == '__main__':

    # pylint: disable=redefined-outer-name
    def randString():
        """helper function for tests, generates a random string"""
        retval = b''
        for _ in range(32):
            retval += chr(random.randint(0, 255))
        return retval

    a = []
    k = RandomTrackingDict()
    d = {}

    print ("populating random tracking dict")
    a.append(time())
    for i in range(50000):
        k[randString()] = True
    a.append(time())
    print ("done")

    while k:
        retval = k.randomKeys(1000)
        if not retval:
            print ("error getting random keys")
        try:
            k.randomKeys(100)
            print( "bad")
        except KeyError:
            pass
        for i in retval:
            del k[i]
    a.append(time())

    for x in range(len(a) - 1):
        print("{}i: {}.3f".format(x, a[x + 1] - a[x]))
