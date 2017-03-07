# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import qrcode

from pybitmessage.tr import _translate


# http://stackoverflow.com/questions/20452486
class Image(qrcode.image.base.BaseImage):
    def __init__(self, border, width, box_size):
        self.border = border
        self.width = width
        self.box_size = box_size
        size = (width + border * 2) * box_size
        self._image = QtGui.QImage(
            size, size, QtGui.QImage.Format_RGB16)
        self._image.fill(QtCore.Qt.white)

    def pixmap(self):
        return QtGui.QPixmap.fromImage(self._image)

    def drawrect(self, row, col):
        painter = QtGui.QPainter(self._image)
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size, self.box_size,
            QtCore.Qt.black)

    def save(self, stream, kind=None):
        pass


class QRCodeDialog(QtGui.QDialog):

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
        self.setWindowTitle(_translate("QRCodeDialog", "QR-code"))

    def render(self, text):
        self.label.setText(text)
        self.image.setPixmap(
            qrcode.make(text, image_factory=Image).pixmap())
        self.setFixedSize(QtGui.QWidget.sizeHint(self))


def connect_plugin(form):
    def on_action_ShowQR():
        try:
            dialog = form.qrcode_dialog
        except AttributeError:
            form.qrcode_dialog = dialog = QRCodeDialog(form)
        dialog.render(str(form.getCurrentAccount()))
        dialog.exec_()

    return on_action_ShowQR, _translate("MainWindow", "Show QR-code")
