# pylint: disable=invalid-name
"""shutdown function"""

from pybitmessage import state


def doCleanShutdown():
    """
    Used to exit Kivy UI.
    """
    state.shutdown = 1
