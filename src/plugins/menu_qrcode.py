# -*- coding: utf-8 -*-
"""
A menu plugin showing QR-Code for bitmessage address in modal dialog.
"""

from PyQt4 import QtGui, QtCore
import qrcode

from pybitmessage.tr import _translate


# http://stackoverflow.com/questions/20452486
class Image(qrcode.image.base.BaseImage):
    """Image output class for qrcode using QPainter"""
    def __init__(self, border, width, box_size):
        self.border = border
        self.width = width
        self.box_size = box_size
        size = (width + border * 2) * box_size
        self._image = QtGui.QImage(
            size, size, QtGui.QImage.Format_RGB16)
        self._image.fill(QtCore.Qt.white)

    def pixmap(self):
        """Get image pixmap"""
        return QtGui.QPixmap.fromImage(self._image)

    def drawrect(self, row, col):
        """Draw a single rectangle - implementation"""
        painter = QtGui.QPainter(self._image)
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size, self.box_size,
            QtCore.Qt.black)


class QRCodeDialog(QtGui.QDialog):
    """The dialog"""
    def __init__(self, parent):
        super(QRCodeDialog, self).__init__(parent)
        self.image = QtGui.QLabel(self)
        self.label = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.image)
        layout.addWidget(self.label)
        layout.addWidget(buttonBox)
        self.retranslateUi()

    def retranslateUi(self):
        """A conventional Qt Designer method for dynamic l10n"""
        self.setWindowTitle(_translate("QRCodeDialog", "QR-code"))

    def render(self, text):
        """Draw QR-code and address in labels"""
        self.label.setText(text)
        self.image.setPixmap(
            qrcode.make(text, image_factory=Image).pixmap())
        self.setFixedSize(QtGui.QWidget.sizeHint(self))


def connect_plugin(form):
    """Plugin entry point"""
    def on_action_ShowQR():
        """A slot for popup menu action"""
        try:
            dialog = form.qrcode_dialog
        except AttributeError:
            form.qrcode_dialog = dialog = QRCodeDialog(form)
        dialog.render('bitmessage:' + str(form.getCurrentAccount()))
        dialog.exec_()

    return on_action_ShowQR, _translate("MainWindow", "Show QR-code")
