"""
A thread for creating addresses
"""
# import queues
try:
    import queue as Queue
except ImportError:
    import Queue

import logging
import random
from pybitmessage import state
import threading

from pybitmessage.bmconfigparser import BMConfigParser

# from network.threads import StoppableThread


fake_addresses = [
    'BM-2cXDconV3bk6nPwWgBwN7wXaqZoT1bEzGv',
    'BM-2cTWjUVedYftZJbnZfs7MWts92v1R35Try',
    'BM-2cV1UN3er2YVQBcmJaaeYMXvpwBVokJNTo',
    'BM-2cWVkWk3TyKUscdcn9E7s9hrwpv2ZsBBog',
    'BM-2cW2a5R1KidMGNByqPKn6nJDDnHtazoere'
]

UISignalQueue = Queue.Queue()
addressGeneratorQueue = Queue.Queue()


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


class FakeAddressGenerator(StoppableThread):
    """A thread for creating fake addresses"""
    name = "addressGenerator"

    def stopThread(self):
        try:
            addressGeneratorQueue.put(("stopThread", "data"))
        except:
            pass
        super(FakeAddressGenerator, self).stopThread()

    def run(self):
        """
        Process the requests for addresses generation
        from `.queues.addressGeneratorQueue`
        """
        while state.shutdown == 0:
            queueValue = addressGeneratorQueue.get()
            streamNumber = 1
            try:
                if len(BMConfigParser().addresses()) > 0:
                    address = fake_addresses[len(BMConfigParser().addresses())]
                else:
                    address = fake_addresses[0]

                label = queueValue[3]
                BMConfigParser().add_section(address)
                BMConfigParser().set(address, 'label', label)
                BMConfigParser().set(address, 'enabled', 'true')
                BMConfigParser().set(
                    address, 'privencryptionkey', '5KUayt1aPSsNWsxMJnk27kv79wfRE3cWVPYLazyLQc752bXfQP3')
                BMConfigParser().save()

                UISignalQueue.put((
                    'updateStatusBar', ""
                ))
                UISignalQueue.put(('writeNewAddressToTable', (
                    label, address, streamNumber)))
                addressGeneratorQueue.task_done()
            except IndexError:
                self.logger.error(
                    'Program error: you can only create 5 fake addresses')
