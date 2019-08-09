from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import threading

import network.asyncore_pollchoose as asyncore
import state
from debug import logger
from helper_threading import StoppableThread
from .fix_circular_imports import BMConnectionPool
from queues import excQueue


class BMNetworkThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="Asyncore")
        self.initStop()
        self.name = "Asyncore"
        logger.info("init asyncore thread")

    def run(self):
        try:
            while not self._stopped and state.shutdown == 0:
                BMConnectionPool().loop()
        except Exception as e:
            excQueue.put((self.name, e))
            raise

    def stopThread(self):
        super(BMNetworkThread, self).stopThread()
        for i in list(BMConnectionPool().listeningSockets.values()):
            try:
                i.close()
            except:
                pass
        for i in list(BMConnectionPool().outboundConnections.values()):
            try:
                i.close()
            except:
                pass
        for i in list(BMConnectionPool().inboundConnections.values()):
            try:
                i.close()
            except:
                pass

        # just in case
        asyncore.close_all()
