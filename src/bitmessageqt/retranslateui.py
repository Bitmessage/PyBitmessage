from os import path
from PyQt6 import QtGui, QtWidgets
from debug import logger
import bitmessageqt.widgets as widgets

class RetranslateMixin(object):
    def retranslateUi(self):
        defaults = QtWidgets.QWidget()
        widgets.load(self.__class__.__name__.lower() + '.ui', defaults)
        for attr, value in defaults.__dict__.items():
            setTextMethod = getattr(value, "setText", None)
            if callable(setTextMethod):
                getattr(self, attr).setText(getattr(defaults, attr).text())
            elif isinstance(value, QtWidgets.QTableWidget):
                for i in range (value.columnCount()):
                    getattr(self, attr).horizontalHeaderItem(i).setText(
                        getattr(defaults, attr).horizontalHeaderItem(i).text())
                for i in range (value.rowCount()):
                    getattr(self, attr).verticalHeaderItem(i).setText(
                        getattr(defaults, attr).verticalHeaderItem(i).text())
