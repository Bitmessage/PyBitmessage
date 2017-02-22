import Queue
from class_objectProcessorQueue import ObjectProcessorQueue

workerQueue = Queue.Queue()
UISignalQueue = Queue.Queue()
addressGeneratorQueue = Queue.Queue()
# receiveDataThreads dump objects they hear on the network into this queue to be processed.
objectProcessorQueue = ObjectProcessorQueue()
apiAddressGeneratorReturnQueue = Queue.Queue(
    )  # The address generator thread uses this queue to get information back to the API thread.
