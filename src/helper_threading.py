"""set_thread_name for threads that don't use StoppableThread"""

import threading

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
    # pylint: disable=protected-access
    threading.Thread.__bootstrap_original__ = threading.Thread._Thread__bootstrap
    threading.Thread._Thread__bootstrap = _thread_name_hack
