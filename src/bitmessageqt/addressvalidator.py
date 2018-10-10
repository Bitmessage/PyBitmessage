"""
src/bitmessageqt/addressvalidator.py
====================================
"""
# pylint: disable=too-many-branches,too-many-arguments
from Queue import Empty

from PyQt4 import QtGui

from account import getSortedAccounts
from addresses import addBMIfNotPresent, decodeAddress
from queues import addressGeneratorQueue, apiAddressGeneratorReturnQueue
from tr import _translate
from utils import str_chan


class AddressPassPhraseValidatorMixin(object):
    """Validator for address or passphrase (for deterministic addresses), mixin to be used by actual validators"""
    def setParams(
            self,
            passPhraseObject=None,
            addressObject=None,
            feedBackObject=None,
            buttonBox=None,
            addressMandatory=True):
        """Set validator references for other UI elements so that it can access their data"""
        # pylint: disable=too-many-arguments
        self.addressObject = addressObject
        self.passPhraseObject = passPhraseObject
        self.feedBackObject = feedBackObject
        self.buttonBox = buttonBox
        self.addressMandatory = addressMandatory
        self.isValid = False
        # save default text
        self.okButtonLabel = self.buttonBox.button(QtGui.QDialogButtonBox.Ok).text()

    def setError(self, string):
        """Indicate in UI that the validation failed"""
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
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(_translate("AddressValidator", "Invalid"))
            else:
                self.buttonBox.button(
                    QtGui.QDialogButtonBox.Ok).setText(
                        _translate(
                            "AddressValidator",
                            "Validating..."))

    def setOK(self, string):
        """Indicate in UI that the validation succeeded"""
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

    def checkQueue(self):  # pylint: disable=inconsistent-return-statements
        """Check address generator return queue status"""
        gotOne = False

        # wait until processing is done
        if not addressGeneratorQueue.empty():
            self.setError(None)
            return

        while True:
            try:
                addressGeneratorReturnValue = apiAddressGeneratorReturnQueue.get(False)
            except Empty:
                if gotOne:
                    break
                else:
                    return
            else:
                gotOne = True

        if not addressGeneratorReturnValue:
            self.setError(_translate("AddressValidator", "Address already present as one of your identities."))
            return (QtGui.QValidator.Intermediate, 0)

        if addressGeneratorReturnValue[0] == 'chan name does not match address':
            self.setError(
                _translate(
                    "AddressValidator",
                    "Although the Bitmessage address you entered was valid, it doesn\'t match the chan name."))
            return (QtGui.QValidator.Intermediate, 0)

        self.setOK(_translate("MainWindow", "Passphrase and address appear to be valid."))

    def returnValid(self):
        """Validator success"""
        if self.isValid:
            return QtGui.QValidator.Acceptable
        return QtGui.QValidator.Intermediate

    def validate(self, s, pos):
        """Perform validation"""
        # pylint: disable=unused-argument
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
                        "Address too new. Although that Bitmessage address might be valid, its version number is"
                        " too new for us to handle. Perhaps you need to upgrade Bitmessage."))
                return (QtGui.QValidator.Intermediate, pos)

            # invalid
            if decodeAddress(address)[0] != 'success':
                self.setError(_translate("AddressValidator", "The Bitmessage address is not valid."))
                return (QtGui.QValidator.Intermediate, pos)

        # this just disables the OK button without changing the feedback text
        # but only if triggered by textEdited, not by clicking the Ok button
        if not self.buttonBox.button(QtGui.QDialogButtonBox.Ok).hasFocus():
            self.setError(None)

        # check through generator
        if address is None:
            addressGeneratorQueue.put(('createChan', 4, 1, str_chan + ' ' + str(passPhrase), passPhrase, False))
        else:
            addressGeneratorQueue.put(
                ('joinChan', addBMIfNotPresent(address),
                 str_chan + ' ' + str(passPhrase),
                 passPhrase, False))

        if self.buttonBox.button(QtGui.QDialogButtonBox.Ok).hasFocus():
            return (self.returnValid(), pos)
        return (QtGui.QValidator.Intermediate, pos)

    def checkData(self):
        """Validator callback"""
        return self.validate("", 0)


class AddressValidator(QtGui.QValidator, AddressPassPhraseValidatorMixin):
    """Validator for address (combined with passpharse references)"""
    def __init__(self, parent=None, passPhraseObject=None, feedBackObject=None, buttonBox=None, addressMandatory=True):
        super(AddressValidator, self).__init__(parent)
        self.setParams(passPhraseObject, parent, feedBackObject, buttonBox, addressMandatory)


class PassPhraseValidator(QtGui.QValidator, AddressPassPhraseValidatorMixin):
    """Validator for passphrases (combined with address references)"""
    def __init__(self, parent=None, addressObject=None, feedBackObject=None, buttonBox=None, addressMandatory=False):
        super(PassPhraseValidator, self).__init__(parent)
        self.setParams(parent, addressObject, feedBackObject, buttonBox, addressMandatory)
