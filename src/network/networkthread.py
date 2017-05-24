import threading

from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
import network.asyncore_pollchoose as asyncore
from network.connectionpool import BMConnectionPool

class BMNetworkThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="BMNetworkThread")
        self.initStop()
        self.name = "AsyncoreThread"
        BMConnectionPool()
        logger.error("init asyncore thread")

    def run(self):
        while not self._stopped:
            BMConnectionPool().loop()

    def stopThread(self):
        super(BMNetworkThread, self).stopThread()
        for i in BMConnectionPool().listeningSockets:
            try:
                i.close()
            except:
                pass
        for i in BMConnectionPool().outboundConnections:
            try:
                i.close()
            except:
                pass
        for i in BMConnectionPool().inboundConnections:
            try:
                i.close()
            except:
                pass

        # just in case
        asyncore.close_all()
