from PyQt4 import QtCore, QtGui

class MessageCompose(QtGui.QTextEdit):
    
    def __init__(self, parent = 0):
        super(MessageCompose, self).__init__(parent)
        self.setAcceptRichText(False) # we'll deal with this later when we have a new message format
        self.defaultFontPointSize = self.currentFont().pointSize()
    
    def wheelEvent(self, event):
        if (QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier and event.orientation() == QtCore.Qt.Vertical:
            numDegrees = event.delta() / 8
            numSteps = numDegrees / 15
            zoomDiff = numSteps + self.currentFont().pointSize() - self.defaultFontPointSize
            if numSteps > 0:
                self.zoomIn(numSteps)
            else:
                self.zoomOut(-numSteps)
            QtGui.QApplication.activeWindow().statusBar().showMessage(QtGui.QApplication.translate("MainWindow", "Zoom level %1").arg(str(zoomDiff)))
        # super will actually automatically take care of zooming
        super(MessageCompose, self).wheelEvent(event)

    def reset(self):
        self.setText('')
