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
            zoom = self.currentFont().pointSize() * 100 / self.defaultFontPointSize
            QtGui.QApplication.activeWindow().statusBar().showMessage(QtGui.QApplication.translate("MainWindow", "Zoom level %1%").arg(str(zoom)))
        else:
            # in QTextEdit, super does not zoom, only scroll
            super(MessageCompose, self).wheelEvent(event)

    def reset(self):
        self.setText('')
