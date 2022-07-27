# pylint: disable=too-many-lines,import-error,no-name-in-module,unused-argument
# pylint: disable=too-many-ancestors,too-many-locals,useless-super-delegation
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel,ungrouped-imports,wrong-import-order,unused-import,arguments-differ
# pylint: disable=invalid-name,unnecessary-comprehension,broad-except,simplifiable-if-expression,no-member
# pylint: disable=too-many-return-statements

"""shutdown function"""

from pybitmessage import state


def doCleanShutdown():
    """
    Used to exit Kivy UI.
    """
    state.shutdown = 1
