"""Most of the queues used by bitmessage threads are defined here."""

import Queue
import threading
import time

from multiqueue import MultiQueue


class ObjectProcessorQueue(Queue.Queue):
    """Special queue class using lock for `.threads.objectProcessor`"""

    maxSize = 32000000

    def __init__(self):
        Queue.Queue.__init__(self)
        self.sizeLock = threading.Lock()
        #: in Bytes. We maintain this to prevent nodes from flooding us
        #: with objects which take up too much memory. If this gets
        #: too big we'll sleep before asking for further objects.
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


workerQueue = Queue.Queue()
UISignalQueue = Queue.Queue()
addressGeneratorQueue = Queue.Queue()
#: `.network.ReceiveQueueThread` instances dump objects they hear
#: on the network into this queue to be processed.
objectProcessorQueue = ObjectProcessorQueue()
invQueue = MultiQueue()
addrQueue = MultiQueue()
portCheckerQueue = Queue.Queue()
receiveDataQueue = Queue.Queue()
#: The address generator thread uses this queue to get information back
#: to the API thread.
apiAddressGeneratorReturnQueue = Queue.Queue()
#: for exceptions
excQueue = Queue.Queue()
