# -*- coding: utf-8 -*-
"""
A menu plugin showing QR-Code for bitmessage address in modal dialog.
"""

import urllib

import qrcode
from PyQt4 import QtCore, QtGui

from pybitmessage.tr import _translate


# http://stackoverflow.com/questions/20452486
class Image(qrcode.image.base.BaseImage):  # pylint: disable=abstract-method
    """Image output class for qrcode using QPainter"""

    def __init__(self, border, width, box_size):
        # pylint: disable=super-init-not-called
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
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
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
        pixmap = qrcode.make(text, image_factory=Image).pixmap()
        self.image.setPixmap(pixmap)
        self.label.setText(text)
        self.label.setToolTip(text)
        self.label.setFixedWidth(pixmap.width())
        self.setFixedSize(QtGui.QWidget.sizeHint(self))


def connect_plugin(form):
    """Plugin entry point"""
    def on_action_ShowQR():
        """A slot for popup menu action"""
        try:
            dialog = form.qrcode_dialog
        except AttributeError:
            form.qrcode_dialog = dialog = QRCodeDialog(form)
        account = form.getContactSelected()
        try:
            label = account._getLabel()  # pylint: disable=protected-access
        except AttributeError:
            try:
                label = account.getLabel()
            except AttributeError:
                return
        dialog.render(
            'bitmessage:%s' % account.address + (
                '?' + urllib.urlencode({'label': label.encode('utf-8')})
                if label != account.address else '')
        )
        dialog.exec_()

    return on_action_ShowQR, _translate("MainWindow", "Show QR-code")
