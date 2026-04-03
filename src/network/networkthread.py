"""
A thread to handle network concerns
"""
import network.asyncore_pollchoose as asyncore
from queues import excQueue
from .threads import StoppableThread


class BMNetworkThread(StoppableThread):
    """Main network thread"""
    name = "Asyncore"

    def __init__(self, pool):
        super(BMNetworkThread, self).__init__()
        self.pool = pool

    def run(self):
        try:
            while not self._stopped:
                self.pool.loop()
        except Exception as e:
            excQueue.put((self.name, e))
            raise

    def stopThread(self):
        super(BMNetworkThread, self).stopThread()
        for i in self.pool.listeningSockets.values():
            try:
                i.close()
            except:  # nosec B110 # pylint:disable=bare-except
                pass
        for i in self.pool.outboundConnections.values():
            try:
                i.close()
            except:  # nosec B110 # pylint:disable=bare-except
                pass
        for i in self.pool.inboundConnections.values():
            try:
                i.close()
            except:  # nosec B110 # pylint:disable=bare-except
                pass

        # just in case
        asyncore.close_all()
