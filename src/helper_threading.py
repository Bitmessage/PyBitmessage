import threading

class StoppableThread(object):
    def initStop(self):
        self.stop = threading.Event()
        self._stopped = False
        
    def stopThread(self):
        self._stopped = True
        self.stop.set()