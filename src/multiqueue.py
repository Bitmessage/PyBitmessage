"""
src/multiqueue.py
=================
"""

import queue as Queue
from collections import deque

import helper_random


class MultiQueue(Queue.Queue):
    """A base queue class"""
    # pylint: disable=redefined-builtin,attribute-defined-outside-init
    defaultQueueCount = 10

    def __init__(self, maxsize=0, count=0):
        if not count:
            self.queueCount = MultiQueue.defaultQueueCount
        else:
            self.queueCount = count
        Queue.Queue.__init__(self, maxsize)

    # Initialize the queue representation
    def _init(self, maxsize):
        self.iter = 0
        self.queues = []
        for _ in range(self.queueCount):
            self.queues.append(deque())

    def _qsize(self, len=len):
        return len(self.queues[self.iter])

    # Put a new item in the queue
    def _put(self, item):
        # self.queue.append(item)
        self.queues[helper_random.randomrandrange(self.queueCount)].append((item))

    # Get an item from the queue
    def _get(self):
        return self.queues[self.iter].popleft()

    def iterate(self):
        """Increment the iteration counter"""
        self.iter = (self.iter + 1) % self.queueCount

    def totalSize(self):
        """Return the total number of items in all the queues"""
        return sum(len(x) for x in self.queues)
