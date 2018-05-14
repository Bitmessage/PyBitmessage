from PyQt4 import QtCore, QtGui

from addresses import addBMIfNotPresent
from addressvalidator import AddressValidator, PassPhraseValidator
from queues import apiAddressGeneratorReturnQueue, addressGeneratorQueue, UISignalQueue
from retranslateui import RetranslateMixin
from tr import _translate
from utils import str_chan
import widgets

class NewChanDialog(QtGui.QDialog, RetranslateMixin):
    def __init__(self, parent=None):
        super(NewChanDialog, self).__init__(parent)
        widgets.load('newchandialog.ui', self)
        self.parent = parent
        self.chanAddress.setValidator(AddressValidator(self.chanAddress, self.chanPassPhrase, self.validatorFeedback, self.buttonBox, False))
        self.chanPassPhrase.setValidator(PassPhraseValidator(self.chanPassPhrase, self.chanAddress, self.validatorFeedback, self.buttonBox, False))

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.delayedUpdateStatus)
        self.timer.start(500) # milliseconds
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.show()

    def delayedUpdateStatus(self):
        self.chanPassPhrase.validator().checkQueue()

    def accept(self):
        self.timer.stop()
        self.hide()
        apiAddressGeneratorReturnQueue.queue.clear()
        if self.chanAddress.text().toUtf8() == "":
            addressGeneratorQueue.put(('createChan', 4, 1, str_chan + ' ' + str(self.chanPassPhrase.text().toUtf8()), self.chanPassPhrase.text().toUtf8(), True))
        else:
            addressGeneratorQueue.put(('joinChan', addBMIfNotPresent(self.chanAddress.text().toUtf8()), str_chan + ' ' + str(self.chanPassPhrase.text().toUtf8()), self.chanPassPhrase.text().toUtf8(), True))
        addressGeneratorReturnValue = apiAddressGeneratorReturnQueue.get(True)
        if len(addressGeneratorReturnValue) > 0 and addressGeneratorReturnValue[0] != 'chan name does not match address':
            UISignalQueue.put(('updateStatusBar', _translate("newchandialog", "Successfully created / joined chan %1").arg(unicode(self.chanPassPhrase.text()))))
            self.parent.ui.tabWidget.setCurrentIndex(
                self.parent.ui.tabWidget.indexOf(self.parent.ui.chans)
            )
            self.done(QtGui.QDialog.Accepted)
        else:
            UISignalQueue.put(('updateStatusBar', _translate("newchandialog", "Chan creation / joining failed")))
            self.done(QtGui.QDialog.Rejected)

    def reject(self):
        self.timer.stop()
        self.hide()
        UISignalQueue.put(('updateStatusBar', _translate("newchandialog", "Chan creation / joining cancelled")))
        self.done(QtGui.QDialog.Rejected)
