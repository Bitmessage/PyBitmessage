
from PyQt6.QtCore import QThread, pyqtSignal
import sys

import queues


class UISignaler(QThread):
    _instance = None

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    rerenderBlackWhiteList = pyqtSignal()
    updateNumberOfMessagesProcessed = pyqtSignal()
    updateNumberOfPubkeysProcessed = pyqtSignal()
    updateNumberOfBroadcastsProcessed = pyqtSignal()
    updateNetworkStatusTab = pyqtSignal(object, object, object)
    writeNewAddressToTable = pyqtSignal(object, object, object)
    updateStatusBar = pyqtSignal(object)
    updateSentItemStatusByToAddress = pyqtSignal(object, object)
    updateSentItemStatusByAckdata = pyqtSignal(object, object)
    displayNewInboxMessage = pyqtSignal(object, object, object, object, object)
    displayNewSentMessage = pyqtSignal(object, object, object, object, object, object)
    setStatusIcon = pyqtSignal(object)
    changedInboxUnread = pyqtSignal(object)
    rerenderMessagelistFromLabels = pyqtSignal()
    rerenderMessagelistToLabels = pyqtSignal()
    rerenderAddressBook = pyqtSignal()
    rerenderSubscriptions = pyqtSignal()
    removeInboxRowByMsgid = pyqtSignal(object)
    newVersionAvailable = pyqtSignal(object)
    displayAlert = pyqtSignal(object, object, object)

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = UISignaler()
        return cls._instance

    def run(self):
        while True:
            command, data = queues.UISignalQueue.get()
            if command == 'writeNewAddressToTable':
                label, address, streamNumber = data
                self.writeNewAddressToTable.emit(label, address, str(streamNumber))
            elif command == 'updateStatusBar':
                self.updateStatusBar.emit(data)
            elif command == 'updateSentItemStatusByToAddress':
                toAddress, message = data
                self.updateSentItemStatusByToAddress.emit(toAddress, message)
            elif command == 'updateSentItemStatusByAckdata':
                ackData, message = data
                self.updateSentItemStatusByAckdata.emit(ackData, message)
            elif command == 'displayNewInboxMessage':
                inventoryHash, toAddress, fromAddress, subject, body = data
                self.displayNewInboxMessage.emit(inventoryHash, toAddress, fromAddress, subject, body)
            elif command == 'displayNewSentMessage':
                toAddress, fromLabel, fromAddress, subject, message, ackdata = data
                self.displayNewSentMessage.emit(toAddress, fromLabel, fromAddress, subject, message, ackdata)
            elif command == 'updateNetworkStatusTab':
                outbound, add, destination = data
                self.updateNetworkStatusTab.emit(outbound, add, destination)
            elif command == 'updateNumberOfMessagesProcessed':
                self.updateNumberOfMessagesProcessed.emit()
            elif command == 'updateNumberOfPubkeysProcessed':
                self.updateNumberOfPubkeysProcessed.emit()
            elif command == 'updateNumberOfBroadcastsProcessed':
                self.updateNumberOfBroadcastsProcessed.emit()
            elif command == 'setStatusIcon':
                self.setStatusIcon.emit(data)
            elif command == 'changedInboxUnread':
                self.changedInboxUnread.emit(data)
            elif command == 'rerenderMessagelistFromLabels':
                self.rerenderMessagelistFromLabels.emit()
            elif command == 'rerenderMessagelistToLabels':
                self.rerenderMessagelistToLabels.emit()
            elif command == 'rerenderAddressBook':
                self.rerenderAddressBook.emit()
            elif command == 'rerenderSubscriptions':
                self.rerenderSubscriptions.emit()
            elif command == 'rerenderBlackWhiteList':
                self.rerenderBlackWhiteList.emit()
            elif command == 'removeInboxRowByMsgid':
                self.removeInboxRowByMsgid.emit(data)
            elif command == 'newVersionAvailable':
                self.newVersionAvailable.emit(data)
            elif command == 'alert':
                title, text, exitAfterUserClicksOk = data
                self.displayAlert.emit(title, text, exitAfterUserClicksOk)
            else:
                sys.stderr.write(
                    'Command sent to UISignaler not recognized: %s\n' % command)
