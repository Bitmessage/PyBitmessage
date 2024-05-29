"""
Slim layer providing environment agnostic _translate()
"""

from unqstr import ustr

try:
    import state
except ImportError:
    from . import state


def _tr_dummy(context, text, disambiguation=None, n=None):
    # pylint: disable=unused-argument
    return text


if state.enableGUI and not state.curses:
    try:
        from qtpy import QtWidgets, QtCore
    except ImportError:
        _translate = _tr_dummy
    else:
        _translate = QtWidgets.QApplication.translate
else:
    _translate = _tr_dummy
