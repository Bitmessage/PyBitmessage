"""
Address validator module.
"""
# pylint: disable=too-many-branches,relative-import,too-many-arguments,unused-argument

from Queue import Empty
from PyQt4 import QtGui
from utils import str_chan
from account import getSortedAccounts

from addresses import decodeAddress, addBMIfNotPresent
from queues import apiAddressGeneratorReturnQueue, addressGeneratorQueue
from tr import _translate


class AddressPassPhraseValidatorMixin(object):
    """Address passphrase validator class for QT UI"""
    def setParams(
            self,
            passPhraseObject=None,
            addressObject=None,
            feedBackObject=None,
            buttonBox=None,
            addressMandatory=True,
    ):
        """setting parameters for pasphrase, button,address etc"""
        self.addressObject = addressObject
        self.passPhraseObject = passPhraseObject
        self.feedBackObject = feedBackObject
        self.buttonBox = buttonBox
        self.addressMandatory = addressMandatory
        self.isValid = False
        # save default text
        self.okButtonLabel = self.buttonBox.button(QtGui.QDialogButtonBox.Ok).text()

    def setError(self, string):
        """setting the error based on AddressValidation"""
        if string is not None and self.feedBackObject is not None:
            font = QtGui.QFont()
            font.setBold(True)
            self.feedBackObject.setFont(font)
            self.feedBackObject.setStyleSheet("QLabel { color : red; }")
            self.feedBackObject.setText(string)
        self.isValid = False
        if self.buttonBox:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
            if string is not None and self.feedBackObject is not None:
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(
                    _translate("AddressValidator", "Invalid")
                )
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(
                    _translate("AddressValidator", "Validating...")
                )

    def setOK(self, string):
        """setting ok button label"""
        if string is not None and self.feedBackObject is not None:
            font = QtGui.QFont()
            font.setBold(False)
            self.feedBackObject.setFont(font)
            self.feedBackObject.setStyleSheet("QLabel { }")
            self.feedBackObject.setText(string)
        self.isValid = True
        if self.buttonBox:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(self.okButtonLabel)

    def checkQueue(self):
        """checking Queue"""
        gotOne = False

        # wait until processing is done
        if not addressGeneratorQueue.empty():
            self.setError(None)
            return None

        while True:
            try:
                addressGeneratorReturnValue = apiAddressGeneratorReturnQueue.get(False)
            except Empty:
                if gotOne:
                    break
                else:
                    return None
            else:
                gotOne = True

        if not addressGeneratorReturnValue:
            self.setError(
                _translate(
                    "AddressValidator",
                    "Address already present as one of your identities."
                )
            )
            return (QtGui.QValidator.Intermediate, 0)
        if addressGeneratorReturnValue[0] == 'chan name does not match address':
            self.setError(
                _translate(
                    "AddressValidator",
                    "Although the Bitmessage address you \
                    entered was valid, it doesn\'t match the chan name."
                )
            )
            return (QtGui.QValidator.Intermediate, 0)
        self.setOK(_translate("MainWindow", "Passphrase and address appear to be valid."))

    def returnValid(self):
        """method to check for validate"""
        if self.isValid:
            return QtGui.QValidator.Acceptable
        return QtGui.QValidator.Intermediate

    def validate(self, s, pos):
        """method check address validation"""
        if self.addressObject is None:
            address = None
        else:
            address = str(self.addressObject.text().toUtf8())
            if address == "":
                address = None
        if self.passPhraseObject is None:
            passPhrase = ""
        else:
            passPhrase = str(self.passPhraseObject.text().toUtf8())
            if passPhrase == "":
                passPhrase = None

        # no chan name
        if passPhrase is None:
            self.setError(_translate("AddressValidator", "Chan name/passphrase needed. You didn't enter a chan name."))
            return (QtGui.QValidator.Intermediate, pos)

        if self.addressMandatory or address is not None:
            # check if address already exists:
            if address in getSortedAccounts():
                self.setError(_translate("AddressValidator", "Address already present as one of your identities."))
                return (QtGui.QValidator.Intermediate, pos)

            # version too high
            if decodeAddress(address)[0] == 'versiontoohigh':
                self.setError(
                    _translate(
                        "AddressValidator",
                        "Address too new. Although that Bitmessage\
                        address might be valid, its version number\
                        is too new for us to handle. Perhaps you \
                        need to upgrade Bitmessage."
                    )
                )
                return (QtGui.QValidator.Intermediate, pos)

            # invalid
            if decodeAddress(address)[0] != 'success':
                self.setError(
                    _translate(
                        "AddressValidator",
                        "The Bitmessage address is not valid."
                    )
                )
                return (QtGui.QValidator.Intermediate, pos)

        # this just disables the OK button without changing the feedback text
        # but only if triggered by textEdited, not by clicking the Ok button
        if not self.buttonBox.button(QtGui.QDialogButtonBox.Ok).hasFocus():
            self.setError(None)

        # check through generator
        if address is None:
            addressGeneratorQueue.put(
                ('createChan', 4, 1,
                 str_chan + ' ' + str(passPhrase), passPhrase, False)
            )
        else:
            addressGeneratorQueue.put(
                ('joinChan', addBMIfNotPresent(address),
                 str_chan + ' ' + str(passPhrase), passPhrase, False)
            )

        if self.buttonBox.button(QtGui.QDialogButtonBox.Ok).hasFocus():
            return (self.returnValid(), pos)
        return (QtGui.QValidator.Intermediate, pos)

    def checkData(self):
        """method to check for data"""
        return self.validate("", 0)


class AddressValidator(QtGui.QValidator, AddressPassPhraseValidatorMixin):
    """AddressValidator class for QT UI"""
    def __init__(self, parent=None, passPhraseObject=None, feedBackObject=None, buttonBox=None, addressMandatory=True):
        super(AddressValidator, self).__init__(parent)
        self.setParams(passPhraseObject, parent, feedBackObject, buttonBox, addressMandatory)


class PassPhraseValidator(QtGui.QValidator, AddressPassPhraseValidatorMixin):
    """PassPhraseValidator class for QT UI"""
    def __init__(self, parent=None, addressObject=None, feedBackObject=None, buttonBox=None, addressMandatory=False):
        super(PassPhraseValidator, self).__init__(parent)
        self.setParams(parent, addressObject, feedBackObject, buttonBox, addressMandatory)
