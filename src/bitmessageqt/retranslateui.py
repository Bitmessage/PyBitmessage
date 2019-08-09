from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import *
from builtins import object
from os import path
from PyQt4 import QtGui
from debug import logger
from . import widgets

class RetranslateMixin(object):
    def retranslateUi(self):
        defaults = QtGui.QWidget()
        widgets.load(self.__class__.__name__.lower() + '.ui', defaults)
        for attr, value in defaults.__dict__.items():
            setTextMethod = getattr(value, "setText", None)
            if callable(setTextMethod):
                getattr(self, attr).setText(getattr(defaults, attr).text())
            elif isinstance(value, QtGui.QTableWidget):
                for i in range (value.columnCount()):
                    getattr(self, attr).horizontalHeaderItem(i).setText(getattr(defaults, attr).horizontalHeaderItem(i).text())
                for i in range (value.rowCount()):
                    getattr(self, attr).verticalHeaderItem(i).setText(getattr(defaults, attr).verticalHeaderItem(i).text())
