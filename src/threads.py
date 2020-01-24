"""
PyBitmessage does various tasks in separate threads. Most of them inherit
from `.network.StoppableThread`. There are `addressGenerator` for
addresses generation, `objectProcessor` for processing the network objects
passed minimal validation, `singleCleaner` to periodically clean various
internal storages (like inventory and knownnodes) and do forced garbage
collection, `singleWorker` for doing PoW, `sqlThread` for querying sqlite
database.

There are also other threads in the `.network` package.

:func:`set_thread_name` is defined here for the threads that don't inherit from
:class:`.network.StoppableThread`
"""

import threading

from class_addressGenerator import addressGenerator
from class_objectProcessor import objectProcessor
from class_singleCleaner import singleCleaner
from class_singleWorker import singleWorker
from class_sqlThread import sqlThread

try:
    import prctl
except ImportError:
    def set_thread_name(name):
        """Set a name for the thread for python internal use."""
        threading.current_thread().name = name
else:
    def set_thread_name(name):
        """Set the thread name for external use (visible from the OS)."""
        prctl.set_name(name)

    def _thread_name_hack(self):
        set_thread_name(self.name)
        threading.Thread.__bootstrap_original__(self)
    # pylint: disable=protected-access
    threading.Thread.__bootstrap_original__ = threading.Thread._Thread__bootstrap
    threading.Thread._Thread__bootstrap = _thread_name_hack


__all__ = [
    "addressGenerator", "objectProcessor", "singleCleaner", "singleWorker",
    "sqlThread"
]
