"""
Dialogs that work with BM address.
"""
# pylint: disable=too-few-public-methods
# https://github.com/PyCQA/pylint/issues/471

import hashlib

from unqstr import ustr, unic
from qtpy import QtGui, QtWidgets

import queues
from bitmessageqt import widgets
import state
from .account import (
    GatewayAccount, MailchuckAccount, AccountMixin, accountClass
)
from addresses import addBMIfNotPresent, decodeAddress, encodeVarint
from bmconfigparser import config as global_config
from tr import _translate


class AddressCheckMixin(object):
    """Base address validation class for Qt UI"""

    def _setup(self):
        self.valid = False
        self.lineEditAddress.textChanged.connect(self.addressChanged)

    def _onSuccess(self, addressVersion, streamNumber, ripe):
        pass

    def addressChanged(self, address):
        """
        Address validation callback, performs validation and gives feedback
        """
        status, addressVersion, streamNumber, ripe = decodeAddress(ustr(address))
        self.valid = status == 'success'
        if self.valid:
            self.labelAddressCheck.setText(
                _translate("MainWindow", "Address is valid."))
            self._onSuccess(addressVersion, streamNumber, ripe)
        elif status == 'missingbm':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",  # dialog name should be here
                "The address should start with ''BM-''"
            ))
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
                "MainWindow",
                "The address contains invalid characters."
            ))
        elif status == 'ripetooshort':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",
                "Some data encoded in the address is too short."
            ))
        elif status == 'ripetoolong':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",
                "Some data encoded in the address is too long."
            ))
        elif status == 'varintmalformed':
            self.labelAddressCheck.setText(_translate(
                "MainWindow",
                "Some data encoded in the address is malformed."
            ))


class AddressDataDialog(QtWidgets.QDialog, AddressCheckMixin):
    """
    Base class for a dialog getting BM-address data.
    Corresponding ui-file should define two fields:
    lineEditAddress - for the address
    lineEditLabel - for it's label
    After address validation the values of that fields are put into
    the data field of the dialog.
    """

    def __init__(self, parent):
        super(AddressDataDialog, self).__init__(parent)
        self.parent = parent
        self.data = None

    def accept(self):
        """Callback for QDialog accepting value"""
        if self.valid:
            self.data = (
                addBMIfNotPresent(ustr(self.lineEditAddress.text())),
                ustr(self.lineEditLabel.text())
            )
        else:
            queues.UISignalQueue.put(('updateStatusBar', _translate(
                "MainWindow",
                "The address you entered was invalid. Ignoring it."
            )))
        super(AddressDataDialog, self).accept()


class AddAddressDialog(AddressDataDialog):
    """QDialog for adding a new address"""

    def __init__(self, parent=None, address=None):
        super(AddAddressDialog, self).__init__(parent)
        widgets.load('addaddressdialog.ui', self)
        self._setup()
        if address:
            self.lineEditAddress.setText(address)


class NewAddressDialog(QtWidgets.QDialog):
    """QDialog for generating a new address"""

    def __init__(self, parent=None):
        super(NewAddressDialog, self).__init__(parent)
        widgets.load('newaddressdialog.ui', self)

        # Let's fill out the 'existing address' combo box with addresses
        # from the 'Your Identities' tab.
        for address in global_config.addresses(True):
            self.radioButtonExisting.click()
            self.comboBoxExisting.addItem(address)
        self.groupBoxDeterministic.setHidden(True)
        QtWidgets.QWidget.resize(self, QtWidgets.QWidget.sizeHint(self))
        self.show()

    def accept(self):
        """accept callback"""
        self.hide()
        # self.buttonBox.enabled = False
        if self.radioButtonRandomAddress.isChecked():
            if self.radioButtonMostAvailable.isChecked():
                streamNumberForAddress = 1
            else:
                # User selected 'Use the same stream as an existing
                # address.'
                streamNumberForAddress = decodeAddress(
                    self.comboBoxExisting.currentText())[2]
            queues.addressGeneratorQueue.put((
                'createRandomAddress', 4, streamNumberForAddress,
                ustr(self.newaddresslabel.text()), 1, "",
                self.checkBoxEighteenByteRipe.isChecked()
            ))
        else:
            if ustr(self.lineEditPassphrase.text()) != \
                    ustr(self.lineEditPassphraseAgain.text()):
                QtWidgets.QMessageBox.about(
                    self, _translate("MainWindow", "Passphrase mismatch"),
                    _translate(
                        "MainWindow",
                        "The passphrase you entered twice doesn\'t"
                        " match. Try again.")
                )
            elif self.lineEditPassphrase.text() == "":
                QtWidgets.QMessageBox.about(
                    self, _translate("MainWindow", "Choose a passphrase"),
                    _translate(
                        "MainWindow", "You really do need a passphrase.")
                )
            else:
                # this will eventually have to be replaced by logic
                # to determine the most available stream number.
                streamNumberForAddress = 1
                queues.addressGeneratorQueue.put((
                    'createDeterministicAddresses', 4, streamNumberForAddress,
                    "unused deterministic address",
                    self.spinBoxNumberOfAddressesToMake.value(),
                    ustr(self.lineEditPassphrase.text()),
                    self.checkBoxEighteenByteRipe.isChecked()
                ))


class NewSubscriptionDialog(AddressDataDialog):
    """QDialog for subscribing to an address"""

    def __init__(self, parent=None):
        super(NewSubscriptionDialog, self).__init__(parent)
        widgets.load('newsubscriptiondialog.ui', self)
        self.recent = []
        self._setup()

    def _onSuccess(self, addressVersion, streamNumber, ripe):
        if addressVersion <= 3:
            self.checkBoxDisplayMessagesAlreadyInInventory.setText(_translate(
                "MainWindow",
                "Address is an old type. We cannot display its past"
                " broadcasts."
            ))
        else:
            state.Inventory.flush()
            doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(
                encodeVarint(addressVersion)
                + encodeVarint(streamNumber) + ripe
            ).digest()).digest()
            tag = doubleHashOfAddressData[32:]
            self.recent = state.Inventory.by_type_and_tag(3, tag)
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
                        "Display the %n recent broadcast(s) from this address.",
                        None, count
                    ))


class RegenerateAddressesDialog(QtWidgets.QDialog):
    """QDialog for regenerating deterministic addresses"""

    def __init__(self, parent=None):
        super(RegenerateAddressesDialog, self).__init__(parent)
        widgets.load('regenerateaddresses.ui', self)
        self.groupBox.setTitle('')
        QtWidgets.QWidget.resize(self, QtWidgets.QWidget.sizeHint(self))


class SpecialAddressBehaviorDialog(QtWidgets.QDialog):
    """
    QDialog for special address behaviour (e.g. mailing list functionality)
    """

    def __init__(self, parent=None, config=global_config):
        super(SpecialAddressBehaviorDialog, self).__init__(parent)
        widgets.load('specialaddressbehavior.ui', self)
        self.address = ustr(parent.getCurrentAccount())
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
                    "SpecialAddressBehaviorDialog",
                    "This is a chan address. You cannot use it as a"
                    " pseudo-mailing list."
                ))
            else:
                if config.safeGetBoolean(self.address, 'mailinglist'):
                    self.radioButtonBehaviorMailingList.click()
                else:
                    self.radioButtonBehaveNormalAddress.click()
                mailingListName = config.safeGet(
                    self.address, 'mailinglistname', '')
                self.lineEditMailingListName.setText(
                    unic(ustr(mailingListName)))

        QtWidgets.QWidget.resize(self, QtWidgets.QWidget.sizeHint(self))
        self.show()

    def accept(self):
        """Accept callback"""
        self.hide()
        if self.address_is_chan:
            return
        if self.radioButtonBehaveNormalAddress.isChecked():
            self.config.set(self.address, 'mailinglist', 'false')
            # Set the color to either black or grey
            if self.config.getboolean(self.address, 'enabled'):
                self.parent.setCurrentItemColor(
                    QtWidgets.QApplication.palette().text().color()
                )
            else:
                self.parent.setCurrentItemColor(QtGui.QColor(128, 128, 128))
        else:
            self.config.set(self.address, 'mailinglist', 'true')
            self.config.set(self.address, 'mailinglistname', ustr(
                self.lineEditMailingListName.text()))
            self.parent.setCurrentItemColor(
                QtGui.QColor(137, 4, 177))  # magenta
        self.parent.rerenderComboBoxSendFrom()
        self.parent.rerenderComboBoxSendFromBroadcast()
        self.config.save()
        self.parent.rerenderMessagelistToLabels()


class EmailGatewayDialog(QtWidgets.QDialog):
    """QDialog for email gateway control"""

    def __init__(self, parent, config=global_config, account=None):
        super(EmailGatewayDialog, self).__init__(parent)
        widgets.load('emailgateway.ui', self)
        self.parent = parent
        self.config = config
        self.data = None
        if account:
            self.acct = account
            self.setWindowTitle(_translate(
                "EmailGatewayDialog", "Registration failed:"))
            self.label.setText(_translate(
                "EmailGatewayDialog",
                "The requested email address is not available,"
                " please try a new one."
            ))
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
        QtWidgets.QWidget.resize(self, QtWidgets.QWidget.sizeHint(self))

    def accept(self):
        """Accept callback"""
        self.hide()
        # no chans / mailinglists
        if self.acct.type != AccountMixin.NORMAL:
            return

        if not isinstance(self.acct, GatewayAccount):
            return

        if self.radioButtonRegister.isChecked() \
                or self.radioButtonRegister.isHidden():
            email = ustr(self.lineEditEmail.text())
            self.acct.register(email)
            self.config.set(self.acct.fromAddress, 'label', email)
            self.config.set(self.acct.fromAddress, 'gateway', 'mailchuck')
            self.config.save()
            queues.UISignalQueue.put(('updateStatusBar', _translate(
                "EmailGatewayDialog",
                "Sending email gateway registration request"
            )))
        elif self.radioButtonUnregister.isChecked():
            self.acct.unregister()
            self.config.remove_option(self.acct.fromAddress, 'gateway')
            self.config.save()
            queues.UISignalQueue.put(('updateStatusBar', _translate(
                "EmailGatewayDialog",
                "Sending email gateway unregistration request"
            )))
        elif self.radioButtonStatus.isChecked():
            self.acct.status()
            queues.UISignalQueue.put(('updateStatusBar', _translate(
                "EmailGatewayDialog",
                "Sending email gateway status request"
            )))
        elif self.radioButtonSettings.isChecked():
            self.data = self.acct

        super(EmailGatewayDialog, self).accept()
