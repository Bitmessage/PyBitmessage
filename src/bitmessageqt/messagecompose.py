from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *
from past.utils import old_div
from PyQt4 import QtCore, QtGui

class MessageCompose(QtGui.QTextEdit):
    
    def __init__(self, parent = 0):
        super(MessageCompose, self).__init__(parent)
        self.setAcceptRichText(False) # we'll deal with this later when we have a new message format
        self.defaultFontPointSize = self.currentFont().pointSize()
    
    def wheelEvent(self, event):
        if (QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier and event.orientation() == QtCore.Qt.Vertical:
            if event.delta() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            zoom = old_div(self.currentFont().pointSize() * 100, self.defaultFontPointSize)
            QtGui.QApplication.activeWindow().statusBar().showMessage(QtGui.QApplication.translate("MainWindow", "Zoom level %1%").arg(str(zoom)))
        else:
            # in QTextEdit, super does not zoom, only scroll
            super(MessageCompose, self).wheelEvent(event)

    def reset(self):
        self.setText('')
