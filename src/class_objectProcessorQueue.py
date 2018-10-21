"""
src/class_objectProcessorQueue.py
=================================
"""

import Queue
import threading
import time


class ObjectProcessorQueue(Queue.Queue):
    """A queue for processsing message objects"""
    maxSize = 32000000

    def __init__(self):
        Queue.Queue.__init__(self)
        self.sizeLock = threading.Lock()
        # in Bytes. We maintain this to prevent nodes from flooing us with objects
        # which take up too much memory. If this gets too big we'll sleep before
        # asking for further objects.
        self.curSize = 0

    def put(self, item, block=True, timeout=None):
        while self.curSize >= self.maxSize:
            time.sleep(1)
        with self.sizeLock:
            self.curSize += len(item[1])
        Queue.Queue.put(self, item, block, timeout)

    def get(self, block=True, timeout=None):
        item = Queue.Queue.get(self, block, timeout)
        with self.sizeLock:
            self.curSize -= len(item[1])
        return item
