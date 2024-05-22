import sys

from qtpy import QtCore

import queues
from network.node import Peer


class UISignaler(QtCore.QThread):
    _instance = None

    writeNewAddressToTable = QtCore.Signal(str, str, str)
    updateStatusBar = QtCore.Signal(object)
    updateSentItemStatusByToAddress = QtCore.Signal(object, str)
    updateSentItemStatusByAckdata = QtCore.Signal(object, str)
    displayNewInboxMessage = QtCore.Signal(object, str, object, object, str)
    displayNewSentMessage = QtCore.Signal(
        object, str, str, object, object, str)
    updateNetworkStatusTab = QtCore.Signal(bool, bool, Peer)
    updateNumberOfMessagesProcessed = QtCore.Signal()
    updateNumberOfPubkeysProcessed = QtCore.Signal()
    updateNumberOfBroadcastsProcessed = QtCore.Signal()
    setStatusIcon = QtCore.Signal(str)
    changedInboxUnread = QtCore.Signal(str)
    rerenderMessagelistFromLabels = QtCore.Signal()
    rerenderMessagelistToLabels = QtCore.Signal()
    rerenderAddressBook = QtCore.Signal()
    rerenderSubscriptions = QtCore.Signal()
    rerenderBlackWhiteList = QtCore.Signal()
    removeInboxRowByMsgid = QtCore.Signal(str)
    newVersionAvailable = QtCore.Signal(str)
    displayAlert = QtCore.Signal(str, str, bool)

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
                self.writeNewAddressToTable.emit(
                    label, address, str(streamNumber))
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

                self.displayNewInboxMessage.emit(
                    inventoryHash, toAddress, fromAddress,
                    subject, body)
            elif command == 'displayNewSentMessage':
                toAddress, fromLabel, fromAddress, subject, message, ackdata = data
                self.displayNewSentMessage.emit(
                    toAddress, fromLabel, fromAddress,
                    subject.decode('utf-8'), message, ackdata)
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
                    'Command sent to UISignaler not recognized: %s\n'
                    % command
                )
