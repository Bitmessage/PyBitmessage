"""Most of the queues used by bitmessage threads are defined here."""

import threading
import time

from six.moves import queue

try:
    from multiqueue import MultiQueue
except ImportError:
    try:
        from .multiqueue import MultiQueue
    except ImportError:
        import sys
        if 'bitmessagemock' not in sys.modules:
            raise
        MultiQueue = queue.Queue


class ObjectProcessorQueue(queue.Queue):
    """Special queue class using lock for `.threads.objectProcessor`"""

    maxSize = 32000000

    def __init__(self):
        queue.Queue.__init__(self)
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
        queue.Queue.put(self, item, block, timeout)

    def get(self, block=True, timeout=None):
        item = queue.Queue.get(self, block, timeout)
        with self.sizeLock:
            self.curSize -= len(item[1])
        return item


workerQueue = queue.Queue()
UISignalQueue = queue.Queue()
addressGeneratorQueue = queue.Queue()
#: `.network.ReceiveQueueThread` instances dump objects they hear
#: on the network into this queue to be processed.
objectProcessorQueue = ObjectProcessorQueue()
invQueue = MultiQueue()
addrQueue = MultiQueue()
portCheckerQueue = queue.Queue()
receiveDataQueue = queue.Queue()
#: The address generator thread uses this queue to get information back
#: to the API thread.
apiAddressGeneratorReturnQueue = queue.Queue()
#: for exceptions
excQueue = queue.Queue()
