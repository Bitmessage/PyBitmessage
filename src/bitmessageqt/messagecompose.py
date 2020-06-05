"""
Message editor with a wheel zoom functionality
"""
# pylint: disable=bad-continuation

from PyQt4 import QtCore, QtGui


class MessageCompose(QtGui.QTextEdit):
    """Editor class with wheel zoom functionality"""
    def __init__(self, parent=0):
        super(MessageCompose, self).__init__(parent)
        self.setAcceptRichText(False)
        self.defaultFontPointSize = self.currentFont().pointSize()

    def wheelEvent(self, event):
        """Mouse wheel scroll event handler"""
        if (
            QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ControlModifier
        ) == QtCore.Qt.ControlModifier and event.orientation() == QtCore.Qt.Vertical:
            if event.delta() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            zoom = self.currentFont().pointSize() * 100 / self.defaultFontPointSize
            QtGui.QApplication.activeWindow().statusBar().showMessage(
                QtGui.QApplication.translate("MainWindow", "Zoom level %1%").arg(
                    str(zoom)
                )
            )
        else:
            # in QTextEdit, super does not zoom, only scroll
            super(MessageCompose, self).wheelEvent(event)

    def reset(self):
        """Clear the edit content"""
        self.setText('')
