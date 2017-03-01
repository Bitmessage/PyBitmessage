# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import qrcode

from pybitmessage.tr import translateText

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


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


class Ui_qrcodeDialog(object):
    def setupUi(self, qrcodeDialog):
        qrcodeDialog.setObjectName(_fromUtf8("qrcodeDialog"))
        self.image = QtGui.QLabel(qrcodeDialog)
        self.label = QtGui.QLabel(qrcodeDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.buttonBox = QtGui.QDialogButtonBox(qrcodeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        layout = QtGui.QVBoxLayout(qrcodeDialog)
        layout.addWidget(self.image)
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)

        self.retranslateUi(qrcodeDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(
            _fromUtf8("accepted()")), qrcodeDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(
            _fromUtf8("rejected()")), qrcodeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(qrcodeDialog)

    def retranslateUi(self, qrcodeDialog):
        qrcodeDialog.setWindowTitle(QtGui.QApplication.translate(
            "qrcodeDialog", "QR-code",
            None, QtGui.QApplication.UnicodeUTF8
        ))

    def render(self, text):
        self.label.setText(text)
        self.image.setPixmap(
            qrcode.make(text, image_factory=Image).pixmap())


class qrcodeDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_qrcodeDialog()
        self.ui.setupUi(self)
        self.parent = parent
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


def connect_plugin(form):
    def on_action_ShowQR():
        form.qrcodeDialogInstance = qrcodeDialog(form)
        form.qrcodeDialogInstance.ui.render(
            str(form.getCurrentAccount())
        )
        form.qrcodeDialogInstance.exec_()

    form.actionShowQRCode = \
        form.ui.addressContextMenuToolbarYourIdentities.addAction(
            translateText("MainWindow", "Show QR-code"),
            on_action_ShowQR
        )
    form.popMenuYourIdentities.addAction(form.actionShowQRCode)
