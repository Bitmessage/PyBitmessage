"""Threading primitives for the network package"""

import logging
import random
import threading


class StoppableThread(threading.Thread):
    """Base class for application threads with stopThread method"""
    name = None
    logger = logging.getLogger('default')

    def __init__(self, name=None):
        if name:
            self.name = name
        super(StoppableThread, self).__init__(name=self.name)
        self.stop = threading.Event()
        self._stopped = False
        random.seed()
        self.logger.info('Init thread %s', self.name)

    def stopThread(self):
        """Stop the thread"""
        self._stopped = True
        self.stop.set()


class BusyError(threading.ThreadError):
    """
    Thread error raised when another connection holds the lock
    we are trying to acquire.
    """
    pass
