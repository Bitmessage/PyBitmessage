try:
    import locale
except:
    pass

withMessagingMenu = False
try:
    from gi.repository import MessagingMenu
    from gi.repository import Notify
    withMessagingMenu = True
except ImportError:
    MessagingMenu = None

from addresses import *
import shared
from bitmessageui import *
from newaddressdialog import *
from newsubscriptiondialog import *
from regenerateaddresses import *
from specialaddressbehavior import *
from settings import *
from about import *
from help import *
from iconglossary import *
import sys
from time import strftime, localtime, gmtime
import time
import os
from pyelliptic.openssl import OpenSSL
import pickle
import platform
import debug
from debug import logger

try:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except Exception as err:
    print 'PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API. You can download it from http://www.riverbankcomputing.com/software/pyqt/download or by searching Google for \'PyQt Download\' (without quotes).'
    print 'Error message:', err
    sys.exit()

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
except AttributeError:
    print 'QtGui.QApplication.UnicodeUTF8 error:', err

def _translate(context, text):
    return QtGui.QApplication.translate(context, text)


class MyForm(QtGui.QMainWindow):

    str_broadcast_subscribers = '[Broadcast subscribers]'

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Ask the user if we may delete their old version 1 addresses if they
        # have any.
        configSections = shared.config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile != 'bitmessagesettings':
                status, addressVersionNumber, streamNumber, hash = decodeAddress(
                    addressInKeysFile)
                if addressVersionNumber == 1:
                    displayMsg = _translate(
                        "MainWindow", "One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. "
                        + "May we delete it now?").arg(addressInKeysFile)
                    reply = QtGui.QMessageBox.question(
                        self, 'Message', displayMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        shared.config.remove_section(addressInKeysFile)
                        with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                            shared.config.write(configfile)

        # Configure Bitmessage to start on startup (or remove the
        # configuration) based on the setting in the keys.dat file
        if 'win32' in sys.platform or 'win64' in sys.platform:
            # Auto-startup for Windows
            RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            self.settings = QSettings(RUN_PATH, QSettings.NativeFormat)
            self.settings.remove(
                "PyBitmessage")  # In case the user moves the program and the registry entry is no longer valid, this will delete the old registry entry.
            if shared.config.getboolean('bitmessagesettings', 'startonlogon'):
                self.settings.setValue("PyBitmessage", sys.argv[0])
        elif 'darwin' in sys.platform:
            # startup for mac
            pass
        elif 'linux' in sys.platform:
            # startup for linux
            pass

        self.ui.labelSendBroadcastWarning.setVisible(False)

        # FILE MENU and other buttons
        QtCore.QObject.connect(self.ui.actionExit, QtCore.SIGNAL(
            "triggered()"), self.quit)
        QtCore.QObject.connect(self.ui.actionManageKeys, QtCore.SIGNAL(
            "triggered()"), self.click_actionManageKeys)
        QtCore.QObject.connect(self.ui.actionDeleteAllTrashedMessages, QtCore.SIGNAL(
            "triggered()"), self.click_actionDeleteAllTrashedMessages)
        QtCore.QObject.connect(self.ui.actionRegenerateDeterministicAddresses, QtCore.SIGNAL(
            "triggered()"), self.click_actionRegenerateDeterministicAddresses)
        QtCore.QObject.connect(self.ui.pushButtonNewAddress, QtCore.SIGNAL(
            "clicked()"), self.click_NewAddressDialog)
        QtCore.QObject.connect(self.ui.comboBoxSendFrom, QtCore.SIGNAL(
            "activated(int)"), self.redrawLabelFrom)
        QtCore.QObject.connect(self.ui.pushButtonAddAddressBook, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonAddAddressBook)
        QtCore.QObject.connect(self.ui.pushButtonAddSubscription, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonAddSubscription)
        QtCore.QObject.connect(self.ui.pushButtonAddBlacklist, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonAddBlacklist)
        QtCore.QObject.connect(self.ui.pushButtonSend, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonSend)
        QtCore.QObject.connect(self.ui.pushButtonLoadFromAddressBook, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonLoadFromAddressBook)
        QtCore.QObject.connect(self.ui.radioButtonBlacklist, QtCore.SIGNAL(
            "clicked()"), self.click_radioButtonBlacklist)
        QtCore.QObject.connect(self.ui.radioButtonWhitelist, QtCore.SIGNAL(
            "clicked()"), self.click_radioButtonWhitelist)
        QtCore.QObject.connect(self.ui.pushButtonStatusIcon, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonStatusIcon)
        QtCore.QObject.connect(self.ui.actionSettings, QtCore.SIGNAL(
            "triggered()"), self.click_actionSettings)
        QtCore.QObject.connect(self.ui.actionAbout, QtCore.SIGNAL(
            "triggered()"), self.click_actionAbout)
        QtCore.QObject.connect(self.ui.actionHelp, QtCore.SIGNAL(
            "triggered()"), self.click_actionHelp)

        # Popup menu for the Inbox tab
        self.ui.inboxContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionReply = self.ui.inboxContextMenuToolbar.addAction(_translate(
            "MainWindow", "Reply"), self.on_action_InboxReply)
        self.actionAddSenderToAddressBook = self.ui.inboxContextMenuToolbar.addAction(_translate(
            "MainWindow", "Add sender to your Address Book"), self.on_action_InboxAddSenderToAddressBook)
        self.actionTrashInboxMessage = self.ui.inboxContextMenuToolbar.addAction(
            _translate("MainWindow", "Move to Trash"), self.on_action_InboxTrash)
        self.actionForceHtml = self.ui.inboxContextMenuToolbar.addAction(_translate(
            "MainWindow", "View HTML code as formatted text"), self.on_action_InboxMessageForceHtml)
        self.actionSaveMessageAs = self.ui.inboxContextMenuToolbar.addAction(_translate(
            "MainWindow", "Save message as..."), self.on_action_InboxSaveMessageAs)
        self.ui.tableWidgetInbox.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.connect(self.ui.tableWidgetInbox, QtCore.SIGNAL(
            'customContextMenuRequested(const QPoint&)'), self.on_context_menuInbox)
        self.popMenuInbox = QtGui.QMenu(self)
        self.popMenuInbox.addAction(self.actionForceHtml)
        self.popMenuInbox.addSeparator()
        self.popMenuInbox.addAction(self.actionReply)
        self.popMenuInbox.addAction(self.actionAddSenderToAddressBook)
        self.popMenuInbox.addSeparator()
        self.popMenuInbox.addAction( self.actionSaveMessageAs )
        self.popMenuInbox.addAction( self.actionTrashInboxMessage )

        # Popup menu for the Your Identities tab
        self.ui.addressContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionNew = self.ui.addressContextMenuToolbar.addAction(_translate(
            "MainWindow", "New"), self.on_action_YourIdentitiesNew)
        self.actionEnable = self.ui.addressContextMenuToolbar.addAction(_translate(
            "MainWindow", "Enable"), self.on_action_YourIdentitiesEnable)
        self.actionDisable = self.ui.addressContextMenuToolbar.addAction(_translate(
            "MainWindow", "Disable"), self.on_action_YourIdentitiesDisable)
        self.actionClipboard = self.ui.addressContextMenuToolbar.addAction(_translate(
            "MainWindow", "Copy address to clipboard"), self.on_action_YourIdentitiesClipboard)
        self.actionSpecialAddressBehavior = self.ui.addressContextMenuToolbar.addAction(_translate(
            "MainWindow", "Special address behavior..."), self.on_action_SpecialAddressBehaviorDialog)
        self.ui.tableWidgetYourIdentities.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.connect(self.ui.tableWidgetYourIdentities, QtCore.SIGNAL(
            'customContextMenuRequested(const QPoint&)'), self.on_context_menuYourIdentities)
        self.popMenu = QtGui.QMenu(self)
        self.popMenu.addAction(self.actionNew)
        self.popMenu.addSeparator()
        self.popMenu.addAction(self.actionClipboard)
        self.popMenu.addSeparator()
        self.popMenu.addAction(self.actionEnable)
        self.popMenu.addAction(self.actionDisable)
        self.popMenu.addAction(self.actionSpecialAddressBehavior)

        # Popup menu for the Address Book page
        self.ui.addressBookContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionAddressBookSend = self.ui.addressBookContextMenuToolbar.addAction(_translate(
            "MainWindow", "Send message to this address"), self.on_action_AddressBookSend)
        self.actionAddressBookClipboard = self.ui.addressBookContextMenuToolbar.addAction(_translate(
            "MainWindow", "Copy address to clipboard"), self.on_action_AddressBookClipboard)
        self.actionAddressBookSubscribe = self.ui.addressBookContextMenuToolbar.addAction(_translate(
            "MainWindow", "Subscribe to this address"), self.on_action_AddressBookSubscribe)
        self.actionAddressBookNew = self.ui.addressBookContextMenuToolbar.addAction(_translate(
            "MainWindow", "Add New Address"), self.on_action_AddressBookNew)
        self.actionAddressBookDelete = self.ui.addressBookContextMenuToolbar.addAction(_translate(
            "MainWindow", "Delete"), self.on_action_AddressBookDelete)
        self.ui.tableWidgetAddressBook.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL(
            'customContextMenuRequested(const QPoint&)'), self.on_context_menuAddressBook)
        self.popMenuAddressBook = QtGui.QMenu(self)
        self.popMenuAddressBook.addAction(self.actionAddressBookSend)
        self.popMenuAddressBook.addAction(self.actionAddressBookClipboard)
        self.popMenuAddressBook.addAction( self.actionAddressBookSubscribe )
        self.popMenuAddressBook.addSeparator()
        self.popMenuAddressBook.addAction(self.actionAddressBookNew)
        self.popMenuAddressBook.addAction(self.actionAddressBookDelete)

        # Popup menu for the Subscriptions page
        self.ui.subscriptionsContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionsubscriptionsNew = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "New"), self.on_action_SubscriptionsNew)
        self.actionsubscriptionsDelete = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Delete"), self.on_action_SubscriptionsDelete)
        self.actionsubscriptionsClipboard = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Copy address to clipboard"), self.on_action_SubscriptionsClipboard)
        self.actionsubscriptionsEnable = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Enable"), self.on_action_SubscriptionsEnable)
        self.actionsubscriptionsDisable = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Disable"), self.on_action_SubscriptionsDisable)
        self.ui.tableWidgetSubscriptions.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.connect(self.ui.tableWidgetSubscriptions, QtCore.SIGNAL(
            'customContextMenuRequested(const QPoint&)'), self.on_context_menuSubscriptions)
        self.popMenuSubscriptions = QtGui.QMenu(self)
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsNew)
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsDelete)
        self.popMenuSubscriptions.addSeparator()
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsEnable)
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsDisable)
        self.popMenuSubscriptions.addSeparator()
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsClipboard)

        # Popup menu for the Sent page
        self.ui.sentContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionTrashSentMessage = self.ui.sentContextMenuToolbar.addAction(_translate(
            "MainWindow", "Move to Trash"), self.on_action_SentTrash)
        self.actionSentClipboard = self.ui.sentContextMenuToolbar.addAction(_translate(
            "MainWindow", "Copy destination address to clipboard"), self.on_action_SentClipboard)
        self.actionForceSend = self.ui.sentContextMenuToolbar.addAction(_translate(
            "MainWindow", "Force send"), self.on_action_ForceSend)
        self.ui.tableWidgetSent.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.connect(self.ui.tableWidgetSent, QtCore.SIGNAL(
            'customContextMenuRequested(const QPoint&)'), self.on_context_menuSent)
        # self.popMenuSent = QtGui.QMenu( self )
        # self.popMenuSent.addAction( self.actionSentClipboard )
        # self.popMenuSent.addAction( self.actionTrashSentMessage )

        # Popup menu for the Blacklist page
        self.ui.blacklistContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionBlacklistNew = self.ui.blacklistContextMenuToolbar.addAction(_translate(
            "MainWindow", "Add new entry"), self.on_action_BlacklistNew)
        self.actionBlacklistDelete = self.ui.blacklistContextMenuToolbar.addAction(_translate(
            "MainWindow", "Delete"), self.on_action_BlacklistDelete)
        self.actionBlacklistClipboard = self.ui.blacklistContextMenuToolbar.addAction(_translate(
            "MainWindow", "Copy address to clipboard"), self.on_action_BlacklistClipboard)
        self.actionBlacklistEnable = self.ui.blacklistContextMenuToolbar.addAction(_translate(
            "MainWindow", "Enable"), self.on_action_BlacklistEnable)
        self.actionBlacklistDisable = self.ui.blacklistContextMenuToolbar.addAction(_translate(
            "MainWindow", "Disable"), self.on_action_BlacklistDisable)
        self.ui.tableWidgetBlacklist.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.connect(self.ui.tableWidgetBlacklist, QtCore.SIGNAL(
            'customContextMenuRequested(const QPoint&)'), self.on_context_menuBlacklist)
        self.popMenuBlacklist = QtGui.QMenu(self)
        # self.popMenuBlacklist.addAction( self.actionBlacklistNew )
        self.popMenuBlacklist.addAction(self.actionBlacklistDelete)
        self.popMenuBlacklist.addSeparator()
        self.popMenuBlacklist.addAction(self.actionBlacklistClipboard)
        self.popMenuBlacklist.addSeparator()
        self.popMenuBlacklist.addAction(self.actionBlacklistEnable)
        self.popMenuBlacklist.addAction(self.actionBlacklistDisable)

        # Initialize the user's list of addresses on the 'Your Identities' tab.
        configSections = shared.config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile != 'bitmessagesettings':
                isEnabled = shared.config.getboolean(
                    addressInKeysFile, 'enabled')
                newItem = QtGui.QTableWidgetItem(unicode(
                    shared.config.get(addressInKeysFile, 'label'), 'utf-8)'))
                if not isEnabled:
                    newItem.setTextColor(QtGui.QColor(128, 128, 128))
                self.ui.tableWidgetYourIdentities.insertRow(0)
                self.ui.tableWidgetYourIdentities.setItem(0, 0, newItem)
                newItem = QtGui.QTableWidgetItem(addressInKeysFile)
                newItem.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                if not isEnabled:
                    newItem.setTextColor(QtGui.QColor(128, 128, 128))
                if shared.safeConfigGetBoolean(addressInKeysFile, 'mailinglist'):
                    newItem.setTextColor(QtGui.QColor(137, 04, 177))  # magenta
                self.ui.tableWidgetYourIdentities.setItem(0, 1, newItem)
                newItem = QtGui.QTableWidgetItem(str(
                    addressStream(addressInKeysFile)))
                newItem.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                if not isEnabled:
                    newItem.setTextColor(QtGui.QColor(128, 128, 128))
                self.ui.tableWidgetYourIdentities.setItem(0, 2, newItem)
                if isEnabled:
                    status, addressVersionNumber, streamNumber, hash = decodeAddress(
                        addressInKeysFile)

        # Load inbox from messages database file
        self.loadInbox()

        # Load Sent items from database
        self.loadSent()

        # Initialize the address book
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put('SELECT * FROM addressbook')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            label, address = row
            self.ui.tableWidgetAddressBook.insertRow(0)
            newItem = QtGui.QTableWidgetItem(unicode(label, 'utf-8'))
            self.ui.tableWidgetAddressBook.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(address)
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetAddressBook.setItem(0, 1, newItem)

        # Initialize the Subscriptions
        self.rerenderSubscriptions()

        # Initialize the inbox search
        QtCore.QObject.connect(self.ui.inboxSearchLineEdit, QtCore.SIGNAL(
            "returnPressed()"), self.inboxSearchLineEditPressed)

        # Initialize the sent search
        QtCore.QObject.connect(self.ui.sentSearchLineEdit, QtCore.SIGNAL(
            "returnPressed()"), self.sentSearchLineEditPressed)

        # Initialize the Blacklist or Whitelist
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            self.loadBlackWhiteList()
        else:
            self.ui.tabWidget.setTabText(6, 'Whitelist')
            self.ui.radioButtonWhitelist.click()
            self.loadBlackWhiteList()

        QtCore.QObject.connect(self.ui.tableWidgetYourIdentities, QtCore.SIGNAL(
            "itemChanged(QTableWidgetItem *)"), self.tableWidgetYourIdentitiesItemChanged)
        QtCore.QObject.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL(
            "itemChanged(QTableWidgetItem *)"), self.tableWidgetAddressBookItemChanged)
        QtCore.QObject.connect(self.ui.tableWidgetSubscriptions, QtCore.SIGNAL(
            "itemChanged(QTableWidgetItem *)"), self.tableWidgetSubscriptionsItemChanged)
        QtCore.QObject.connect(self.ui.tableWidgetInbox, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.tableWidgetInboxItemClicked)
        QtCore.QObject.connect(self.ui.tableWidgetSent, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.tableWidgetSentItemClicked)

        # Put the colored icon on the status bar
        # self.ui.pushButtonStatusIcon.setIcon(QIcon(":/newPrefix/images/yellowicon.png"))
        self.statusbar = self.statusBar()
        self.statusbar.insertPermanentWidget(0, self.ui.pushButtonStatusIcon)
        self.ui.labelStartupTime.setText(_translate("MainWindow", "Since startup on %1").arg(
            unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))),'utf-8')))
        self.numberOfMessagesProcessed = 0
        self.numberOfBroadcastsProcessed = 0
        self.numberOfPubkeysProcessed = 0

        self.UISignalThread = UISignaler()
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByHash)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByAckdata)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "displayNewInboxMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewInboxMessage)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewSentMessage)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNetworkStatusTab()"), self.updateNetworkStatusTab)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "incrementNumberOfMessagesProcessed()"), self.incrementNumberOfMessagesProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "incrementNumberOfPubkeysProcessed()"), self.incrementNumberOfPubkeysProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "incrementNumberOfBroadcastsProcessed()"), self.incrementNumberOfBroadcastsProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "setStatusIcon(PyQt_PyObject)"), self.setStatusIcon)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderInboxFromLabels()"), self.rerenderInboxFromLabels)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderSubscriptions()"), self.rerenderSubscriptions)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "removeInboxRowByMsgid(PyQt_PyObject)"), self.removeInboxRowByMsgid)
        self.UISignalThread.start()

# Below this point, it would be good if all of the necessary global data
# structures were initialized.

        self.rerenderComboBoxSendFrom()

    # Show or hide the application window after clicking an item within the
    # tray icon or, on Windows, the try icon itself.
    def appIndicatorShowOrHideWindow(self):
        if not self.actionShow.isChecked():
            self.hide()
        else:
            if sys.platform[0:3] == 'win':
                self.setWindowFlags(Qt.Window)
            # else:
                # self.showMaximized()
            self.show()
            self.setWindowState(
                self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.activateWindow()

    # pointer to the application
    # app = None
    # The most recent message
    newMessageItem = None

    # The most recent broadcast
    newBroadcastItem = None

    # show the application window
    def appIndicatorShow(self):
        if self.actionShow is None:
            return
        if not self.actionShow.isChecked():
            self.actionShow.setChecked(True)
            self.appIndicatorShowOrHideWindow()

    # unchecks the show item on the application indicator
    def appIndicatorHide(self):
        if self.actionShow is None:
            return
        if self.actionShow.isChecked():
            self.actionShow.setChecked(False)
            self.appIndicatorShowOrHideWindow()

    # application indicator show or hide
    """# application indicator show or hide
    def appIndicatorShowBitmessage(self):
        #if self.actionShow == None:
        #    return
        print self.actionShow.isChecked()
        if not self.actionShow.isChecked():
            self.hide()
            #self.setWindowState(self.windowState() & QtCore.Qt.WindowMinimized)
        else:
            self.appIndicatorShowOrHideWindow()"""

    # Show the program window and select inbox tab
    def appIndicatorInbox(self, mm_app, source_id):
        self.appIndicatorShow()
        # select inbox
        self.ui.tabWidget.setCurrentIndex(0)
        selectedItem = None
        if source_id == 'Subscriptions':
            # select unread broadcast
            if self.newBroadcastItem is not None:
                selectedItem = self.newBroadcastItem
                self.newBroadcastItem = None
        else:
            # select unread message
            if self.newMessageItem is not None:
                selectedItem = self.newMessageItem
                self.newMessageItem = None
        # make it the current item
        if selectedItem is not None:
            try:
                self.ui.tableWidgetInbox.setCurrentItem(selectedItem)
            except Exception:
                self.ui.tableWidgetInbox.setCurrentCell(0, 0)
            self.tableWidgetInboxItemClicked()
        else:
            # just select the first item
            self.ui.tableWidgetInbox.setCurrentCell(0, 0)
            self.tableWidgetInboxItemClicked()

    # Show the program window and select send tab
    def appIndicatorSend(self):
        self.appIndicatorShow()
        self.ui.tabWidget.setCurrentIndex(1)

    # Show the program window and select subscriptions tab
    def appIndicatorSubscribe(self):
        self.appIndicatorShow()
        self.ui.tabWidget.setCurrentIndex(4)

    # Show the program window and select the address book tab
    def appIndicatorAddressBook(self):
        self.appIndicatorShow()
        self.ui.tabWidget.setCurrentIndex(5)

    # Load Sent items from database
    def loadSent(self, where="", what=""):
        what = "%" + what + "%"
        if where == "To":
            where = "toaddress"
        elif where == "From":
            where = "fromaddress"
        elif where == "Subject":
            where = "subject"
        elif where == "Message":
            where = "message"
        else:
            where = "toaddress || fromaddress || subject || message"

        sqlQuery = '''
            SELECT toaddress, fromaddress, subject, message, status, ackdata, lastactiontime 
            FROM sent WHERE folder="sent" AND %s LIKE ? 
            ORDER BY lastactiontime
            ''' % (where,)

        while self.ui.tableWidgetSent.rowCount() > 0:
            self.ui.tableWidgetSent.removeRow(0)

        t = (what,)
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(sqlQuery)
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            toAddress, fromAddress, subject, message, status, ackdata, lastactiontime = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            try:
                fromLabel = shared.config.get(fromAddress, 'label')
            except:
                fromLabel = ''
            if fromLabel == '':
                fromLabel = fromAddress

            toLabel = ''
            t = (toAddress,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''select label from addressbook where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()

            if queryreturn != []:
                for row in queryreturn:
                    toLabel, = row

            self.ui.tableWidgetSent.insertRow(0)
            if toLabel == '':
                newItem = QtGui.QTableWidgetItem(unicode(toAddress, 'utf-8'))
                newItem.setToolTip(unicode(toAddress, 'utf-8'))
            else:
                newItem = QtGui.QTableWidgetItem(unicode(toLabel, 'utf-8'))
                newItem.setToolTip(unicode(toLabel, 'utf-8'))
            newItem.setData(Qt.UserRole, str(toAddress))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetSent.setItem(0, 0, newItem)
            if fromLabel == '':
                newItem = QtGui.QTableWidgetItem(
                    unicode(fromAddress, 'utf-8'))
                newItem.setToolTip(unicode(fromAddress, 'utf-8'))
            else:
                newItem = QtGui.QTableWidgetItem(unicode(fromLabel, 'utf-8'))
                newItem.setToolTip(unicode(fromLabel, 'utf-8'))
            newItem.setData(Qt.UserRole, str(fromAddress))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetSent.setItem(0, 1, newItem)
            newItem = QtGui.QTableWidgetItem(unicode(subject, 'utf-8'))
            newItem.setToolTip(unicode(subject, 'utf-8'))
            newItem.setData(Qt.UserRole, unicode(message, 'utf-8)'))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetSent.setItem(0, 2, newItem)
            if status == 'awaitingpubkey':
                statusText = _translate(
                    "MainWindow", "Waiting on their encryption key. Will request it again soon.")
            elif status == 'doingpowforpubkey':
                statusText = _translate(
                    "MainWindow", "Encryption key request queued.")
            elif status == 'msgqueued':
                statusText = _translate(
                    "MainWindow", "Queued.")
            elif status == 'msgsent':
                statusText = _translate("MainWindow", "Message sent. Waiting on acknowledgement. Sent at %1").arg(
                    unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(lastactiontime)),'utf-8'))
            elif status == 'doingmsgpow':
                statusText = _translate(
                    "MainWindow", "Need to do work to send message. Work is queued.")
            elif status == 'ackreceived':
                statusText = _translate("MainWindow", "Acknowledgement of the message received %1").arg(
                    unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(lastactiontime)),'utf-8'))
            elif status == 'broadcastqueued':
                statusText = _translate(
                    "MainWindow", "Broadcast queued.")
            elif status == 'broadcastsent':
                statusText = _translate("MainWindow", "Broadcast on %1").arg(unicode(strftime(
                    shared.config.get('bitmessagesettings', 'timeformat'), localtime(lastactiontime)),'utf-8'))
            elif status == 'toodifficult':
                statusText = _translate("MainWindow", "Problem: The work demanded by the recipient is more difficult than you are willing to do. %1").arg(
                    unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(lastactiontime)),'utf-8'))
            elif status == 'badkey':
                statusText = _translate("MainWindow", "Problem: The recipient\'s encryption key is no good. Could not encrypt message. %1").arg(
                    unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(lastactiontime)),'utf-8'))
            elif status == 'forcepow':
                statusText = _translate(
                    "MainWindow", "Forced difficulty override. Send should start soon.")
            else:
                statusText = _translate("MainWindow", "Unknown status: %1 %2").arg(status).arg(unicode(
                    strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(lastactiontime)),'utf-8'))
            newItem = myTableWidgetItem(statusText)
            newItem.setToolTip(statusText)
            newItem.setData(Qt.UserRole, QByteArray(ackdata))
            newItem.setData(33, int(lastactiontime))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetSent.setItem(0, 3, newItem)
        self.ui.tableWidgetSent.sortItems(3, Qt.DescendingOrder)
        self.ui.tableWidgetSent.keyPressEvent = self.tableWidgetSentKeyPressEvent

    # Load inbox from messages database file
    def loadInbox(self, where="", what=""):
        what = "%" + what + "%"
        if where == "To":
            where = "toaddress"
        elif where == "From":
            where = "fromaddress"
        elif where == "Subject":
            where = "subject"
        elif where == "Message":
            where = "message"
        else:
            where = "toaddress || fromaddress || subject || message"

        sqlQuery = '''
            SELECT msgid, toaddress, fromaddress, subject, received, message, read 
            FROM inbox WHERE folder="inbox" AND %s LIKE ? 
            ORDER BY received
            ''' % (where,)

        while self.ui.tableWidgetInbox.rowCount() > 0:
            self.ui.tableWidgetInbox.removeRow(0)

        font = QFont()
        font.setBold(True)
        t = (what,)
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(sqlQuery)
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, received, message, read = row
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            message = shared.fixPotentiallyInvalidUTF8Data(message)
            try:
                if toAddress == self.str_broadcast_subscribers:
                    toLabel = self.str_broadcast_subscribers
                else:
                    toLabel = shared.config.get(toAddress, 'label')
            except:
                toLabel = ''
            if toLabel == '':
                toLabel = toAddress

            fromLabel = ''
            t = (fromAddress,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''select label from addressbook where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()

            if queryreturn != []:
                for row in queryreturn:
                    fromLabel, = row

            if fromLabel == '':  # If this address wasn't in our address book...
                t = (fromAddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''select label from subscriptions where address=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()

                if queryreturn != []:
                    for row in queryreturn:
                        fromLabel, = row

            self.ui.tableWidgetInbox.insertRow(0)
            newItem = QtGui.QTableWidgetItem(unicode(toLabel, 'utf-8'))
            newItem.setToolTip(unicode(toLabel, 'utf-8'))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not read:
                newItem.setFont(font)
            newItem.setData(Qt.UserRole, str(toAddress))
            if shared.safeConfigGetBoolean(toAddress, 'mailinglist'):
                newItem.setTextColor(QtGui.QColor(137, 04, 177))
            self.ui.tableWidgetInbox.setItem(0, 0, newItem)
            if fromLabel == '':
                newItem = QtGui.QTableWidgetItem(
                    unicode(fromAddress, 'utf-8'))
                newItem.setToolTip(unicode(fromAddress, 'utf-8'))
            else:
                newItem = QtGui.QTableWidgetItem(unicode(fromLabel, 'utf-8'))
                newItem.setToolTip(unicode(fromLabel, 'utf-8'))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not read:
                newItem.setFont(font)
            newItem.setData(Qt.UserRole, str(fromAddress))

            self.ui.tableWidgetInbox.setItem(0, 1, newItem)
            newItem = QtGui.QTableWidgetItem(unicode(subject, 'utf-8'))
            newItem.setToolTip(unicode(subject, 'utf-8'))
            newItem.setData(Qt.UserRole, unicode(message, 'utf-8)'))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not read:
                newItem.setFont(font)
            self.ui.tableWidgetInbox.setItem(0, 2, newItem)
            newItem = myTableWidgetItem(unicode(strftime(shared.config.get(
                'bitmessagesettings', 'timeformat'), localtime(int(received))), 'utf-8'))
            newItem.setToolTip(unicode(strftime(shared.config.get(
                'bitmessagesettings', 'timeformat'), localtime(int(received))), 'utf-8'))
            newItem.setData(Qt.UserRole, QByteArray(msgid))
            newItem.setData(33, int(received))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not read:
                newItem.setFont(font)
            self.ui.tableWidgetInbox.setItem(0, 3, newItem)
        self.ui.tableWidgetInbox.sortItems(3, Qt.DescendingOrder)
        self.ui.tableWidgetInbox.keyPressEvent = self.tableWidgetInboxKeyPressEvent

    # create application indicator
    def appIndicatorInit(self, app):
        self.tray = QSystemTrayIcon(QtGui.QIcon(
            ":/newPrefix/images/can-icon-24px-red.png"), app)
        if sys.platform[0:3] == 'win':
            traySignal = "activated(QSystemTrayIcon::ActivationReason)"
            QtCore.QObject.connect(self.tray, QtCore.SIGNAL(
                traySignal), self.__icon_activated)

        m = QMenu()

        self.actionStatus = QtGui.QAction(_translate(
            "MainWindow", "Not Connected"), m, checkable=False)
        m.addAction(self.actionStatus)

        # separator
        actionSeparator = QtGui.QAction('', m, checkable=False)
        actionSeparator.setSeparator(True)
        m.addAction(actionSeparator)

        # show bitmessage
        self.actionShow = QtGui.QAction(_translate(
            "MainWindow", "Show Bitmessage"), m, checkable=True)
        self.actionShow.setChecked(not shared.config.getboolean(
            'bitmessagesettings', 'startintray'))
        self.actionShow.triggered.connect(self.appIndicatorShowOrHideWindow)
        if not sys.platform[0:3] == 'win':
            m.addAction(self.actionShow)

        # Send
        actionSend = QtGui.QAction(_translate(
            "MainWindow", "Send"), m, checkable=False)
        actionSend.triggered.connect(self.appIndicatorSend)
        m.addAction(actionSend)

        # Subscribe
        actionSubscribe = QtGui.QAction(_translate(
            "MainWindow", "Subscribe"), m, checkable=False)
        actionSubscribe.triggered.connect(self.appIndicatorSubscribe)
        m.addAction(actionSubscribe)

        # Address book
        actionAddressBook = QtGui.QAction(_translate(
            "MainWindow", "Address Book"), m, checkable=False)
        actionAddressBook.triggered.connect(self.appIndicatorAddressBook)
        m.addAction(actionAddressBook)

        # separator
        actionSeparator = QtGui.QAction('', m, checkable=False)
        actionSeparator.setSeparator(True)
        m.addAction(actionSeparator)

        # Quit
        m.addAction(_translate(
            "MainWindow", "Quit"), self.quit)

        self.tray.setContextMenu(m)
        self.tray.show()

    # Ubuntu Messaging menu object
    mmapp = None

    # is the operating system Ubuntu?
    def isUbuntu(self):
        for entry in platform.uname():
            if "Ubuntu" in entry:
                return True
        return False

    # When an unread inbox row is selected on then clear the messaging menu
    def ubuntuMessagingMenuClear(self, inventoryHash):
        global withMessagingMenu

        # if this isn't ubuntu then don't do anything
        if not self.isUbuntu():
            return

        # has messageing menu been installed
        if not withMessagingMenu:
            return

        # if there are no items on the messaging menu then
        # the subsequent query can be avoided
        if not (self.mmapp.has_source("Subscriptions") or self.mmapp.has_source("Messages")):
            return

        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''SELECT toaddress, read FROM inbox WHERE msgid=?''')
        shared.sqlSubmitQueue.put(inventoryHash)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            toAddress, read = row
            if not read:
                if toAddress == self.str_broadcast_subscribers:
                    if self.mmapp.has_source("Subscriptions"):
                        self.mmapp.remove_source("Subscriptions")
                else:
                    if self.mmapp.has_source("Messages"):
                        self.mmapp.remove_source("Messages")

    # returns the number of unread messages and subscriptions
    def getUnread(self):
        unreadMessages = 0
        unreadSubscriptions = 0

        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''SELECT msgid, toaddress, read FROM inbox where folder='inbox' ''')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            msgid, toAddress, read = row

            try:
                if toAddress == self.str_broadcast_subscribers:
                    toLabel = self.str_broadcast_subscribers
                else:
                    toLabel = shared.config.get(toAddress, 'label')
            except:
                toLabel = ''
            if toLabel == '':
                toLabel = toAddress

            if not read:
                if toLabel == self.str_broadcast_subscribers:
                    # increment the unread subscriptions
                    unreadSubscriptions = unreadSubscriptions + 1
                else:
                    # increment the unread messages
                    unreadMessages = unreadMessages + 1
        return unreadMessages, unreadSubscriptions

    # show the number of unread messages and subscriptions on the messaging
    # menu
    def ubuntuMessagingMenuUnread(self, drawAttention):
        unreadMessages, unreadSubscriptions = self.getUnread()
        # unread messages
        if unreadMessages > 0:
            self.mmapp.append_source(
                "Messages", None, "Messages (" + str(unreadMessages) + ")")
            if drawAttention:
                self.mmapp.draw_attention("Messages")

        # unread subscriptions
        if unreadSubscriptions > 0:
            self.mmapp.append_source("Subscriptions", None, "Subscriptions (" + str(
                unreadSubscriptions) + ")")
            if drawAttention:
                self.mmapp.draw_attention("Subscriptions")

    # initialise the Ubuntu messaging menu
    def ubuntuMessagingMenuInit(self):
        global withMessagingMenu

        # if this isn't ubuntu then don't do anything
        if not self.isUbuntu():
            return

        # has messageing menu been installed
        if not withMessagingMenu:
            print 'WARNING: MessagingMenu is not available.  Is libmessaging-menu-dev installed?'
            return

        # create the menu server
        if withMessagingMenu:
            try:
                self.mmapp = MessagingMenu.App(
                    desktop_id='pybitmessage.desktop')
                self.mmapp.register()
                self.mmapp.connect('activate-source', self.appIndicatorInbox)
                self.ubuntuMessagingMenuUnread(True)
            except Exception:
                withMessagingMenu = False
                print 'WARNING: messaging menu disabled'

    # update the Ubuntu messaging menu
    def ubuntuMessagingMenuUpdate(self, drawAttention, newItem, toLabel):
        global withMessagingMenu

        # if this isn't ubuntu then don't do anything
        if not self.isUbuntu():
            return

        # has messageing menu been installed
        if not withMessagingMenu:
            print 'WARNING: messaging menu disabled or libmessaging-menu-dev not installed'
            return

        # remember this item to that the messaging menu can find it
        if toLabel == self.str_broadcast_subscribers:
            self.newBroadcastItem = newItem
        else:
            self.newMessageItem = newItem

        # Remove previous messages and subscriptions entries, then recreate them
        # There might be a better way to do it than this
        if self.mmapp.has_source("Messages"):
            self.mmapp.remove_source("Messages")

        if self.mmapp.has_source("Subscriptions"):
            self.mmapp.remove_source("Subscriptions")

        # update the menu entries
        self.ubuntuMessagingMenuUnread(drawAttention)

    # initialise the message notifier
    def notifierInit(self):
        global withMessagingMenu
        if withMessagingMenu:
            Notify.init('pybitmessage')

    # shows a notification
    def notifierShow(self, title, subtitle):
        global withMessagingMenu
        if withMessagingMenu:
            n = Notify.Notification.new(
                title, subtitle, 'notification-message-email')
            n.show()
            return
        else:
            self.tray.showMessage(title, subtitle, 1, 2000)

    def tableWidgetInboxKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.on_action_InboxTrash()
        return QtGui.QTableWidget.keyPressEvent(self.ui.tableWidgetInbox, event)

    def tableWidgetSentKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.on_action_SentTrash()
        return QtGui.QTableWidget.keyPressEvent(self.ui.tableWidgetSent, event)

    def click_actionManageKeys(self):
        if 'darwin' in sys.platform or 'linux' in sys.platform:
            if shared.appdata == '':
                # reply = QtGui.QMessageBox.information(self, 'keys.dat?','You
                # may manage your keys by editing the keys.dat file stored in
                # the same directory as this program. It is important that you
                # back up this file.', QMessageBox.Ok)
                reply = QtGui.QMessageBox.information(self, 'keys.dat?', _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file."), QMessageBox.Ok)

            else:
                QtGui.QMessageBox.information(self, 'keys.dat?', _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in\n %1 \nIt is important that you back up this file.").arg(shared.appdata), QMessageBox.Ok)
        elif sys.platform == 'win32' or sys.platform == 'win64':
            if shared.appdata == '':
                reply = QtGui.QMessageBox.question(self, _translate("MainWindow", "Open keys.dat?"), _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)"), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            else:
                reply = QtGui.QMessageBox.question(self, _translate("MainWindow", "Open keys.dat?"), _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in\n %1 \nIt is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)").arg(shared.appdata), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.openKeysFile()

    def click_actionDeleteAllTrashedMessages(self):
        if QtGui.QMessageBox.question(self, _translate("MainWindow", "Delete trash?"), _translate("MainWindow", "Are you sure you want to delete all trashed messages?"), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
            return
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put('deleteandvacuume')
        shared.sqlLock.release()

    def click_actionRegenerateDeterministicAddresses(self):
        self.regenerateAddressesDialogInstance = regenerateAddressesDialog(
            self)
        if self.regenerateAddressesDialogInstance.exec_():
            if self.regenerateAddressesDialogInstance.ui.lineEditPassphrase.text() == "":
                QMessageBox.about(self, _translate("MainWindow", "bad passphrase"), _translate(
                    "MainWindow", "You must type your passphrase. If you don\'t have one then this is not the form for you."))
            else:
                streamNumberForAddress = int(
                    self.regenerateAddressesDialogInstance.ui.lineEditStreamNumber.text())
                addressVersionNumber = int(
                    self.regenerateAddressesDialogInstance.ui.lineEditAddressVersionNumber.text())
                # self.addressGenerator = addressGenerator()
                # self.addressGenerator.setup(addressVersionNumber,streamNumberForAddress,"unused address",self.regenerateAddressesDialogInstance.ui.spinBoxNumberOfAddressesToMake.value(),self.regenerateAddressesDialogInstance.ui.lineEditPassphrase.text().toUtf8(),self.regenerateAddressesDialogInstance.ui.checkBoxEighteenByteRipe.isChecked())
                # QtCore.QObject.connect(self.addressGenerator, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
                # QtCore.QObject.connect(self.addressGenerator, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
                # self.addressGenerator.start()
                shared.addressGeneratorQueue.put(('createDeterministicAddresses', addressVersionNumber, streamNumberForAddress, "regenerated deterministic address", self.regenerateAddressesDialogInstance.ui.spinBoxNumberOfAddressesToMake.value(
                ), self.regenerateAddressesDialogInstance.ui.lineEditPassphrase.text().toUtf8(), self.regenerateAddressesDialogInstance.ui.checkBoxEighteenByteRipe.isChecked()))
                self.ui.tabWidget.setCurrentIndex(3)

    def openKeysFile(self):
        if 'linux' in sys.platform:
            subprocess.call(["xdg-open", shared.appdata + 'keys.dat'])
        else:
            os.startfile(shared.appdata + 'keys.dat')

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                self.actionShow.setChecked(False)
        if shared.config.getboolean('bitmessagesettings', 'minimizetotray') and not 'darwin' in sys.platform:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.windowState() & QtCore.Qt.WindowMinimized:
                    self.appIndicatorHide()
                    if 'win32' in sys.platform or 'win64' in sys.platform:
                        self.setWindowFlags(Qt.ToolTip)
                elif event.oldState() & QtCore.Qt.WindowMinimized:
                    # The window state has just been changed to
                    # Normal/Maximised/FullScreen
                    pass
            # QtGui.QWidget.changeEvent(self, event)

    def __icon_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.actionShow.setChecked(not self.actionShow.isChecked())
            self.appIndicatorShowOrHideWindow()

    def incrementNumberOfMessagesProcessed(self):
        self.numberOfMessagesProcessed += 1
        self.ui.labelMessageCount.setText(_translate(
            "MainWindow", "Processed %1 person-to-person messages.").arg(str(self.numberOfMessagesProcessed)))

    def incrementNumberOfBroadcastsProcessed(self):
        self.numberOfBroadcastsProcessed += 1
        self.ui.labelBroadcastCount.setText(_translate(
            "MainWindow", "Processed %1 broadcast messages.").arg(str(self.numberOfBroadcastsProcessed)))

    def incrementNumberOfPubkeysProcessed(self):
        self.numberOfPubkeysProcessed += 1
        self.ui.labelPubkeyCount.setText(_translate(
            "MainWindow", "Processed %1 public keys.").arg(str(self.numberOfPubkeysProcessed)))

    def updateNetworkStatusTab(self):
        # print 'updating network status tab'
        totalNumberOfConnectionsFromAllStreams = 0  # One would think we could use len(sendDataQueues) for this but the number doesn't always match: just because we have a sendDataThread running doesn't mean that the connection has been fully established (with the exchange of version messages).
        streamNumberTotals = {}
        for host, streamNumber in shared.connectedHostsList.items():
            if not streamNumber in streamNumberTotals:
                streamNumberTotals[streamNumber] = 1
            else:
                streamNumberTotals[streamNumber] += 1

        while self.ui.tableWidgetConnectionCount.rowCount() > 0:
            self.ui.tableWidgetConnectionCount.removeRow(0)
        for streamNumber, connectionCount in streamNumberTotals.items():
            self.ui.tableWidgetConnectionCount.insertRow(0)
            if streamNumber == 0:
                newItem = QtGui.QTableWidgetItem("?")
            else:
                newItem = QtGui.QTableWidgetItem(str(streamNumber))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetConnectionCount.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(str(connectionCount))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetConnectionCount.setItem(0, 1, newItem)
        """for currentRow in range(self.ui.tableWidgetConnectionCount.rowCount()):
            rowStreamNumber = int(self.ui.tableWidgetConnectionCount.item(currentRow,0).text())
            if streamNumber == rowStreamNumber:
                foundTheRowThatNeedsUpdating = True
                self.ui.tableWidgetConnectionCount.item(currentRow,1).setText(str(connectionCount))
                #totalNumberOfConnectionsFromAllStreams += connectionCount
        if foundTheRowThatNeedsUpdating == False:
            #Add a line to the table for this stream number and update its count with the current connection count.
            self.ui.tableWidgetConnectionCount.insertRow(0)
            newItem =  QtGui.QTableWidgetItem(str(streamNumber))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetConnectionCount.setItem(0,0,newItem)
            newItem =  QtGui.QTableWidgetItem(str(connectionCount))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetConnectionCount.setItem(0,1,newItem)
            totalNumberOfConnectionsFromAllStreams += connectionCount"""
        self.ui.labelTotalConnections.setText(_translate(
            "MainWindow", "Total Connections: %1").arg(str(len(shared.connectedHostsList))))
        if len(shared.connectedHostsList) > 0 and shared.statusIconColor == 'red':  # FYI: The 'singlelistener' thread sets the icon color to green when it receives an incoming connection, meaning that the user's firewall is configured correctly.
            self.setStatusIcon('yellow')
        elif len(shared.connectedHostsList) == 0:
            self.setStatusIcon('red')

    # Indicates whether or not there is a connection to the Bitmessage network
    connected = False

    def setStatusIcon(self, color):
        global withMessagingMenu
        # print 'setting status icon color'
        if color == 'red':
            self.ui.pushButtonStatusIcon.setIcon(
                QIcon(":/newPrefix/images/redicon.png"))
            shared.statusIconColor = 'red'
            # if the connection is lost then show a notification
            if self.connected:
                self.notifierShow('Bitmessage', unicode(_translate(
                    "MainWindow", "Connection lost").toUtf8(),'utf-8'))
            self.connected = False

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Not Connected"))
                self.tray.setIcon(QtGui.QIcon(
                    ":/newPrefix/images/can-icon-24px-red.png"))
        if color == 'yellow':
            if self.statusBar().currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusBar().showMessage('')
            self.ui.pushButtonStatusIcon.setIcon(QIcon(
                ":/newPrefix/images/yellowicon.png"))
            shared.statusIconColor = 'yellow'
            # if a new connection has been established then show a notification
            if not self.connected:
                self.notifierShow('Bitmessage', unicode(_translate(
                    "MainWindow", "Connected").toUtf8(),'utf-8'))
            self.connected = True

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Connected"))
                self.tray.setIcon(QtGui.QIcon(
                    ":/newPrefix/images/can-icon-24px-yellow.png"))
        if color == 'green':
            if self.statusBar().currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusBar().showMessage('')
            self.ui.pushButtonStatusIcon.setIcon(
                QIcon(":/newPrefix/images/greenicon.png"))
            shared.statusIconColor = 'green'
            if not self.connected:
                self.notifierShow('Bitmessage', unicode(_translate(
                    "MainWindow", "Connected").toUtf8(),'utf-8'))
            self.connected = True

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Connected"))
                self.tray.setIcon(QtGui.QIcon(
                    ":/newPrefix/images/can-icon-24px-green.png"))

    def updateSentItemStatusByHash(self, toRipe, textToDisplay):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            toAddress = str(self.ui.tableWidgetSent.item(
                i, 0).data(Qt.UserRole).toPyObject())
            status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                toAddress)
            if ripe == toRipe:
                self.ui.tableWidgetSent.item(i, 3).setToolTip(textToDisplay)
                try:
                    newlinePosition = textToDisplay.indexOf('\n')
                except: # If someone misses adding a "_translate" to a string before passing it to this function, this function won't receive a qstring which will cause an exception.
                    newlinePosition = 0
                if newlinePosition > 1:
                    self.ui.tableWidgetSent.item(i, 3).setText(
                        textToDisplay[:newlinePosition])
                else:
                    self.ui.tableWidgetSent.item(i, 3).setText(textToDisplay)

    def updateSentItemStatusByAckdata(self, ackdata, textToDisplay):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            toAddress = str(self.ui.tableWidgetSent.item(
                i, 0).data(Qt.UserRole).toPyObject())
            tableAckdata = self.ui.tableWidgetSent.item(
                i, 3).data(Qt.UserRole).toPyObject()
            status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                toAddress)
            if ackdata == tableAckdata:
                self.ui.tableWidgetSent.item(i, 3).setToolTip(textToDisplay)
                try:
                    newlinePosition = textToDisplay.indexOf('\n')
                except: # If someone misses adding a "_translate" to a string before passing it to this function, this function won't receive a qstring which will cause an exception.
                    newlinePosition = 0
                if newlinePosition > 1:
                    self.ui.tableWidgetSent.item(i, 3).setText(
                        textToDisplay[:newlinePosition])
                else:
                    self.ui.tableWidgetSent.item(i, 3).setText(textToDisplay)

    def removeInboxRowByMsgid(self, msgid):  # msgid and inventoryHash are the same thing
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            if msgid == str(self.ui.tableWidgetInbox.item(i, 3).data(Qt.UserRole).toPyObject()):
                self.statusBar().showMessage(_translate(
                    "MainWindow", "Message trashed"))
                self.ui.tableWidgetInbox.removeRow(i)
                break

    def rerenderInboxFromLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            addressToLookup = str(self.ui.tableWidgetInbox.item(
                i, 1).data(Qt.UserRole).toPyObject())
            fromLabel = ''
            t = (addressToLookup,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''select label from addressbook where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()

            if queryreturn != []:
                for row in queryreturn:
                    fromLabel, = row
                    self.ui.tableWidgetInbox.item(
                        i, 1).setText(unicode(fromLabel, 'utf-8'))
            else:
                # It might be a broadcast message. We should check for that
                # label.
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''select label from subscriptions where address=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()

                if queryreturn != []:
                    for row in queryreturn:
                        fromLabel, = row
                        self.ui.tableWidgetInbox.item(
                            i, 1).setText(unicode(fromLabel, 'utf-8'))

    def rerenderInboxToLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            toAddress = str(self.ui.tableWidgetInbox.item(
                i, 0).data(Qt.UserRole).toPyObject())
            try:
                toLabel = shared.config.get(toAddress, 'label')
            except:
                toLabel = ''
            if toLabel == '':
                toLabel = toAddress
            self.ui.tableWidgetInbox.item(
                i, 0).setText(unicode(toLabel, 'utf-8'))
            # Set the color according to whether it is the address of a mailing
            # list or not.
            if shared.safeConfigGetBoolean(toAddress, 'mailinglist'):
                self.ui.tableWidgetInbox.item(i, 0).setTextColor(QtGui.QColor(137, 04, 177))
            else:
                self.ui.tableWidgetInbox.item(
                    i, 0).setTextColor(QtGui.QColor(0, 0, 0))

    def rerenderSentFromLabels(self):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            fromAddress = str(self.ui.tableWidgetSent.item(
                i, 1).data(Qt.UserRole).toPyObject())
            try:
                fromLabel = shared.config.get(fromAddress, 'label')
            except:
                fromLabel = ''
            if fromLabel == '':
                fromLabel = fromAddress
            self.ui.tableWidgetSent.item(
                i, 1).setText(unicode(fromLabel, 'utf-8'))

    def rerenderSentToLabels(self):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            addressToLookup = str(self.ui.tableWidgetSent.item(
                i, 0).data(Qt.UserRole).toPyObject())
            toLabel = ''
            t = (addressToLookup,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''select label from addressbook where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()

            if queryreturn != []:
                for row in queryreturn:
                    toLabel, = row
                    self.ui.tableWidgetSent.item(
                        i, 0).setText(unicode(toLabel, 'utf-8'))

    def rerenderSubscriptions(self):
        self.ui.tableWidgetSubscriptions.setRowCount(0)
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            'SELECT label, address, enabled FROM subscriptions')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            label, address, enabled = row
            self.ui.tableWidgetSubscriptions.insertRow(0)
            newItem = QtGui.QTableWidgetItem(unicode(label, 'utf-8'))
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            self.ui.tableWidgetSubscriptions.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(address)
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            self.ui.tableWidgetSubscriptions.setItem(0, 1, newItem)

    def click_pushButtonSend(self):
        self.statusBar().showMessage('')
        toAddresses = str(self.ui.lineEditTo.text())
        fromAddress = str(self.ui.labelFrom.text())
        subject = str(self.ui.lineEditSubject.text().toUtf8())
        message = str(
            self.ui.textEditMessage.document().toPlainText().toUtf8())
        if self.ui.radioButtonSpecific.isChecked():  # To send a message to specific people (rather than broadcast)
            toAddressesList = [s.strip()
                               for s in toAddresses.replace(',', ';').split(';')]
            toAddressesList = list(set(
                toAddressesList))  # remove duplicate addresses. If the user has one address with a BM- and the same address without the BM-, this will not catch it. They'll send the message to the person twice.
            for toAddress in toAddressesList:
                if toAddress != '':
                    status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                        toAddress)
                    if status != 'success':
                        with shared.printLock:
                            print 'Error: Could not decode', toAddress, ':', status

                        if status == 'missingbm':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: Bitmessage addresses start with BM-   Please check %1").arg(toAddress))
                        elif status == 'checksumfailed':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: The address %1 is not typed or copied correctly. Please check it.").arg(toAddress))
                        elif status == 'invalidcharacters':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: The address %1 contains invalid characters. Please check it.").arg(toAddress))
                        elif status == 'versiontoohigh':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: The address version in %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.").arg(toAddress))
                        elif status == 'ripetooshort':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: Some data encoded in the address %1 is too short. There might be something wrong with the software of your acquaintance.").arg(toAddress))
                        elif status == 'ripetoolong':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: Some data encoded in the address %1 is too long. There might be something wrong with the software of your acquaintance.").arg(toAddress))
                        else:
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: Something is wrong with the address %1.").arg(toAddress))
                    elif fromAddress == '':
                        self.statusBar().showMessage(_translate(
                            "MainWindow", "Error: You must specify a From address. If you don\'t have one, go to the \'Your Identities\' tab."))
                    else:
                        toAddress = addBMIfNotPresent(toAddress)
                        try:
                            shared.config.get(toAddress, 'enabled')
                            # The toAddress is one owned by me. We cannot send
                            # messages to ourselves without significant changes
                            # to the codebase.
                            QMessageBox.about(self, _translate("MainWindow", "Sending to your address"), _translate(
                                "MainWindow", "Error: One of the addresses to which you are sending a message, %1, is yours. Unfortunately the Bitmessage client cannot process its own messages. Please try running a second client on a different computer or within a VM.").arg(toAddress))
                            continue
                        except:
                            pass
                        if addressVersionNumber > 3 or addressVersionNumber <= 1:
                            QMessageBox.about(self, _translate("MainWindow", "Address version number"), _translate(
                                "MainWindow", "Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.").arg(toAddress).arg(str(addressVersionNumber)))
                            continue
                        if streamNumber > 1 or streamNumber == 0:
                            QMessageBox.about(self, _translate("MainWindow", "Stream number"), _translate(
                                "MainWindow", "Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.").arg(toAddress).arg(str(streamNumber)))
                            continue
                        self.statusBar().showMessage('')
                        if shared.statusIconColor == 'red':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect."))
                        ackdata = OpenSSL.rand(32)
                        shared.sqlLock.acquire()
                        t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                            time.time()), 'msgqueued', 1, 1, 'sent', 2)
                        shared.sqlSubmitQueue.put(
                            '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''')
                        shared.sqlSubmitQueue.put(t)
                        shared.sqlReturnQueue.get()
                        shared.sqlSubmitQueue.put('commit')
                        shared.sqlLock.release()

                        toLabel = ''
                        t = (toAddress,)
                        shared.sqlLock.acquire()
                        shared.sqlSubmitQueue.put(
                            '''select label from addressbook where address=?''')
                        shared.sqlSubmitQueue.put(t)
                        queryreturn = shared.sqlReturnQueue.get()
                        shared.sqlLock.release()
                        if queryreturn != []:
                            for row in queryreturn:
                                toLabel, = row

                        self.displayNewSentMessage(
                            toAddress, toLabel, fromAddress, subject, message, ackdata)
                        shared.workerQueue.put(('sendmessage', toAddress))

                        self.ui.comboBoxSendFrom.setCurrentIndex(0)
                        self.ui.labelFrom.setText('')
                        self.ui.lineEditTo.setText('')
                        self.ui.lineEditSubject.setText('')
                        self.ui.textEditMessage.setText('')
                        self.ui.tabWidget.setCurrentIndex(2)
                        self.ui.tableWidgetSent.setCurrentCell(0, 0)
                else:
                    self.statusBar().showMessage(_translate(
                        "MainWindow", "Your \'To\' field is empty."))
        else:  # User selected 'Broadcast'
            if fromAddress == '':
                self.statusBar().showMessage(_translate(
                    "MainWindow", "Error: You must specify a From address. If you don\'t have one, go to the \'Your Identities\' tab."))
            else:
                self.statusBar().showMessage('')
                # We don't actually need the ackdata for acknowledgement since
                # this is a broadcast message, but we can use it to update the
                # user interface when the POW is done generating.
                ackdata = OpenSSL.rand(32)
                toAddress = self.str_broadcast_subscribers
                ripe = ''
                shared.sqlLock.acquire()
                t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                    time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
                shared.sqlSubmitQueue.put(
                    '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''')
                shared.sqlSubmitQueue.put(t)
                shared.sqlReturnQueue.get()
                shared.sqlSubmitQueue.put('commit')
                shared.sqlLock.release()

                shared.workerQueue.put(('sendbroadcast', ''))

                try:
                    fromLabel = shared.config.get(fromAddress, 'label')
                except:
                    fromLabel = ''
                if fromLabel == '':
                    fromLabel = fromAddress

                toLabel = self.str_broadcast_subscribers

                self.ui.tableWidgetSent.insertRow(0)
                newItem = QtGui.QTableWidgetItem(unicode(toLabel, 'utf-8'))
                newItem.setData(Qt.UserRole, str(toAddress))
                self.ui.tableWidgetSent.setItem(0, 0, newItem)

                if fromLabel == '':
                    newItem = QtGui.QTableWidgetItem(
                        unicode(fromAddress, 'utf-8'))
                else:
                    newItem = QtGui.QTableWidgetItem(
                        unicode(fromLabel, 'utf-8'))
                newItem.setData(Qt.UserRole, str(fromAddress))
                self.ui.tableWidgetSent.setItem(0, 1, newItem)
                newItem = QtGui.QTableWidgetItem(unicode(subject, 'utf-8)'))
                newItem.setData(Qt.UserRole, unicode(message, 'utf-8)'))
                self.ui.tableWidgetSent.setItem(0, 2, newItem)
                # newItem =  QtGui.QTableWidgetItem('Doing work necessary to
                # send broadcast...'+
                # unicode(strftime(config.get('bitmessagesettings',
                # 'timeformat'),localtime(int(time.time()))),'utf-8'))
                newItem = myTableWidgetItem(_translate("MainWindow", "Work is queued."))
                newItem.setData(Qt.UserRole, QByteArray(ackdata))
                newItem.setData(33, int(time.time()))
                self.ui.tableWidgetSent.setItem(0, 3, newItem)

                self.ui.textEditSentMessage.setPlainText(
                    self.ui.tableWidgetSent.item(0, 2).data(Qt.UserRole).toPyObject())

                self.ui.comboBoxSendFrom.setCurrentIndex(0)
                self.ui.labelFrom.setText('')
                self.ui.lineEditTo.setText('')
                self.ui.lineEditSubject.setText('')
                self.ui.textEditMessage.setText('')
                self.ui.tabWidget.setCurrentIndex(2)
                self.ui.tableWidgetSent.setCurrentCell(0, 0)

    def click_pushButtonLoadFromAddressBook(self):
        self.ui.tabWidget.setCurrentIndex(5)
        for i in range(4):
            time.sleep(0.1)
            self.statusBar().showMessage('')
            time.sleep(0.1)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Right click one or more entries in your address book and select \'Send message to this address\'."))

    def redrawLabelFrom(self, index):
        self.ui.labelFrom.setText(
            self.ui.comboBoxSendFrom.itemData(index).toPyObject())

    def rerenderComboBoxSendFrom(self):
        self.ui.comboBoxSendFrom.clear()
        self.ui.labelFrom.setText('')
        configSections = shared.config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile != 'bitmessagesettings':
                isEnabled = shared.config.getboolean(
                    addressInKeysFile, 'enabled')  # I realize that this is poor programming practice but I don't care. It's easier for others to read.
                if isEnabled:
                    self.ui.comboBoxSendFrom.insertItem(0, unicode(shared.config.get(
                        addressInKeysFile, 'label'), 'utf-8'), addressInKeysFile)
        self.ui.comboBoxSendFrom.insertItem(0, '', '')
        if(self.ui.comboBoxSendFrom.count() == 2):
            self.ui.comboBoxSendFrom.setCurrentIndex(1)
            self.redrawLabelFrom(self.ui.comboBoxSendFrom.currentIndex())
        else:
            self.ui.comboBoxSendFrom.setCurrentIndex(0)

    # This function is called by the processmsg function when that function
    # receives a message to an address that is acting as a
    # pseudo-mailing-list. The message will be broadcast out. This function
    # puts the message on the 'Sent' tab.
    def displayNewSentMessage(self, toAddress, toLabel, fromAddress, subject, message, ackdata):
        subject = shared.fixPotentiallyInvalidUTF8Data(subject)
        message = shared.fixPotentiallyInvalidUTF8Data(message)
        try:
            fromLabel = shared.config.get(fromAddress, 'label')
        except:
            fromLabel = ''
        if fromLabel == '':
            fromLabel = fromAddress

        self.ui.tableWidgetSent.setSortingEnabled(False)
        self.ui.tableWidgetSent.insertRow(0)
        if toLabel == '':
            newItem = QtGui.QTableWidgetItem(unicode(toAddress, 'utf-8'))
            newItem.setToolTip(unicode(toAddress, 'utf-8'))
        else:
            newItem = QtGui.QTableWidgetItem(unicode(toLabel, 'utf-8'))
            newItem.setToolTip(unicode(toLabel, 'utf-8'))
        newItem.setData(Qt.UserRole, str(toAddress))
        self.ui.tableWidgetSent.setItem(0, 0, newItem)
        if fromLabel == '':
            newItem = QtGui.QTableWidgetItem(unicode(fromAddress, 'utf-8'))
            newItem.setToolTip(unicode(fromAddress, 'utf-8'))
        else:
            newItem = QtGui.QTableWidgetItem(unicode(fromLabel, 'utf-8'))
            newItem.setToolTip(unicode(fromLabel, 'utf-8'))
        newItem.setData(Qt.UserRole, str(fromAddress))
        self.ui.tableWidgetSent.setItem(0, 1, newItem)
        newItem = QtGui.QTableWidgetItem(unicode(subject, 'utf-8)'))
        newItem.setToolTip(unicode(subject, 'utf-8)'))
        newItem.setData(Qt.UserRole, unicode(message, 'utf-8)'))
        self.ui.tableWidgetSent.setItem(0, 2, newItem)
        # newItem =  QtGui.QTableWidgetItem('Doing work necessary to send
        # broadcast...'+
        # unicode(strftime(shared.config.get('bitmessagesettings',
        # 'timeformat'),localtime(int(time.time()))),'utf-8'))
        newItem = myTableWidgetItem(_translate("MainWindow", "Work is queued. %1").arg(unicode(strftime(shared.config.get(
            'bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))
        newItem.setToolTip(_translate("MainWindow", "Work is queued. %1").arg(unicode(strftime(shared.config.get(
            'bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))
        newItem.setData(Qt.UserRole, QByteArray(ackdata))
        newItem.setData(33, int(time.time()))
        self.ui.tableWidgetSent.setItem(0, 3, newItem)
        self.ui.textEditSentMessage.setPlainText(
            self.ui.tableWidgetSent.item(0, 2).data(Qt.UserRole).toPyObject())
        self.ui.tableWidgetSent.setSortingEnabled(True)

    def displayNewInboxMessage(self, inventoryHash, toAddress, fromAddress, subject, message):
        subject = shared.fixPotentiallyInvalidUTF8Data(subject)
        message = shared.fixPotentiallyInvalidUTF8Data(message)
        fromLabel = ''
        shared.sqlLock.acquire()
        t = (fromAddress,)
        shared.sqlSubmitQueue.put(
            '''select label from addressbook where address=?''')
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        if queryreturn != []:
            for row in queryreturn:
                fromLabel, = row
        else:
            # There might be a label in the subscriptions table
            shared.sqlLock.acquire()
            t = (fromAddress,)
            shared.sqlSubmitQueue.put(
                '''select label from subscriptions where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:
                for row in queryreturn:
                    fromLabel, = row

        try:
            if toAddress == self.str_broadcast_subscribers:
                toLabel = self.str_broadcast_subscribers
            else:
                toLabel = shared.config.get(toAddress, 'label')
        except:
            toLabel = ''
        if toLabel == '':
            toLabel = toAddress

        font = QFont()
        font.setBold(True)
        self.ui.tableWidgetInbox.setSortingEnabled(False)
        newItem = QtGui.QTableWidgetItem(unicode(toLabel, 'utf-8'))
        newItem.setToolTip(unicode(toLabel, 'utf-8'))
        newItem.setFont(font)
        newItem.setData(Qt.UserRole, str(toAddress))
        if shared.safeConfigGetBoolean(str(toAddress), 'mailinglist'):
            newItem.setTextColor(QtGui.QColor(137, 04, 177))
        self.ui.tableWidgetInbox.insertRow(0)
        self.ui.tableWidgetInbox.setItem(0, 0, newItem)

        if fromLabel == '':
            newItem = QtGui.QTableWidgetItem(unicode(fromAddress, 'utf-8'))
            newItem.setToolTip(unicode(fromAddress, 'utf-8'))
            if shared.config.getboolean('bitmessagesettings', 'showtraynotifications'):
                self.notifierShow(unicode(_translate("MainWindow",'New Message').toUtf8(),'utf-8'), unicode(_translate("MainWindow",'From ').toUtf8(),'utf-8') + unicode(fromAddress, 'utf-8'))
        else:
            newItem = QtGui.QTableWidgetItem(unicode(fromLabel, 'utf-8'))
            newItem.setToolTip(unicode(unicode(fromLabel, 'utf-8')))
            if shared.config.getboolean('bitmessagesettings', 'showtraynotifications'):
                self.notifierShow(unicode(_translate("MainWindow",'New Message').toUtf8(),'utf-8'), unicode(_translate("MainWindow",'From ').toUtf8(),'utf-8') + unicode(fromLabel, 'utf-8'))
        newItem.setData(Qt.UserRole, str(fromAddress))
        newItem.setFont(font)
        self.ui.tableWidgetInbox.setItem(0, 1, newItem)
        newItem = QtGui.QTableWidgetItem(unicode(subject, 'utf-8)'))
        newItem.setToolTip(unicode(subject, 'utf-8)'))
        newItem.setData(Qt.UserRole, unicode(message, 'utf-8)'))
        newItem.setFont(font)
        self.ui.tableWidgetInbox.setItem(0, 2, newItem)
        newItem = myTableWidgetItem(unicode(strftime(shared.config.get(
            'bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8'))
        newItem.setToolTip(unicode(strftime(shared.config.get(
            'bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8'))
        newItem.setData(Qt.UserRole, QByteArray(inventoryHash))
        newItem.setData(33, int(time.time()))
        newItem.setFont(font)
        self.ui.tableWidgetInbox.setItem(0, 3, newItem)
        self.ui.tableWidgetInbox.setSortingEnabled(True)
        self.ubuntuMessagingMenuUpdate(True, newItem, toLabel)

    def click_pushButtonAddAddressBook(self):
        self.NewSubscriptionDialogInstance = NewSubscriptionDialog(self)
        if self.NewSubscriptionDialogInstance.exec_():
            if self.NewSubscriptionDialogInstance.ui.labelSubscriptionAddressCheck.text() == _translate("MainWindow", "Address is valid."):
                # First we must check to see if the address is already in the
                # address book. The user cannot add it again or else it will
                # cause problems when updating and deleting the entry.
                shared.sqlLock.acquire()
                t = (addBMIfNotPresent(str(
                    self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text())),)
                shared.sqlSubmitQueue.put(
                    '''select * from addressbook where address=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn == []:
                    self.ui.tableWidgetAddressBook.setSortingEnabled(False)
                    self.ui.tableWidgetAddressBook.insertRow(0)
                    newItem = QtGui.QTableWidgetItem(unicode(
                        self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8(), 'utf-8'))
                    self.ui.tableWidgetAddressBook.setItem(0, 0, newItem)
                    newItem = QtGui.QTableWidgetItem(addBMIfNotPresent(
                        self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text()))
                    newItem.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.ui.tableWidgetAddressBook.setItem(0, 1, newItem)
                    self.ui.tableWidgetAddressBook.setSortingEnabled(True)
                    t = (str(self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8()), addBMIfNotPresent(
                        str(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text())))
                    shared.sqlLock.acquire()
                    shared.sqlSubmitQueue.put(
                        '''INSERT INTO addressbook VALUES (?,?)''')
                    shared.sqlSubmitQueue.put(t)
                    queryreturn = shared.sqlReturnQueue.get()
                    shared.sqlSubmitQueue.put('commit')
                    shared.sqlLock.release()
                    self.rerenderInboxFromLabels()
                    self.rerenderSentToLabels()
                else:
                    self.statusBar().showMessage(_translate(
                        "MainWindow", "Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want."))
            else:
                self.statusBar().showMessage(_translate(
                    "MainWindow", "The address you entered was invalid. Ignoring it."))

    def addSubscription(self, label, address):
        address = addBMIfNotPresent(address)
        #This should be handled outside of this function, for error displaying and such, but it must also be checked here.
        if shared.isAddressInMySubscriptionsList(address):
            return
        #Add to UI list
        self.ui.tableWidgetSubscriptions.setSortingEnabled(False)
        self.ui.tableWidgetSubscriptions.insertRow(0)
        newItem =  QtGui.QTableWidgetItem(unicode(label, 'utf-8'))
        self.ui.tableWidgetSubscriptions.setItem(0,0,newItem)
        newItem =  QtGui.QTableWidgetItem(address)
        newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.ui.tableWidgetSubscriptions.setItem(0,1,newItem)
        self.ui.tableWidgetSubscriptions.setSortingEnabled(True)
        #Add to database (perhaps this should be separated from the MyForm class)
        t = (str(label),address,True)
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put('''INSERT INTO subscriptions VALUES (?,?,?)''')
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        self.rerenderInboxFromLabels()
        shared.reloadBroadcastSendersForWhichImWatching()

    def click_pushButtonAddSubscription(self):
        self.NewSubscriptionDialogInstance = NewSubscriptionDialog(self)
        if self.NewSubscriptionDialogInstance.exec_():
            if self.NewSubscriptionDialogInstance.ui.labelSubscriptionAddressCheck.text() != _translate("MainWindow", "Address is valid."):
                self.statusBar().showMessage(_translate("MainWindow", "The address you entered was invalid. Ignoring it."))
                return
            address = addBMIfNotPresent(str(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text()))
            # We must check to see if the address is already in the subscriptions list. The user cannot add it again or else it will cause problems when updating and deleting the entry.
            if shared.isAddressInMySubscriptionsList(address):
                self.statusBar().showMessage(_translate("MainWindow", "Error: You cannot add the same address to your subsciptions twice. Perhaps rename the existing one if you want."))
                return
            label = self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8()
            self.addSubscription(label, address)

    def loadBlackWhiteList(self):
        # Initialize the Blacklist or Whitelist table
        listType = shared.config.get('bitmessagesettings', 'blackwhitelist')
        shared.sqlLock.acquire()
        if listType == 'black':
            shared.sqlSubmitQueue.put(
                '''SELECT label, address, enabled FROM blacklist''')
        else:
            shared.sqlSubmitQueue.put(
                '''SELECT label, address, enabled FROM whitelist''')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            label, address, enabled = row
            self.ui.tableWidgetBlacklist.insertRow(0)
            newItem = QtGui.QTableWidgetItem(unicode(label, 'utf-8'))
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            self.ui.tableWidgetBlacklist.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(address)
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            self.ui.tableWidgetBlacklist.setItem(0, 1, newItem)

    def click_pushButtonStatusIcon(self):
        print 'click_pushButtonStatusIcon'
        self.iconGlossaryInstance = iconGlossaryDialog(self)
        if self.iconGlossaryInstance.exec_():
            pass

    def click_actionHelp(self):
        self.helpDialogInstance = helpDialog(self)
        self.helpDialogInstance.exec_()

    def click_actionAbout(self):
        self.aboutDialogInstance = aboutDialog(self)
        self.aboutDialogInstance.exec_()

    def click_actionSettings(self):
        self.settingsDialogInstance = settingsDialog(self)
        if self.settingsDialogInstance.exec_():
            shared.config.set('bitmessagesettings', 'startonlogon', str(
                self.settingsDialogInstance.ui.checkBoxStartOnLogon.isChecked()))
            shared.config.set('bitmessagesettings', 'minimizetotray', str(
                self.settingsDialogInstance.ui.checkBoxMinimizeToTray.isChecked()))
            shared.config.set('bitmessagesettings', 'showtraynotifications', str(
                self.settingsDialogInstance.ui.checkBoxShowTrayNotifications.isChecked()))
            shared.config.set('bitmessagesettings', 'startintray', str(
                self.settingsDialogInstance.ui.checkBoxStartInTray.isChecked()))
            if int(shared.config.get('bitmessagesettings', 'port')) != int(self.settingsDialogInstance.ui.lineEditTCPPort.text()):
                QMessageBox.about(self, _translate("MainWindow", "Restart"), _translate(
                    "MainWindow", "You must restart Bitmessage for the port number change to take effect."))
                shared.config.set('bitmessagesettings', 'port', str(
                    self.settingsDialogInstance.ui.lineEditTCPPort.text()))
            if shared.config.get('bitmessagesettings', 'socksproxytype') == 'none' and str(self.settingsDialogInstance.ui.comboBoxProxyType.currentText())[0:5] == 'SOCKS':
                if shared.statusIconColor != 'red':
                    QMessageBox.about(self, _translate("MainWindow", "Restart"), _translate(
                        "MainWindow", "Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections."))
            if shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and str(self.settingsDialogInstance.ui.comboBoxProxyType.currentText()) == 'none':
                self.statusBar().showMessage('')
            shared.config.set('bitmessagesettings', 'socksproxytype', str(
                self.settingsDialogInstance.ui.comboBoxProxyType.currentText()))
            shared.config.set('bitmessagesettings', 'socksauthentication', str(
                self.settingsDialogInstance.ui.checkBoxAuthentication.isChecked()))
            shared.config.set('bitmessagesettings', 'sockshostname', str(
                self.settingsDialogInstance.ui.lineEditSocksHostname.text()))
            shared.config.set('bitmessagesettings', 'socksport', str(
                self.settingsDialogInstance.ui.lineEditSocksPort.text()))
            shared.config.set('bitmessagesettings', 'socksusername', str(
                self.settingsDialogInstance.ui.lineEditSocksUsername.text()))
            shared.config.set('bitmessagesettings', 'sockspassword', str(
                self.settingsDialogInstance.ui.lineEditSocksPassword.text()))
            shared.config.set('bitmessagesettings', 'sockslisten', str(
                self.settingsDialogInstance.ui.checkBoxSocksListen.isChecked()))
            if float(self.settingsDialogInstance.ui.lineEditTotalDifficulty.text()) >= 1:
                shared.config.set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(int(float(
                    self.settingsDialogInstance.ui.lineEditTotalDifficulty.text()) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
            if float(self.settingsDialogInstance.ui.lineEditSmallMessageDifficulty.text()) >= 1:
                shared.config.set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(int(float(
                    self.settingsDialogInstance.ui.lineEditSmallMessageDifficulty.text()) * shared.networkDefaultPayloadLengthExtraBytes)))
            if float(self.settingsDialogInstance.ui.lineEditMaxAcceptableTotalDifficulty.text()) >= 1 or float(self.settingsDialogInstance.ui.lineEditMaxAcceptableTotalDifficulty.text()) == 0:
                shared.config.set('bitmessagesettings', 'maxacceptablenoncetrialsperbyte', str(int(float(
                    self.settingsDialogInstance.ui.lineEditMaxAcceptableTotalDifficulty.text()) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
            if float(self.settingsDialogInstance.ui.lineEditMaxAcceptableSmallMessageDifficulty.text()) >= 1 or float(self.settingsDialogInstance.ui.lineEditMaxAcceptableSmallMessageDifficulty.text()) == 0:
                shared.config.set('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes', str(int(float(
                    self.settingsDialogInstance.ui.lineEditMaxAcceptableSmallMessageDifficulty.text()) * shared.networkDefaultPayloadLengthExtraBytes)))

            # if str(self.settingsDialogInstance.ui.comboBoxMaxCores.currentText()) == 'All':
            #    shared.config.set('bitmessagesettings', 'maxcores', '99999')
            # else:
            # shared.config.set('bitmessagesettings', 'maxcores',
            # str(self.settingsDialogInstance.ui.comboBoxMaxCores.currentText()))

            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                shared.config.write(configfile)

            if 'win32' in sys.platform or 'win64' in sys.platform:
            # Auto-startup for Windows
                RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                self.settings = QSettings(RUN_PATH, QSettings.NativeFormat)
                if shared.config.getboolean('bitmessagesettings', 'startonlogon'):
                    self.settings.setValue("PyBitmessage", sys.argv[0])
                else:
                    self.settings.remove("PyBitmessage")
            elif 'darwin' in sys.platform:
                # startup for mac
                pass
            elif 'linux' in sys.platform:
                # startup for linux
                pass

            if shared.appdata != '' and self.settingsDialogInstance.ui.checkBoxPortableMode.isChecked():  # If we are NOT using portable mode now but the user selected that we should...
                # Write the keys.dat file to disk in the new location
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put('movemessagstoprog')
                shared.sqlLock.release()
                with open('keys.dat', 'wb') as configfile:
                    shared.config.write(configfile)
                # Write the knownnodes.dat file to disk in the new location
                shared.knownNodesLock.acquire()
                output = open('knownnodes.dat', 'wb')
                pickle.dump(shared.knownNodes, output)
                output.close()
                shared.knownNodesLock.release()
                os.remove(shared.appdata + 'keys.dat')
                os.remove(shared.appdata + 'knownnodes.dat')
                previousAppdataLocation = shared.appdata
                shared.appdata = ''
                debug.restartLoggingInUpdatedAppdataLocation()
                try:
                    os.remove(previousAppdataLocation + 'debug.log')
                    os.remove(previousAppdataLocation + 'debug.log.1')
                except:
                    pass

            if shared.appdata == '' and not self.settingsDialogInstance.ui.checkBoxPortableMode.isChecked():  # If we ARE using portable mode now but the user selected that we shouldn't...
                shared.appdata = shared.lookupAppdataFolder()
                if not os.path.exists(shared.appdata):
                    os.makedirs(shared.appdata)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put('movemessagstoappdata')
                shared.sqlLock.release()
                # Write the keys.dat file to disk in the new location
                with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                    shared.config.write(configfile)
                # Write the knownnodes.dat file to disk in the new location
                shared.knownNodesLock.acquire()
                output = open(shared.appdata + 'knownnodes.dat', 'wb')
                pickle.dump(shared.knownNodes, output)
                output.close()
                shared.knownNodesLock.release()
                os.remove('keys.dat')
                os.remove('knownnodes.dat')
                debug.restartLoggingInUpdatedAppdataLocation()
                try:
                    os.remove('debug.log')
                    os.remove('debug.log.1')
                except:
                    pass

    def click_radioButtonBlacklist(self):
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'white':
            shared.config.set('bitmessagesettings', 'blackwhitelist', 'black')
            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                shared.config.write(configfile)
            # self.ui.tableWidgetBlacklist.clearContents()
            self.ui.tableWidgetBlacklist.setRowCount(0)
            self.loadBlackWhiteList()
            self.ui.tabWidget.setTabText(6, 'Blacklist')

    def click_radioButtonWhitelist(self):
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            shared.config.set('bitmessagesettings', 'blackwhitelist', 'white')
            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                shared.config.write(configfile)
            # self.ui.tableWidgetBlacklist.clearContents()
            self.ui.tableWidgetBlacklist.setRowCount(0)
            self.loadBlackWhiteList()
            self.ui.tabWidget.setTabText(6, 'Whitelist')

    def click_pushButtonAddBlacklist(self):
        self.NewBlacklistDialogInstance = NewSubscriptionDialog(self)
        if self.NewBlacklistDialogInstance.exec_():
            if self.NewBlacklistDialogInstance.ui.labelSubscriptionAddressCheck.text() == _translate("MainWindow", "Address is valid."):
                # First we must check to see if the address is already in the
                # address book. The user cannot add it again or else it will
                # cause problems when updating and deleting the entry.
                shared.sqlLock.acquire()
                t = (addBMIfNotPresent(str(
                    self.NewBlacklistDialogInstance.ui.lineEditSubscriptionAddress.text())),)
                if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                    shared.sqlSubmitQueue.put(
                        '''select * from blacklist where address=?''')
                else:
                    shared.sqlSubmitQueue.put(
                        '''select * from whitelist where address=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn == []:
                    self.ui.tableWidgetBlacklist.setSortingEnabled(False)
                    self.ui.tableWidgetBlacklist.insertRow(0)
                    newItem = QtGui.QTableWidgetItem(unicode(
                        self.NewBlacklistDialogInstance.ui.newsubscriptionlabel.text().toUtf8(), 'utf-8'))
                    self.ui.tableWidgetBlacklist.setItem(0, 0, newItem)
                    newItem = QtGui.QTableWidgetItem(addBMIfNotPresent(
                        self.NewBlacklistDialogInstance.ui.lineEditSubscriptionAddress.text()))
                    newItem.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.ui.tableWidgetBlacklist.setItem(0, 1, newItem)
                    self.ui.tableWidgetBlacklist.setSortingEnabled(True)
                    t = (str(self.NewBlacklistDialogInstance.ui.newsubscriptionlabel.text().toUtf8()), addBMIfNotPresent(
                        str(self.NewBlacklistDialogInstance.ui.lineEditSubscriptionAddress.text())), True)
                    shared.sqlLock.acquire()
                    if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                        shared.sqlSubmitQueue.put(
                            '''INSERT INTO blacklist VALUES (?,?,?)''')
                    else:
                        shared.sqlSubmitQueue.put(
                            '''INSERT INTO whitelist VALUES (?,?,?)''')
                    shared.sqlSubmitQueue.put(t)
                    queryreturn = shared.sqlReturnQueue.get()
                    shared.sqlSubmitQueue.put('commit')
                    shared.sqlLock.release()
                else:
                    self.statusBar().showMessage(_translate(
                        "MainWindow", "Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want."))
            else:
                self.statusBar().showMessage(_translate(
                    "MainWindow", "The address you entered was invalid. Ignoring it."))

    def on_action_SpecialAddressBehaviorDialog(self):
        self.dialog = SpecialAddressBehaviorDialog(self)
        # For Modal dialogs
        if self.dialog.exec_():
            currentRow = self.ui.tableWidgetYourIdentities.currentRow()
            addressAtCurrentRow = str(
                self.ui.tableWidgetYourIdentities.item(currentRow, 1).text())
            if self.dialog.ui.radioButtonBehaveNormalAddress.isChecked():
                shared.config.set(str(
                    addressAtCurrentRow), 'mailinglist', 'false')
                # Set the color to either black or grey
                if shared.config.getboolean(addressAtCurrentRow, 'enabled'):
                    self.ui.tableWidgetYourIdentities.item(
                        currentRow, 1).setTextColor(QtGui.QColor(0, 0, 0))
                else:
                    self.ui.tableWidgetYourIdentities.item(
                        currentRow, 1).setTextColor(QtGui.QColor(128, 128, 128))
            else:
                shared.config.set(str(
                    addressAtCurrentRow), 'mailinglist', 'true')
                shared.config.set(str(addressAtCurrentRow), 'mailinglistname', str(
                    self.dialog.ui.lineEditMailingListName.text().toUtf8()))
                self.ui.tableWidgetYourIdentities.item(currentRow, 1).setTextColor(QtGui.QColor(137, 04, 177))
            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                shared.config.write(configfile)
            self.rerenderInboxToLabels()

    def click_NewAddressDialog(self):
        self.dialog = NewAddressDialog(self)
        # For Modal dialogs
        if self.dialog.exec_():
            # self.dialog.ui.buttonBox.enabled = False
            if self.dialog.ui.radioButtonRandomAddress.isChecked():
                if self.dialog.ui.radioButtonMostAvailable.isChecked():
                    streamNumberForAddress = 1
                else:
                    # User selected 'Use the same stream as an existing
                    # address.'
                    streamNumberForAddress = addressStream(
                        self.dialog.ui.comboBoxExisting.currentText())

                # self.addressGenerator = addressGenerator()
                # self.addressGenerator.setup(3,streamNumberForAddress,str(self.dialog.ui.newaddresslabel.text().toUtf8()),1,"",self.dialog.ui.checkBoxEighteenByteRipe.isChecked())
                # QtCore.QObject.connect(self.addressGenerator, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
                # QtCore.QObject.connect(self.addressGenerator, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
                # self.addressGenerator.start()
                shared.addressGeneratorQueue.put(('createRandomAddress', 3, streamNumberForAddress, str(
                    self.dialog.ui.newaddresslabel.text().toUtf8()), 1, "", self.dialog.ui.checkBoxEighteenByteRipe.isChecked()))
            else:
                if self.dialog.ui.lineEditPassphrase.text() != self.dialog.ui.lineEditPassphraseAgain.text():
                    QMessageBox.about(self, _translate("MainWindow", "Passphrase mismatch"), _translate(
                        "MainWindow", "The passphrase you entered twice doesn\'t match. Try again."))
                elif self.dialog.ui.lineEditPassphrase.text() == "":
                    QMessageBox.about(self, _translate(
                        "MainWindow", "Choose a passphrase"), _translate("MainWindow", "You really do need a passphrase."))
                else:
                    streamNumberForAddress = 1  # this will eventually have to be replaced by logic to determine the most available stream number.
                    # self.addressGenerator = addressGenerator()
                    # self.addressGenerator.setup(3,streamNumberForAddress,"unused address",self.dialog.ui.spinBoxNumberOfAddressesToMake.value(),self.dialog.ui.lineEditPassphrase.text().toUtf8(),self.dialog.ui.checkBoxEighteenByteRipe.isChecked())
                    # QtCore.QObject.connect(self.addressGenerator, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
                    # QtCore.QObject.connect(self.addressGenerator, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
                    # self.addressGenerator.start()
                    shared.addressGeneratorQueue.put(('createDeterministicAddresses', 3, streamNumberForAddress, "unused deterministic address", self.dialog.ui.spinBoxNumberOfAddressesToMake.value(
                    ), self.dialog.ui.lineEditPassphrase.text().toUtf8(), self.dialog.ui.checkBoxEighteenByteRipe.isChecked()))
        else:
            print 'new address dialog box rejected'

    # Quit selected from menu or application indicator
    def quit(self):
        '''quit_msg = "Are you sure you want to exit Bitmessage?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply is QtGui.QMessageBox.No:
            return
        '''
        shared.doCleanShutdown()
        self.tray.hide()
        # unregister the messaging system
        if self.mmapp is not None:
            self.mmapp.unregister()
        self.statusBar().showMessage(_translate(
            "MainWindow", "All done. Closing user interface..."))
        os._exit(0)

    # window close event
    def closeEvent(self, event):
        self.appIndicatorHide()
        minimizeonclose = False

        try:
            minimizeonclose = shared.config.getboolean(
                'bitmessagesettings', 'minimizeonclose')
        except Exception:
            pass

        if minimizeonclose:
            # minimize the application
            event.ignore()
        else:
            # quit the application
            event.accept()
            self.quit()

    def on_action_InboxMessageForceHtml(self):
        currentInboxRow = self.ui.tableWidgetInbox.currentRow()
        lines = self.ui.tableWidgetInbox.item(
            currentInboxRow, 2).data(Qt.UserRole).toPyObject().split('\n')
        for i in xrange(len(lines)):
            if lines[i].contains('Message ostensibly from '):
                lines[i] = '<p style="font-size: 12px; color: grey;">%s</span></p>' % (
                    lines[i])
            elif lines[i] == '------------------------------------------------------':
                lines[i] = '<hr>'
        content = ''
        for i in xrange(len(lines)):
            content += lines[i]
        content = content.replace('\n\n', '<br><br>')
        self.ui.textEditInboxMessage.setHtml(QtCore.QString(content))

    def on_action_InboxReply(self):
        currentInboxRow = self.ui.tableWidgetInbox.currentRow()
        toAddressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(
            currentInboxRow, 0).data(Qt.UserRole).toPyObject())
        fromAddressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(
            currentInboxRow, 1).data(Qt.UserRole).toPyObject())
        if toAddressAtCurrentInboxRow == self.str_broadcast_subscribers:
            self.ui.labelFrom.setText('')
        elif not shared.config.has_section(toAddressAtCurrentInboxRow):
            QtGui.QMessageBox.information(self, _translate("MainWindow", "Address is gone"), _translate(
                "MainWindow", "Bitmessage cannot find your address %1. Perhaps you removed it?").arg(toAddressAtCurrentInboxRow), QMessageBox.Ok)
            self.ui.labelFrom.setText('')
        elif not shared.config.getboolean(toAddressAtCurrentInboxRow, 'enabled'):
            QtGui.QMessageBox.information(self, _translate("MainWindow", "Address disabled"), _translate(
                "MainWindow", "Error: The address from which you are trying to send is disabled. You\'ll have to enable it on the \'Your Identities\' tab before using it."), QMessageBox.Ok)
            self.ui.labelFrom.setText('')
        else:
            self.ui.labelFrom.setText(toAddressAtCurrentInboxRow)
        self.ui.lineEditTo.setText(str(fromAddressAtCurrentInboxRow))
        self.ui.comboBoxSendFrom.setCurrentIndex(0)
        # self.ui.comboBoxSendFrom.setEditText(str(self.ui.tableWidgetInbox.item(currentInboxRow,0).text))
        self.ui.textEditMessage.setText('\n\n------------------------------------------------------\n' + self.ui.tableWidgetInbox.item(
            currentInboxRow, 2).data(Qt.UserRole).toPyObject())
        if self.ui.tableWidgetInbox.item(currentInboxRow, 2).text()[0:3] == 'Re:':
            self.ui.lineEditSubject.setText(
                self.ui.tableWidgetInbox.item(currentInboxRow, 2).text())
        else:
            self.ui.lineEditSubject.setText(
                'Re: ' + self.ui.tableWidgetInbox.item(currentInboxRow, 2).text())
        self.ui.radioButtonSpecific.setChecked(True)
        self.ui.tabWidget.setCurrentIndex(1)

    def on_action_InboxAddSenderToAddressBook(self):
        currentInboxRow = self.ui.tableWidgetInbox.currentRow()
        # self.ui.tableWidgetInbox.item(currentRow,1).data(Qt.UserRole).toPyObject()
        addressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(
            currentInboxRow, 1).data(Qt.UserRole).toPyObject())
        # Let's make sure that it isn't already in the address book
        shared.sqlLock.acquire()
        t = (addressAtCurrentInboxRow,)
        shared.sqlSubmitQueue.put(
            '''select * from addressbook where address=?''')
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        if queryreturn == []:
            self.ui.tableWidgetAddressBook.insertRow(0)
            newItem = QtGui.QTableWidgetItem(
                '--New entry. Change label in Address Book.--')
            self.ui.tableWidgetAddressBook.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(addressAtCurrentInboxRow)
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.ui.tableWidgetAddressBook.setItem(0, 1, newItem)
            t = ('--New entry. Change label in Address Book.--',
                 addressAtCurrentInboxRow)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO addressbook VALUES (?,?)''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            self.ui.tabWidget.setCurrentIndex(5)
            self.ui.tableWidgetAddressBook.setCurrentCell(0, 0)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Entry added to the Address Book. Edit the label to your liking."))
        else:
            self.statusBar().showMessage(_translate(
                "MainWindow", "Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want."))

    # Send item on the Inbox tab to trash
    def on_action_InboxTrash(self):
        while self.ui.tableWidgetInbox.selectedIndexes() != []:
            currentRow = self.ui.tableWidgetInbox.selectedIndexes()[0].row()
            inventoryHashToTrash = str(self.ui.tableWidgetInbox.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            t = (inventoryHashToTrash,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''UPDATE inbox SET folder='trash' WHERE msgid=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            self.ui.textEditInboxMessage.setText("")
            self.ui.tableWidgetInbox.removeRow(currentRow)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Moved items to trash. There is no user interface to view your trash, but it is still on disk if you are desperate to get it back."))
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        if currentRow == 0:
            self.ui.tableWidgetInbox.selectRow(currentRow)
        else:
            self.ui.tableWidgetInbox.selectRow(currentRow - 1)

    def on_action_InboxSaveMessageAs(self):
        currentInboxRow = self.ui.tableWidgetInbox.currentRow()
        try:
            subjectAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(currentInboxRow,2).text())
        except:
            subjectAtCurrentInboxRow = ''
        defaultFilename = "".join(x for x in subjectAtCurrentInboxRow if x.isalnum()) + '.txt'
        data = self.ui.tableWidgetInbox.item(currentInboxRow,2).data(Qt.UserRole).toPyObject()
        filename = QFileDialog.getSaveFileName(self, _translate("MainWindow","Save As..."), defaultFilename, "Text files (*.txt);;All files (*.*)")
        if filename == '':
            return
        try:
            f = open(filename, 'w')
            f.write( self.ui.tableWidgetInbox.item(currentInboxRow,2).data(Qt.UserRole).toPyObject() )
            f.close()
        except Exception, e:
            sys.stderr.write('Write error: '+ e)
            self.statusBar().showMessage(_translate("MainWindow", "Write error."))

    # Send item on the Sent tab to trash
    def on_action_SentTrash(self):
        while self.ui.tableWidgetSent.selectedIndexes() != []:
            currentRow = self.ui.tableWidgetSent.selectedIndexes()[0].row()
            ackdataToTrash = str(self.ui.tableWidgetSent.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            t = (ackdataToTrash,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''UPDATE sent SET folder='trash' WHERE ackdata=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            self.ui.textEditSentMessage.setPlainText("")
            self.ui.tableWidgetSent.removeRow(currentRow)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Moved items to trash. There is no user interface to view your trash, but it is still on disk if you are desperate to get it back."))
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        if currentRow == 0:
            self.ui.tableWidgetSent.selectRow(currentRow)
        else:
            self.ui.tableWidgetSent.selectRow(currentRow - 1)

    def on_action_ForceSend(self):
        currentRow = self.ui.tableWidgetSent.currentRow()
        addressAtCurrentRow = str(self.ui.tableWidgetSent.item(
            currentRow, 0).data(Qt.UserRole).toPyObject())
        toRipe = decodeAddress(addressAtCurrentRow)[3]
        t = (toRipe,)
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''UPDATE sent SET status='forcepow' WHERE toripe=? AND status='toodifficult' and folder='sent' ''')
        shared.sqlSubmitQueue.put(t)
        shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlSubmitQueue.put(
            '''select ackdata FROM sent WHERE status='forcepow' ''')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            ackdata, = row
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                ackdata, 'Overriding maximum-difficulty setting. Work queued.')))
        shared.workerQueue.put(('sendmessage', ''))

    def on_action_SentClipboard(self):
        currentRow = self.ui.tableWidgetSent.currentRow()
        addressAtCurrentRow = str(self.ui.tableWidgetSent.item(
            currentRow, 0).data(Qt.UserRole).toPyObject())
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))

    # Group of functions for the Address Book dialog box
    def on_action_AddressBookNew(self):
        self.click_pushButtonAddAddressBook()

    def on_action_AddressBookDelete(self):
        while self.ui.tableWidgetAddressBook.selectedIndexes() != []:
            currentRow = self.ui.tableWidgetAddressBook.selectedIndexes()[
                0].row()
            labelAtCurrentRow = self.ui.tableWidgetAddressBook.item(
                currentRow, 0).text().toUtf8()
            addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(
                currentRow, 1).text()
            t = (str(labelAtCurrentRow), str(addressAtCurrentRow))
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''DELETE FROM addressbook WHERE label=? AND address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            self.ui.tableWidgetAddressBook.removeRow(currentRow)
            self.rerenderInboxFromLabels()
            self.rerenderSentToLabels()

    def on_action_AddressBookClipboard(self):
        fullStringOfAddresses = ''
        listOfSelectedRows = {}
        for i in range(len(self.ui.tableWidgetAddressBook.selectedIndexes())):
            listOfSelectedRows[
                self.ui.tableWidgetAddressBook.selectedIndexes()[i].row()] = 0
        for currentRow in listOfSelectedRows:
            addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(
                currentRow, 1).text()
            if fullStringOfAddresses == '':
                fullStringOfAddresses = addressAtCurrentRow
            else:
                fullStringOfAddresses += ', ' + str(addressAtCurrentRow)
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(fullStringOfAddresses)

    def on_action_AddressBookSend(self):
        listOfSelectedRows = {}
        for i in range(len(self.ui.tableWidgetAddressBook.selectedIndexes())):
            listOfSelectedRows[
                self.ui.tableWidgetAddressBook.selectedIndexes()[i].row()] = 0
        for currentRow in listOfSelectedRows:
            addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(
                currentRow, 1).text()
            if self.ui.lineEditTo.text() == '':
                self.ui.lineEditTo.setText(str(addressAtCurrentRow))
            else:
                self.ui.lineEditTo.setText(str(
                    self.ui.lineEditTo.text()) + '; ' + str(addressAtCurrentRow))
        if listOfSelectedRows == {}:
            self.statusBar().showMessage(_translate(
                "MainWindow", "No addresses selected."))
        else:
            self.statusBar().showMessage('')
            self.ui.tabWidget.setCurrentIndex(1)

    def on_action_AddressBookSubscribe(self):
        listOfSelectedRows = {}
        for i in range(len(self.ui.tableWidgetAddressBook.selectedIndexes())):
            listOfSelectedRows[self.ui.tableWidgetAddressBook.selectedIndexes()[i].row()] = 0
        for currentRow in listOfSelectedRows:
            addressAtCurrentRow = str(self.ui.tableWidgetAddressBook.item(currentRow,1).text())
            # Then subscribe to it... provided it's not already in the address book
            if shared.isAddressInMySubscriptionsList(addressAtCurrentRow):
                self.statusBar().showMessage(QtGui.QApplication.translate("MainWindow", "Error: You cannot add the same address to your subsciptions twice. Perhaps rename the existing one if you want."))
                continue
            labelAtCurrentRow = self.ui.tableWidgetAddressBook.item(currentRow,0).text().toUtf8()
            self.addSubscription(labelAtCurrentRow, addressAtCurrentRow)
            self.ui.tabWidget.setCurrentIndex(4)

    def on_context_menuAddressBook(self, point):
        self.popMenuAddressBook.exec_(
            self.ui.tableWidgetAddressBook.mapToGlobal(point))

    # Group of functions for the Subscriptions dialog box
    def on_action_SubscriptionsNew(self):
        self.click_pushButtonAddSubscription()
        
    def on_action_SubscriptionsDelete(self):
        print 'clicked Delete'
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
            currentRow, 0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
            currentRow, 1).text()
        t = (str(labelAtCurrentRow), str(addressAtCurrentRow))
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''DELETE FROM subscriptions WHERE label=? AND address=?''')
        shared.sqlSubmitQueue.put(t)
        shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        self.ui.tableWidgetSubscriptions.removeRow(currentRow)
        self.rerenderInboxFromLabels()
        shared.reloadBroadcastSendersForWhichImWatching()

    def on_action_SubscriptionsClipboard(self):
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
            currentRow, 1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))

    def on_action_SubscriptionsEnable(self):
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
            currentRow, 0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
            currentRow, 1).text()
        t = (str(labelAtCurrentRow), str(addressAtCurrentRow))
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''update subscriptions set enabled=1 WHERE label=? AND address=?''')
        shared.sqlSubmitQueue.put(t)
        shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        self.ui.tableWidgetSubscriptions.item(
            currentRow, 0).setTextColor(QtGui.QColor(0, 0, 0))
        self.ui.tableWidgetSubscriptions.item(
            currentRow, 1).setTextColor(QtGui.QColor(0, 0, 0))
        shared.reloadBroadcastSendersForWhichImWatching()

    def on_action_SubscriptionsDisable(self):
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
            currentRow, 0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
            currentRow, 1).text()
        t = (str(labelAtCurrentRow), str(addressAtCurrentRow))
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''update subscriptions set enabled=0 WHERE label=? AND address=?''')
        shared.sqlSubmitQueue.put(t)
        shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        self.ui.tableWidgetSubscriptions.item(
            currentRow, 0).setTextColor(QtGui.QColor(128, 128, 128))
        self.ui.tableWidgetSubscriptions.item(
            currentRow, 1).setTextColor(QtGui.QColor(128, 128, 128))
        shared.reloadBroadcastSendersForWhichImWatching()

    def on_context_menuSubscriptions(self, point):
        self.popMenuSubscriptions.exec_(
            self.ui.tableWidgetSubscriptions.mapToGlobal(point))

    # Group of functions for the Blacklist dialog box
    def on_action_BlacklistNew(self):
        self.click_pushButtonAddBlacklist()

    def on_action_BlacklistDelete(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 1).text()
        t = (str(labelAtCurrentRow), str(addressAtCurrentRow))
        shared.sqlLock.acquire()
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            shared.sqlSubmitQueue.put(
                '''DELETE FROM blacklist WHERE label=? AND address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
        else:
            shared.sqlSubmitQueue.put(
                '''DELETE FROM whitelist WHERE label=? AND address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        self.ui.tableWidgetBlacklist.removeRow(currentRow)

    def on_action_BlacklistClipboard(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))

    def on_context_menuBlacklist(self, point):
        self.popMenuBlacklist.exec_(
            self.ui.tableWidgetBlacklist.mapToGlobal(point))

    def on_action_BlacklistEnable(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 1).text()
        self.ui.tableWidgetBlacklist.item(
            currentRow, 0).setTextColor(QtGui.QColor(0, 0, 0))
        self.ui.tableWidgetBlacklist.item(
            currentRow, 1).setTextColor(QtGui.QColor(0, 0, 0))
        t = (str(addressAtCurrentRow),)
        shared.sqlLock.acquire()
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            shared.sqlSubmitQueue.put(
                '''UPDATE blacklist SET enabled=1 WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
        else:
            shared.sqlSubmitQueue.put(
                '''UPDATE whitelist SET enabled=1 WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()

    def on_action_BlacklistDisable(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 1).text()
        self.ui.tableWidgetBlacklist.item(
            currentRow, 0).setTextColor(QtGui.QColor(128, 128, 128))
        self.ui.tableWidgetBlacklist.item(
            currentRow, 1).setTextColor(QtGui.QColor(128, 128, 128))
        t = (str(addressAtCurrentRow),)
        shared.sqlLock.acquire()
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            shared.sqlSubmitQueue.put(
                '''UPDATE blacklist SET enabled=0 WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
        else:
            shared.sqlSubmitQueue.put(
                '''UPDATE whitelist SET enabled=0 WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()

    # Group of functions for the Your Identities dialog box
    def on_action_YourIdentitiesNew(self):
        self.click_NewAddressDialog()

    def on_action_YourIdentitiesEnable(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = str(
            self.ui.tableWidgetYourIdentities.item(currentRow, 1).text())
        shared.config.set(addressAtCurrentRow, 'enabled', 'true')
        with open(shared.appdata + 'keys.dat', 'wb') as configfile:
            shared.config.write(configfile)
        self.ui.tableWidgetYourIdentities.item(
            currentRow, 0).setTextColor(QtGui.QColor(0, 0, 0))
        self.ui.tableWidgetYourIdentities.item(
            currentRow, 1).setTextColor(QtGui.QColor(0, 0, 0))
        self.ui.tableWidgetYourIdentities.item(
            currentRow, 2).setTextColor(QtGui.QColor(0, 0, 0))
        if shared.safeConfigGetBoolean(addressAtCurrentRow, 'mailinglist'):
            self.ui.tableWidgetYourIdentities.item(currentRow, 1).setTextColor(QtGui.QColor(137, 04, 177))
        shared.reloadMyAddressHashes()

    def on_action_YourIdentitiesDisable(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = str(
            self.ui.tableWidgetYourIdentities.item(currentRow, 1).text())
        shared.config.set(str(addressAtCurrentRow), 'enabled', 'false')
        self.ui.tableWidgetYourIdentities.item(
            currentRow, 0).setTextColor(QtGui.QColor(128, 128, 128))
        self.ui.tableWidgetYourIdentities.item(
            currentRow, 1).setTextColor(QtGui.QColor(128, 128, 128))
        self.ui.tableWidgetYourIdentities.item(
            currentRow, 2).setTextColor(QtGui.QColor(128, 128, 128))
        if shared.safeConfigGetBoolean(addressAtCurrentRow, 'mailinglist'):
            self.ui.tableWidgetYourIdentities.item(currentRow, 1).setTextColor(QtGui.QColor(137, 04, 177))
        with open(shared.appdata + 'keys.dat', 'wb') as configfile:
            shared.config.write(configfile)
        shared.reloadMyAddressHashes()

    def on_action_YourIdentitiesClipboard(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetYourIdentities.item(
            currentRow, 1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))

    def on_context_menuYourIdentities(self, point):
        self.popMenu.exec_(
            self.ui.tableWidgetYourIdentities.mapToGlobal(point))

    def on_context_menuInbox(self, point):
        self.popMenuInbox.exec_(self.ui.tableWidgetInbox.mapToGlobal(point))

    def on_context_menuSent(self, point):
        self.popMenuSent = QtGui.QMenu(self)
        self.popMenuSent.addAction(self.actionSentClipboard)
        self.popMenuSent.addAction(self.actionTrashSentMessage)

        # Check to see if this item is toodifficult and display an additional
        # menu option (Force Send) if it is.
        currentRow = self.ui.tableWidgetSent.currentRow()
        ackData = str(self.ui.tableWidgetSent.item(
            currentRow, 3).data(Qt.UserRole).toPyObject())
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''SELECT status FROM sent where ackdata=?''')
        shared.sqlSubmitQueue.put((ackData,))
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            status, = row
        if status == 'toodifficult':
            self.popMenuSent.addAction(self.actionForceSend)
        self.popMenuSent.exec_(self.ui.tableWidgetSent.mapToGlobal(point))

    def inboxSearchLineEditPressed(self):
        searchKeyword = self.ui.inboxSearchLineEdit.text().toUtf8().data()
        searchOption = self.ui.inboxSearchOptionCB.currentText().toUtf8().data()
        self.ui.inboxSearchLineEdit.setText(QString(""))
        self.ui.textEditInboxMessage.setPlainText(QString(""))
        self.loadInbox(searchOption, searchKeyword)

    def sentSearchLineEditPressed(self):
        searchKeyword = self.ui.sentSearchLineEdit.text().toUtf8().data()
        searchOption = self.ui.sentSearchOptionCB.currentText().toUtf8().data()
        self.ui.sentSearchLineEdit.setText(QString(""))
        self.ui.textEditInboxMessage.setPlainText(QString(""))
        self.loadSent(searchOption, searchKeyword)

    def tableWidgetInboxItemClicked(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        if currentRow >= 0:
            fromAddress = str(self.ui.tableWidgetInbox.item(
                currentRow, 1).data(Qt.UserRole).toPyObject())
            # If we have received this message from either a broadcast address
            # or from someone in our address book, display as HTML
            if decodeAddress(fromAddress)[3] in shared.broadcastSendersForWhichImWatching or shared.isAddressInMyAddressBook(fromAddress):
                if len(self.ui.tableWidgetInbox.item(currentRow, 2).data(Qt.UserRole).toPyObject()) < 30000:
                    self.ui.textEditInboxMessage.setText(self.ui.tableWidgetInbox.item(
                        currentRow, 2).data(Qt.UserRole).toPyObject())  # Only show the first 30K characters
                else:
                    self.ui.textEditInboxMessage.setText(self.ui.tableWidgetInbox.item(currentRow, 2).data(Qt.UserRole).toPyObject()[
                                                         :30000] + '\n\nDisplay of the remainder of the message truncated because it is too long.')  # Only show the first 30K characters
            else:
                if len(self.ui.tableWidgetInbox.item(currentRow, 2).data(Qt.UserRole).toPyObject()) < 30000:
                    self.ui.textEditInboxMessage.setPlainText(self.ui.tableWidgetInbox.item(
                        currentRow, 2).data(Qt.UserRole).toPyObject())  # Only show the first 30K characters
                else:
                    self.ui.textEditInboxMessage.setPlainText(self.ui.tableWidgetInbox.item(currentRow, 2).data(Qt.UserRole).toPyObject()[
                                                              :30000] + '\n\nDisplay of the remainder of the message truncated because it is too long.')  # Only show the first 30K characters

            font = QFont()
            font.setBold(False)
            self.ui.tableWidgetInbox.item(currentRow, 0).setFont(font)
            self.ui.tableWidgetInbox.item(currentRow, 1).setFont(font)
            self.ui.tableWidgetInbox.item(currentRow, 2).setFont(font)
            self.ui.tableWidgetInbox.item(currentRow, 3).setFont(font)

            inventoryHash = str(self.ui.tableWidgetInbox.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            t = (inventoryHash,)
            self.ubuntuMessagingMenuClear(t)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''update inbox set read=1 WHERE msgid=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()

    def tableWidgetSentItemClicked(self):
        currentRow = self.ui.tableWidgetSent.currentRow()
        if currentRow >= 0:
            self.ui.textEditSentMessage.setPlainText(self.ui.tableWidgetSent.item(
                currentRow, 2).data(Qt.UserRole).toPyObject())

    def tableWidgetYourIdentitiesItemChanged(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        if currentRow >= 0:
            addressAtCurrentRow = self.ui.tableWidgetYourIdentities.item(
                currentRow, 1).text()
            shared.config.set(str(addressAtCurrentRow), 'label', str(
                self.ui.tableWidgetYourIdentities.item(currentRow, 0).text().toUtf8()))
            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                shared.config.write(configfile)
            self.rerenderComboBoxSendFrom()
            # self.rerenderInboxFromLabels()
            self.rerenderInboxToLabels()
            self.rerenderSentFromLabels()
            # self.rerenderSentToLabels()

    def tableWidgetAddressBookItemChanged(self):
        currentRow = self.ui.tableWidgetAddressBook.currentRow()
        shared.sqlLock.acquire()
        if currentRow >= 0:
            addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(
                currentRow, 1).text()
            t = (str(self.ui.tableWidgetAddressBook.item(
                currentRow, 0).text().toUtf8()), str(addressAtCurrentRow))
            shared.sqlSubmitQueue.put(
                '''UPDATE addressbook set label=? WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        self.rerenderInboxFromLabels()
        self.rerenderSentToLabels()

    def tableWidgetSubscriptionsItemChanged(self):
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        shared.sqlLock.acquire()
        if currentRow >= 0:
            addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(
                currentRow, 1).text()
            t = (str(self.ui.tableWidgetSubscriptions.item(
                currentRow, 0).text().toUtf8()), str(addressAtCurrentRow))
            shared.sqlSubmitQueue.put(
                '''UPDATE subscriptions set label=? WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()
        self.rerenderInboxFromLabels()
        self.rerenderSentToLabels()

    def writeNewAddressToTable(self, label, address, streamNumber):
        self.ui.tableWidgetYourIdentities.setSortingEnabled(False)
        self.ui.tableWidgetYourIdentities.insertRow(0)
        self.ui.tableWidgetYourIdentities.setItem(
            0, 0, QtGui.QTableWidgetItem(unicode(label, 'utf-8')))
        newItem = QtGui.QTableWidgetItem(address)
        newItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.ui.tableWidgetYourIdentities.setItem(0, 1, newItem)
        newItem = QtGui.QTableWidgetItem(streamNumber)
        newItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.ui.tableWidgetYourIdentities.setItem(0, 2, newItem)
        # self.ui.tableWidgetYourIdentities.setSortingEnabled(True)
        self.rerenderComboBoxSendFrom()

    def updateStatusBar(self, data):
        if data != "":
            with shared.printLock:
                print 'Status bar:', data

        self.statusBar().showMessage(data)


class helpDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_helpDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.labelHelpURI.setOpenExternalLinks(True)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


class aboutDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.labelVersion.setText('version ' + shared.softwareVersion)


class regenerateAddressesDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_regenerateAddressesDialog()
        self.ui.setupUi(self)
        self.parent = parent
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


class settingsDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_settingsDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.checkBoxStartOnLogon.setChecked(
            shared.config.getboolean('bitmessagesettings', 'startonlogon'))
        self.ui.checkBoxMinimizeToTray.setChecked(
            shared.config.getboolean('bitmessagesettings', 'minimizetotray'))
        self.ui.checkBoxShowTrayNotifications.setChecked(
            shared.config.getboolean('bitmessagesettings', 'showtraynotifications'))
        self.ui.checkBoxStartInTray.setChecked(
            shared.config.getboolean('bitmessagesettings', 'startintray'))
        if shared.appdata == '':
            self.ui.checkBoxPortableMode.setChecked(True)
        if 'darwin' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.checkBoxMinimizeToTray.setDisabled(True)
            self.ui.checkBoxShowTrayNotifications.setDisabled(True)
            self.ui.labelSettingsNote.setText(_translate(
                "MainWindow", "Options have been disabled because they either aren\'t applicable or because they haven\'t yet been implemented for your operating system."))
        elif 'linux' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.checkBoxMinimizeToTray.setDisabled(True)
            self.ui.labelSettingsNote.setText(_translate(
                "MainWindow", "Options have been disabled because they either aren\'t applicable or because they haven\'t yet been implemented for your operating system."))
        # On the Network settings tab:
        self.ui.lineEditTCPPort.setText(str(
            shared.config.get('bitmessagesettings', 'port')))
        self.ui.checkBoxAuthentication.setChecked(shared.config.getboolean(
            'bitmessagesettings', 'socksauthentication'))
        self.ui.checkBoxSocksListen.setChecked(shared.config.getboolean(
            'bitmessagesettings', 'sockslisten'))
        if str(shared.config.get('bitmessagesettings', 'socksproxytype')) == 'none':
            self.ui.comboBoxProxyType.setCurrentIndex(0)
            self.ui.lineEditSocksHostname.setEnabled(False)
            self.ui.lineEditSocksPort.setEnabled(False)
            self.ui.lineEditSocksUsername.setEnabled(False)
            self.ui.lineEditSocksPassword.setEnabled(False)
            self.ui.checkBoxAuthentication.setEnabled(False)
            self.ui.checkBoxSocksListen.setEnabled(False)
        elif str(shared.config.get('bitmessagesettings', 'socksproxytype')) == 'SOCKS4a':
            self.ui.comboBoxProxyType.setCurrentIndex(1)
            self.ui.lineEditTCPPort.setEnabled(False)
        elif str(shared.config.get('bitmessagesettings', 'socksproxytype')) == 'SOCKS5':
            self.ui.comboBoxProxyType.setCurrentIndex(2)
            self.ui.lineEditTCPPort.setEnabled(False)

        self.ui.lineEditSocksHostname.setText(str(
            shared.config.get('bitmessagesettings', 'sockshostname')))
        self.ui.lineEditSocksPort.setText(str(
            shared.config.get('bitmessagesettings', 'socksport')))
        self.ui.lineEditSocksUsername.setText(str(
            shared.config.get('bitmessagesettings', 'socksusername')))
        self.ui.lineEditSocksPassword.setText(str(
            shared.config.get('bitmessagesettings', 'sockspassword')))
        QtCore.QObject.connect(self.ui.comboBoxProxyType, QtCore.SIGNAL(
            "currentIndexChanged(int)"), self.comboBoxProxyTypeChanged)

        self.ui.lineEditTotalDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'defaultnoncetrialsperbyte')) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
        self.ui.lineEditSmallMessageDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes')) / shared.networkDefaultPayloadLengthExtraBytes)))

        # Max acceptable difficulty tab
        self.ui.lineEditMaxAcceptableTotalDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'maxacceptablenoncetrialsperbyte')) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
        self.ui.lineEditMaxAcceptableSmallMessageDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes')) / shared.networkDefaultPayloadLengthExtraBytes)))

        #'System' tab removed for now.
        """try:
            maxCores = shared.config.getint('bitmessagesettings', 'maxcores')
        except:
            maxCores = 99999
        if maxCores <= 1:
            self.ui.comboBoxMaxCores.setCurrentIndex(0)
        elif maxCores == 2:
            self.ui.comboBoxMaxCores.setCurrentIndex(1)
        elif maxCores <= 4:
            self.ui.comboBoxMaxCores.setCurrentIndex(2)
        elif maxCores <= 8:
            self.ui.comboBoxMaxCores.setCurrentIndex(3)
        elif maxCores <= 16:
            self.ui.comboBoxMaxCores.setCurrentIndex(4)
        else:
            self.ui.comboBoxMaxCores.setCurrentIndex(5)"""

        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))

    def comboBoxProxyTypeChanged(self, comboBoxIndex):
        if comboBoxIndex == 0:
            self.ui.lineEditSocksHostname.setEnabled(False)
            self.ui.lineEditSocksPort.setEnabled(False)
            self.ui.lineEditSocksUsername.setEnabled(False)
            self.ui.lineEditSocksPassword.setEnabled(False)
            self.ui.checkBoxAuthentication.setEnabled(False)
            self.ui.checkBoxSocksListen.setEnabled(False)
            self.ui.lineEditTCPPort.setEnabled(True)
        elif comboBoxIndex == 1 or comboBoxIndex == 2:
            self.ui.lineEditSocksHostname.setEnabled(True)
            self.ui.lineEditSocksPort.setEnabled(True)
            self.ui.checkBoxAuthentication.setEnabled(True)
            self.ui.checkBoxSocksListen.setEnabled(True)
            if self.ui.checkBoxAuthentication.isChecked():
                self.ui.lineEditSocksUsername.setEnabled(True)
                self.ui.lineEditSocksPassword.setEnabled(True)
            self.ui.lineEditTCPPort.setEnabled(False)


class SpecialAddressBehaviorDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SpecialAddressBehaviorDialog()
        self.ui.setupUi(self)
        self.parent = parent
        currentRow = parent.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = str(
            parent.ui.tableWidgetYourIdentities.item(currentRow, 1).text())
        if shared.safeConfigGetBoolean(addressAtCurrentRow, 'mailinglist'):
            self.ui.radioButtonBehaviorMailingList.click()
        else:
            self.ui.radioButtonBehaveNormalAddress.click()
        try:
            mailingListName = shared.config.get(
                addressAtCurrentRow, 'mailinglistname')
        except:
            mailingListName = ''
        self.ui.lineEditMailingListName.setText(
            unicode(mailingListName, 'utf-8'))
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


class NewSubscriptionDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewSubscriptionDialog()
        self.ui.setupUi(self)
        self.parent = parent
        QtCore.QObject.connect(self.ui.lineEditSubscriptionAddress, QtCore.SIGNAL(
            "textChanged(QString)"), self.subscriptionAddressChanged)

    def subscriptionAddressChanged(self, QString):
        status, a, b, c = decodeAddress(str(QString))
        if status == 'missingbm':
            self.ui.labelSubscriptionAddressCheck.setText(_translate(
                "MainWindow", "The address should start with ''BM-''"))
        elif status == 'checksumfailed':
            self.ui.labelSubscriptionAddressCheck.setText(_translate(
                "MainWindow", "The address is not typed or copied correctly (the checksum failed)."))
        elif status == 'versiontoohigh':
            self.ui.labelSubscriptionAddressCheck.setText(_translate(
                "MainWindow", "The version number of this address is higher than this software can support. Please upgrade Bitmessage."))
        elif status == 'invalidcharacters':
            self.ui.labelSubscriptionAddressCheck.setText(_translate(
                "MainWindow", "The address contains invalid characters."))
        elif status == 'ripetooshort':
            self.ui.labelSubscriptionAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too short."))
        elif status == 'ripetoolong':
            self.ui.labelSubscriptionAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too long."))
        elif status == 'success':
            self.ui.labelSubscriptionAddressCheck.setText(
                _translate("MainWindow", "Address is valid."))


class NewAddressDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewAddressDialog()
        self.ui.setupUi(self)
        self.parent = parent
        row = 1
        # Let's fill out the 'existing address' combo box with addresses from
        # the 'Your Identities' tab.
        while self.parent.ui.tableWidgetYourIdentities.item(row - 1, 1):
            self.ui.radioButtonExisting.click()
            # print
            # self.parent.ui.tableWidgetYourIdentities.item(row-1,1).text()
            self.ui.comboBoxExisting.addItem(
                self.parent.ui.tableWidgetYourIdentities.item(row - 1, 1).text())
            row += 1
        self.ui.groupBoxDeterministic.setHidden(True)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))

class NewChanDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewChanDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.groupBoxCreateChan.setHidden(True)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))     


class iconGlossaryDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_iconGlossaryDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.labelPortNumber.setText(_translate(
            "MainWindow", "You are using TCP port %1. (This can be changed in the settings).").arg(str(shared.config.getint('bitmessagesettings', 'port'))))
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


# In order for the time columns on the Inbox and Sent tabs to be sorted
# correctly (rather than alphabetically), we need to overload the <
# operator and use this class instead of QTableWidgetItem.
class myTableWidgetItem(QTableWidgetItem):

    def __lt__(self, other):
        return int(self.data(33).toPyObject()) < int(other.data(33).toPyObject())

from threading import Thread
class UISignaler(Thread,QThread):

    def __init__(self, parent=None):
        Thread.__init__(self, parent)
        QThread.__init__(self, parent)

    def run(self):
        while True:
            try:
                command, data = shared.UISignalQueue.get()
                if command == 'writeNewAddressToTable':
                    label, address, streamNumber = data
                    self.emit(SIGNAL(
                        "writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), label, address, str(streamNumber))
                elif command == 'updateStatusBar':
                    self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"), data)
                elif command == 'updateSentItemStatusByHash':
                    hash, message = data
                    self.emit(SIGNAL(
                        "updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"), hash, message)
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
                    self.emit(SIGNAL("updateNetworkStatusTab()"))
                elif command == 'incrementNumberOfMessagesProcessed':
                    self.emit(SIGNAL("incrementNumberOfMessagesProcessed()"))
                elif command == 'incrementNumberOfPubkeysProcessed':
                    self.emit(SIGNAL("incrementNumberOfPubkeysProcessed()"))
                elif command == 'incrementNumberOfBroadcastsProcessed':
                    self.emit(SIGNAL("incrementNumberOfBroadcastsProcessed()"))
                elif command == 'setStatusIcon':
                    self.emit(SIGNAL("setStatusIcon(PyQt_PyObject)"), data)
                elif command == 'rerenderInboxFromLabels':
                    self.emit(SIGNAL("rerenderInboxFromLabels()"))
                elif command == 'rerenderSubscriptions':
                    self.emit(SIGNAL("rerenderSubscriptions()"))
                elif command == 'removeInboxRowByMsgid':
                    self.emit(SIGNAL("removeInboxRowByMsgid(PyQt_PyObject)"), data)
                else:
                    sys.stderr.write(
                        'Command sent to UISignaler not recognized: %s\n' % command)
            except Exception,ex:
                # uncaught exception will block gevent
                import traceback
                traceback.print_exc()
                traceback.print_stack()
                print ex
                pass

try:
    import gevent
except ImportError as ex:
    gevent = None
else:
    def mainloop(app):
        while True:
            app.processEvents()
            gevent.sleep(0.01)
    def testprint():
        #print 'this is running'
        gevent.spawn_later(1, testprint)

def run():
    app = QtGui.QApplication(sys.argv)
    translator = QtCore.QTranslator()

    try:
        translator.load("translations/bitmessage_" + str(locale.getlocale()[0]))
    except:
        # The above is not compatible with all versions of OSX.
        translator.load("translations/bitmessage_en_US") # Default to english.

    QtGui.QApplication.installTranslator(translator)
    app.setStyleSheet("QStatusBar::item { border: 0px solid black }")
    myapp = MyForm()

    if not shared.config.getboolean('bitmessagesettings', 'startintray'):
        myapp.show()

    myapp.appIndicatorInit(app)
    myapp.ubuntuMessagingMenuInit()
    myapp.notifierInit()
    if gevent is None:
        sys.exit(app.exec_())
    else:
        gevent.joinall([gevent.spawn(testprint), gevent.spawn(mainloop, app), gevent.spawn(mainloop, app), gevent.spawn(mainloop, app), gevent.spawn(mainloop, app), gevent.spawn(mainloop, app)])
        print 'done'
