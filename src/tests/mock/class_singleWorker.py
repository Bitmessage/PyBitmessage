"""
Thread for performing PoW
"""

from __future__ import division

import proofofwork
import queues
import state

from network import StoppableThread
from six.moves import queue


class MockSingleWorker(StoppableThread):
    """Thread for performing PoW"""

    def __init__(self):
        super(MockSingleWorker, self).__init__(name="singleWorker")
        proofofwork.init()
        self.busy = None

    def stopThread(self):
        """Signal through the queue that the thread should be stopped"""

        try:
            queues.workerQueue.put(("stopThread", "data"))
        except queue.Full:
            self.logger.error('workerQueue is Full')
        super(MockSingleWorker, self).stopThread()

    def run(self):

        if state.shutdown > 0:
            return

        while state.shutdown == 0:
            self.busy = 0
            command, _ = queues.workerQueue.get()
            self.busy = 1
            if command == 'stopThread':
                self.busy = 0
                return

            queues.workerQueue.task_done()
        self.logger.info("Quitting...")
