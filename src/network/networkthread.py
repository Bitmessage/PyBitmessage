"""
A thread to handle network concerns
"""
import network.asyncore_pollchoose as asyncore
from network import connectionpool
from queues import excQueue
from .threads import StoppableThread


class BMNetworkThread(StoppableThread):
    """Main network thread"""
    name = "Asyncore"

    def run(self):
        try:
            while not self._stopped:
                connectionpool.pool.loop()
        except Exception as e:
            excQueue.put((self.name, e))
            raise

    def stopThread(self):
        super(BMNetworkThread, self).stopThread()
        for i in connectionpool.pool.listeningSockets.values():
            try:
                i.close()
            except:  # nosec B110 # pylint:disable=bare-except
                pass
        for i in connectionpool.pool.outboundConnections.values():
            try:
                i.close()
            except:  # nosec B110 # pylint:disable=bare-except
                pass
        for i in connectionpool.pool.inboundConnections.values():
            try:
                i.close()
            except:  # nosec B110 # pylint:disable=bare-except
                pass

        # just in case
        asyncore.close_all()
