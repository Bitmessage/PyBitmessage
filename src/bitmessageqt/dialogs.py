from PyQt4 import QtCore, QtGui
from addaddressdialog import Ui_AddAddressDialog
from addresses import decodeAddress
from tr import _translate


class AddAddressDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AddAddressDialog()
        self.ui.setupUi(self)
        self.parent = parent
        QtCore.QObject.connect(self.ui.lineEditAddress, QtCore.SIGNAL(
            "textChanged(QString)"), self.addressChanged)

    def addressChanged(self, QString):
        status, a, b, c = decodeAddress(str(QString))
        if status == 'missingbm':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address should start with ''BM-''"))
        elif status == 'checksumfailed':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address is not typed or copied correctly (the checksum failed)."))
        elif status == 'versiontoohigh':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The version number of this address is higher than this software can support. Please upgrade Bitmessage."))
        elif status == 'invalidcharacters':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address contains invalid characters."))
        elif status == 'ripetooshort':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too short."))
        elif status == 'ripetoolong':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too long."))
        elif status == 'varintmalformed':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is malformed."))
        elif status == 'success':
            self.ui.labelAddressCheck.setText(
                _translate("MainWindow", "Address is valid."))
