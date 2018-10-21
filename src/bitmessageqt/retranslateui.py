"""
src/bitmessageqt/retranslateui.py
=================================

"""

from PyQt4 import QtGui

import widgets
from debug import logger  # pylint: disable=unused-import
# .. todo:: Consider moving the dependence of side-effects earlier in the application. Or better, not depending on it.


class RetranslateMixin(object):
    """Mixin class to support dynamic translations in QWidgets"""
    # pylint: disable=too-few-public-methods

    def retranslateUi(self):
        """Support dynamic language switching"""
        defaults = QtGui.QWidget()
        widgets.load(self.__class__.__name__.lower() + '.ui', defaults)
        for attr, value in defaults.__dict__.iteritems():
            setTextMethod = getattr(value, "setText", None)
            if callable(setTextMethod):
                getattr(self, attr).setText(getattr(defaults, attr).text())
            elif isinstance(value, QtGui.QTableWidget):
                for i in range(value.columnCount()):
                    getattr(self, attr).horizontalHeaderItem(i).setText(
                        getattr(defaults, attr).horizontalHeaderItem(i).text())
                for i in range(value.rowCount()):
                    getattr(self, attr).verticalHeaderItem(i).setText(
                        getattr(defaults, attr).verticalHeaderItem(i).text())
