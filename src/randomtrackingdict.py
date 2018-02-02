import random
from threading import RLock
from time import time

class RandomTrackingDict(object):
    maxPending = 10
    pendingTimeout = 60
    def __init__(self): # O(1)
        self.dictionary = {}
        self.indexDict = []
        self.len = 0
        self.pendingLen = 0
        self.lastPoll = 0
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
        if not key in self.dictionary:
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
        self.maxPending = maxPending

    def setPendingTimeout(self, pendingTimeout):
        self.pendingTimeout = pendingTimeout

    def randomKeys(self, count=1):
        if self.len == 0 or ((self.pendingLen >= self.maxPending or
            self.pendingLen == self.len) and self.lastPoll +
            self.pendingTimeout > time()):
            raise KeyError
        # reset if we've requested all
        with self.lock:
            if self.pendingLen == self.len:
                self.pendingLen = 0
            available = self.len - self.pendingLen
            if count > available:
                count = available
            randomIndex = random.sample(range(self.len - self.pendingLen), count)
            retval = [self.indexDict[i] for i in randomIndex]

            for i in sorted(randomIndex, reverse=True):
                # swap with one below lowest pending
                self._swap(i, self.len - self.pendingLen - 1)
                self.pendingLen += 1
            self.lastPoll = time()
            return retval

if __name__ == '__main__':
    def randString():
        retval = b''
        for _ in range(32):
            retval += chr(random.randint(0,255))
        return retval

    a = []
    k = RandomTrackingDict()
    d = {}
    
#    print "populating normal dict"
#    a.append(time())
#    for i in range(50000):
#        d[randString()] = True
#    a.append(time())
    print "populating random tracking dict"
    a.append(time())
    for i in range(50000):
        k[randString()] = True
    a.append(time())
    print "done"
    while len(k) > 0:
        retval = k.randomKeys(1000)
        if not retval:
            print "error getting random keys"
        #a.append(time())
        try:
            k.randomKeys(100)
            print "bad"
        except KeyError:
            pass
        #a.append(time())
        for i in retval:
            del k[i]
        #a.append(time())
    a.append(time())

    for x in range(len(a) - 1):
        print "%i: %.3f" % (x, a[x+1] - a[x])
