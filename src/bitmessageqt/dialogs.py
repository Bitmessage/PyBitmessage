from PyQt4 import QtCore, QtGui
from addresses import decodeAddress, encodeVarint
from tr import _translate
from retranslateui import RetranslateMixin
import widgets

import hashlib
import paths
from inventory import Inventory
from version import softwareVersion


class AddressCheckMixin(object):

    def __init__(self):
        self.valid = False
        QtCore.QObject.connect(self.lineEditAddress, QtCore.SIGNAL(
            "textChanged(QString)"), self.addressChanged)

    def _onSuccess(self, addressVersion, streamNumber, ripe):
        pass

    def addressChanged(self, QString):
        status, addressVersion, streamNumber, ripe = decodeAddress(
            str(QString))
        self.valid = status == 'success'
        if self.valid:
            self.labelAddressCheck.setText(
                _translate("MainWindow", "Address is valid."))
            self._onSuccess(addressVersion, streamNumber, ripe)
        elif status == 'missingbm':
            self.labelAddressCheck.setText(_translate(
                "MainWindow", "The address should start with ''BM-''"))
        elif status == 'checksumfailed':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",
                "The address is not typed or copied correctly"
                " (the checksum failed)."
            ))
        elif status == 'versiontoohigh':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",
                "The version number of this address is higher than this"
                " software can support. Please upgrade Bitmessage."
            ))
        elif status == 'invalidcharacters':
            self.labelAddressCheck.setText(_translate(
                "MainWindow", "The address contains invalid characters."))
        elif status == 'ripetooshort':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",
                "Some data encoded in the address is too short."
            ))
        elif status == 'ripetoolong':
            self.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too long."))
        elif status == 'varintmalformed':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",
                "Some data encoded in the address is malformed."
            ))


class AddAddressDialog(QtGui.QDialog, RetranslateMixin, AddressCheckMixin):

    def __init__(self, parent=None):
        super(AddAddressDialog, self).__init__(parent)
        widgets.load('addaddressdialog.ui', self)
        AddressCheckMixin.__init__(self)


class NewSubscriptionDialog(
        QtGui.QDialog, RetranslateMixin, AddressCheckMixin):

    def __init__(self, parent=None):
        super(NewSubscriptionDialog, self).__init__(parent)
        widgets.load('newsubscriptiondialog.ui', self)
        AddressCheckMixin.__init__(self)

    def _onSuccess(self, addressVersion, streamNumber, ripe):
        if addressVersion <= 3:
            self.checkBoxDisplayMessagesAlreadyInInventory.setText(_translate(
                "MainWindow",
                "Address is an old type. We cannot display its past"
                " broadcasts."
            ))
        else:
            Inventory().flush()
            doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(
                encodeVarint(addressVersion) +
                encodeVarint(streamNumber) + ripe
            ).digest()).digest()
            tag = doubleHashOfAddressData[32:]
            self.recent = Inventory().by_type_and_tag(3, tag)
            count = len(self.recent)
            if count == 0:
                self.checkBoxDisplayMessagesAlreadyInInventory.setText(
                    _translate(
                        "MainWindow",
                        "There are no recent broadcasts from this address"
                        " to display."
                    ))
            else:
                self.checkBoxDisplayMessagesAlreadyInInventory.setEnabled(True)
                self.checkBoxDisplayMessagesAlreadyInInventory.setText(
                    _translate(
                        "MainWindow",
                        "Display the %1 recent broadcast(s) from this address."
                    ).arg(count))


class AboutDialog(QtGui.QDialog, RetranslateMixin):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        widgets.load('about.ui', self)
        commit = paths.lastCommit()[:7]
        label = "PyBitmessage " + softwareVersion
        if commit:
            label += '-' + commit
        self.labelVersion.setText(label)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


class IconGlossaryDialog(QtGui.QDialog, RetranslateMixin):
    def __init__(self, parent=None, config=None):
        super(IconGlossaryDialog, self).__init__(parent)
        widgets.load('iconglossary.ui', self)

        self.labelPortNumber.setText(_translate(
            "iconGlossaryDialog",
            "You are using TCP port %1. (This can be changed in the settings)."
            ).arg(config.getint('bitmessagesettings', 'port')))
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))
