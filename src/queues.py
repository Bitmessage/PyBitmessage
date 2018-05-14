import Queue

from class_objectProcessorQueue import ObjectProcessorQueue
from multiqueue import MultiQueue

workerQueue = Queue.Queue()
UISignalQueue = Queue.Queue()
addressGeneratorQueue = Queue.Queue()
# receiveDataThreads dump objects they hear on the network into this queue to be processed.
objectProcessorQueue = ObjectProcessorQueue()
invQueue = MultiQueue()
addrQueue = MultiQueue()
portCheckerQueue = Queue.Queue()
receiveDataQueue = Queue.Queue()
apiAddressGeneratorReturnQueue = Queue.Queue(
    )  # The address generator thread uses this queue to get information back to the API thread.
