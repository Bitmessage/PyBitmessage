"""
src/helper_threading.py
=======================

Helper threading perform all the threading operations.

"""
# pylint: disable=protected-access,attribute-defined-outside-init

import threading
from contextlib import contextmanager

try:
    import prctl
except ImportError:
    def set_thread_name(name):
        """Set the thread name for external use (visible from the OS)."""
        threading.current_thread().name = name
else:
    def set_thread_name(name):
        """Set a name for the thread for python internal use."""
        prctl.set_name(name)

    def _thread_name_hack(self):
        set_thread_name(self.name)
        threading.Thread.__bootstrap_original__(self)

    threading.Thread.__bootstrap_original__ = threading.Thread._Thread__bootstrap
    threading.Thread._Thread__bootstrap = _thread_name_hack


class StoppableThread(object):
    """A base class for threads giving them a custom stopping mechanism"""
    def initStop(self):
        """Start the process of stopping the thread"""
        self.stop = threading.Event()
        self._stopped = False

    def stopThread(self):
        """Complete the process of stopping a thread"""
        self._stopped = True
        self.stop.set()


class BusyError(threading.ThreadError):
    """Custom exception for our custom stopping mechanism"""
    pass


@contextmanager
def nonBlocking(lock):
    """A context manager for obtaining and releasing non-blocking locks"""
    locked = lock.acquire(False)
    if not locked:
        raise BusyError
    try:
        yield
    finally:
        lock.release()
