"""
The validator for address and passphrase QLineEdits
used in `.dialogs.NewChanDialog`.
"""
# pylint: disable=too-many-arguments

from six.moves.queue import Empty

from unqstr import ustr
from qtpy import QtGui

from addresses import decodeAddress, addBMIfNotPresent
from bmconfigparser import config
from queues import apiAddressGeneratorReturnQueue, addressGeneratorQueue
from tr import _translate
from .utils import str_chan


class AddressPassPhraseValidatorMixin(object):
    """Bitmessage address or passphrase validator class for Qt UI"""
    def setParams(
        self, passPhraseObject=None, addressObject=None,
        feedBackObject=None, button=None, addressMandatory=True
    ):
        """Initialization"""
        self.addressObject = addressObject
        self.passPhraseObject = passPhraseObject
        self.feedBackObject = feedBackObject
        self.addressMandatory = addressMandatory
        self.isValid = False
        # save default text
        self.okButton = button
        self.okButtonLabel = button.text()

    def setError(self, string):
        """Indicate that the validation is pending or failed"""
        if string is not None and self.feedBackObject is not None:
            font = QtGui.QFont()
            font.setBold(True)
            self.feedBackObject.setFont(font)
            self.feedBackObject.setStyleSheet("QLabel { color : red; }")
            self.feedBackObject.setText(string)
        self.isValid = False
        if self.okButton:
            self.okButton.setEnabled(False)
            if string is not None and self.feedBackObject is not None:
                self.okButton.setText(
                    _translate("AddressValidator", "Invalid"))
            else:
                self.okButton.setText(
                    _translate("AddressValidator", "Validating..."))

    def setOK(self, string):
        """Indicate that the validation succeeded"""
        if string is not None and self.feedBackObject is not None:
            font = QtGui.QFont()
            font.setBold(False)
            self.feedBackObject.setFont(font)
            self.feedBackObject.setStyleSheet("QLabel { }")
            self.feedBackObject.setText(string)
        self.isValid = True
        if self.okButton:
            self.okButton.setEnabled(True)
            self.okButton.setText(self.okButtonLabel)

    def checkQueue(self):
        """Validator queue loop"""
        gotOne = False

        # wait until processing is done
        if not addressGeneratorQueue.empty():
            self.setError(None)
            return None

        while True:
            try:
                addressGeneratorReturnValue = \
                    apiAddressGeneratorReturnQueue.get(False)
            except Empty:
                if gotOne:
                    break
                else:
                    return None
            else:
                gotOne = True

        if not addressGeneratorReturnValue:
            self.setError(_translate(
                "AddressValidator",
                "Address already present as one of your identities."
            ))
            return
        if addressGeneratorReturnValue[0] == \
                'chan name does not match address':
            self.setError(_translate(
                "AddressValidator",
                "Although the Bitmessage address you entered was valid,"
                " it doesn\'t match the chan name."
            ))
            return
        self.setOK(_translate(
            "MainWindow", "Passphrase and address appear to be valid."))

    def returnValid(self):
        """Return the value of whether the validation was successful"""
        return QtGui.QValidator.Acceptable if self.isValid \
            else QtGui.QValidator.Intermediate

    def validate(self, s, pos):
        """Top level validator method"""
        try:
            address = ustr(self.addressObject.text())
        except AttributeError:
            address = None
        try:
            passPhrase = ustr(self.passPhraseObject.text())
        except AttributeError:
            passPhrase = ""

        # no chan name
        if not passPhrase:
            self.setError(_translate(
                "AddressValidator",
                "Chan name/passphrase needed. You didn't enter a chan name."
            ))
            return (QtGui.QValidator.Intermediate, s, pos)

        if self.addressMandatory or address:
            # check if address already exists:
            if address in config.addresses(True):
                self.setError(_translate(
                    "AddressValidator",
                    "Address already present as one of your identities."
                ))
                return (QtGui.QValidator.Intermediate, s, pos)

            status = decodeAddress(address)[0]
            # version too high
            if status == 'versiontoohigh':
                self.setError(_translate(
                    "AddressValidator",
                    "Address too new. Although that Bitmessage address"
                    " might be valid, its version number is too new"
                    " for us to handle. Perhaps you need to upgrade"
                    " Bitmessage."
                ))
                return (QtGui.QValidator.Intermediate, s, pos)
            # invalid
            if status != 'success':
                self.setError(_translate(
                    "AddressValidator",
                    "The Bitmessage address is not valid."
                ))
                return (QtGui.QValidator.Intermediate, s, pos)

        # this just disables the OK button without changing the feedback text
        # but only if triggered by textEdited, not by clicking the Ok button
        if not self.okButton.hasFocus():
            self.setError(None)

        # check through generator
        if not address:
            addressGeneratorQueue.put((
                'createChan', 4, 1,
                str_chan + ' ' + passPhrase, passPhrase.encode("utf-8", "replace"), False
            ))
        else:
            addressGeneratorQueue.put((
                'joinChan', addBMIfNotPresent(address),
                "{} {}".format(str_chan, passPhrase), passPhrase.encode("utf-8", "replace"), False
            ))

        if self.okButton.hasFocus():
            return (self.returnValid(), s, pos)
        else:
            return (QtGui.QValidator.Intermediate, s, pos)

    def checkData(self):
        """Validator Qt signal interface"""
        return self.validate(u"", 0)


class AddressValidator(QtGui.QValidator, AddressPassPhraseValidatorMixin):
    """AddressValidator class for Qt UI"""
    def __init__(
        self, parent=None, passPhraseObject=None, feedBackObject=None,
        button=None, addressMandatory=True
    ):
        super(AddressValidator, self).__init__(parent)
        self.setParams(
            passPhraseObject, parent, feedBackObject, button,
            addressMandatory)


class PassPhraseValidator(QtGui.QValidator, AddressPassPhraseValidatorMixin):
    """PassPhraseValidator class for Qt UI"""
    def __init__(
        self, parent=None, addressObject=None, feedBackObject=None,
        button=None, addressMandatory=False
    ):
        super(PassPhraseValidator, self).__init__(parent)
        self.setParams(
            parent, addressObject, feedBackObject, button,
            addressMandatory)
