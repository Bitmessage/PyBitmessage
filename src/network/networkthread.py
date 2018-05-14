import threading

from bmconfigparser import BMConfigParser
from debug import logger
from helper_threading import StoppableThread
import network.asyncore_pollchoose as asyncore
from network.connectionpool import BMConnectionPool
import state

class BMNetworkThread(threading.Thread, StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="Asyncore")
        self.initStop()
        self.name = "Asyncore"
        logger.info("init asyncore thread")

    def run(self):
        while not self._stopped and state.shutdown == 0:
            BMConnectionPool().loop()

    def stopThread(self):
        super(BMNetworkThread, self).stopThread()
        for i in BMConnectionPool().listeningSockets.values():
            try:
                i.close()
            except:
                pass
        for i in BMConnectionPool().outboundConnections.values():
            try:
                i.close()
            except:
                pass
        for i in BMConnectionPool().inboundConnections.values():
            try:
                i.close()
            except:
                pass

        # just in case
        asyncore.close_all()
