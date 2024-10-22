from unqstr import ustr
import six
from bitmessageqt import widgets
from qtpy import QtWidgets


class RetranslateMixin(object):
    def retranslateUi(self):
        defaults = QtWidgets.QWidget()
        widgets.load(self.__class__.__name__.lower() + '.ui', defaults)
        for attr, value in six.iteritems(defaults.__dict__):
            setTextMethod = getattr(value, "setText", None)
            if callable(setTextMethod):
                getattr(self, attr).setText(ustr(getattr(defaults, attr).text()))
            elif isinstance(value, QtWidgets.QTableWidget):
                for i in range(value.columnCount()):
                    getattr(self, attr).horizontalHeaderItem(i).setText(
                        ustr(getattr(defaults, attr).horizontalHeaderItem(i).text()))
                for i in range(value.rowCount()):
                    getattr(self, attr).verticalHeaderItem(i).setText(
                        ustr(getattr(defaults, attr).verticalHeaderItem(i).text()))
