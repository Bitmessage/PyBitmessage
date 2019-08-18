from queue import Queue

from class_objectProcessorQueue import ObjectProcessorQueue
from multiqueue import MultiQueue

workerQueue = Queue()
UISignalQueue = Queue()
addressGeneratorQueue = Queue()
# receiveDataThreads dump objects they hear on the network into this
# queue to be processed.
objectProcessorQueue = ObjectProcessorQueue()
invQueue = MultiQueue()
addrQueue = MultiQueue()
portCheckerQueue = Queue()
receiveDataQueue = Queue()
# The address generator thread uses this queue to get information back
# to the API thread.
apiAddressGeneratorReturnQueue = Queue()
# Exceptions
excQueue = Queue()
