"""
src/network/receivequeuethread.py
=================================
"""

import errno
import Queue
import socket
import threading

import state
from debug import logger
from helper_threading import StoppableThread
from network.advanceddispatcher import UnknownStateError
from network.connectionpool import BMConnectionPool
from queues import receiveDataQueue


class ReceiveQueueThread(threading.Thread, StoppableThread):
    """A thread for receiving items"""
    def __init__(self, num=0):
        threading.Thread.__init__(self, name="ReceiveQueue_%i" % (num))
        self.initStop()
        self.name = "ReceiveQueue_%i" % (num)
        logger.info("init receive queue thread %i", num)

    def run(self):
        while not self._stopped and state.shutdown == 0:
            try:
                dest = receiveDataQueue.get(block=True, timeout=1)
            except Queue.Empty:
                continue

            if self._stopped or state.shutdown:
                break

            # cycle as long as there is data
            # methods should return False if there isn't enough data, or the connection is to be aborted

            # state_* methods should return False if there isn't enough data,
            # or the connection is to be aborted

            try:
                connection = BMConnectionPool().getConnectionByAddr(dest)
            # KeyError = connection object not found
            except KeyError:
                receiveDataQueue.task_done()
                continue
            try:
                connection.process()
            # UnknownStateError = state isn't implemented
            except UnknownStateError:
                pass
            except socket.error as err:
                if err.errno == errno.EBADF:
                    connection.set_state("close", 0)
                else:
                    logger.error("Socket error: %s", str(err))
            except BaseException:
                logger.error("Error processing", exc_info=True)
            receiveDataQueue.task_done()
