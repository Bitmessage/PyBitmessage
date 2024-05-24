"""
src/bitmessageqt/newchandialog.py
=================================

"""

from ver import ustr, unic
from PyQt4 import QtCore, QtGui

from bitmessageqt import widgets
from addresses import addBMIfNotPresent
from .addressvalidator import AddressValidator, PassPhraseValidator
from queues import (
    addressGeneratorQueue, apiAddressGeneratorReturnQueue, UISignalQueue)
from tr import _translate
from .utils import str_chan


class NewChanDialog(QtGui.QDialog):
    """The `New Chan` dialog"""
    def __init__(self, parent=None):
        super(NewChanDialog, self).__init__(parent)
        widgets.load('newchandialog.ui', self)
        self.parent = parent
        self.chanAddress.setValidator(
            AddressValidator(
                self.chanAddress,
                self.chanPassPhrase,
                self.validatorFeedback,
                self.buttonBox,
                False))
        self.chanPassPhrase.setValidator(
            PassPhraseValidator(
                self.chanPassPhrase,
                self.chanAddress,
                self.validatorFeedback,
                self.buttonBox,
                False))

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(  # pylint: disable=no-member
            self.timer, QtCore.SIGNAL("timeout()"), self.delayedUpdateStatus)
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
        if ustr(self.chanAddress.text()) == "":
            addressGeneratorQueue.put(
                ('createChan', 4, 1, str_chan + ' ' + ustr(self.chanPassPhrase.text()),
                 ustr(self.chanPassPhrase.text()),
                 True))
        else:
            addressGeneratorQueue.put(
                ('joinChan', addBMIfNotPresent(ustr(self.chanAddress.text())),
                 str_chan + ' ' + ustr(self.chanPassPhrase.text()),
                 ustr(self.chanPassPhrase.text()),
                 True))
        addressGeneratorReturnValue = apiAddressGeneratorReturnQueue.get(True)
        if addressGeneratorReturnValue and addressGeneratorReturnValue[0] != 'chan name does not match address':
            UISignalQueue.put(('updateStatusBar', _translate(
                "newchandialog", "Successfully created / joined chan {0}").format(unic(ustr(self.chanPassPhrase.text())))))
            self.parent.ui.tabWidget.setCurrentIndex(
                self.parent.ui.tabWidget.indexOf(self.parent.ui.chans)
            )
            self.done(QtGui.QDialog.Accepted)
        else:
            UISignalQueue.put(('updateStatusBar', _translate("newchandialog", "Chan creation / joining failed")))
            self.done(QtGui.QDialog.Rejected)

    def reject(self):
        """Cancel joining the chan"""
        self.timer.stop()
        self.hide()
        UISignalQueue.put(('updateStatusBar', _translate("newchandialog", "Chan creation / joining cancelled")))
        self.done(QtGui.QDialog.Rejected)
