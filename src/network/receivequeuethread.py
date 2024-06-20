"""
Process data incoming from network
"""
import errno
import Queue
import socket

import connectionpool
from network.advanceddispatcher import UnknownStateError
from threads import StoppableThread


class ReceiveQueueThread(StoppableThread):
    """This thread processes data received from the network
    (which is done by the asyncore thread)"""
    def __init__(self, queues, num=0):
        self.queues = queues
        super(ReceiveQueueThread, self).__init__(name="ReceiveQueue_%i" % num)

    def run(self):
        while not self._stopped:
            try:
                dest = self.queues.receiveDataQueue.get(block=True, timeout=1)
            except Queue.Empty:
                continue

            if self._stopped:
                break

            # cycle as long as there is data
            # methods should return False if there isn't enough data,
            # or the connection is to be aborted

            # state_* methods should return False if there isn't
            # enough data, or the connection is to be aborted

            try:
                connection = connectionpool.pool.getConnectionByAddr(dest)
            # connection object not found
            except KeyError:
                self.queues.receiveDataQueue.task_done()
                continue
            try:
                connection.process()
            # state isn't implemented
            except UnknownStateError:
                pass
            except socket.error as err:
                if err.errno == errno.EBADF:
                    connection.set_state("close", 0)
                else:
                    self.logger.error('Socket error: %s', err)
            except:  # noqa:E722
                self.logger.error('Error processing', exc_info=True)
            self.queues.receiveDataQueue.task_done()
