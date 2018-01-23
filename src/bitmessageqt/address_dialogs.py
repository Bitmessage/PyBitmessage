from PyQt4 import QtCore, QtGui
from addresses import decodeAddress, encodeVarint
from account import (
    GatewayAccount, MailchuckAccount, AccountMixin, accountClass,
    getSortedAccounts
)
from tr import _translate
from retranslateui import RetranslateMixin
import widgets

import hashlib
from inventory import Inventory


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


class NewAddressDialog(QtGui.QDialog, RetranslateMixin):

    def __init__(self, parent=None):
        super(NewAddressDialog, self).__init__(parent)
        widgets.load('newaddressdialog.ui', self)

        # Let's fill out the 'existing address' combo box with addresses
        # from the 'Your Identities' tab.
        for address in getSortedAccounts():
            self.radioButtonExisting.click()
            self.comboBoxExisting.addItem(address)
        self.groupBoxDeterministic.setHidden(True)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


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


class RegenerateAddressesDialog(QtGui.QDialog, RetranslateMixin):
    def __init__(self, parent=None):
        super(RegenerateAddressesDialog, self).__init__(parent)
        widgets.load('regenerateaddresses.ui', self)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


class SpecialAddressBehaviorDialog(QtGui.QDialog, RetranslateMixin):

    def __init__(self, parent=None, config=None):
        super(SpecialAddressBehaviorDialog, self).__init__(parent)
        widgets.load('specialaddressbehavior.ui', self)
        self.address = parent.getCurrentAccount()
        self.parent = parent
        self.config = config

        try:
            self.address_is_chan = config.safeGetBoolean(
                self.address, 'chan'
            )
        except AttributeError:
            pass
        else:
            if self.address_is_chan:  # address is a chan address
                self.radioButtonBehaviorMailingList.setDisabled(True)
                self.lineEditMailingListName.setText(_translate(
                    "MainWindow",
                    "This is a chan address. You cannot use it as a"
                    " pseudo-mailing list."
                ))
            else:
                if config.safeGetBoolean(self.address, 'mailinglist'):
                    self.radioButtonBehaviorMailingList.click()
                else:
                    self.radioButtonBehaveNormalAddress.click()
                try:
                    mailingListName = config.get(
                        self.address, 'mailinglistname')
                except:
                    mailingListName = ''
                self.lineEditMailingListName.setText(
                    unicode(mailingListName, 'utf-8')
                )

        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))
        self.show()

    def accept(self):
        self.hide()
        if self.address_is_chan:
            return
        if self.radioButtonBehaveNormalAddress.isChecked():
            self.config.set(str(self.address), 'mailinglist', 'false')
            # Set the color to either black or grey
            if self.config.getboolean(self.address, 'enabled'):
                self.parent.setCurrentItemColor(
                    QtGui.QApplication.palette().text().color()
                )
            else:
                self.parent.setCurrentItemColor(QtGui.QColor(128, 128, 128))
        else:
            self.config.set(str(self.address), 'mailinglist', 'true')
            self.config.set(str(self.address), 'mailinglistname', str(
                self.lineEditMailingListName.text().toUtf8()))
            self.parent.setCurrentItemColor(
                QtGui.QColor(137, 04, 177))  # magenta
        self.parent.rerenderComboBoxSendFrom()
        self.parent.rerenderComboBoxSendFromBroadcast()
        self.config.save()
        self.parent.rerenderMessagelistToLabels()


class EmailGatewayDialog(QtGui.QDialog, RetranslateMixin):
    def __init__(self, parent, title=None, label=None, config=None):
        super(EmailGatewayDialog, self).__init__(parent)
        widgets.load('emailgateway.ui', self)
        self.parent = parent
        self.config = config
        if title and label:
            self.setWindowTitle(title)
            self.label.setText(label)
            self.radioButtonRegister.hide()
            self.radioButtonStatus.hide()
            self.radioButtonSettings.hide()
            self.radioButtonUnregister.hide()
        else:
            address = parent.getCurrentAccount()
            self.acct = accountClass(address)
            try:
                label = config.get(address, 'label')
            except AttributeError:
                pass
            else:
                if "@" in label:
                    self.lineEditEmail.setText(label)
            if isinstance(self.acct, GatewayAccount):
                self.radioButtonUnregister.setEnabled(True)
                self.radioButtonStatus.setEnabled(True)
                self.radioButtonStatus.setChecked(True)
                self.radioButtonSettings.setEnabled(True)
                self.lineEditEmail.setEnabled(False)
            else:
                self.acct = MailchuckAccount(address)
        self.lineEditEmail.setFocus()
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))

    def register(self, acct=None):
        email = str(self.lineEditEmail.text().toUtf8())
        if acct is None:
            acct = self.acct
        acct.register(email)
        self.config.set(acct.fromAddress, 'label', email)
        self.config.set(acct.fromAddress, 'gateway', 'mailchuck')
        self.config.save()
        self.parent.statusBar().showMessage(_translate(
            "MainWindow",
            "Sending email gateway registration request"
        ), 10000)

    def accept(self):
        self.hide()
        # no chans / mailinglists
        if self.acct.type != AccountMixin.NORMAL:
            return

        if not isinstance(self.acct, GatewayAccount):
            return

        if self.radioButtonRegister.isChecked():
            self.register()
        elif self.radioButtonUnregister.isChecked():
            self.acct.unregister()
            self.config.remove_option(self.acct.fromAddress, 'gateway')
            self.config.save()
            self.parent.statusBar().showMessage(_translate(
                "MainWindow",
                "Sending email gateway unregistration request"
            ), 10000)
        elif self.radioButtonStatus.isChecked():
            self.acct.status()
            self.parent.statusBar().showMessage(_translate(
                "MainWindow",
                "Sending email gateway status request"
            ), 10000)
        elif self.radioButtonSettings.isChecked():
            return self.acct
