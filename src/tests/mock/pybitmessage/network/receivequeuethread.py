"""
Process data incoming from network
"""
import errno
import Queue
import socket

import state
from network.advanceddispatcher import UnknownStateError
from network.connectionpool import BMConnectionPool
from queues import receiveDataQueue
from threads import StoppableThread


class ReceiveQueueThread(StoppableThread):
    """This thread processes data received from the network
    (which is done by the asyncore thread)"""
    def __init__(self, num=0):
        super(ReceiveQueueThread, self).__init__(name="ReceiveQueue_%i" % num)

    def run(self):
        while not self._stopped and state.shutdown == 0:
            try:
                dest = receiveDataQueue.get(block=True, timeout=1)
            except Queue.Empty:
                continue

            if self._stopped or state.shutdown:
                break

            # cycle as long as there is data
            # methods should return False if there isn't enough data,
            # or the connection is to be aborted

            # state_* methods should return False if there isn't
            # enough data, or the connection is to be aborted

            try:
                connection = BMConnectionPool().getConnectionByAddr(dest)
            # connection object not found
            except KeyError:
                receiveDataQueue.task_done()
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
            receiveDataQueue.task_done()
