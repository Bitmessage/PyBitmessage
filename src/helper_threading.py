from contextlib import contextmanager
import threading

try:
    import prctl
    def set_thread_name(name): prctl.set_name(name)

    def _thread_name_hack(self):
        set_thread_name(self.name)
        threading.Thread.__bootstrap_original__(self)

    threading.Thread.__bootstrap_original__ = threading.Thread._Thread__bootstrap
    threading.Thread._Thread__bootstrap = _thread_name_hack
except ImportError:
    def set_thread_name(name): threading.current_thread().name = name

class StoppableThread(object):
    def initStop(self):
        self.stop = threading.Event()
        self._stopped = False
        
    def stopThread(self):
        self._stopped = True
        self.stop.set()

class BusyError(threading.ThreadError):
    pass

@contextmanager
def nonBlocking(lock):
    locked = lock.acquire(False)
    if not locked:
        raise BusyError
    try:
        yield
    finally:
        lock.release()
