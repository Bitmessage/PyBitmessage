"""Helper threading perform all the threading operations."""

from contextlib import contextmanager
import threading


def set_thread_name(name):
    """Set the thread name for external use (visible from the OS)."""
    threading.current_thread().name = name


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
