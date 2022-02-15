"""
NewChanDialog class definition
"""

from PyQt5 import QtCore, QtWidgets

import widgets
from addresses import addBMIfNotPresent
from addressvalidator import AddressValidator, PassPhraseValidator
from queues import (
    addressGeneratorQueue, apiAddressGeneratorReturnQueue, UISignalQueue)
from tr import _translate
from utils import str_chan


class NewChanDialog(QtWidgets.QDialog):
    """The "New Chan" dialog"""
    def __init__(self, parent=None):
        super(NewChanDialog, self).__init__(parent)
        widgets.load('newchandialog.ui', self)
        self.parent = parent
        self.chanAddress.setValidator(AddressValidator(
            self.chanAddress, self.chanPassPhrase, self.validatorFeedback,
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok), False))
        self.chanPassPhrase.setValidator(PassPhraseValidator(
            self.chanPassPhrase, self.chanAddress, self.validatorFeedback,
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok), False))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.delayedUpdateStatus)
        self.timer.start(500)  # milliseconds
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.show()

    def delayedUpdateStatus(self):
        """Related to updating the UI for the chan passphrase validity"""
        self.chanPassPhrase.validator().checkQueue()

    def accept(self):
        """Proceed in joining the chan"""
        self.timer.stop()
        self.hide()
        apiAddressGeneratorReturnQueue.queue.clear()
        passPhrase = self.chanPassPhrase.text().encode('utf-8')
        if self.chanAddress.text() == "":
            addressGeneratorQueue.put((
                'createChan', 4, 1,
                str_chan + ' ' + passPhrase, passPhrase, True
            ))
        else:
            addressGeneratorQueue.put((
                'joinChan', addBMIfNotPresent(self.chanAddress.text()),
                str_chan + ' ' + passPhrase, passPhrase, True
            ))
        addressGeneratorReturnValue = apiAddressGeneratorReturnQueue.get(True)
        if (
            len(addressGeneratorReturnValue) > 0
            and addressGeneratorReturnValue[0]
            != 'chan name does not match address'
        ):
            UISignalQueue.put((
                'updateStatusBar',
                _translate(
                    "newchandialog",
                    "Successfully created / joined chan {0}"
                ).format(passPhrase)
            ))
            self.parent.ui.tabWidget.setCurrentIndex(
                self.parent.ui.tabWidget.indexOf(self.parent.ui.chans)
            )
            self.done(QtWidgets.QDialog.Accepted)
        else:
            UISignalQueue.put((
                'updateStatusBar',
                _translate("newchandialog", "Chan creation / joining failed")
            ))
            self.done(QtWidgets.QDialog.Rejected)

    def reject(self):
        """Cancel joining the chan"""
        self.timer.stop()
        self.hide()
        UISignalQueue.put((
            'updateStatusBar',
            _translate("newchandialog", "Chan creation / joining cancelled")
        ))
        self.done(QtWidgets.QDialog.Rejected)
