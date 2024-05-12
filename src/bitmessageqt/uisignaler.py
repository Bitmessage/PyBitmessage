
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
                self.emit(
                    SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),
                    label,
                    address,
                    str(streamNumber))
            elif command == 'updateStatusBar':
                self.updateStatusBar.emit(data)
            elif command == 'updateSentItemStatusByToAddress':
                toAddress, message = data
                self.emit(SIGNAL(
                    "updateSentItemStatusByToAddress(PyQt_PyObject,PyQt_PyObject)"), toAddress, message)
            elif command == 'updateSentItemStatusByAckdata':
                ackData, message = data
                self.emit(SIGNAL(
                    "updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"), ackData, message)
            elif command == 'displayNewInboxMessage':
                inventoryHash, toAddress, fromAddress, subject, body = data
                self.emit(SIGNAL(
                    "displayNewInboxMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),
                    inventoryHash, toAddress, fromAddress, subject, body)
            elif command == 'displayNewSentMessage':
                toAddress, fromLabel, fromAddress, subject, message, ackdata = data
                self.emit(SIGNAL(
                    "displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),
                    toAddress, fromLabel, fromAddress, subject, message, ackdata)
            elif command == 'updateNetworkStatusTab':
                outbound, add, destination = data
                self.emit(
                    SIGNAL("updateNetworkStatusTab(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),
                    outbound,
                    add,
                    destination)
            elif command == 'updateNumberOfMessagesProcessed':
                self.emit(SIGNAL("updateNumberOfMessagesProcessed()"))
            elif command == 'updateNumberOfPubkeysProcessed':
                self.emit(SIGNAL("updateNumberOfPubkeysProcessed()"))
            elif command == 'updateNumberOfBroadcastsProcessed':
                self.emit(SIGNAL("updateNumberOfBroadcastsProcessed()"))
            elif command == 'setStatusIcon':
                self.emit(SIGNAL("setStatusIcon(PyQt_PyObject)"), data)
            elif command == 'changedInboxUnread':
                self.emit(SIGNAL("changedInboxUnread(PyQt_PyObject)"), data)
            elif command == 'rerenderMessagelistFromLabels':
                self.emit(SIGNAL("rerenderMessagelistFromLabels()"))
            elif command == 'rerenderMessagelistToLabels':
                self.emit(SIGNAL("rerenderMessagelistToLabels()"))
            elif command == 'rerenderAddressBook':
                self.emit(SIGNAL("rerenderAddressBook()"))
            elif command == 'rerenderSubscriptions':
                self.emit(SIGNAL("rerenderSubscriptions()"))
            elif command == 'rerenderBlackWhiteList':
                self.emit(SIGNAL("rerenderBlackWhiteList()"))
            elif command == 'removeInboxRowByMsgid':
                self.emit(SIGNAL("removeInboxRowByMsgid(PyQt_PyObject)"), data)
            elif command == 'newVersionAvailable':
                self.emit(SIGNAL("newVersionAvailable(PyQt_PyObject)"), data)
            elif command == 'alert':
                title, text, exitAfterUserClicksOk = data
                self.emit(
                    SIGNAL("displayAlert(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"),
                    title,
                    text,
                    exitAfterUserClicksOk)
            else:
                sys.stderr.write(
                    'Command sent to UISignaler not recognized: %s\n' % command)
