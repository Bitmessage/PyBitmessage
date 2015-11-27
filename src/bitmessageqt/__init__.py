from debug import logger
withMessagingMenu = False
try:
    from gi.repository import MessagingMenu
    from gi.repository import Notify
    withMessagingMenu = True
except ImportError:
    MessagingMenu = None

try:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4.QtNetwork import QLocalSocket, QLocalServer

except Exception as err:
    logmsg = 'PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API. You can download it from http://www.riverbankcomputing.com/software/pyqt/download or by searching Google for \'PyQt Download\' (without quotes).'
    logger.critical(logmsg, exc_info=True)
    sys.exit()

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
except AttributeError:
    logger.exception('QtGui.QApplication.UnicodeUTF8 error', exc_info=True)

from addresses import *
import shared
from bitmessageui import *
from namecoin import namecoinConnection, ensureNamecoinOptions
from newaddressdialog import *
from newaddresswizard import *
from migrationwizard import *
from foldertree import *
from addaddressdialog import *
from newsubscriptiondialog import *
from regenerateaddresses import *
from newchandialog import *
from specialaddressbehavior import *
from emailgateway import *
from settings import *
import settingsmixin
from about import *
from help import *
from iconglossary import *
from connect import *
import sys
from time import strftime, localtime, gmtime
import time
import os
import hashlib
from pyelliptic.openssl import OpenSSL
import pickle
import platform
import textwrap
import debug
import subprocess
import datetime
from helper_sql import *
import l10n
import openclpow
import types
from utils import *
from collections import OrderedDict
from account import *

def _translate(context, text):
    return QtGui.QApplication.translate(context, text)

def change_translation(locale):
    global qtranslator
    qtranslator = QtCore.QTranslator()
    translationpath = os.path.join (shared.codePath(), 'translations', 'bitmessage_' + locale)
    qtranslator.load(translationpath)
    QtGui.QApplication.installTranslator(qtranslator)

class MyForm(settingsmixin.SMainWindow):

    # sound type constants
    SOUND_NONE = 0
    SOUND_KNOWN = 1
    SOUND_UNKNOWN = 2
    SOUND_CONNECTED = 3
    SOUND_DISCONNECTED = 4
    SOUND_CONNECTION_GREEN = 5

    # the last time that a message arrival sound was played
    lastSoundTime = datetime.datetime.now() - datetime.timedelta(days=1)

    # the maximum frequency of message sounds in seconds
    maxSoundFrequencySec = 60

    str_chan = '[chan]'

    def init_file_menu(self):
        QtCore.QObject.connect(self.ui.actionExit, QtCore.SIGNAL(
            "triggered()"), self.quit)
        QtCore.QObject.connect(self.ui.actionManageKeys, QtCore.SIGNAL(
            "triggered()"), self.click_actionManageKeys)
        QtCore.QObject.connect(self.ui.actionDeleteAllTrashedMessages,
                               QtCore.SIGNAL(
                                   "triggered()"),
                               self.click_actionDeleteAllTrashedMessages)
        QtCore.QObject.connect(self.ui.actionRegenerateDeterministicAddresses,
                               QtCore.SIGNAL(
                                   "triggered()"),
                               self.click_actionRegenerateDeterministicAddresses)
        QtCore.QObject.connect(self.ui.pushButtonAddChan, QtCore.SIGNAL(
            "clicked()"),
                               self.click_actionJoinChan) # also used for creating chans.
        QtCore.QObject.connect(self.ui.pushButtonNewAddress, QtCore.SIGNAL(
            "clicked()"), self.click_NewAddressDialog)
        QtCore.QObject.connect(self.ui.pushButtonAddAddressBook, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonAddAddressBook)
        QtCore.QObject.connect(self.ui.pushButtonAddSubscription, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonAddSubscription)
        QtCore.QObject.connect(self.ui.pushButtonAddBlacklist, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonAddBlacklist)
        QtCore.QObject.connect(self.ui.pushButtonTTL, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonTTL)
        QtCore.QObject.connect(self.ui.pushButtonSend, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonSend)
        QtCore.QObject.connect(self.ui.pushButtonFetchNamecoinID, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonFetchNamecoinID)
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

    def init_inbox_popup_menu(self, connectSignal=True):
        # Popup menu for the Inbox tab
        self.ui.inboxContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionReply = self.ui.inboxContextMenuToolbar.addAction(_translate(
            "MainWindow", "Reply"), self.on_action_InboxReply)
        self.actionAddSenderToAddressBook = self.ui.inboxContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Add sender to your Address Book"),
            self.on_action_InboxAddSenderToAddressBook)
        self.actionAddSenderToBlackList = self.ui.inboxContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Add sender to your Blacklist"),
            self.on_action_InboxAddSenderToBlackList)
        self.actionTrashInboxMessage = self.ui.inboxContextMenuToolbar.addAction(
            _translate("MainWindow", "Move to Trash"),
            self.on_action_InboxTrash)
        self.actionUndeleteTrashedMessage = self.ui.inboxContextMenuToolbar.addAction(
            _translate("MainWindow", "Undelete"),
            self.on_action_TrashUndelete)
        self.actionForceHtml = self.ui.inboxContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "View HTML code as formatted text"),
            self.on_action_InboxMessageForceHtml)
        self.actionSaveMessageAs = self.ui.inboxContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Save message as..."),
            self.on_action_InboxSaveMessageAs)
        self.actionMarkUnread = self.ui.inboxContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Mark Unread"), self.on_action_InboxMarkUnread)

        # contextmenu messagelists
        self.ui.tableWidgetInbox.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.tableWidgetInbox, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuInbox)
        self.ui.tableWidgetInboxSubscriptions.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.tableWidgetInboxSubscriptions, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuInbox)
        self.ui.tableWidgetInboxChans.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.tableWidgetInboxChans, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuInbox)

    def init_identities_popup_menu(self, connectSignal=True):
        # Popup menu for the Your Identities tab
        self.ui.addressContextMenuToolbarYourIdentities = QtGui.QToolBar()
        # Actions
        self.actionNewYourIdentities = self.ui.addressContextMenuToolbarYourIdentities.addAction(_translate(
            "MainWindow", "New"), self.on_action_YourIdentitiesNew)
        self.actionEnableYourIdentities = self.ui.addressContextMenuToolbarYourIdentities.addAction(
            _translate(
                "MainWindow", "Enable"), self.on_action_Enable)
        self.actionDisableYourIdentities = self.ui.addressContextMenuToolbarYourIdentities.addAction(
            _translate(
                "MainWindow", "Disable"), self.on_action_Disable)
        self.actionSetAvatarYourIdentities = self.ui.addressContextMenuToolbarYourIdentities.addAction(
            _translate(
                "MainWindow", "Set avatar..."),
            self.on_action_TreeWidgetSetAvatar)
        self.actionClipboardYourIdentities = self.ui.addressContextMenuToolbarYourIdentities.addAction(
            _translate(
                "MainWindow", "Copy address to clipboard"),
            self.on_action_Clipboard)
        self.actionSpecialAddressBehaviorYourIdentities = self.ui.addressContextMenuToolbarYourIdentities.addAction(
            _translate(
                "MainWindow", "Special address behavior..."),
            self.on_action_SpecialAddressBehaviorDialog)
        self.actionEmailGateway = self.ui.addressContextMenuToolbarYourIdentities.addAction(
            _translate(
                "MainWindow", "Email gateway"),
            self.on_action_EmailGatewayDialog)

        self.ui.treeWidgetYourIdentities.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.treeWidgetYourIdentities, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuYourIdentities)

    def init_chan_popup_menu(self, connectSignal=True):
        # Popup menu for the Channels tab
        self.ui.addressContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionNew = self.ui.addressContextMenuToolbar.addAction(_translate(
            "MainWindow", "New"), self.on_action_YourIdentitiesNew)
        self.actionDelete = self.ui.addressContextMenuToolbar.addAction(
            _translate("MainWindow", "Delete"),
            self.on_action_YourIdentitiesDelete)
        self.actionEnable = self.ui.addressContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Enable"), self.on_action_Enable)
        self.actionDisable = self.ui.addressContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Disable"), self.on_action_Disable)
        self.actionSetAvatar = self.ui.addressContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Set avatar..."),
            self.on_action_TreeWidgetSetAvatar)
        self.actionClipboard = self.ui.addressContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Copy address to clipboard"),
            self.on_action_Clipboard)
        self.actionSpecialAddressBehavior = self.ui.addressContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Special address behavior..."),
            self.on_action_SpecialAddressBehaviorDialog)

        self.ui.treeWidgetChans.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.treeWidgetChans, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuChan)

    def init_addressbook_popup_menu(self, connectSignal=True):
        # Popup menu for the Address Book page
        self.ui.addressBookContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionAddressBookSend = self.ui.addressBookContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Send message to this address"),
            self.on_action_AddressBookSend)
        self.actionAddressBookClipboard = self.ui.addressBookContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Copy address to clipboard"),
            self.on_action_AddressBookClipboard)
        self.actionAddressBookSubscribe = self.ui.addressBookContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Subscribe to this address"),
            self.on_action_AddressBookSubscribe)
        self.actionAddressBookSetAvatar = self.ui.addressBookContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Set avatar..."),
            self.on_action_AddressBookSetAvatar)
        self.actionAddressBookNew = self.ui.addressBookContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Add New Address"), self.on_action_AddressBookNew)
        self.actionAddressBookDelete = self.ui.addressBookContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Delete"), self.on_action_AddressBookDelete)
        self.ui.tableWidgetAddressBook.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuAddressBook)

    def init_subscriptions_popup_menu(self, connectSignal=True):
        # Popup menu for the Subscriptions page
        self.ui.subscriptionsContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionsubscriptionsNew = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "New"), self.on_action_SubscriptionsNew)
        self.actionsubscriptionsDelete = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Delete"),
            self.on_action_SubscriptionsDelete)
        self.actionsubscriptionsClipboard = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Copy address to clipboard"),
            self.on_action_SubscriptionsClipboard)
        self.actionsubscriptionsEnable = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Enable"),
            self.on_action_SubscriptionsEnable)
        self.actionsubscriptionsDisable = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Disable"),
            self.on_action_SubscriptionsDisable)
        self.actionsubscriptionsSetAvatar = self.ui.subscriptionsContextMenuToolbar.addAction(
            _translate("MainWindow", "Set avatar..."),
            self.on_action_TreeWidgetSetAvatar)
        self.ui.treeWidgetSubscriptions.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.treeWidgetSubscriptions, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuSubscriptions)

    def init_sent_popup_menu(self, connectSignal=True):
        # Popup menu for the Sent page
        self.ui.sentContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionTrashSentMessage = self.ui.sentContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Move to Trash"), self.on_action_SentTrash)
        self.actionSentClipboard = self.ui.sentContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Copy destination address to clipboard"),
            self.on_action_SentClipboard)
        self.actionForceSend = self.ui.sentContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Force send"), self.on_action_ForceSend)
        # self.popMenuSent = QtGui.QMenu( self )
        # self.popMenuSent.addAction( self.actionSentClipboard )
        # self.popMenuSent.addAction( self.actionTrashSentMessage )

    def init_blacklist_popup_menu(self, connectSignal=True):
        # Popup menu for the Blacklist page
        self.ui.blacklistContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionBlacklistNew = self.ui.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Add new entry"), self.on_action_BlacklistNew)
        self.actionBlacklistDelete = self.ui.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Delete"), self.on_action_BlacklistDelete)
        self.actionBlacklistClipboard = self.ui.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Copy address to clipboard"),
            self.on_action_BlacklistClipboard)
        self.actionBlacklistEnable = self.ui.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Enable"), self.on_action_BlacklistEnable)
        self.actionBlacklistDisable = self.ui.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Disable"), self.on_action_BlacklistDisable)
        self.actionBlacklistSetAvatar = self.ui.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Set avatar..."),
            self.on_action_BlacklistSetAvatar)
        self.ui.tableWidgetBlacklist.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.tableWidgetBlacklist, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                        self.on_context_menuBlacklist)
        self.popMenuBlacklist = QtGui.QMenu(self)
        # self.popMenuBlacklist.addAction( self.actionBlacklistNew )
        self.popMenuBlacklist.addAction(self.actionBlacklistDelete)
        self.popMenuBlacklist.addSeparator()
        self.popMenuBlacklist.addAction(self.actionBlacklistClipboard)
        self.popMenuBlacklist.addSeparator()
        self.popMenuBlacklist.addAction(self.actionBlacklistEnable)
        self.popMenuBlacklist.addAction(self.actionBlacklistDisable)
        self.popMenuBlacklist.addAction(self.actionBlacklistSetAvatar)

    def rerenderTabTreeSubscriptions(self):
        treeWidget = self.ui.treeWidgetSubscriptions
        folders = Ui_FolderWidget.folderWeight.keys()
        folders.remove("new")

        # sort ascending when creating
        if treeWidget.topLevelItemCount() == 0:
            treeWidget.header().setSortIndicator(0, Qt.AscendingOrder)
        # init dictionary
        
        db = getSortedSubscriptions(True)
        for address in db:
            for folder in folders:
                if not folder in db[address]:
                    db[address][folder] = {}
            
        if treeWidget.isSortingEnabled():
            treeWidget.setSortingEnabled(False)

        widgets = {}
        i = 0
        while i < treeWidget.topLevelItemCount():
            widget = treeWidget.topLevelItem(i)
            if widget is not None:
                toAddress = widget.address
            else:
                toAddress = None
            
            if not toAddress in db:
                treeWidget.takeTopLevelItem(i)
                # no increment
                continue
            unread = 0
            j = 0
            while j < widget.childCount():
                subwidget = widget.child(j)
                try:
                    subwidget.setUnreadCount(db[toAddress][subwidget.folderName]['count'])
                    unread += db[toAddress][subwidget.folderName]['count']
                    db[toAddress].pop(subwidget.folderName, None)
                except:
                    widget.takeChild(j)
                    # no increment
                    continue
                j += 1

            # add missing folders
            if len(db[toAddress]) > 0:
                j = 0
                for f, c in db[toAddress].iteritems():
                    try:
                        subwidget = Ui_FolderWidget(widget, j, toAddress, f, c['count'])
                    except KeyError:
                        subwidget = Ui_FolderWidget(widget, j, toAddress, f, 0)
                    j += 1
            widget.setUnreadCount(unread)
            db.pop(toAddress, None)
            i += 1
        
        i = 0
        for toAddress in db:
            widget = Ui_SubscriptionWidget(treeWidget, i, toAddress, db[toAddress]["inbox"]['count'], db[toAddress]["inbox"]['label'], db[toAddress]["inbox"]['enabled'])
            j = 0
            unread = 0
            for folder in folders:
                try:
                    subwidget = Ui_FolderWidget(widget, j, toAddress, folder, db[toAddress][folder]['count'])
                    unread += db[toAddress][folder]['count']
                except KeyError:
                    subwidget = Ui_FolderWidget(widget, j, toAddress, folder, 0)
                j += 1
            widget.setUnreadCount(unread)
            widget.setFlags (widget.flags() | QtCore.Qt.ItemIsEditable)
            i += 1
        
        treeWidget.setSortingEnabled(True)


    def rerenderTabTreeMessages(self):
        self.rerenderTabTree('messages')

    def rerenderTabTreeChans(self):
        self.rerenderTabTree('chan')
        
    def rerenderTabTree(self, tab):
        if tab == 'messages':
            treeWidget = self.ui.treeWidgetYourIdentities
        elif tab == 'chan':
            treeWidget = self.ui.treeWidgetChans
        folders = Ui_FolderWidget.folderWeight.keys()
        
        # sort ascending when creating
        if treeWidget.topLevelItemCount() == 0:
            treeWidget.header().setSortIndicator(0, Qt.AscendingOrder)
        # init dictionary
        db = {}
        enabled = {}
        
        for toAddress in getSortedAccounts():
            isEnabled = shared.config.getboolean(
                toAddress, 'enabled')
            isChan = shared.safeConfigGetBoolean(
                toAddress, 'chan')
            isMaillinglist = shared.safeConfigGetBoolean(
                toAddress, 'mailinglist')

            if tab == 'messages':
                if isChan:
                    continue
            elif tab == 'chan':
                if not isChan:
                    continue

            db[toAddress] = {}
            for folder in folders:
                db[toAddress][folder] = 0
                
            enabled[toAddress] = isEnabled

        # get number of (unread) messages
        total = 0
        queryreturn = sqlQuery('SELECT toaddress, folder, count(msgid) as cnt FROM inbox WHERE read = 0 GROUP BY toaddress, folder')
        for row in queryreturn:
            toaddress, folder, cnt = row
            total += cnt
            if toaddress in db and folder in db[toaddress]:
                db[toaddress][folder] = cnt
        if tab == "messages":
            db[None] = {}
            db[None]["inbox"] = total
            db[None]["new"] = total
            enabled[None] = True
        
        if treeWidget.isSortingEnabled():
            treeWidget.setSortingEnabled(False)
        
        widgets = {}
        i = 0
        while i < treeWidget.topLevelItemCount():
            widget = treeWidget.topLevelItem(i)
            if widget is not None:
                toAddress = widget.address
            else:
                toAddress = None
            
            if not toAddress in db:
                treeWidget.takeTopLevelItem(i)
                # no increment
                continue
            unread = 0
            j = 0
            while j < widget.childCount():
                subwidget = widget.child(j)
                try:
                    subwidget.setUnreadCount(db[toAddress][subwidget.folderName])
                    unread += db[toAddress][subwidget.folderName]
                    db[toAddress].pop(subwidget.folderName, None)
                except:
                    widget.takeChild(j)
                    # no increment
                    continue
                j += 1

            # add missing folders
            if len(db[toAddress]) > 0:
                j = 0
                for f, c in db[toAddress].iteritems():
                    subwidget = Ui_FolderWidget(widget, j, toAddress, f, c)
                    j += 1
            widget.setUnreadCount(unread)
            db.pop(toAddress, None)
            i += 1
        
        i = 0
        for toAddress in db:
            widget = Ui_AddressWidget(treeWidget, i, toAddress, db[toAddress]["inbox"], enabled[toAddress])
            j = 0
            unread = 0
            for folder in folders:
                if toAddress is not None and folder == "new":
                    continue
                if toAddress is None and folder in ["trash", "sent"]:
                    continue
                subwidget = Ui_FolderWidget(widget, j, toAddress, folder, db[toAddress][folder])
                unread += db[toAddress][folder]
                j += 1
            widget.setUnreadCount(unread)
            widget.setFlags (widget.flags() | QtCore.Qt.ItemIsEditable)
            i += 1
        
        treeWidget.setSortingEnabled(True)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Ask the user if we may delete their old version 1 addresses if they
        # have any.
        for addressInKeysFile in getSortedAccounts():
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
                    shared.writeKeysFile()

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


        self.totalNumberOfBytesReceived = 0
        self.totalNumberOfBytesSent = 0
        
        self.timer = QtCore.QTimer()
        self.timer.start(2000) # milliseconds
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.runEveryTwoSeconds)

        # e.g. for editing labels
        self.recurDepth = 0
        
        # switch back to this when replying
        self.replyFromTab = None
        
        self.init_file_menu()
        self.init_inbox_popup_menu()
        self.init_identities_popup_menu()
        self.init_addressbook_popup_menu()
        self.init_subscriptions_popup_menu()
        self.init_chan_popup_menu()
        self.init_sent_popup_menu()
        self.init_blacklist_popup_menu()
        
        # Initialize the user's list of addresses on the 'Chan' tab.
        self.rerenderTabTreeChans()

        # Initialize the user's list of addresses on the 'Messages' tab.
        self.rerenderTabTreeMessages()

        # Set welcome message
        self.ui.textEditInboxMessage.setText(
        """
        Welcome to easy and secure Bitmessage
            * send messages to other people
            * send broadcast messages like twitter or
            * discuss in chan(nel)s with other people
        """
        )

        # Initialize the address book
        self.rerenderAddressBook()

        # Initialize the Subscriptions
        self.rerenderSubscriptions()

        # Initialize the inbox search
        QtCore.QObject.connect(self.ui.inboxSearchLineEdit, QtCore.SIGNAL(
            "returnPressed()"), self.inboxSearchLineEditPressed)
        QtCore.QObject.connect(self.ui.inboxSearchLineEditSubscriptions, QtCore.SIGNAL(
            "returnPressed()"), self.inboxSearchLineEditPressed)
        QtCore.QObject.connect(self.ui.inboxSearchLineEditChans, QtCore.SIGNAL(
            "returnPressed()"), self.inboxSearchLineEditPressed)

        # Initialize the Blacklist or Whitelist
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'white':
            self.ui.tabWidget.setTabText(6, 'Whitelist')
            self.ui.radioButtonWhitelist.click()
        self.rerenderBlackWhiteList()

        # Initialize addressbook
        QtCore.QObject.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL(
            "itemChanged(QTableWidgetItem *)"), self.tableWidgetAddressBookItemChanged)

        # show messages from message list
        QtCore.QObject.connect(self.ui.tableWidgetInbox, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.tableWidgetInboxItemClicked)
        QtCore.QObject.connect(self.ui.tableWidgetInboxSubscriptions, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.tableWidgetInboxItemClicked)
        QtCore.QObject.connect(self.ui.tableWidgetInboxChans, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.tableWidgetInboxItemClicked)

        # tree address lists
        QtCore.QObject.connect(self.ui.treeWidgetYourIdentities, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.treeWidgetItemClicked)
        QtCore.QObject.connect(self.ui.treeWidgetYourIdentities, QtCore.SIGNAL(
            "itemChanged (QTreeWidgetItem *, int)"), self.treeWidgetItemChanged)
        QtCore.QObject.connect(self.ui.treeWidgetSubscriptions, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.treeWidgetItemClicked)
        QtCore.QObject.connect(self.ui.treeWidgetSubscriptions, QtCore.SIGNAL(
            "itemChanged (QTreeWidgetItem *, int)"), self.treeWidgetItemChanged)
        QtCore.QObject.connect(self.ui.treeWidgetChans, QtCore.SIGNAL(
            "itemSelectionChanged ()"), self.treeWidgetItemClicked)
        QtCore.QObject.connect(self.ui.treeWidgetChans, QtCore.SIGNAL(
            "itemChanged (QTreeWidgetItem *, int)"), self.treeWidgetItemChanged)

        # Put the colored icon on the status bar
        # self.ui.pushButtonStatusIcon.setIcon(QIcon(":/newPrefix/images/yellowicon.png"))
        self.statusbar = self.statusBar()
        self.statusbar.insertPermanentWidget(0, self.ui.pushButtonStatusIcon)
        self.ui.labelStartupTime.setText(_translate("MainWindow", "Since startup on %1").arg(
            l10n.formatTimestamp()))
        self.numberOfMessagesProcessed = 0
        self.numberOfBroadcastsProcessed = 0
        self.numberOfPubkeysProcessed = 0
        self.unreadCount = 0

        # Set the icon sizes for the identicons
        identicon_size = 3*7
        self.ui.tableWidgetInbox.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.treeWidgetChans.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.treeWidgetYourIdentities.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.treeWidgetSubscriptions.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.tableWidgetAddressBook.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.tableWidgetBlacklist.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        
        self.UISignalThread = UISignaler()
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateSentItemStatusByToAddress(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByToAddress)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByAckdata)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "displayNewInboxMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewInboxMessage)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewSentMessage)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNetworkStatusTab()"), self.updateNetworkStatusTab)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfMessagesProcessed()"), self.updateNumberOfMessagesProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfPubkeysProcessed()"), self.updateNumberOfPubkeysProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfBroadcastsProcessed()"), self.updateNumberOfBroadcastsProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "setStatusIcon(PyQt_PyObject)"), self.setStatusIcon)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "changedInboxUnread(PyQt_PyObject)"), self.changedInboxUnread)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderInboxFromLabels()"), self.rerenderInboxFromLabels)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderSentToLabels()"), self.rerenderSentToLabels)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderAddressBook()"), self.rerenderAddressBook)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderSubscriptions()"), self.rerenderSubscriptions)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderBlackWhiteList()"), self.rerenderBlackWhiteList)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "removeInboxRowByMsgid(PyQt_PyObject)"), self.removeInboxRowByMsgid)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "newVersionAvailable(PyQt_PyObject)"), self.newVersionAvailable)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "displayAlert(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayAlert)
        self.UISignalThread.start()

        # Below this point, it would be good if all of the necessary global data
        # structures were initialized.

        self.rerenderComboBoxSendFrom()
        self.rerenderComboBoxSendFromBroadcast()
        
        # Put the TTL slider in the correct spot
        TTL = shared.config.getint('bitmessagesettings', 'ttl')
        if TTL < 3600: # an hour
            TTL = 3600
        elif TTL > 28*24*60*60: # 28 days
            TTL = 28*24*60*60
        self.ui.horizontalSliderTTL.setSliderPosition((TTL - 3600) ** (1/3.199))
        self.updateHumanFriendlyTTLDescription(TTL)
        
        QtCore.QObject.connect(self.ui.horizontalSliderTTL, QtCore.SIGNAL(
            "valueChanged(int)"), self.updateTTL)

        self.initSettings()
            
        # Check to see whether we can connect to namecoin. Hide the 'Fetch Namecoin ID' button if we can't.
        try:
            options = {}
            options["type"] = shared.config.get('bitmessagesettings', 'namecoinrpctype')
            options["host"] = shared.config.get('bitmessagesettings', 'namecoinrpchost')
            options["port"] = shared.config.get('bitmessagesettings', 'namecoinrpcport')
            options["user"] = shared.config.get('bitmessagesettings', 'namecoinrpcuser')
            options["password"] = shared.config.get('bitmessagesettings', 'namecoinrpcpassword')
            nc = namecoinConnection(options)
            if nc.test()[0] == 'failed':
                self.ui.pushButtonFetchNamecoinID.hide()
        except:
            logger.error('There was a problem testing for a Namecoin daemon. Hiding the Fetch Namecoin ID button')
            self.ui.pushButtonFetchNamecoinID.hide()
            
    def updateTTL(self, sliderPosition):
        TTL = int(sliderPosition ** 3.199 + 3600)
        self.updateHumanFriendlyTTLDescription(TTL)
        shared.config.set('bitmessagesettings', 'ttl', str(TTL))
        shared.writeKeysFile()
        
    def updateHumanFriendlyTTLDescription(self, TTL):
        numberOfHours = int(round(TTL / (60*60)))
        if numberOfHours < 48:
            if numberOfHours == 1:
                self.ui.labelHumanFriendlyTTLDescription.setText(_translate("MainWindow", "1 hour"))
            else:
                self.ui.labelHumanFriendlyTTLDescription.setText(_translate("MainWindow", "%1 hours").arg(numberOfHours))
        else:
            numberOfDays = int(round(TTL / (24*60*60)))
            self.ui.labelHumanFriendlyTTLDescription.setText(_translate("MainWindow", "%1 days").arg(numberOfDays))

    # Show or hide the application window after clicking an item within the
    # tray icon or, on Windows, the try icon itself.
    def appIndicatorShowOrHideWindow(self):
        if not self.actionShow.isChecked():
            self.hide()
        else:
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
        self.ui.tabWidget.setCurrentIndex(2)

    # Show the program window and select channels tab
    def appIndicatorChannel(self):
        self.appIndicatorShow()
        self.ui.tabWidget.setCurrentIndex(3)
        
    def propagateUnreadCount(self, address = None, folder = "inbox", widget = None, type = 1):
        def updateUnreadCount(item):
            # if refreshing the account root, we need to rescan folders
            if type == 0 or (folder is None and isinstance(item, Ui_FolderWidget)):
                if addressItem.type in [AccountMixin.SUBSCRIPTION, AccountMixin.MAILINGLIST]:
                    xAddress = "fromaddress"
                else:
                    xAddress = "toaddress"
                xFolder = folder
                if isinstance(item, Ui_FolderWidget):
                    xFolder = item.folderName
                if address and xFolder:
                    queryreturn = sqlQuery("SELECT COUNT(*) FROM inbox WHERE " + xAddress + " = ? AND folder = ? AND read = 0", address, xFolder)
                elif address:
                    queryreturn = sqlQuery("SELECT COUNT(*) FROM inbox WHERE " + xAddress + " = ? AND read = 0", address)
                elif xFolder:
                    queryreturn = sqlQuery("SELECT COUNT(*) FROM inbox WHERE folder = ? AND read = 0", xFolder)
                else:
                    queryreturn = sqlQuery("SELECT COUNT(*) FROM inbox WHERE read = 0")
                for row in queryreturn:
                    item.setUnreadCount(int(row[0]))
                if isinstance(item, Ui_AddressWidget) and item.type == AccountMixin.ALL:
                    self.drawTrayIcon(self.currentTrayIconFileName, self.findInboxUnreadCount())
            elif type == 1:
                item.setUnreadCount(item.unreadCount + 1)
                if isinstance(item, Ui_AddressWidget) and item.type == AccountMixin.ALL:
                    self.drawTrayIcon(self.currentTrayIconFileName, self.findInboxUnreadCount(self.unreadCount + 1))
            elif type == -1:
                item.setUnreadCount(item.unreadCount - 1)
                if isinstance(item, Ui_AddressWidget) and item.type == AccountMixin.ALL:
                    self.drawTrayIcon(self.currentTrayIconFileName, self.findInboxUnreadCount(self.unreadCount -1))
                
        widgets = [self.ui.treeWidgetYourIdentities, self.ui.treeWidgetSubscriptions, self.ui.treeWidgetChans]
        # FIXME this is a hack
        if folder == "new":
            folder = "inbox"
        for treeWidget in widgets:
            root = treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                addressItem = root.child(i)
                if addressItem.type != AccountMixin.ALL and address is not None and addressItem.data(0, QtCore.Qt.UserRole) != address:
                    continue
                updateUnreadCount(addressItem)
                if addressItem.childCount == 0:
                    continue
                for j in range(addressItem.childCount()):
                    folderItem = addressItem.child(j)
                    if folder is not None and folderItem.folderName != folder and addressItem.type != AccountMixin.ALL:
                        continue
                    updateUnreadCount(folderItem)

    def addMessageListItem(self, tableWidget, items):
        tableWidget.insertRow(0)
        for i in range(len(items)):
            tableWidget.setItem(0, i, items[i])

    def addMessageListItemSent(self, tableWidget, toAddress, fromAddress, subject, status, ackdata, lastactiontime):
        subject = shared.fixPotentiallyInvalidUTF8Data(subject)
        acct = accountClass(fromAddress)
        acct.parseMessage(toAddress, fromAddress, subject, "")

        items = []
        toAddressItem = QtGui.QTableWidgetItem(unicode(acct.toLabel, 'utf-8'))
        toAddressItem.setToolTip(unicode(acct.toLabel, 'utf-8') + " (" + str(acct.toAddress) + ")")
        toAddressItem.setIcon(avatarize(toAddress))
        toAddressItem.setData(Qt.UserRole, str(toAddress))
        toAddressItem.setTextColor(AccountColor(toAddress).accountColor())
        toAddressItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        items.append(toAddressItem)

        fromAddressItem = QtGui.QTableWidgetItem(unicode(acct.fromLabel, 'utf-8'))
        fromAddressItem.setToolTip(unicode(acct.fromLabel, 'utf-8') + " (" + str(acct.fromAddress) + ")")
        fromAddressItem.setIcon(avatarize(fromAddress))
        fromAddressItem.setData(Qt.UserRole, str(fromAddress))
        fromAddressItem.setTextColor(AccountColor(fromAddress).accountColor())
        fromAddressItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        items.append(fromAddressItem)

        subjectItem = QtGui.QTableWidgetItem(unicode(acct.subject, 'utf-8'))
        subjectItem.setToolTip(unicode(acct.subject, 'utf-8'))
        subjectItem.setData(Qt.UserRole, str(subject))
        subjectItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        items.append(subjectItem)

        if status == 'awaitingpubkey':
            statusText = _translate(
                "MainWindow", "Waiting for their encryption key. Will request it again soon.")
        elif status == 'doingpowforpubkey':
            statusText = _translate(
                "MainWindow", "Encryption key request queued.")
        elif status == 'msgqueued':
            statusText = _translate(
                "MainWindow", "Queued.")
        elif status == 'msgsent':
            statusText = _translate("MainWindow", "Message sent. Waiting for acknowledgement. Sent at %1").arg(
                l10n.formatTimestamp(lastactiontime))
        elif status == 'msgsentnoackexpected':
            statusText = _translate("MainWindow", "Message sent. Sent at %1").arg(
                l10n.formatTimestamp(lastactiontime))
        elif status == 'doingmsgpow':
            statusText = _translate(
                "MainWindow", "Need to do work to send message. Work is queued.")
        elif status == 'ackreceived':
            statusText = _translate("MainWindow", "Acknowledgement of the message received %1").arg(
                l10n.formatTimestamp(lastactiontime))
        elif status == 'broadcastqueued':
            statusText = _translate(
                "MainWindow", "Broadcast queued.")
        elif status == 'broadcastsent':
            statusText = _translate("MainWindow", "Broadcast on %1").arg(
                l10n.formatTimestamp(lastactiontime))
        elif status == 'toodifficult':
            statusText = _translate("MainWindow", "Problem: The work demanded by the recipient is more difficult than you are willing to do. %1").arg(
                l10n.formatTimestamp(lastactiontime))
        elif status == 'badkey':
            statusText = _translate("MainWindow", "Problem: The recipient\'s encryption key is no good. Could not encrypt message. %1").arg(
                l10n.formatTimestamp(lastactiontime))
        elif status == 'forcepow':
            statusText = _translate(
                "MainWindow", "Forced difficulty override. Send should start soon.")
        else:
            statusText = _translate("MainWindow", "Unknown status: %1 %2").arg(status).arg(
                l10n.formatTimestamp(lastactiontime))
        newItem = myTableWidgetItem(statusText)
        newItem.setToolTip(statusText)
        newItem.setData(Qt.UserRole, QByteArray(ackdata))
        newItem.setData(33, int(lastactiontime))
        newItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        items.append(newItem)
        self.addMessageListItem(tableWidget, items)
        return acct

    def addMessageListItemInbox(self, tableWidget, msgfolder, msgid, toAddress, fromAddress, subject, received, read):
        font = QFont()
        font.setBold(True)
        if tableWidget == self.ui.tableWidgetInboxSubscriptions:
            acct = accountClass(fromAddress)
        else:
            acct = accountClass(toAddress)
        subject = shared.fixPotentiallyInvalidUTF8Data(subject)
        acct.parseMessage(toAddress, fromAddress, subject, "")
            
        items = []
        #to
        to_item = QtGui.QTableWidgetItem(unicode(acct.toLabel, 'utf-8'))
        to_item.setToolTip(unicode(acct.toLabel, 'utf-8') + " (" + str(acct.toAddress) + ")")
        to_item.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        if not read:
            to_item.setFont(font)
        to_item.setData(Qt.UserRole, str(toAddress))
        to_item.setTextColor(AccountColor(toAddress).accountColor())
        to_item.setIcon(avatarize(toAddress))
        items.append(to_item)
        # from
        from_item = QtGui.QTableWidgetItem(unicode(acct.fromLabel, 'utf-8'))
        from_item.setToolTip(unicode(acct.fromLabel, 'utf-8') + " (" + str(fromAddress) + ")")
        from_item.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        if not read:
            from_item.setFont(font)
        from_item.setData(Qt.UserRole, str(fromAddress))
        from_item.setTextColor(AccountColor(fromAddress).accountColor())
        from_item.setIcon(avatarize(fromAddress))
        items.append(from_item)
        # subject
        subject_item = QtGui.QTableWidgetItem(unicode(acct.subject, 'utf-8'))
        subject_item.setToolTip(unicode(acct.subject, 'utf-8'))
        subject_item.setData(Qt.UserRole, str(subject))
        subject_item.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        if not read:
            subject_item.setFont(font)
        items.append(subject_item)
        # time received
        time_item = myTableWidgetItem(l10n.formatTimestamp(received))
        time_item.setToolTip(l10n.formatTimestamp(received))
        time_item.setData(Qt.UserRole, QByteArray(msgid))
        time_item.setData(33, int(received))
        time_item.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        if not read:
            time_item.setFont(font)
        items.append(time_item)
        self.addMessageListItem(tableWidget, items)
        return acct

    # Load Sent items from database
    def loadSent(self, tableWidget, account, where="", what=""):
        what = "%" + what + "%"
        if where == _translate("MainWindow", "To"):
            where = "toaddress"
        elif where == _translate("MainWindow", "From"):
            where = "fromaddress"
        elif where == _translate("MainWindow", "Subject"):
            where = "subject"
        elif where == _translate("MainWindow", "Message"):
            where = "message"
        else:
            where = "toaddress || fromaddress || subject || message"

        tableWidget.setSortingEnabled(False)
        
        if tableWidget == self.ui.tableWidgetInboxChans or tableWidget == self.ui.tableWidgetInboxSubscriptions:
            tableWidget.setColumnHidden(0, True)
            tableWidget.setColumnHidden(1, False)
            xAddress = 'toaddress'
        else:
            tableWidget.setColumnHidden(0, False)
            tableWidget.setColumnHidden(1, True)
            xAddress = 'fromaddress'
        
        sqlStatement = '''
            SELECT toaddress, fromaddress, subject, status, ackdata, lastactiontime 
            FROM sent WHERE ''' + xAddress + '''=? AND folder="sent" AND %s LIKE ? 
            ORDER BY lastactiontime
            ''' % (where,)

        tableWidget.setRowCount(0)
        acct = None
        queryreturn = sqlQuery(sqlStatement, account, what)
        for row in queryreturn:
            toAddress, fromAddress, subject, status, ackdata, lastactiontime = row
            self.addMessageListItemSent(tableWidget, toAddress, fromAddress, subject, status, ackdata, lastactiontime)

        tableWidget.setSortingEnabled(False)
        tableWidget.horizontalHeader().setSortIndicator(3, Qt.DescendingOrder)
        tableWidget.keyPressEvent = self.tableWidgetSentKeyPressEvent

    # Load messages from database file
    def loadMessagelist(self, tableWidget, account, folder="inbox", where="", what="", unreadOnly = False):
        if folder == 'sent':
            self.loadSent(tableWidget, account, where, what)
            return

        if what != "":
            what = "%" + what + "%"
            if where == _translate("MainWindow", "To"):
                where = "toaddress"
            elif where == _translate("MainWindow", "From"):
                where = "fromaddress"
            elif where == _translate("MainWindow", "Subject"):
                where = "subject"
            elif where == _translate("MainWindow", "Message"):
                where = "message"
            else:
                where = "toaddress || fromaddress || subject || message"
        else:
            what = None
        
        if tableWidget == self.ui.tableWidgetInboxSubscriptions:
            xAddress = "fromaddress"
        else:
            xAddress = "toaddress"
        sqlStatementBase = '''SELECT folder, msgid, toaddress, fromaddress, subject, received, read
            FROM inbox '''
        sqlStatementParts = []
        sqlArguments = []
        if account is not None:
            sqlStatementParts.append(xAddress + " = ? ")
            sqlArguments.append(account)
        if folder is not None:
            sqlStatementParts.append("folder = ? ")
            sqlArguments.append(folder)
        if what is not None:
            sqlStatementParts.append("%s LIKE ?" % (where))
            sqlArguments.append(what)
        if unreadOnly:
            sqlStatementParts.append("read = 0")
        if len(sqlStatementParts) > 0:
            sqlStatementBase += "WHERE " + " AND ".join(sqlStatementParts)
        queryreturn = sqlQuery(sqlStatementBase, sqlArguments)

        tableWidget.setRowCount(0)
        if account is not None:
            tableWidget.setColumnHidden(0, True)
            tableWidget.setColumnHidden(1, False)
        else:
            tableWidget.setColumnHidden(0, False)
            tableWidget.setColumnHidden(1, False)
        tableWidget.setSortingEnabled(False)
        
        for row in queryreturn:
            msgfolder, msgid, toAddress, fromAddress, subject, received, read = row
            self.addMessageListItemInbox(tableWidget, msgfolder, msgid, toAddress, fromAddress, subject, received, read)

        tableWidget.horizontalHeader().setSortIndicator(3, Qt.DescendingOrder)
        tableWidget.setSortingEnabled(True)
        tableWidget.keyPressEvent = self.tableWidgetInboxKeyPressEvent

    # create application indicator
    def appIndicatorInit(self, app):
        self.initTrayIcon("can-icon-24px-red.png", app)
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

        # Channels
        actionSubscribe = QtGui.QAction(_translate(
            "MainWindow", "Channel"), m, checkable=False)
        actionSubscribe.triggered.connect(self.appIndicatorChannel)
        m.addAction(actionSubscribe)

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

        queryreturn = sqlQuery(
            '''SELECT toaddress, read FROM inbox WHERE msgid=?''', inventoryHash)
        for row in queryreturn:
            toAddress, read = row
            if not read:
                if toAddress == str_broadcast_subscribers:
                    if self.mmapp.has_source("Subscriptions"):
                        self.mmapp.remove_source("Subscriptions")
                else:
                    if self.mmapp.has_source("Messages"):
                        self.mmapp.remove_source("Messages")

    # returns the number of unread messages and subscriptions
    def getUnread(self):
        unreadMessages = 0
        unreadSubscriptions = 0

        queryreturn = sqlQuery(
            '''SELECT msgid, toaddress, read FROM inbox where folder='inbox' ''')
        for row in queryreturn:
            msgid, toAddress, read = row

            try:
                if toAddress == str_broadcast_subscribers:
                    toLabel = str_broadcast_subscribers
                else:
                    toLabel = shared.config.get(toAddress, 'label')
            except:
                toLabel = ''
            if toLabel == '':
                toLabel = toAddress

            if not read:
                if toLabel == str_broadcast_subscribers:
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
            logger.warning('WARNING: MessagingMenu is not available.  Is libmessaging-menu-dev installed?')
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
                logger.warning('WARNING: messaging menu disabled')

    # update the Ubuntu messaging menu
    def ubuntuMessagingMenuUpdate(self, drawAttention, newItem, toLabel):
        global withMessagingMenu

        # if this isn't ubuntu then don't do anything
        if not self.isUbuntu():
            return

        # has messageing menu been installed
        if not withMessagingMenu:
            logger.warning('WARNING: messaging menu disabled or libmessaging-menu-dev not installed')
            return

        # remember this item to that the messaging menu can find it
        if toLabel == str_broadcast_subscribers:
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

    # returns true if the given sound category is a connection sound
    # rather than a received message sound
    def isConnectionSound(self, category):
        if (category is self.SOUND_CONNECTED or
            category is self.SOUND_DISCONNECTED or
            category is self.SOUND_CONNECTION_GREEN):
            return True
        return False

    # play a sound
    def playSound(self, category, label):
        # filename of the sound to be played
        soundFilename = None

        # whether to play a sound or not
        play = True

        # if the address had a known label in the address book
        if label is not None:
            # Does a sound file exist for this particular contact?
            if (os.path.isfile(shared.appdata + 'sounds/' + label + '.wav') or
                os.path.isfile(shared.appdata + 'sounds/' + label + '.mp3')):
                soundFilename = shared.appdata + 'sounds/' + label

        # Avoid making sounds more frequently than the threshold.
        # This suppresses playing sounds repeatedly when there
        # are many new messages
        if (soundFilename is None and
            not self.isConnectionSound(category)):
            # elapsed time since the last sound was played
            dt = datetime.datetime.now() - self.lastSoundTime
            # suppress sounds which are more frequent than the threshold
            if dt.total_seconds() < self.maxSoundFrequencySec:
                play = False

        if soundFilename is None:
            # the sound is for an address which exists in the address book
            if category is self.SOUND_KNOWN:
                soundFilename = shared.appdata + 'sounds/known'
            # the sound is for an unknown address
            elif category is self.SOUND_UNKNOWN:
                soundFilename = shared.appdata + 'sounds/unknown'
            # initial connection sound
            elif category is self.SOUND_CONNECTED:
                soundFilename = shared.appdata + 'sounds/connected'
            # disconnected sound
            elif category is self.SOUND_DISCONNECTED:
                soundFilename = shared.appdata + 'sounds/disconnected'
            # sound when the connection status becomes green
            elif category is self.SOUND_CONNECTION_GREEN:
                soundFilename = shared.appdata + 'sounds/green'            

        if soundFilename is not None and play is True:
            if not self.isConnectionSound(category):
                # record the last time that a received message sound was played
                self.lastSoundTime = datetime.datetime.now()

            # if not wav then try mp3 format
            if not os.path.isfile(soundFilename + '.wav'):
                soundFilename = soundFilename + '.mp3'
            else:
                soundFilename = soundFilename + '.wav'

            if os.path.isfile(soundFilename):
                if 'linux' in sys.platform:
                    # Note: QSound was a nice idea but it didn't work
                    if '.mp3' in soundFilename:
                        gst_available=False
                        try:
                            subprocess.call(["gst123", soundFilename],
                                            stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE)
                            gst_available=True
                        except:
                            logger.warning("WARNING: gst123 must be installed in order to play mp3 sounds")
                        if not gst_available:
                            try:
                                subprocess.call(["mpg123", soundFilename],
                                                stdin=subprocess.PIPE, 
                                                stdout=subprocess.PIPE)
                                gst_available=True
                            except:
                                logger.warning("WARNING: mpg123 must be installed in order to play mp3 sounds")
                    else:
                        try:
                            subprocess.call(["aplay", soundFilename],
                                            stdin=subprocess.PIPE, 
                                            stdout=subprocess.PIPE)
                        except:
                            logger.warning("WARNING: aplay must be installed in order to play WAV sounds")
                elif sys.platform[0:3] == 'win':
                    # use winsound on Windows
                    import winsound
                    winsound.PlaySound(soundFilename, winsound.SND_FILENAME)

    # initialise the message notifier
    def notifierInit(self):
        global withMessagingMenu
        if withMessagingMenu:
            Notify.init('pybitmessage')

    # shows a notification
    def notifierShow(self, title, subtitle, fromCategory, label):
        global withMessagingMenu

        self.playSound(fromCategory, label)

        if withMessagingMenu:
            n = Notify.Notification.new(
                title, subtitle, 'notification-message-email')
            try:
                n.show()
            except:
                # n.show() has been known to throw this exception:
                # gi._glib.GError: GDBus.Error:org.freedesktop.Notifications.
                # MaxNotificationsExceeded: Exceeded maximum number of
                # notifications
                pass
            return
        else:
            self.tray.showMessage(title, subtitle, 1, 2000)

    # set delete key in inbox
    def tableWidgetInboxKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.on_action_InboxTrash()
        return QtGui.QTableWidget.keyPressEvent(self.getCurrentMessagelist(), event)

    # set delete key in inbox
    def tableWidgetSentKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.on_action_SentTrash()
        return QtGui.QTableWidget.keyPressEvent(self.getCurrentMessagelist(), event)

    # menu button 'manage keys'
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
                shared.openKeysFile()

    # menu button 'delete all treshed messages'
    def click_actionDeleteAllTrashedMessages(self):
        if QtGui.QMessageBox.question(self, _translate("MainWindow", "Delete trash?"), _translate("MainWindow", "Are you sure you want to delete all trashed messages?"), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
            return
        sqlStoredProcedure('deleteandvacuume')
        self.rerenderTabTreeMessages()
        self.rerenderTabTreeSubscriptions()
        self.rerenderTabTreeChans()
        if self.getCurrentFolder(self.ui.treeWidgetYourIdentities) == "trash":
            self.loadMessagelist(self.ui.tableWidgetInbox, self.getCurrentAccount(self.ui.treeWidgetYourIdentities), "trash")
        elif self.getCurrentFolder(self.ui.treeWidgetSubscriptions) == "trash":
            self.loadMessagelist(self.ui.tableWidgetInboxSubscriptions, self.getCurrentAccount(self.ui.treeWidgetSubscriptions), "trash")
        elif self.getCurrentFolder(self.ui.treeWidgetChans) == "trash":
            self.loadMessagelist(self.ui.tableWidgetInboxChans, self.getCurrentAccount(self.ui.treeWidgetChans), "trash")


    # menu botton 'regenerate deterministic addresses'
    def click_actionRegenerateDeterministicAddresses(self):
        self.regenerateAddressesDialogInstance = regenerateAddressesDialog(
            self)
        if self.regenerateAddressesDialogInstance.exec_():
            if self.regenerateAddressesDialogInstance.ui.lineEditPassphrase.text() == "":
                QMessageBox.about(self, _translate("MainWindow", "bad passphrase"), _translate(
                    "MainWindow", "You must type your passphrase. If you don\'t have one then this is not the form for you."))
                return
            streamNumberForAddress = int(
                self.regenerateAddressesDialogInstance.ui.lineEditStreamNumber.text())
            try:
                addressVersionNumber = int(
                    self.regenerateAddressesDialogInstance.ui.lineEditAddressVersionNumber.text())
            except:
                QMessageBox.about(self, _translate("MainWindow", "Bad address version number"), _translate(
                    "MainWindow", "Your address version number must be a number: either 3 or 4."))
                return
            if addressVersionNumber < 3 or addressVersionNumber > 4:
                QMessageBox.about(self, _translate("MainWindow", "Bad address version number"), _translate(
                    "MainWindow", "Your address version number must be either 3 or 4."))
                return
            shared.addressGeneratorQueue.put(('createDeterministicAddresses', addressVersionNumber, streamNumberForAddress, "regenerated deterministic address", self.regenerateAddressesDialogInstance.ui.spinBoxNumberOfAddressesToMake.value(
            ), self.regenerateAddressesDialogInstance.ui.lineEditPassphrase.text().toUtf8(), self.regenerateAddressesDialogInstance.ui.checkBoxEighteenByteRipe.isChecked()))
            self.ui.tabWidget.setCurrentIndex(3)

    # opens 'join chan' dialog
    def click_actionJoinChan(self):
        self.newChanDialogInstance = newChanDialog(self)
        if self.newChanDialogInstance.exec_():
            if self.newChanDialogInstance.ui.radioButtonCreateChan.isChecked():
                if self.newChanDialogInstance.ui.lineEditChanNameCreate.text() == "":
                    QMessageBox.about(self, _translate("MainWindow", "Chan name needed"), _translate(
                        "MainWindow", "You didn't enter a chan name."))
                    return
                shared.apiAddressGeneratorReturnQueue.queue.clear()
                shared.addressGeneratorQueue.put(('createChan', 4, 1, self.str_chan + ' ' + str(self.newChanDialogInstance.ui.lineEditChanNameCreate.text().toUtf8()), self.newChanDialogInstance.ui.lineEditChanNameCreate.text().toUtf8()))
                addressGeneratorReturnValue = shared.apiAddressGeneratorReturnQueue.get()
                logger.debug('addressGeneratorReturnValue ' + str(addressGeneratorReturnValue))
                if len(addressGeneratorReturnValue) == 0:
                    QMessageBox.about(self, _translate("MainWindow", "Address already present"), _translate(
                        "MainWindow", "Could not add chan because it appears to already be one of your identities."))
                    return
                createdAddress = addressGeneratorReturnValue[0]
                QMessageBox.about(self, _translate("MainWindow", "Success"), _translate(
                    "MainWindow", "Successfully created chan. To let others join your chan, give them the chan name and this Bitmessage address: %1. This address also appears in 'Your Identities'.").arg(createdAddress))
                self.ui.tabWidget.setCurrentIndex(3)
            elif self.newChanDialogInstance.ui.radioButtonJoinChan.isChecked():
                if self.newChanDialogInstance.ui.lineEditChanNameJoin.text() == "":
                    QMessageBox.about(self, _translate("MainWindow", "Chan name needed"), _translate(
                        "MainWindow", "You didn't enter a chan name."))
                    return
                if decodeAddress(self.newChanDialogInstance.ui.lineEditChanBitmessageAddress.text())[0] == 'versiontoohigh':
                    QMessageBox.about(self, _translate("MainWindow", "Address too new"), _translate(
                        "MainWindow", "Although that Bitmessage address might be valid, its version number is too new for us to handle. Perhaps you need to upgrade Bitmessage."))
                    return
                if decodeAddress(self.newChanDialogInstance.ui.lineEditChanBitmessageAddress.text())[0] != 'success':
                    QMessageBox.about(self, _translate("MainWindow", "Address invalid"), _translate(
                        "MainWindow", "That Bitmessage address is not valid."))
                    return
                shared.apiAddressGeneratorReturnQueue.queue.clear()
                shared.addressGeneratorQueue.put(('joinChan', addBMIfNotPresent(self.newChanDialogInstance.ui.lineEditChanBitmessageAddress.text()), self.str_chan + ' ' + str(self.newChanDialogInstance.ui.lineEditChanNameJoin.text().toUtf8()), self.newChanDialogInstance.ui.lineEditChanNameJoin.text().toUtf8()))
                addressGeneratorReturnValue = shared.apiAddressGeneratorReturnQueue.get()
                logger.debug('addressGeneratorReturnValue ' + str(addressGeneratorReturnValue))
                if addressGeneratorReturnValue == 'chan name does not match address':
                    QMessageBox.about(self, _translate("MainWindow", "Address does not match chan name"), _translate(
                        "MainWindow", "Although the Bitmessage address you entered was valid, it doesn\'t match the chan name."))
                    return
                if len(addressGeneratorReturnValue) == 0:
                    QMessageBox.about(self, _translate("MainWindow", "Address already present"), _translate(
                        "MainWindow", "Could not add chan because it appears to already be one of your identities."))
                    return
                createdAddress = addressGeneratorReturnValue[0]
                QMessageBox.about(self, _translate("MainWindow", "Success"), _translate(
                    "MainWindow", "Successfully joined chan. "))
                self.ui.tabWidget.setCurrentIndex(3)
            self.rerenderAddressBook()

    def showConnectDialog(self):
        self.connectDialogInstance = connectDialog(self)
        if self.connectDialogInstance.exec_():
            if self.connectDialogInstance.ui.radioButtonConnectNow.isChecked():
                shared.config.remove_option('bitmessagesettings', 'dontconnect')
                shared.writeKeysFile()
            else:
                self.click_actionSettings()

    def showMigrationWizard(self, level):
        self.migrationWizardInstance = Ui_MigrationWizard(["a"])
        if self.migrationWizardInstance.exec_():
            pass
        else:
            pass
        
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.ui.retranslateUi(self)
            self.init_inbox_popup_menu(False)
            self.init_chan_popup_menu(False)
            self.init_addressbook_popup_menu(False)
            self.init_subscriptions_popup_menu(False)
            self.init_sent_popup_menu(False)
            self.init_blacklist_popup_menu(False)
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                if shared.config.getboolean('bitmessagesettings', 'minimizetotray') and not 'darwin' in sys.platform:
                    QTimer.singleShot(0, self.appIndicatorHide)
            elif event.oldState() & QtCore.Qt.WindowMinimized:
                # The window state has just been changed to
                # Normal/Maximised/FullScreen
                pass
        # QtGui.QWidget.changeEvent(self, event)


    def __icon_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.actionShow.setChecked(not self.actionShow.isChecked())
            self.appIndicatorShowOrHideWindow()

    def updateNumberOfMessagesProcessed(self):
        self.ui.labelSyncStatus.setText(_translate("MainWindow", "Objects to be synced: %1").arg(str(sum(shared.numberOfObjectsThatWeHaveYetToGetPerPeer.itervalues()))))
        self.ui.labelMessageCount.setText(_translate(
            "MainWindow", "Processed %1 person-to-person messages.").arg(str(shared.numberOfMessagesProcessed)))

    def updateNumberOfBroadcastsProcessed(self):
        self.ui.labelSyncStatus.setText(_translate("MainWindow", "Objects to be synced: %1").arg(str(sum(shared.numberOfObjectsThatWeHaveYetToGetPerPeer.itervalues()))))
        self.ui.labelBroadcastCount.setText(_translate(
            "MainWindow", "Processed %1 broadcast messages.").arg(str(shared.numberOfBroadcastsProcessed)))

    def updateNumberOfPubkeysProcessed(self):
        self.ui.labelSyncStatus.setText(_translate("MainWindow", "Objects to be synced: %1").arg(str(sum(shared.numberOfObjectsThatWeHaveYetToGetPerPeer.itervalues()))))
        self.ui.labelPubkeyCount.setText(_translate(
            "MainWindow", "Processed %1 public keys.").arg(str(shared.numberOfPubkeysProcessed)))

    def formatBytes(self, num):
        for x in ['bytes','KB','MB','GB']:
            if num < 1000.0:
                return "%3.0f %s" % (num, x)
            num /= 1000.0
        return "%3.0f %s" % (num, 'TB')
    
    def formatByteRate(self, num):
        num /= 1000
        return "%4.0f KB" % num

    def updateNumberOfBytes(self):
        """
        This function is run every two seconds, so we divide the rate of bytes
        sent and received by 2.
        """
        self.ui.labelBytesRecvCount.setText(_translate(
            "MainWindow", "Down: %1/s  Total: %2").arg(self.formatByteRate(shared.numberOfBytesReceived/2), self.formatBytes(self.totalNumberOfBytesReceived)))
        self.ui.labelBytesSentCount.setText(_translate(
            "MainWindow", "Up: %1/s  Total: %2").arg(self.formatByteRate(shared.numberOfBytesSent/2), self.formatBytes(self.totalNumberOfBytesSent)))
        self.totalNumberOfBytesReceived += shared.numberOfBytesReceived
        self.totalNumberOfBytesSent += shared.numberOfBytesSent
        shared.numberOfBytesReceived = 0
        shared.numberOfBytesSent = 0

    def updateNetworkStatusTab(self):
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

    # timer driven
    def runEveryTwoSeconds(self):
        self.ui.labelLookupsPerSecond.setText(_translate(
            "MainWindow", "Inventory lookups per second: %1").arg(str(shared.numberOfInventoryLookupsPerformed/2)))
        shared.numberOfInventoryLookupsPerformed = 0
        self.updateNumberOfBytes()

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
                            "MainWindow", "Connection lost").toUtf8(),'utf-8'),
                                  self.SOUND_DISCONNECTED, None)
            self.connected = False

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Not Connected"))
                self.setTrayIconFile("can-icon-24px-red.png")
        if color == 'yellow':
            if self.statusBar().currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusBar().showMessage('')
            self.ui.pushButtonStatusIcon.setIcon(QIcon(
                ":/newPrefix/images/yellowicon.png"))
            shared.statusIconColor = 'yellow'
            # if a new connection has been established then show a notification
            if not self.connected:
                self.notifierShow('Bitmessage', unicode(_translate(
                            "MainWindow", "Connected").toUtf8(),'utf-8'),
                                  self.SOUND_CONNECTED, None)
            self.connected = True

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Connected"))
                self.setTrayIconFile("can-icon-24px-yellow.png")
        if color == 'green':
            if self.statusBar().currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusBar().showMessage('')
            self.ui.pushButtonStatusIcon.setIcon(
                QIcon(":/newPrefix/images/greenicon.png"))
            shared.statusIconColor = 'green'
            if not self.connected:
                self.notifierShow('Bitmessage', unicode(_translate(
                            "MainWindow", "Connected").toUtf8(),'utf-8'),
                                  self.SOUND_CONNECTION_GREEN, None)
            self.connected = True

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Connected"))
                self.setTrayIconFile("can-icon-24px-green.png")

    def initTrayIcon(self, iconFileName, app):
        self.currentTrayIconFileName = iconFileName
        self.tray = QSystemTrayIcon(
            self.calcTrayIcon(iconFileName, self.findInboxUnreadCount()), app)

    def setTrayIconFile(self, iconFileName):
        self.currentTrayIconFileName = iconFileName
        self.drawTrayIcon(iconFileName, self.findInboxUnreadCount())

    def calcTrayIcon(self, iconFileName, inboxUnreadCount):
        pixmap = QtGui.QPixmap(":/newPrefix/images/"+iconFileName)
        if inboxUnreadCount > 0:
            # choose font and calculate font parameters
            fontName = "Lucida"
            fontSize = 10
            font = QtGui.QFont(fontName, fontSize, QtGui.QFont.Bold)
            fontMetrics = QtGui.QFontMetrics(font)
            # text
            txt = str(inboxUnreadCount)
            rect = fontMetrics.boundingRect(txt)
            # margins that we add in the top-right corner
            marginX = 2
            marginY = 0 # it looks like -2 is also ok due to the error of metric
            # if it renders too wide we need to change it to a plus symbol
            if rect.width() > 20:
                txt = "+"
                fontSize = 15
                font = QtGui.QFont(fontName, fontSize, QtGui.QFont.Bold)
                fontMetrics = QtGui.QFontMetrics(font)
                rect = fontMetrics.boundingRect(txt)
            # draw text
            painter = QPainter()
            painter.begin(pixmap)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), Qt.SolidPattern))
            painter.setFont(font)
            painter.drawText(24-rect.right()-marginX, -rect.top()+marginY, txt)
            painter.end()
        return QtGui.QIcon(pixmap)

    def drawTrayIcon(self, iconFileName, inboxUnreadCount):
        self.tray.setIcon(self.calcTrayIcon(iconFileName, inboxUnreadCount))

    def changedInboxUnread(self, row = None):
        self.drawTrayIcon(self.currentTrayIconFileName, self.findInboxUnreadCount())
        self.rerenderTabTreeMessages()
        self.rerenderTabTreeSubscriptions()
        self.rerenderTabTreeChans()

    def findInboxUnreadCount(self, count = None):
        if count is None:
            queryreturn = sqlQuery('''SELECT count(*) from inbox WHERE folder='inbox' and read=0''')
            cnt = 0
            for row in queryreturn:
                cnt, = row
            self.unreadCount = int(cnt)
        else:
            self.unreadCount = count
        return self.unreadCount

    def updateSentItemStatusByToAddress(self, toAddress, textToDisplay):
        for sent in [self.ui.tableWidgetInbox, self.ui.tableWidgetInboxSubscriptions, self.ui.tableWidgetInboxChans]:
            treeWidget = self.widgetConvert(sent)
            if self.getCurrentFolder(treeWidget) != "sent":
                continue
            if treeWidget in [self.ui.treeWidgetSubscriptions, self.ui.treeWidgetChans] and self.getCurrentAccount(treeWidget) != toAddress:
                continue

            for i in range(sent.rowCount()):
                rowAddress = str(sent.item(
                    i, 0).data(Qt.UserRole).toPyObject())
                if toAddress == rowAddress:
                    sent.item(i, 3).setToolTip(textToDisplay)
                    try:
                        newlinePosition = textToDisplay.indexOf('\n')
                    except: # If someone misses adding a "_translate" to a string before passing it to this function, this function won't receive a qstring which will cause an exception.
                        newlinePosition = 0
                    if newlinePosition > 1:
                        sent.item(i, 3).setText(
                            textToDisplay[:newlinePosition])
                    else:
                        sent.item(i, 3).setText(textToDisplay)

    def updateSentItemStatusByAckdata(self, ackdata, textToDisplay):
        for sent in [self.ui.tableWidgetInbox, self.ui.tableWidgetInboxSubscriptions, self.ui.tableWidgetInboxChans]:
            treeWidget = self.widgetConvert(sent)
            if self.getCurrentFolder(treeWidget) != "sent":
                continue
            for i in range(sent.rowCount()):
                toAddress = str(sent.item(
                    i, 0).data(Qt.UserRole).toPyObject())
                tableAckdata = sent.item(
                    i, 3).data(Qt.UserRole).toPyObject()
                status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                    toAddress)
                if ackdata == tableAckdata:
                    sent.item(i, 3).setToolTip(textToDisplay)
                    try:
                        newlinePosition = textToDisplay.indexOf('\n')
                    except: # If someone misses adding a "_translate" to a string before passing it to this function, this function won't receive a qstring which will cause an exception.
                        newlinePosition = 0
                    if newlinePosition > 1:
                        sent.item(i, 3).setText(
                            textToDisplay[:newlinePosition])
                    else:
                        sent.item(i, 3).setText(textToDisplay)

    def removeInboxRowByMsgid(self, msgid):  # msgid and inventoryHash are the same thing
        for inbox in ([
            self.ui.tableWidgetInbox,
            self.ui.tableWidgetInboxSubscriptions,
            self.ui.tableWidgetInboxChans]):
            for i in range(inbox.rowCount()):
                if msgid == str(inbox.item(i, 3).data(Qt.UserRole).toPyObject()):
                    self.statusBar().showMessage(_translate(
                        "MainWindow", "Message trashed"))
                    treeWidget = self.widgetConvert(inbox)
                    self.propagateUnreadCount(str(inbox.item(i, 1 if inbox == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), self.getCurrentFolder(treeWidget), treeWidget, 0)
                    inbox.removeRow(i)
                    break
        
    def newVersionAvailable(self, version):
#        if (not (self.windowState() & QtCore.Qt.WindowActive)) or (self.windowState() & QtCore.Qt.WindowMinimized):
#            return
        # only notify once until next restart
        try:
            if self.notifiedNewVersion:
                return
        except AttributeError:
            pass

        self.notifiedNewVersion = ".".join(str(n) for n in version)
        message = "New "
        if version[1] % 2:
            message += "UNSTABLE"
        else:
            message += "stable"
        message += " version of PyBitmessage is available: " + self.notifiedNewVersion + ". Download it from https://github.com/"
        if version[0] == 0 and version[1] == 5:
            message += "mailchuck"
        else:
            message += "Bitmessage"
        message += "/PyBitmessage/releases/latest"
        self.displayAlert("New release of PyBitmessage available", message, False)

    def displayAlert(self, title, text, exitAfterUserClicksOk):
        self.statusBar().showMessage(text)
        QtGui.QMessageBox.critical(self, title, text, QMessageBox.Ok)
        if exitAfterUserClicksOk:
            os._exit(0)

    def rerenderInboxFromLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            addressToLookup = str(self.ui.tableWidgetInbox.item(
                i, 1).data(Qt.UserRole).toPyObject())
            fromLabel = ''
            queryreturn = sqlQuery(
                '''select label from addressbook where address=?''', addressToLookup)

            if queryreturn != []:
                for row in queryreturn:
                    fromLabel, = row
            
            if fromLabel == '':
                # It might be a broadcast message. We should check for that
                # label.
                queryreturn = sqlQuery(
                    '''select label from subscriptions where address=?''', addressToLookup)

                if queryreturn != []:
                    for row in queryreturn:
                        fromLabel, = row
            if fromLabel == '':
                # Message might be from an address we own like a chan address. Let's look for that label.
                if shared.config.has_section(addressToLookup):
                    fromLabel = shared.config.get(addressToLookup, 'label')
            if fromLabel == '':
                fromLabel = addressToLookup
            self.ui.tableWidgetInbox.item(
                i, 1).setText(unicode(fromLabel, 'utf-8'))
            self.ui.tableWidgetInbox.item(
                i, 1).setIcon(avatarize(addressToLookup))
            # Set the color according to whether it is the address of a mailing
            # list or not.
            if shared.safeConfigGetBoolean(addressToLookup, 'chan'):
                self.ui.tableWidgetInbox.item(i, 1).setTextColor(QtGui.QColor(216, 119, 0)) # orange
            else:
                self.ui.tableWidgetInbox.item(
                    i, 1).setTextColor(QApplication.palette().text().color())
                    

    def rerenderInboxToLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            toAddress = str(self.ui.tableWidgetInbox.item(
                i, 0).data(Qt.UserRole).toPyObject())
            # Message might be to an address we own like a chan address. Let's look for that label.
            if shared.config.has_section(toAddress):
                toLabel = shared.config.get(toAddress, 'label')
            else:
                toLabel = toAddress
            self.ui.tableWidgetInbox.item(
                i, 0).setText(unicode(toLabel, 'utf-8'))
            self.ui.tableWidgetInbox.item(
                i, 0).setIcon(avatarize(toAddress))
            # Set the color according to whether it is the address of a mailing
            # list, a chan or neither.
            if shared.safeConfigGetBoolean(toAddress, 'chan'):
                self.ui.tableWidgetInbox.item(i, 0).setTextColor(QtGui.QColor(216, 119, 0)) # orange
            elif shared.safeConfigGetBoolean(toAddress, 'mailinglist'):
                self.ui.tableWidgetInbox.item(i, 0).setTextColor(QtGui.QColor(137, 04, 177)) # magenta
            else:
                self.ui.tableWidgetInbox.item(
                    i, 0).setTextColor(QApplication.palette().text().color())

    def rerenderSentFromLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            fromAddress = str(self.ui.tableWidgetInbox.item(
                i, 1).data(Qt.UserRole).toPyObject())
            # Message might be from an address we own like a chan address. Let's look for that label.
            if shared.config.has_section(fromAddress):
                fromLabel = shared.config.get(fromAddress, 'label')
            else:
                fromLabel = fromAddress
            self.ui.tableWidgetInbox.item(
                i, 1).setText(unicode(fromLabel, 'utf-8'))
            self.ui.tableWidgetInbox.item(
                i, 1).setIcon(avatarize(fromAddress))

    def rerenderSentToLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            addressToLookup = str(self.ui.tableWidgetInbox.item(
                i, 0).data(Qt.UserRole).toPyObject())
            toLabel = ''
            queryreturn = sqlQuery(
                '''select label from addressbook where address=?''', addressToLookup)
            if queryreturn != []:
                for row in queryreturn:
                    toLabel, = row
            
            if toLabel == '':
                # Message might be to an address we own like a chan address. Let's look for that label.
                if shared.config.has_section(addressToLookup):
                    toLabel = shared.config.get(addressToLookup, 'label')
            if toLabel == '':
                toLabel = addressToLookup
            self.ui.tableWidgetInbox.item(
                i, 0).setText(unicode(toLabel, 'utf-8'))

    def rerenderAddressBook(self):
        def addRow (address, label, type):
            self.ui.tableWidgetAddressBook.insertRow(0)
            newItem = Ui_AddressBookWidgetItemLabel(address, unicode(label, 'utf-8'), type)
            newItem.setData(Qt.UserRole, type)
            self.ui.tableWidgetAddressBook.setItem(0, 0, newItem)
            newItem = Ui_AddressBookWidgetItemAddress(address, unicode(label, 'utf-8'), type)
            self.ui.tableWidgetAddressBook.setItem(0, 1, newItem)
        
        self.ui.tableWidgetAddressBook.setSortingEnabled(False)
        self.ui.tableWidgetAddressBook.setRowCount(0)

        # subscriptions
        queryreturn = sqlQuery('SELECT label, address FROM subscriptions WHERE enabled = 1')
        for row in queryreturn:
            label, address = row
            addRow(address, label, AccountMixin.SUBSCRIPTION)

        # chans
        addresses = getSortedAccounts()
        for address in addresses:
            account = accountClass(address)
            if (account.type == AccountMixin.CHAN and shared.safeConfigGetBoolean(address, 'enabled')):
                addRow(address, account.getLabel(), AccountMixin.CHAN)
        
        # normal accounts
        queryreturn = sqlQuery('SELECT * FROM addressbook')
        for row in queryreturn:
            label, address = row
            addRow(address, label, AccountMixin.NORMAL)

        # sort
        self.ui.tableWidgetAddressBook.sortItems(0, QtCore.Qt.AscendingOrder)
        self.ui.tableWidgetAddressBook.setSortingEnabled(True)

    def rerenderSubscriptions(self):
        self.rerenderTabTreeSubscriptions()

    def rerenderBlackWhiteList(self):
        self.ui.tableWidgetBlacklist.setRowCount(0)
        listType = shared.config.get('bitmessagesettings', 'blackwhitelist')
        if listType == 'black':
            queryreturn = sqlQuery('''SELECT label, address, enabled FROM blacklist''')
        else:
            queryreturn = sqlQuery('''SELECT label, address, enabled FROM whitelist''')
        for row in queryreturn:
            label, address, enabled = row
            self.ui.tableWidgetBlacklist.insertRow(0)
            newItem = QtGui.QTableWidgetItem(unicode(label, 'utf-8'))
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            newItem.setIcon(avatarize(address))
            self.ui.tableWidgetBlacklist.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(address)
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            self.ui.tableWidgetBlacklist.setItem(0, 1, newItem)

    def click_pushButtonTTL(self):
        QtGui.QMessageBox.information(self, 'Time To Live', _translate(
            "MainWindow", """The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate."""), QMessageBox.Ok)

    def click_pushButtonSend(self):
        self.statusBar().showMessage('')

        if self.ui.tabWidgetSend.currentIndex() == 0:
            # message to specific people
            sendMessageToPeople = True
            fromAddress = str(self.ui.comboBoxSendFrom.itemData(
                self.ui.comboBoxSendFrom.currentIndex(), 
                Qt.UserRole).toString())
            toAddresses = str(self.ui.lineEditTo.text())
            subject = str(self.ui.lineEditSubject.text().toUtf8())
            message = str(
                self.ui.textEditMessage.document().toPlainText().toUtf8())
        else:
            # broadcast message
            sendMessageToPeople = False
            fromAddress = str(self.ui.comboBoxSendFromBroadcast.itemData(
                self.ui.comboBoxSendFromBroadcast.currentIndex(), 
                Qt.UserRole).toString())
            subject = str(self.ui.lineEditSubjectBroadcast.text().toUtf8())
            message = str(
                self.ui.textEditMessageBroadcast.document().toPlainText().toUtf8())
        """
        The whole network message must fit in 2^18 bytes. Let's assume 500 
        bytes of overhead. If someone wants to get that too an exact 
        number you are welcome to but I think that it would be a better
        use of time to support message continuation so that users can
        send messages of any length.
        """
        if len(message) > (2 ** 18 - 500):  
            QMessageBox.about(self, _translate("MainWindow", "Message too long"), _translate(
                "MainWindow", "The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.").arg(len(message) - (2 ** 18 - 500)))
            return
            
        acct = accountClass(fromAddress)

        if sendMessageToPeople: # To send a message to specific people (rather than broadcast)
            toAddressesList = [s.strip()
                               for s in toAddresses.replace(',', ';').split(';')]
            toAddressesList = list(set(
                toAddressesList))  # remove duplicate addresses. If the user has one address with a BM- and the same address without the BM-, this will not catch it. They'll send the message to the person twice.
            for toAddress in toAddressesList:
                if toAddress != '':
                    if toAddress.find("@") >= 0 and isinstance(acct, GatewayAccount):
                        acct.createMessage(toAddress, fromAddress, subject, message)
                        subject = acct.subject
                        toAddress = acct.toAddress
                        logger.debug("Subject: %s" % (subject))
                        logger.debug("address: %s" % (toAddress))
                    status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                        toAddress)
                    if status != 'success':
                        logger.error('Error: Could not decode ' + toAddress + ':' + status)

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
                        elif status == 'varintmalformed':
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: Some data encoded in the address %1 is malformed. There might be something wrong with the software of your acquaintance.").arg(toAddress))
                        else:
                            self.statusBar().showMessage(_translate(
                                "MainWindow", "Error: Something is wrong with the address %1.").arg(toAddress))
                    elif fromAddress == '':
                        self.statusBar().showMessage(_translate(
                            "MainWindow", "Error: You must specify a From address. If you don\'t have one, go to the \'Your Identities\' tab."))
                    else:
                        toAddress = addBMIfNotPresent(toAddress)

                        if addressVersionNumber > 4 or addressVersionNumber <= 1:
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
                        t = ()
                        sqlExecute(
                            '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                            '',
                            toAddress,
                            ripe,
                            fromAddress,
                            subject,
                            message,
                            ackdata,
                            int(time.time()), # sentTime (this will never change)
                            int(time.time()), # lastActionTime
                            0, # sleepTill time. This will get set when the POW gets done.
                            'msgqueued',
                            0, # retryNumber
                            'sent', # folder
                            2, # encodingtype
                            shared.config.getint('bitmessagesettings', 'ttl')
                            )

                        toLabel = ''
                        queryreturn = sqlQuery('''select label from addressbook where address=?''',
                                               toAddress)
                        if queryreturn != []:
                            for row in queryreturn:
                                toLabel, = row

                        self.displayNewSentMessage(
                            toAddress, toLabel, fromAddress, subject, message, ackdata)
                        shared.workerQueue.put(('sendmessage', toAddress))

                        self.ui.comboBoxSendFrom.setCurrentIndex(0)
                        self.ui.lineEditTo.setText('')
                        self.ui.lineEditSubject.setText('')
                        self.ui.textEditMessage.setText('')
                        if self.replyFromTab is not None:
                            self.ui.tabWidget.setCurrentIndex(self.replyFromTab)
                            self.replyFromTab = None
                        self.statusBar().showMessage(_translate(
                            "MainWindow", "Message queued."))
                        #self.ui.tableWidgetInbox.setCurrentCell(0, 0)
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
                toAddress = str_broadcast_subscribers
                ripe = ''
                t = ('', # msgid. We don't know what this will be until the POW is done. 
                     toAddress, 
                     ripe, 
                     fromAddress, 
                     subject, 
                     message, 
                     ackdata, 
                     int(time.time()), # sentTime (this will never change)
                     int(time.time()), # lastActionTime
                     0, # sleepTill time. This will get set when the POW gets done.
                     'broadcastqueued', 
                     0, # retryNumber
                     'sent', # folder
                     2, # encoding type
                     shared.config.getint('bitmessagesettings', 'ttl')
                     )
                sqlExecute(
                    '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)

                toLabel = str_broadcast_subscribers
                
                self.displayNewSentMessage(
                    toAddress, toLabel, fromAddress, subject, message, ackdata)

                shared.workerQueue.put(('sendbroadcast', ''))

                self.ui.comboBoxSendFromBroadcast.setCurrentIndex(0)
                self.ui.lineEditSubjectBroadcast.setText('')
                self.ui.textEditMessageBroadcast.setText('')
                self.ui.tabWidget.setCurrentIndex(1)
                self.ui.tableWidgetInboxSubscriptions.setCurrentCell(0, 0)
                self.statusBar().showMessage(_translate(
                    "MainWindow", "Broadcast queued."))

    def click_pushButtonLoadFromAddressBook(self):
        self.ui.tabWidget.setCurrentIndex(5)
        for i in range(4):
            time.sleep(0.1)
            self.statusBar().showMessage('')
            time.sleep(0.1)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Right click one or more entries in your address book and select \'Send message to this address\'."))

    def click_pushButtonFetchNamecoinID(self):
        nc = namecoinConnection()
        err, addr = nc.query(str(self.ui.lineEditTo.text()))
        if err is not None:
            self.statusBar().showMessage(_translate(
                "MainWindow", "Error: " + err))
        else:
            self.ui.lineEditTo.setText(addr)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Fetched address from namecoin identity."))

    def setBroadcastEnablementDependingOnWhetherThisIsAMailingListAddress(self, address):
        # If this is a chan then don't let people broadcast because no one
        # should subscribe to chan addresses.
        if shared.safeConfigGetBoolean(str(address), 'mailinglist'):
            self.ui.tabWidgetSend.setCurrentIndex(1)
        else:
            self.ui.tabWidgetSend.setCurrentIndex(0)

    def rerenderComboBoxSendFrom(self):
        self.ui.comboBoxSendFrom.clear()
        for addressInKeysFile in getSortedAccounts():
            isEnabled = shared.config.getboolean(
                addressInKeysFile, 'enabled')  # I realize that this is poor programming practice but I don't care. It's easier for others to read.
            isMaillinglist = shared.safeConfigGetBoolean(addressInKeysFile, 'mailinglist')
            if isEnabled and not isMaillinglist:
                self.ui.comboBoxSendFrom.addItem(avatarize(addressInKeysFile), unicode(shared.config.get(
                     addressInKeysFile, 'label'), 'utf-8'), addressInKeysFile)
#        self.ui.comboBoxSendFrom.model().sort(1, Qt.AscendingOrder)
        for i in range(self.ui.comboBoxSendFrom.count()):
            address = str(self.ui.comboBoxSendFrom.itemData(i, Qt.UserRole).toString())
            self.ui.comboBoxSendFrom.setItemData(i, AccountColor(address).accountColor(), Qt.ForegroundRole)
        self.ui.comboBoxSendFrom.insertItem(0, '', '')
        if(self.ui.comboBoxSendFrom.count() == 2):
            self.ui.comboBoxSendFrom.setCurrentIndex(1)
        else:
            self.ui.comboBoxSendFrom.setCurrentIndex(0)

    def rerenderComboBoxSendFromBroadcast(self):
        self.ui.comboBoxSendFromBroadcast.clear()
        for addressInKeysFile in getSortedAccounts():
            isEnabled = shared.config.getboolean(
                addressInKeysFile, 'enabled')  # I realize that this is poor programming practice but I don't care. It's easier for others to read.
            isChan = shared.safeConfigGetBoolean(addressInKeysFile, 'chan')
            if isEnabled and not isChan:
                self.ui.comboBoxSendFromBroadcast.addItem(avatarize(addressInKeysFile), unicode(shared.config.get(
                    addressInKeysFile, 'label'), 'utf-8'), addressInKeysFile)
        for i in range(self.ui.comboBoxSendFromBroadcast.count()):
            address = str(self.ui.comboBoxSendFromBroadcast.itemData(i, Qt.UserRole).toString())
            self.ui.comboBoxSendFromBroadcast.setItemData(i, AccountColor(address).accountColor(), Qt.ForegroundRole)
        self.ui.comboBoxSendFromBroadcast.insertItem(0, '', '')
        if(self.ui.comboBoxSendFromBroadcast.count() == 2):
            self.ui.comboBoxSendFromBroadcast.setCurrentIndex(1)
        else:
            self.ui.comboBoxSendFromBroadcast.setCurrentIndex(0)

    # This function is called by the processmsg function when that function
    # receives a message to an address that is acting as a
    # pseudo-mailing-list. The message will be broadcast out. This function
    # puts the message on the 'Sent' tab.
    def displayNewSentMessage(self, toAddress, toLabel, fromAddress, subject, message, ackdata):
        subject = shared.fixPotentiallyInvalidUTF8Data(subject)
        message = shared.fixPotentiallyInvalidUTF8Data(message)
        acct = accountClass(fromAddress)
        acct.parseMessage(toAddress, fromAddress, subject, message)
        for sent in [self.ui.tableWidgetInbox, self.ui.tableWidgetInboxSubscriptions, self.ui.tableWidgetInboxChans]:
            treeWidget = self.widgetConvert(sent)
            if self.getCurrentFolder(treeWidget) != "sent":
                continue
            if treeWidget == self.ui.treeWidgetYourIdentities and self.getCurrentAccount(treeWidget) != fromAddress:
                continue
            elif treeWidget in [self.ui.treeWidgetSubscriptions, self.ui.treeWidgetChans] and self.getCurrentAccount(treeWidget) != toAddress:
                continue
            
            self.addMessageListItemSent(sent, toAddress, fromAddress, subject, "msgqueued", ackdata, time.time())
            self.getAccountTextedit(acct).setPlainText(unicode(message, 'utf-8)'))

    def displayNewInboxMessage(self, inventoryHash, toAddress, fromAddress, subject, message):
        if toAddress == str_broadcast_subscribers:
            acct = accountClass(fromAddress)
        else:
            acct = accountClass(toAddress)
        inbox = self.getAccountMessagelist(acct)
        ret = None
        for treeWidget in [self.ui.treeWidgetYourIdentities, self.ui.treeWidgetSubscriptions, self.ui.treeWidgetChans]:
            tableWidget = self.widgetConvert(treeWidget)
            if tableWidget == inbox and self.getCurrentAccount(treeWidget) == acct.address and self.getCurrentFolder(treeWidget) == "inbox":
                ret = self.addMessageListItemInbox(inbox, "inbox", inventoryHash, toAddress, fromAddress, subject, time.time(), 0)
            elif treeWidget == self.ui.treeWidgetYourIdentities and self.getCurrentAccount(treeWidget) is None:
                ret = self.addMessageListItemInbox(tableWidget, "inbox", inventoryHash, toAddress, fromAddress, subject, time.time(), 0)
        if ret is None:
            subject = shared.fixPotentiallyInvalidUTF8Data(subject)
            acct.parseMessage(toAddress, fromAddress, subject, "")
        else:
            acct = ret
        self.propagateUnreadCount(acct.address)
        if shared.config.getboolean('bitmessagesettings', 'showtraynotifications'):
            self.notifierShow(unicode(_translate("MainWindow",'New Message').toUtf8(),'utf-8'), unicode(_translate("MainWindow",'From ').toUtf8(),'utf-8') + unicode(acct.fromLabel, 'utf-8'), self.SOUND_UNKNOWN, None)
        if self.getCurrentAccount() is not None and ((self.getCurrentFolder(treeWidget) != "inbox" and self.getCurrentFolder(treeWidget) is not None) or self.getCurrentAccount(treeWidget) != acct.address):
            # Ubuntu should notify of new message irespective of whether it's in current message list or not
            self.ubuntuMessagingMenuUpdate(True, None, acct.toLabel)
            return

    def click_pushButtonAddAddressBook(self):
        self.AddAddressDialogInstance = AddAddressDialog(self)
        if self.AddAddressDialogInstance.exec_():
            if self.AddAddressDialogInstance.ui.labelAddressCheck.text() == _translate("MainWindow", "Address is valid."):
                # First we must check to see if the address is already in the
                # address book. The user cannot add it again or else it will
                # cause problems when updating and deleting the entry.
                address = addBMIfNotPresent(str(
                    self.AddAddressDialogInstance.ui.lineEditAddress.text()))
                label = self.AddAddressDialogInstance.ui.newAddressLabel.text().toUtf8()
                self.addEntryToAddressBook(address,label)
            else:
                self.statusBar().showMessage(_translate(
                    "MainWindow", "The address you entered was invalid. Ignoring it."))

    def addEntryToAddressBook(self,address,label):
        queryreturn = sqlQuery('''select * from addressbook where address=?''', address)
        if queryreturn == []:
            sqlExecute('''INSERT INTO addressbook VALUES (?,?)''', str(label), address)
            self.rerenderAddressBook()
            self.rerenderInboxFromLabels()
            self.rerenderSentToLabels()
        else:
            self.statusBar().showMessage(_translate(
                        "MainWindow", "Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want."))

    def addSubscription(self, address, label):
        address = addBMIfNotPresent(address)
        #This should be handled outside of this function, for error displaying and such, but it must also be checked here.
        if shared.isAddressInMySubscriptionsList(address):
            return
        #Add to database (perhaps this should be separated from the MyForm class)
        sqlExecute('''INSERT INTO subscriptions VALUES (?,?,?)''',str(label),address,True)
        self.rerenderInboxFromLabels()
        shared.reloadBroadcastSendersForWhichImWatching()
        self.rerenderAddressBook()
        self.rerenderTabTreeSubscriptions()

    def click_pushButtonAddSubscription(self):
        self.NewSubscriptionDialogInstance = NewSubscriptionDialog(self)
        if self.NewSubscriptionDialogInstance.exec_():
            if self.NewSubscriptionDialogInstance.ui.labelAddressCheck.text() != _translate("MainWindow", "Address is valid."):
                self.statusBar().showMessage(_translate("MainWindow", "The address you entered was invalid. Ignoring it."))
                return
            address = addBMIfNotPresent(str(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text()))
            # We must check to see if the address is already in the subscriptions list. The user cannot add it again or else it will cause problems when updating and deleting the entry.
            if shared.isAddressInMySubscriptionsList(address):
                self.statusBar().showMessage(_translate("MainWindow", "Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want."))
                return
            label = self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8()
            self.addSubscription(address, label)
            # Now, if the user wants to display old broadcasts, let's get them out of the inventory and put them 
            # in the objectProcessorQueue to be processed
            if self.NewSubscriptionDialogInstance.ui.checkBoxDisplayMessagesAlreadyInInventory.isChecked():
                status, addressVersion, streamNumber, ripe = decodeAddress(address)
                shared.flushInventory()
                doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                    addressVersion) + encodeVarint(streamNumber) + ripe).digest()).digest()
                tag = doubleHashOfAddressData[32:]
                queryreturn = sqlQuery(
                    '''select payload from inventory where objecttype=3 and tag=?''', tag)
                for row in queryreturn:
                    payload, = row
                    objectType = 3
                    with shared.objectProcessorQueueSizeLock:
                        shared.objectProcessorQueueSize += len(payload)
                        shared.objectProcessorQueue.put((objectType,payload))

    def click_pushButtonStatusIcon(self):
        logger.debug('click_pushButtonStatusIcon')
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
            shared.config.set('bitmessagesettings', 'willinglysendtomobile', str(
                self.settingsDialogInstance.ui.checkBoxWillinglySendToMobile.isChecked()))
            shared.config.set('bitmessagesettings', 'useidenticons', str(
                self.settingsDialogInstance.ui.checkBoxUseIdenticons.isChecked()))
            shared.config.set('bitmessagesettings', 'replybelow', str(
                self.settingsDialogInstance.ui.checkBoxReplyBelow.isChecked()))
                
            lang_ind = int(self.settingsDialogInstance.ui.languageComboBox.currentIndex())
            if not languages[lang_ind] == 'other':
                shared.config.set('bitmessagesettings', 'userlocale', languages[lang_ind])
                change_translation(languages[lang_ind])
            
            if int(shared.config.get('bitmessagesettings', 'port')) != int(self.settingsDialogInstance.ui.lineEditTCPPort.text()):
                if not shared.safeConfigGetBoolean('bitmessagesettings', 'dontconnect'):
                    QMessageBox.about(self, _translate("MainWindow", "Restart"), _translate(
                        "MainWindow", "You must restart Bitmessage for the port number change to take effect."))
                shared.config.set('bitmessagesettings', 'port', str(
                    self.settingsDialogInstance.ui.lineEditTCPPort.text()))
            if self.settingsDialogInstance.ui.checkBoxUPnP.isChecked() != shared.safeConfigGetBoolean('bitmessagesettings', 'upnp'):
                shared.config.set('bitmessagesettings', 'upnp', str(self.settingsDialogInstance.ui.checkBoxUPnP.isChecked()))
                if self.settingsDialogInstance.ui.checkBoxUPnP.isChecked():
                    import upnp
                    upnpThread = upnp.uPnPThread()
                    upnpThread.start()
            #print 'self.settingsDialogInstance.ui.comboBoxProxyType.currentText()', self.settingsDialogInstance.ui.comboBoxProxyType.currentText()
            #print 'self.settingsDialogInstance.ui.comboBoxProxyType.currentText())[0:5]', self.settingsDialogInstance.ui.comboBoxProxyType.currentText()[0:5]
            if shared.config.get('bitmessagesettings', 'socksproxytype') == 'none' and self.settingsDialogInstance.ui.comboBoxProxyType.currentText()[0:5] == 'SOCKS':
                if shared.statusIconColor != 'red':
                    QMessageBox.about(self, _translate("MainWindow", "Restart"), _translate(
                        "MainWindow", "Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any)."))
            if shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and self.settingsDialogInstance.ui.comboBoxProxyType.currentText()[0:5] != 'SOCKS':
                self.statusBar().showMessage('')
            if self.settingsDialogInstance.ui.comboBoxProxyType.currentText()[0:5] == 'SOCKS':
                shared.config.set('bitmessagesettings', 'socksproxytype', str(
                    self.settingsDialogInstance.ui.comboBoxProxyType.currentText()))
            else:
                shared.config.set('bitmessagesettings', 'socksproxytype', 'none')
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
            try:
                # Rounding to integers just for aesthetics
                shared.config.set('bitmessagesettings', 'maxdownloadrate', str(
                    int(float(self.settingsDialogInstance.ui.lineEditMaxDownloadRate.text()))))
                shared.config.set('bitmessagesettings', 'maxuploadrate', str(
                    int(float(self.settingsDialogInstance.ui.lineEditMaxUploadRate.text()))))
            except:
                QMessageBox.about(self, _translate("MainWindow", "Number needed"), _translate(
                    "MainWindow", "Your maximum download and upload rate must be numbers. Ignoring what you typed."))

            shared.config.set('bitmessagesettings', 'namecoinrpctype',
                self.settingsDialogInstance.getNamecoinType())
            shared.config.set('bitmessagesettings', 'namecoinrpchost', str(
                self.settingsDialogInstance.ui.lineEditNamecoinHost.text()))
            shared.config.set('bitmessagesettings', 'namecoinrpcport', str(
                self.settingsDialogInstance.ui.lineEditNamecoinPort.text()))
            shared.config.set('bitmessagesettings', 'namecoinrpcuser', str(
                self.settingsDialogInstance.ui.lineEditNamecoinUser.text()))
            shared.config.set('bitmessagesettings', 'namecoinrpcpassword', str(
                self.settingsDialogInstance.ui.lineEditNamecoinPassword.text()))
            
            # Demanded difficulty tab
            if float(self.settingsDialogInstance.ui.lineEditTotalDifficulty.text()) >= 1:
                shared.config.set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(int(float(
                    self.settingsDialogInstance.ui.lineEditTotalDifficulty.text()) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
            if float(self.settingsDialogInstance.ui.lineEditSmallMessageDifficulty.text()) >= 1:
                shared.config.set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(int(float(
                    self.settingsDialogInstance.ui.lineEditSmallMessageDifficulty.text()) * shared.networkDefaultPayloadLengthExtraBytes)))

            if openclpow.has_opencl() and self.settingsDialogInstance.ui.checkBoxOpenCL.isChecked() != shared.safeConfigGetBoolean("bitmessagesettings", "opencl"):
                shared.config.set('bitmessagesettings', 'opencl', str(self.settingsDialogInstance.ui.checkBoxOpenCL.isChecked()))

            acceptableDifficultyChanged = False
            
            if float(self.settingsDialogInstance.ui.lineEditMaxAcceptableTotalDifficulty.text()) >= 1 or float(self.settingsDialogInstance.ui.lineEditMaxAcceptableTotalDifficulty.text()) == 0:
                if shared.config.get('bitmessagesettings','maxacceptablenoncetrialsperbyte') != str(int(float(
                    self.settingsDialogInstance.ui.lineEditMaxAcceptableTotalDifficulty.text()) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)):
                    # the user changed the max acceptable total difficulty
                    acceptableDifficultyChanged = True
                    shared.config.set('bitmessagesettings', 'maxacceptablenoncetrialsperbyte', str(int(float(
                        self.settingsDialogInstance.ui.lineEditMaxAcceptableTotalDifficulty.text()) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
            if float(self.settingsDialogInstance.ui.lineEditMaxAcceptableSmallMessageDifficulty.text()) >= 1 or float(self.settingsDialogInstance.ui.lineEditMaxAcceptableSmallMessageDifficulty.text()) == 0:
                if shared.config.get('bitmessagesettings','maxacceptablepayloadlengthextrabytes') != str(int(float(
                    self.settingsDialogInstance.ui.lineEditMaxAcceptableSmallMessageDifficulty.text()) * shared.networkDefaultPayloadLengthExtraBytes)):
                    # the user changed the max acceptable small message difficulty
                    acceptableDifficultyChanged = True
                    shared.config.set('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes', str(int(float(
                        self.settingsDialogInstance.ui.lineEditMaxAcceptableSmallMessageDifficulty.text()) * shared.networkDefaultPayloadLengthExtraBytes)))
            if acceptableDifficultyChanged:
                # It might now be possible to send msgs which were previously marked as toodifficult. 
                # Let us change them to 'msgqueued'. The singleWorker will try to send them and will again
                # mark them as toodifficult if the receiver's required difficulty is still higher than
                # we are willing to do.
                sqlExecute('''UPDATE sent SET status='msgqueued' WHERE status='toodifficult' ''')
                shared.workerQueue.put(('sendmessage', ''))
            
            #start:UI setting to stop trying to send messages after X days/months
            # I'm open to changing this UI to something else if someone has a better idea.
            if ((self.settingsDialogInstance.ui.lineEditDays.text()=='') and (self.settingsDialogInstance.ui.lineEditMonths.text()=='')):#We need to handle this special case. Bitmessage has its default behavior. The input is blank/blank
                shared.config.set('bitmessagesettings', 'stopresendingafterxdays', '')
                shared.config.set('bitmessagesettings', 'stopresendingafterxmonths', '')
                shared.maximumLengthOfTimeToBotherResendingMessages = float('inf')
            try:
                float(self.settingsDialogInstance.ui.lineEditDays.text())
                lineEditDaysIsValidFloat = True
            except:
                lineEditDaysIsValidFloat = False
            try:
                float(self.settingsDialogInstance.ui.lineEditMonths.text())
                lineEditMonthsIsValidFloat = True
            except:
                lineEditMonthsIsValidFloat = False
            if lineEditDaysIsValidFloat and not lineEditMonthsIsValidFloat:
                self.settingsDialogInstance.ui.lineEditMonths.setText("0")
            if lineEditMonthsIsValidFloat and not lineEditDaysIsValidFloat:
                self.settingsDialogInstance.ui.lineEditDays.setText("0")
            if lineEditDaysIsValidFloat or lineEditMonthsIsValidFloat:
                if (float(self.settingsDialogInstance.ui.lineEditDays.text()) >=0 and float(self.settingsDialogInstance.ui.lineEditMonths.text()) >=0):
                    shared.maximumLengthOfTimeToBotherResendingMessages = (float(str(self.settingsDialogInstance.ui.lineEditDays.text())) * 24 * 60 * 60) + (float(str(self.settingsDialogInstance.ui.lineEditMonths.text())) * (60 * 60 * 24 *365)/12)
                    if shared.maximumLengthOfTimeToBotherResendingMessages < 432000: # If the time period is less than 5 hours, we give zero values to all fields. No message will be sent again.
                        QMessageBox.about(self, _translate("MainWindow", "Will not resend ever"), _translate(
                            "MainWindow", "Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent."))
                        shared.config.set('bitmessagesettings', 'stopresendingafterxdays', '0')
                        shared.config.set('bitmessagesettings', 'stopresendingafterxmonths', '0')
                        shared.maximumLengthOfTimeToBotherResendingMessages = 0
                    else:
                        shared.config.set('bitmessagesettings', 'stopresendingafterxdays', str(float(
                        self.settingsDialogInstance.ui.lineEditDays.text())))
                        shared.config.set('bitmessagesettings', 'stopresendingafterxmonths', str(float(
                        self.settingsDialogInstance.ui.lineEditMonths.text())))

            shared.writeKeysFile()

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
                sqlStoredProcedure('movemessagstoprog')
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
                sqlStoredProcedure('movemessagstoappdata')
                # Write the keys.dat file to disk in the new location
                shared.writeKeysFile()
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
            shared.writeKeysFile()
            # self.ui.tableWidgetBlacklist.clearContents()
            self.ui.tableWidgetBlacklist.setRowCount(0)
            self.rerenderBlackWhiteList()
            self.ui.tabWidget.setTabText(6, 'Blacklist')

    def click_radioButtonWhitelist(self):
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            shared.config.set('bitmessagesettings', 'blackwhitelist', 'white')
            shared.writeKeysFile()
            # self.ui.tableWidgetBlacklist.clearContents()
            self.ui.tableWidgetBlacklist.setRowCount(0)
            self.rerenderBlackWhiteList()
            self.ui.tabWidget.setTabText(6, 'Whitelist')

    def click_pushButtonAddBlacklist(self):
        self.NewBlacklistDialogInstance = AddAddressDialog(self)
        if self.NewBlacklistDialogInstance.exec_():
            if self.NewBlacklistDialogInstance.ui.labelAddressCheck.text() == _translate("MainWindow", "Address is valid."):
                address = addBMIfNotPresent(str(
                    self.NewBlacklistDialogInstance.ui.lineEditAddress.text()))
                # First we must check to see if the address is already in the
                # address book. The user cannot add it again or else it will
                # cause problems when updating and deleting the entry.
                t = (address,)
                if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                    sql = '''select * from blacklist where address=?'''
                else:
                    sql = '''select * from whitelist where address=?'''
                queryreturn = sqlQuery(sql,*t)
                if queryreturn == []:
                    self.ui.tableWidgetBlacklist.setSortingEnabled(False)
                    self.ui.tableWidgetBlacklist.insertRow(0)
                    newItem = QtGui.QTableWidgetItem(unicode(
                        self.NewBlacklistDialogInstance.ui.newAddressLabel.text().toUtf8(), 'utf-8'))
                    newItem.setIcon(avatarize(address))
                    self.ui.tableWidgetBlacklist.setItem(0, 0, newItem)
                    newItem = QtGui.QTableWidgetItem(address)
                    newItem.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.ui.tableWidgetBlacklist.setItem(0, 1, newItem)
                    self.ui.tableWidgetBlacklist.setSortingEnabled(True)
                    t = (str(self.NewBlacklistDialogInstance.ui.newAddressLabel.text().toUtf8()), address, True)
                    if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                        sql = '''INSERT INTO blacklist VALUES (?,?,?)'''
                    else:
                        sql = '''INSERT INTO whitelist VALUES (?,?,?)'''
                    sqlExecute(sql, *t)
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
            addressAtCurrentRow = self.getCurrentAccount()
            if shared.safeConfigGetBoolean(addressAtCurrentRow, 'chan'):
                return
            if self.dialog.ui.radioButtonBehaveNormalAddress.isChecked():
                shared.config.set(str(
                    addressAtCurrentRow), 'mailinglist', 'false')
                # Set the color to either black or grey
                if shared.config.getboolean(addressAtCurrentRow, 'enabled'):
                    self.setCurrentItemColor(QApplication.palette()
                        .text().color())
                else:
                    self.setCurrentItemColor(QtGui.QColor(128, 128, 128))
            else:
                shared.config.set(str(
                    addressAtCurrentRow), 'mailinglist', 'true')
                shared.config.set(str(addressAtCurrentRow), 'mailinglistname', str(
                    self.dialog.ui.lineEditMailingListName.text().toUtf8()))
                self.setCurrentItemColor(QtGui.QColor(137, 04, 177)) #magenta
            self.rerenderComboBoxSendFrom()
            self.rerenderComboBoxSendFromBroadcast()
            shared.writeKeysFile()
            self.rerenderInboxToLabels()

    def on_action_EmailGatewayDialog(self):
        self.dialog = EmailGatewayDialog(self)
        # For Modal dialogs
        if self.dialog.exec_():
            addressAtCurrentRow = self.getCurrentAccount()
            acct = accountClass(addressAtCurrentRow)
            # no chans / mailinglists
            if acct.type != AccountMixin.NORMAL:
                return
            if self.dialog.ui.radioButtonUnregister.isChecked() and isinstance(acct, GatewayAccount):
                acct.unregister()
                shared.config.remove_option(addressAtCurrentRow, 'gateway')
                shared.writeKeysFile()
            elif self.dialog.ui.radioButtonRegister.isChecked():
                email = str(self.dialog.ui.lineEditEmail.text().toUtf8())
                acct = MailchuckAccount(addressAtCurrentRow)
                acct.register(email)
                shared.config.set(addressAtCurrentRow, 'label', email)
                shared.config.set(addressAtCurrentRow, 'gateway', 'mailchuck')
                self.getCurrentTreeWidget().currentItem().updateText()
                shared.writeKeysFile()
            else:
                pass
                #print "well nothing"
#            shared.writeKeysFile()
#            self.rerenderInboxToLabels()
    
    def click_NewAddressDialog(self):
        addresses = []
        for addressInKeysFile in getSortedAccounts():
            addresses.append(addressInKeysFile)
#        self.dialog = Ui_NewAddressWizard(addresses)
#        self.dialog.exec_()
#        print "Name: " + self.dialog.field("name").toString()
#        print "Email: " + self.dialog.field("email").toString()
#        return
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
                    streamNumberForAddress = decodeAddress(
                        self.dialog.ui.comboBoxExisting.currentText())[2]
                shared.addressGeneratorQueue.put(('createRandomAddress', 4, streamNumberForAddress, str(
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
                    shared.addressGeneratorQueue.put(('createDeterministicAddresses', 4, streamNumberForAddress, "unused deterministic address", self.dialog.ui.spinBoxNumberOfAddressesToMake.value(
                    ), self.dialog.ui.lineEditPassphrase.text().toUtf8(), self.dialog.ui.checkBoxEighteenByteRipe.isChecked()))
        else:
            logger.debug('new address dialog box rejected')

    # Quit selected from menu or application indicator
    def quit(self):
        '''quit_msg = "Are you sure you want to exit Bitmessage?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply is QtGui.QMessageBox.No:
            return
        '''
        # save state and geometry self and all widgets
        self.saveSettings()
        for attr, obj in self.ui.__dict__.iteritems():
            if hasattr(obj, "__class__") and isinstance(obj, settingsmixin.SettingsMixin):
                saveMethod = getattr(obj, "saveSettings", None)
                if callable (saveMethod):
                    obj.saveSettings()

        shared.doCleanShutdown()
        self.tray.hide()
        # unregister the messaging system
        if self.mmapp is not None:
            self.mmapp.unregister()

#        settings = QSettings("Bitmessage", "PyBitmessage")
#        settings.setValue("geometry", self.saveGeometry())
#        settings.setValue("state", self.saveState())

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
        msgid = self.getCurrentMessageId()
        textEdit = self.getCurrentMessageTextedit()
        if not msgid:
            return
        queryreturn = sqlQuery(
            '''select message from inbox where msgid=?''', msgid)
        if queryreturn != []:
            for row in queryreturn:
                messageText, = row

        lines = messageText.split('\n')
        totalLines = len(lines)
        for i in xrange(totalLines):
            if 'Message ostensibly from ' in lines[i]:
                lines[i] = '<p style="font-size: 12px; color: grey;">%s</span></p>' % (
                    lines[i])
            elif lines[i] == '------------------------------------------------------':
                lines[i] = '<hr>'
            elif lines[i] == '' and (i+1) < totalLines and \
                 lines[i+1] != '------------------------------------------------------':
                lines[i] = '<br><br>'
        content = ' '.join(lines) # To keep the whitespace between lines
        content = shared.fixPotentiallyInvalidUTF8Data(content)
        content = unicode(content, 'utf-8)')
        textEdit.setHtml(QtCore.QString(content))

    def on_action_InboxMarkUnread(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        font = QFont()
        font.setBold(True)
        inventoryHashesToMarkUnread = []
        modified = 0
        for row in tableWidget.selectedIndexes():
            currentRow = row.row()
            inventoryHashToMarkUnread = str(tableWidget.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            if inventoryHashToMarkUnread in inventoryHashesToMarkUnread:
                # it returns columns as separate items, so we skip dupes
                continue
            if not tableWidget.item(currentRow, 0).font().bold():
                modified += 1
            inventoryHashesToMarkUnread.append(inventoryHashToMarkUnread)
            tableWidget.item(currentRow, 0).setFont(font)
            tableWidget.item(currentRow, 1).setFont(font)
            tableWidget.item(currentRow, 2).setFont(font)
            tableWidget.item(currentRow, 3).setFont(font)
        #sqlite requires the exact number of ?s to prevent injection
        sqlExecute('''UPDATE inbox SET read=0 WHERE msgid IN (%s)''' % (
            "?," * len(inventoryHashesToMarkUnread))[:-1], *inventoryHashesToMarkUnread)
        if modified == 1:
            # performance optimisation
            self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), self.getCurrentFolder())
        else:
            self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), self.getCurrentFolder(), self.getCurrentTreeWidget(), 0)
        # tableWidget.selectRow(currentRow + 1) 
        # This doesn't de-select the last message if you try to mark it unread, but that doesn't interfere. Might not be necessary.
        # We could also select upwards, but then our problem would be with the topmost message.
        # tableWidget.clearSelection() manages to mark the message as read again.

    # Format predefined text on message reply.
    def quoted_text(self, message):
        if not shared.safeConfigGetBoolean('bitmessagesettings', 'replybelow'):
          return '\n\n------------------------------------------------------\n' + message

        quoteWrapper = textwrap.TextWrapper(replace_whitespace = False,
                                            initial_indent = '> ',
                                            subsequent_indent = '> ',
                                            break_long_words = False,
                                            break_on_hyphens = False)
        def quote_line(line):
            # Do quote empty lines.
            if line == '' or line.isspace():
                return '> '
            # Quote already quoted lines, but do not wrap them.
            elif line[0:2] == '> ':
                return '> ' + line
            # Wrap and quote lines/paragraphs new to this message.
            else:
                return quoteWrapper.fill(line)
        return '\n'.join([quote_line(l) for l in message.splitlines()]) + '\n\n'

    def on_action_InboxReply(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        
        # save this to return back after reply is done
        self.replyFromTab = self.ui.tabWidget.currentIndex()
        
        currentInboxRow = tableWidget.currentRow()
        toAddressAtCurrentInboxRow = str(tableWidget.item(
            currentInboxRow, 0).data(Qt.UserRole).toPyObject())
        acct = accountClass(toAddressAtCurrentInboxRow)
        fromAddressAtCurrentInboxRow = str(tableWidget.item(
            currentInboxRow, 1).data(Qt.UserRole).toPyObject())
        msgid = str(tableWidget.item(
            currentInboxRow, 3).data(Qt.UserRole).toPyObject())
        queryreturn = sqlQuery(
            '''select message from inbox where msgid=?''', msgid)
        if queryreturn != []:
            for row in queryreturn:
                messageAtCurrentInboxRow, = row
        acct.parseMessage(toAddressAtCurrentInboxRow, fromAddressAtCurrentInboxRow, unicode(tableWidget.item(currentInboxRow, 2).data(Qt.UserRole).toPyObject(), 'utf-8'), messageAtCurrentInboxRow)
        widget = {
            'subject': self.ui.lineEditSubject,
            'from': self.ui.comboBoxSendFrom,
            'message': self.ui.textEditMessage
        }
        if toAddressAtCurrentInboxRow == str_broadcast_subscribers:
            self.ui.tabWidgetSend.setCurrentIndex(0)
#            toAddressAtCurrentInboxRow = fromAddressAtCurrentInboxRow
        elif not shared.config.has_section(toAddressAtCurrentInboxRow):
            QtGui.QMessageBox.information(self, _translate("MainWindow", "Address is gone"), _translate(
                "MainWindow", "Bitmessage cannot find your address %1. Perhaps you removed it?").arg(toAddressAtCurrentInboxRow), QMessageBox.Ok)
        elif not shared.config.getboolean(toAddressAtCurrentInboxRow, 'enabled'):
            QtGui.QMessageBox.information(self, _translate("MainWindow", "Address disabled"), _translate(
                "MainWindow", "Error: The address from which you are trying to send is disabled. You\'ll have to enable it on the \'Your Identities\' tab before using it."), QMessageBox.Ok)
        else:
            self.setBroadcastEnablementDependingOnWhetherThisIsAMailingListAddress(toAddressAtCurrentInboxRow)
            if self.ui.tabWidgetSend.currentIndex() == 1:
                widget = {
                    'subject': self.ui.lineEditSubjectBroadcast,
                    'from': self.ui.comboBoxSendFromBroadcast,
                    'message': self.ui.textEditMessageBroadcast
                }
                self.ui.tabWidgetSend.setCurrentIndex(1)
                toAddressAtCurrentInboxRow = fromAddressAtCurrentInboxRow

        self.ui.lineEditTo.setText(str(acct.fromAddress))
        
        # If the previous message was to a chan then we should send our reply to the chan rather than to the particular person who sent the message.
        if shared.config.has_section(toAddressAtCurrentInboxRow):
            if shared.safeConfigGetBoolean(toAddressAtCurrentInboxRow, 'chan'):
                logger.debug('original sent to a chan. Setting the to address in the reply to the chan address.')
                self.ui.lineEditTo.setText(str(toAddressAtCurrentInboxRow))
        
        listOfAddressesInComboBoxSendFrom = [str(widget['from'].itemData(i).toPyObject()) for i in range(widget['from'].count())]
        if toAddressAtCurrentInboxRow in listOfAddressesInComboBoxSendFrom:
            currentIndex = listOfAddressesInComboBoxSendFrom.index(toAddressAtCurrentInboxRow)
            widget['from'].setCurrentIndex(currentIndex)
        else:
            widget['from'].setCurrentIndex(0)
        
        quotedText = self.quoted_text(unicode(messageAtCurrentInboxRow, 'utf-8'))
        widget['message'].setText(quotedText)
        if acct.subject[0:3] in ['Re:', 'RE:']:
            widget['subject'].setText(acct.subject)
        else:
            widget['subject'].setText('Re: ' + acct.subject)
        self.ui.tabWidget.setCurrentIndex(1)

    def on_action_InboxAddSenderToAddressBook(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentInboxRow = tableWidget.currentRow()
        # tableWidget.item(currentRow,1).data(Qt.UserRole).toPyObject()
        addressAtCurrentInboxRow = str(tableWidget.item(
            currentInboxRow, 1).data(Qt.UserRole).toPyObject())
        # Let's make sure that it isn't already in the address book
        queryreturn = sqlQuery('''select * from addressbook where address=?''',
                               addressAtCurrentInboxRow)
        if queryreturn == []:
            sqlExecute('''INSERT INTO addressbook VALUES (?,?)''',
                       '--New entry. Change label in Address Book.--',
                       addressAtCurrentInboxRow)
            self.rerenderAddressBook()
            self.statusBar().showMessage(_translate(
                "MainWindow", "Entry added to the Address Book. Edit the label to your liking."))
        else:
            self.statusBar().showMessage(_translate(
                "MainWindow", "Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want."))

    def on_action_InboxAddSenderToBlackList(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentInboxRow = tableWidget.currentRow()
        # tableWidget.item(currentRow,1).data(Qt.UserRole).toPyObject()
        addressAtCurrentInboxRow = str(tableWidget.item(
            currentInboxRow, 1).data(Qt.UserRole).toPyObject())
        # Let's make sure that it isn't already in the address book
        queryreturn = sqlQuery('''select * from blacklist where address=?''',
                               addressAtCurrentInboxRow)
        if queryreturn == []:
            label = "\"" + str(tableWidget.item(currentInboxRow, 2).data(Qt.UserRole).toPyObject()) + "\" in " + shared.config.get(self.getCurrentAccount(), "label")
            sqlExecute('''INSERT INTO blacklist VALUES (?,?, ?)''',
                       label,
                       addressAtCurrentInboxRow, True)
            self.rerenderBlackWhiteList()
            self.statusBar().showMessage(_translate(
                "MainWindow", "Entry added to the blacklist. Edit the label to your liking."))
        else:
            self.statusBar().showMessage(_translate(
                "MainWindow", "Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want."))

    # Send item on the Inbox tab to trash
    def on_action_InboxTrash(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        unread = False
        currentRow = 0
        folder = self.getCurrentFolder()
        shifted = QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ShiftModifier
        while tableWidget.selectedIndexes():
            currentRow = tableWidget.selectedIndexes()[0].row()
            inventoryHashToTrash = str(tableWidget.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            if folder == "trash" or shifted:
                sqlExecute('''DELETE FROM inbox WHERE msgid=?''', inventoryHashToTrash)
            else:
                sqlExecute('''UPDATE inbox SET folder='trash' WHERE msgid=?''', inventoryHashToTrash)
            if tableWidget.item(currentRow, 0).font().bold():
                self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), folder, self.getCurrentTreeWidget(), -1)
                if folder != "trash" and not shifted:
                    self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), "trash", self.getCurrentTreeWidget(), 1)

            self.getCurrentMessageTextedit().setText("")
            tableWidget.removeRow(currentRow)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Moved items to trash."))
        if currentRow == 0:
            tableWidget.selectRow(currentRow)
        else:
            tableWidget.selectRow(currentRow - 1)
            
    def on_action_TrashUndelete(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        unread = False
        currentRow = 0
        while tableWidget.selectedIndexes():
            currentRow = tableWidget.selectedIndexes()[0].row()
            inventoryHashToTrash = str(tableWidget.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            sqlExecute('''UPDATE inbox SET folder='inbox' WHERE msgid=?''', inventoryHashToTrash)
            if tableWidget.item(currentRow, 0).font().bold():
                self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), "inbox", self.getCurrentTreeWidget(), 1)
                self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), "trash", self.getCurrentTreeWidget(), -1)
            self.getCurrentMessageTextedit().setText("")
            tableWidget.removeRow(currentRow)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Undeleted item."))
        if currentRow == 0:
            tableWidget.selectRow(currentRow)
        else:
            tableWidget.selectRow(currentRow - 1)

    def on_action_InboxSaveMessageAs(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentInboxRow = tableWidget.currentRow()
        try:
            subjectAtCurrentInboxRow = str(tableWidget.item(currentInboxRow,2).text())
        except:
            subjectAtCurrentInboxRow = ''

        # Retrieve the message data out of the SQL database
        msgid = str(tableWidget.item(
            currentInboxRow, 3).data(Qt.UserRole).toPyObject())
        queryreturn = sqlQuery(
            '''select message from inbox where msgid=?''', msgid)
        if queryreturn != []:
            for row in queryreturn:
                message, = row

        defaultFilename = "".join(x for x in subjectAtCurrentInboxRow if x.isalnum()) + '.txt'
        filename = QFileDialog.getSaveFileName(self, _translate("MainWindow","Save As..."), defaultFilename, "Text files (*.txt);;All files (*.*)")
        if filename == '':
            return
        try:
            f = open(filename, 'w')
            f.write(message)
            f.close()
        except Exception, e:
            logger.exception('Message not saved', exc_info=True)
            self.statusBar().showMessage(_translate("MainWindow", "Write error."))

    # Send item on the Sent tab to trash
    def on_action_SentTrash(self):
        currentRow = 0
        unread = False
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        folder = self.getCurrentFolder()
        shifted = (QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ShiftModifier) > 0
        while tableWidget.selectedIndexes() != []:
            currentRow = tableWidget.selectedIndexes()[0].row()
            ackdataToTrash = str(tableWidget.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            if folder == "trash" or shifted:
                sqlExecute('''DELETE FROM sent WHERE ackdata=?''', ackdataToTrash)
            else:
                sqlExecute('''UPDATE sent SET folder='trash' WHERE ackdata=?''', ackdataToTrash)
            if tableWidget.item(currentRow, 0).font().bold():
                self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), folder, self.getCurrentTreeWidget(), -1)
            self.getCurrentMessageTextedit().setPlainText("")
            tableWidget.removeRow(currentRow)
            self.statusBar().showMessage(_translate(
                "MainWindow", "Moved items to trash."))
        if currentRow == 0:
            self.ui.tableWidgetInbox.selectRow(currentRow)
        else:
            self.ui.tableWidgetInbox.selectRow(currentRow - 1)

    def on_action_ForceSend(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        addressAtCurrentRow = str(self.ui.tableWidgetInbox.item(
            currentRow, 0).data(Qt.UserRole).toPyObject())
        toRipe = decodeAddress(addressAtCurrentRow)[3]
        sqlExecute(
            '''UPDATE sent SET status='forcepow' WHERE toripe=? AND status='toodifficult' and folder='sent' ''',
            toRipe)
        queryreturn = sqlQuery('''select ackdata FROM sent WHERE status='forcepow' ''')
        for row in queryreturn:
            ackdata, = row
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                ackdata, 'Overriding maximum-difficulty setting. Work queued.')))
        shared.workerQueue.put(('sendmessage', ''))

    def on_action_SentClipboard(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        addressAtCurrentRow = str(self.ui.tableWidgetInbox.item(
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
            sqlExecute('''DELETE FROM addressbook WHERE label=? AND address=?''',
                       str(labelAtCurrentRow), str(addressAtCurrentRow))
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
                self.statusBar().showMessage(QtGui.QApplication.translate("MainWindow", "Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want."))
                continue
            labelAtCurrentRow = self.ui.tableWidgetAddressBook.item(currentRow,0).text().toUtf8()
            self.addSubscription(addressAtCurrentRow, labelAtCurrentRow)
            self.ui.tabWidget.setCurrentIndex(4)

    def on_context_menuAddressBook(self, point):
        self.popMenuAddressBook = QtGui.QMenu(self)
        self.popMenuAddressBook.addAction(self.actionAddressBookSend)
        self.popMenuAddressBook.addAction(self.actionAddressBookClipboard)
        self.popMenuAddressBook.addAction(self.actionAddressBookSubscribe)
        self.popMenuAddressBook.addAction(self.actionAddressBookSetAvatar)
        self.popMenuAddressBook.addSeparator()
        self.popMenuAddressBook.addAction(self.actionAddressBookNew)
        normal = True
        for row in self.ui.tableWidgetAddressBook.selectedIndexes():
            currentRow = row.row()
            type = str(self.ui.tableWidgetAddressBook.item(
                currentRow, 0).data(Qt.UserRole).toPyObject())
            if type != AccountMixin.NORMAL:
                normal = False
        if normal:
            # only if all selected addressbook items are normal, allow delete
            self.popMenuAddressBook.addAction(self.actionAddressBookDelete)
        self.popMenuAddressBook.exec_(
            self.ui.tableWidgetAddressBook.mapToGlobal(point))

    # Group of functions for the Subscriptions dialog box
    def on_action_SubscriptionsNew(self):
        self.click_pushButtonAddSubscription()
        
    def on_action_SubscriptionsDelete(self):
        if QtGui.QMessageBox.question(self, "Delete subscription?", _translate("MainWindow", "If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.\n\nAre you sure you want to delete the subscription?"), QMessageBox.Yes|QMessageBox.No) != QMessageBox.Yes:
            return
        address = self.getCurrentAccount()
        sqlExecute('''DELETE FROM subscriptions WHERE address=?''',
                   address)
        self.rerenderTabTreeSubscriptions()
        self.rerenderInboxFromLabels()
        self.rerenderAddressBook()
        shared.reloadBroadcastSendersForWhichImWatching()

    def on_action_SubscriptionsClipboard(self):
        address = self.getCurrentAccount()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(address))

    def on_action_SubscriptionsEnable(self):
        address = self.getCurrentAccount()
        sqlExecute(
            '''update subscriptions set enabled=1 WHERE address=?''',
            address)
        account = self.getCurrentItem()
        account.setEnabled(True)
        self.rerenderAddressBook()
        shared.reloadBroadcastSendersForWhichImWatching()

    def on_action_SubscriptionsDisable(self):
        address = self.getCurrentAccount()
        sqlExecute(
            '''update subscriptions set enabled=0 WHERE address=?''',
            address)
        account = self.getCurrentItem()
        account.setEnabled(False)
        self.rerenderAddressBook()
        shared.reloadBroadcastSendersForWhichImWatching()

    def on_context_menuSubscriptions(self, point):
        self.popMenuSubscriptions = QtGui.QMenu(self)
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsNew)
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsDelete)
        self.popMenuSubscriptions.addSeparator()
        if self.getCurrentItem().isEnabled:
            self.popMenuSubscriptions.addAction(self.actionsubscriptionsDisable)
        else:
            self.popMenuSubscriptions.addAction(self.actionsubscriptionsEnable)
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsSetAvatar)
        self.popMenuSubscriptions.addSeparator()
        self.popMenuSubscriptions.addAction(self.actionsubscriptionsClipboard)
        self.popMenuSubscriptions.exec_(
            self.ui.treeWidgetSubscriptions.mapToGlobal(point))

    # Group of functions for the Blacklist dialog box
    def on_action_BlacklistNew(self):
        self.click_pushButtonAddBlacklist()

    def on_action_BlacklistDelete(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 1).text()
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlExecute(
                '''DELETE FROM blacklist WHERE label=? AND address=?''',
                str(labelAtCurrentRow), str(addressAtCurrentRow))
        else:
            sqlExecute(
                '''DELETE FROM whitelist WHERE label=? AND address=?''',
                str(labelAtCurrentRow), str(addressAtCurrentRow))
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
            currentRow, 0).setTextColor(QApplication.palette().text().color())
        self.ui.tableWidgetBlacklist.item(
            currentRow, 1).setTextColor(QApplication.palette().text().color())
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlExecute(
                '''UPDATE blacklist SET enabled=1 WHERE address=?''',
                str(addressAtCurrentRow))
        else:
            sqlExecute(
                '''UPDATE whitelist SET enabled=1 WHERE address=?''',
                str(addressAtCurrentRow))

    def on_action_BlacklistDisable(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(
            currentRow, 1).text()
        self.ui.tableWidgetBlacklist.item(
            currentRow, 0).setTextColor(QtGui.QColor(128, 128, 128))
        self.ui.tableWidgetBlacklist.item(
            currentRow, 1).setTextColor(QtGui.QColor(128, 128, 128))
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlExecute(
                '''UPDATE blacklist SET enabled=0 WHERE address=?''', str(addressAtCurrentRow))
        else:
            sqlExecute(
                '''UPDATE whitelist SET enabled=0 WHERE address=?''', str(addressAtCurrentRow))

    def widgetConvert (self, widget):
        if widget == self.ui.tableWidgetInbox:
            return self.ui.treeWidgetYourIdentities
        elif widget == self.ui.tableWidgetInboxSubscriptions:
            return self.ui.treeWidgetSubscriptions
        elif widget == self.ui.tableWidgetInboxChans:
            return self.ui.treeWidgetChans
        elif widget == self.ui.treeWidgetYourIdentities:
            return self.ui.tableWidgetInbox
        elif widget == self.ui.treeWidgetSubscriptions:
            return self.ui.tableWidgetInboxSubscriptions
        elif widget == self.ui.treeWidgetChans:
            return self.ui.tableWidgetInboxChans
        else:
            return None

    def getCurrentTreeWidget(self):
        currentIndex = self.ui.tabWidget.currentIndex();
        treeWidgetList = [
            self.ui.treeWidgetYourIdentities,
            False,
            self.ui.treeWidgetSubscriptions,
            self.ui.treeWidgetChans
        ]
        if currentIndex >= 0 and currentIndex < len(treeWidgetList):
            return treeWidgetList[currentIndex]
        else:
            return False

    def getAccountTreeWidget(self, account):
        try:
            if account.type == AccountMixin.CHAN:
                return self.ui.treeWidgetChans
            elif account.type == AccountMixin.SUBSCRIPTION:
                return self.ui.treeWidgetSubscriptions
            else:
                return self.ui.treeWidgetYourIdentities
        except:
            return self.ui.treeWidgetYourIdentities

    def getCurrentMessagelist(self):
        currentIndex = self.ui.tabWidget.currentIndex();
        messagelistList = [
            self.ui.tableWidgetInbox,
            False,
            self.ui.tableWidgetInboxSubscriptions,
            self.ui.tableWidgetInboxChans,
        ]
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return messagelistList[currentIndex]
        else:
            return False
            
    def getAccountMessagelist(self, account):
        try:
            if account.type == AccountMixin.CHAN:
                return self.ui.tableWidgetInboxChans
            elif account.type == AccountMixin.SUBSCRIPTION:
                return self.ui.tableWidgetInboxSubscriptions
            else:
                return self.ui.tableWidgetInbox
        except:
            return self.ui.tableWidgetInbox

    def getCurrentMessageId(self):
        messagelist = self.getCurrentMessagelist()
        if messagelist:
            currentRow = messagelist.currentRow()
            if currentRow >= 0:
                msgid = str(messagelist.item(
                    currentRow, 3).data(Qt.UserRole).toPyObject()) # data is saved at the 4. column of the table...
                return msgid
        return False

    def getCurrentMessageTextedit(self):
        currentIndex = self.ui.tabWidget.currentIndex();
        messagelistList = [
            self.ui.textEditInboxMessage,
            False,
            self.ui.textEditInboxMessageSubscriptions,
            self.ui.textEditInboxMessageChans,
        ]
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return messagelistList[currentIndex]
        else:
            return False

    def getAccountTextedit(self, account):
        try:
            if account.type == AccountMixin.CHAN:
                return self.ui.textEditInboxMessageChans
            elif account.type == AccountMixin.SUBSCRIPTION:
                return self.ui.textEditInboxSubscriptions
            else:
                return self.ui.textEditInboxMessage
        except:
            return self.ui.textEditInboxMessage

    def getCurrentSearchLine(self):
        currentIndex = self.ui.tabWidget.currentIndex();
        messagelistList = [
            self.ui.inboxSearchLineEdit,
            False,
            self.ui.inboxSearchLineEditSubscriptions,
            self.ui.inboxSearchLineEditChans,
        ]
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return messagelistList[currentIndex]
        else:
            return False

    def getCurrentSearchOption(self):
        currentIndex = self.ui.tabWidget.currentIndex();
        messagelistList = [
            self.ui.inboxSearchOption,
            False,
            self.ui.inboxSearchOptionSubscriptions,
            self.ui.inboxSearchOptionChans,
        ]
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return messagelistList[currentIndex].currentText().toUtf8().data()
        else:
            return False

    # Group of functions for the Your Identities dialog box
    def getCurrentItem(self, treeWidget = None):
        if treeWidget is None:
            treeWidget = self.getCurrentTreeWidget()
        if treeWidget:
            currentItem = treeWidget.currentItem()
            if currentItem:
                return currentItem
        return False
    
    def getCurrentAccount(self, treeWidget = None):
        currentItem = self.getCurrentItem(treeWidget)
        if currentItem:
            account = currentItem.address
            return account
        else:
            # TODO need debug msg?
            return False

    def getCurrentFolder(self, treeWidget = None):
        if treeWidget is None:
            treeWidget = self.getCurrentTreeWidget()
        #treeWidget = self.ui.treeWidgetYourIdentities
        if treeWidget:
            currentItem = treeWidget.currentItem()
            if currentItem and hasattr(currentItem, 'folderName'):
                return currentItem.folderName
            else:
                return None

    def setCurrentItemColor(self, color):
        treeWidget = self.getCurrentTreeWidget()
        if treeWidget:
            brush = QtGui.QBrush()
            brush.setStyle(QtCore.Qt.NoBrush)
            brush.setColor(color)
            currentItem = treeWidget.currentItem()
            currentItem.setForeground(0, brush)

    def on_action_YourIdentitiesNew(self):
        self.click_NewAddressDialog()

    def on_action_YourIdentitiesDelete(self):
        account = self.getCurrentItem()
        if account.type == AccountMixin.NORMAL:
            return # maybe in the future
        elif account.type == AccountMixin.CHAN:
            if QtGui.QMessageBox.question(self, "Delete channel?", _translate("MainWindow", "If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.\n\nAre you sure you want to delete the channel?"), QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                shared.config.remove_section(str(account.address))
            else:
                return
        else:
            return
        shared.writeKeysFile()
        shared.reloadMyAddressHashes()
        self.rerenderAddressBook()
        if account.type == AccountMixin.NORMAL:
            self.rerenderTabTreeMessages()
        elif account.type == AccountMixin.CHAN:
            self.rerenderTabTreeChans()

    def on_action_Enable(self):
        addressAtCurrentRow = self.getCurrentAccount()
        self.enableIdentity(addressAtCurrentRow)
        account = self.getCurrentItem()
        account.setEnabled(True)

    def enableIdentity(self, address):
        shared.config.set(address, 'enabled', 'true')
        shared.writeKeysFile()
        shared.reloadMyAddressHashes()
        self.rerenderAddressBook()

    def on_action_Disable(self):
        address = self.getCurrentAccount()
        self.disableIdentity(address)
        account = self.getCurrentItem()
        account.setEnabled(False)

    def disableIdentity(self, address):
        shared.config.set(str(address), 'enabled', 'false')
        shared.writeKeysFile()
        shared.reloadMyAddressHashes()
        self.rerenderAddressBook()

    def on_action_Clipboard(self):
        address = self.getCurrentAccount()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(address))

    #set avatar functions
    def on_action_TreeWidgetSetAvatar(self):
        address = self.getCurrentAccount()
        self.setAvatar(address)

    def on_action_AddressBookSetAvatar(self):
        self.on_action_SetAvatar(self.ui.tableWidgetAddressBook)
        
    def on_action_BlacklistSetAvatar(self):
        self.on_action_SetAvatar(self.ui.tableWidgetBlacklist)

    def on_action_SetAvatar(self, thisTableWidget):
        currentRow = thisTableWidget.currentRow()
        addressAtCurrentRow = thisTableWidget.item(
            currentRow, 1).text()
        setToIdenticon = not self.setAvatar(addressAtCurrentRow)
        if setToIdenticon:
            thisTableWidget.item(
                currentRow, 0).setIcon(avatarize(addressAtCurrentRow))

    def setAvatar(self, addressAtCurrentRow):
        if not os.path.exists(shared.appdata + 'avatars/'):
            os.makedirs(shared.appdata + 'avatars/')
        hash = hashlib.md5(addBMIfNotPresent(addressAtCurrentRow)).hexdigest()
        extensions = ['PNG', 'GIF', 'JPG', 'JPEG', 'SVG', 'BMP', 'MNG', 'PBM', 'PGM', 'PPM', 'TIFF', 'XBM', 'XPM', 'TGA']
        # http://pyqt.sourceforge.net/Docs/PyQt4/qimagereader.html#supportedImageFormats
        names = {'BMP':'Windows Bitmap', 'GIF':'Graphic Interchange Format', 'JPG':'Joint Photographic Experts Group', 'JPEG':'Joint Photographic Experts Group', 'MNG':'Multiple-image Network Graphics', 'PNG':'Portable Network Graphics', 'PBM':'Portable Bitmap', 'PGM':'Portable Graymap', 'PPM':'Portable Pixmap', 'TIFF':'Tagged Image File Format', 'XBM':'X11 Bitmap', 'XPM':'X11 Pixmap', 'SVG':'Scalable Vector Graphics', 'TGA':'Targa Image Format'}
        filters = []
        all_images_filter = []
        current_files = []
        for ext in extensions:
            filters += [ names[ext] + ' (*.' + ext.lower() + ')' ]
            all_images_filter += [ '*.' + ext.lower() ]
            upper = shared.appdata + 'avatars/' + hash + '.' + ext.upper()
            lower = shared.appdata + 'avatars/' + hash + '.' + ext.lower()
            if os.path.isfile(lower):
                current_files += [lower]
            elif os.path.isfile(upper):
                current_files += [upper]
        filters[0:0] = ['Image files (' + ' '.join(all_images_filter) + ')']
        filters[1:1] = ['All files (*.*)']
        sourcefile = QFileDialog.getOpenFileName(self, _translate("MainWindow","Set avatar..."), filter = ';;'.join(filters))
        # determine the correct filename (note that avatars don't use the suffix)
        destination = shared.appdata + 'avatars/' + hash + '.' + sourcefile.split('.')[-1]
        exists = QtCore.QFile.exists(destination)
        if sourcefile == '':
            # ask for removal of avatar
            if exists | (len(current_files)>0):
                displayMsg = _translate("MainWindow", "Do you really want to remove this avatar?")
                overwrite = QtGui.QMessageBox.question(
                            self, 'Message', displayMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            else:
                overwrite = QtGui.QMessageBox.No
        else:
            # ask whether to overwrite old avatar
            if exists | (len(current_files)>0):
                displayMsg = _translate("MainWindow", "You have already set an avatar for this address. Do you really want to overwrite it?")
                overwrite = QtGui.QMessageBox.question(
                            self, 'Message', displayMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            else:
                overwrite = QtGui.QMessageBox.No
            
        # copy the image file to the appdata folder
        if (not exists) | (overwrite == QtGui.QMessageBox.Yes):
            if overwrite == QtGui.QMessageBox.Yes:
                for file in current_files:
                    QtCore.QFile.remove(file)
                QtCore.QFile.remove(destination)
            # copy it
            if sourcefile != '':
                copied = QtCore.QFile.copy(sourcefile, destination)
                if not copied:
                    logger.error('couldn\'t copy :(')
            # set the icon
            self.rerenderTabTreeMessages()
            self.rerenderTabTreeSubscriptions()
            self.rerenderTabTreeChans()
            self.rerenderComboBoxSendFrom()
            self.rerenderComboBoxSendFromBroadcast()
            self.rerenderInboxFromLabels()
            self.rerenderInboxToLabels()
            self.rerenderSentFromLabels()
            self.rerenderSentToLabels()
            self.rerenderBlackWhiteList()
            # generate identicon
            return False

        return True
        
    def on_context_menuYourIdentities(self, point):
        self.popMenuYourIdentities = QtGui.QMenu(self)
        self.popMenuYourIdentities.addAction(self.actionNewYourIdentities)
        self.popMenuYourIdentities.addSeparator()
        self.popMenuYourIdentities.addAction(self.actionClipboardYourIdentities)
        self.popMenuYourIdentities.addSeparator()
        if self.getCurrentItem().isEnabled:
            self.popMenuYourIdentities.addAction(self.actionDisableYourIdentities)
        else:
            self.popMenuYourIdentities.addAction(self.actionEnableYourIdentities)
        self.popMenuYourIdentities.addAction(self.actionSetAvatarYourIdentities)
        self.popMenuYourIdentities.addAction(self.actionSpecialAddressBehaviorYourIdentities)
        self.popMenuYourIdentities.addAction(self.actionEmailGateway)
        self.popMenuYourIdentities.exec_(
            self.ui.treeWidgetYourIdentities.mapToGlobal(point))

    # TODO make one popMenu
    def on_context_menuChan(self, point):
        self.popMenu = QtGui.QMenu(self)
        self.popMenu.addAction(self.actionNew)
        self.popMenu.addAction(self.actionDelete)
        self.popMenu.addSeparator()
        self.popMenu.addAction(self.actionClipboard)
        self.popMenu.addSeparator()
        if self.getCurrentItem().isEnabled:
            self.popMenu.addAction(self.actionDisable)
        else:
            self.popMenu.addAction(self.actionEnable)
        self.popMenu.addAction(self.actionSetAvatar)
        self.popMenu.exec_(
            self.ui.treeWidgetChans.mapToGlobal(point))

    def on_context_menuInbox(self, point):
        tableWidget = self.getCurrentMessagelist()
        if tableWidget:
            currentFolder = self.getCurrentFolder()
            if currentFolder is None:
                pass
            if currentFolder == 'sent':
                self.on_context_menuSent(point)
            else:
                self.popMenuInbox = QtGui.QMenu(self)
                self.popMenuInbox.addAction(self.actionForceHtml)
                self.popMenuInbox.addAction(self.actionMarkUnread)
                self.popMenuInbox.addSeparator()
                self.popMenuInbox.addAction(self.actionReply)
                self.popMenuInbox.addAction(self.actionAddSenderToAddressBook)
                self.popMenuInbox.addSeparator()
                self.popMenuInbox.addAction(self.actionAddSenderToBlackList)
                self.popMenuInbox.addSeparator()
                self.popMenuInbox.addAction(self.actionSaveMessageAs)
                if currentFolder == "trash":
                    self.popMenuInbox.addAction(self.actionUndeleteTrashedMessage)
                else:
                    self.popMenuInbox.addAction(self.actionTrashInboxMessage)
                self.popMenuInbox.exec_(tableWidget.mapToGlobal(point))

    def on_context_menuSent(self, point):
        self.popMenuSent = QtGui.QMenu(self)
        self.popMenuSent.addAction(self.actionSentClipboard)
        self.popMenuSent.addAction(self.actionTrashSentMessage)

        # Check to see if this item is toodifficult and display an additional
        # menu option (Force Send) if it is.
        currentRow = self.ui.tableWidgetInbox.currentRow()
        if currentRow >= 0:
            ackData = str(self.ui.tableWidgetInbox.item(
                currentRow, 3).data(Qt.UserRole).toPyObject())
            queryreturn = sqlQuery('''SELECT status FROM sent where ackdata=?''', ackData)
            for row in queryreturn:
                status, = row
            if status == 'toodifficult':
                self.popMenuSent.addAction(self.actionForceSend)

        self.popMenuSent.exec_(self.ui.tableWidgetInbox.mapToGlobal(point))

    def inboxSearchLineEditPressed(self):
        searchLine = self.getCurrentSearchLine()
        searchOption = self.getCurrentSearchOption()
        if searchLine:
            searchKeyword = searchLine.text().toUtf8().data()
            searchLine.setText(QString(""))
            messageTextedit = self.getCurrentMessageTextedit()
            if messageTextedit:
                messageTextedit.setPlainText(QString(""))
            messagelist = self.getCurrentMessagelist()
            if messagelist:
                account = self.getCurrentAccount()
                folder = self.getCurrentFolder()
                self.loadMessagelist(messagelist, account, folder, searchOption, searchKeyword)

    def treeWidgetItemClicked(self):
        messagelist = self.getCurrentMessagelist()
        if messagelist:
            account = self.getCurrentAccount()
            folder = self.getCurrentFolder()
            if folder == "new":
                self.loadMessagelist(messagelist, account, None, unreadOnly = True)
            else:
                self.loadMessagelist(messagelist, account, folder)

    def treeWidgetItemChanged(self, item, column):
        # only for manual edits. automatic edits (setText) are ignored
        if column != 0:
            return
        # only account names of normal addresses (no chans/mailinglists)
        if (not isinstance(item, Ui_AddressWidget)) or (not self.getCurrentTreeWidget()) or self.getCurrentTreeWidget().currentItem() is None:
            return
        # not visible
        if (not self.getCurrentItem()) or (not isinstance (self.getCurrentItem(), Ui_AddressWidget)):
            return
        # only currently selected item
        if item.address != self.getCurrentAccount():
            return
        
        newLabel = str(item.text(0))
        if item.type == AccountMixin.SUBSCRIPTION:
            oldLabel = item.label
        else:
            oldLabel = shared.config.get(str(item.address), 'label')
        # unchanged, do not do anything either
        if newLabel == oldLabel:
            return

        # recursion prevention
        if self.recurDepth > 0:
            return

        self.recurDepth += 1
        item.setData(0, QtCore.Qt.EditRole, newLabel)
        item.updateText()
        if item.type == AccountMixin.MAILINGLIST:
            self.rerenderComboBoxSendFromBroadcast()
        elif item.type != AccountMixin.SUBSCRIPTION:
            self.rerenderComboBoxSendFrom()
        self.recurDepth -= 1

    def tableWidgetInboxItemClicked(self):
        folder = self.getCurrentFolder()
        messageTextedit = self.getCurrentMessageTextedit()
        if not messageTextedit:
            return
        queryreturn = []
        message = ""

        if folder == 'sent':
            ackdata = self.getCurrentMessageId()
            if ackdata and messageTextedit:
                queryreturn = sqlQuery(
                    '''select message, 1 from sent where ackdata=?''', ackdata)
        else:
            msgid = self.getCurrentMessageId()
            if msgid and messageTextedit:
                queryreturn = sqlQuery(
                    '''select message, read from inbox where msgid=?''', msgid)

        if queryreturn != []:
            refresh = False
            for row in queryreturn:
                message, read = row
                if folder != 'sent' and read == 0:
                    markread = sqlQuery(
                        '''UPDATE inbox SET read = 1 WHERE msgid = ?''', msgid)
                    refresh = True
            if refresh:
                tableWidget = self.getCurrentMessagelist()
                if not tableWidget:
                    return
                font = QFont()
                font.setBold(False)
#                inventoryHashesToMarkRead = []
                currentRow = tableWidget.currentRow()
#                inventoryHashToMarkRead = str(tableWidget.item(
#                    currentRow, 3).data(Qt.UserRole).toPyObject())
#                inventoryHashesToMarkRead.append(inventoryHashToMarkRead)
                tableWidget.item(currentRow, 0).setFont(font)
                tableWidget.item(currentRow, 0).setTextColor(AccountColor(str(tableWidget.item(currentRow, 0).data(Qt.UserRole).toPyObject())).accountColor())
                tableWidget.item(currentRow, 1).setFont(font)
                tableWidget.item(currentRow, 1).setTextColor(AccountColor(str(tableWidget.item(currentRow, 1).data(Qt.UserRole).toPyObject())).accountColor())
                tableWidget.item(currentRow, 2).setFont(font)
                tableWidget.item(currentRow, 3).setFont(font)
                self.propagateUnreadCount(str(tableWidget.item(currentRow, 1 if tableWidget == self.ui.tableWidgetInboxSubscriptions else 0).data(Qt.UserRole).toPyObject()), folder, self.getCurrentTreeWidget(), -1)

        else:
            data = self.getCurrentMessageId()
            if data != False:
                message = "Error occurred: could not load message from disk."
        message = unicode(message, 'utf-8)')
        messageTextedit.setCurrentFont(QtGui.QFont())
        messageTextedit.setTextColor(QtGui.QColor())
        messageTextedit.setPlainText(message)

    def tableWidgetAddressBookItemChanged(self):
        currentRow = self.ui.tableWidgetAddressBook.currentRow()
        if currentRow >= 0:
            addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(
                currentRow, 1).text()
            sqlExecute('''UPDATE addressbook set label=? WHERE address=?''',
                       str(self.ui.tableWidgetAddressBook.item(currentRow, 0).text().toUtf8()),
                       str(addressAtCurrentRow))
            self.ui.tableWidgetAddressBook.item(currentRow, 0).setLabel(str(self.ui.tableWidgetAddressBook.item(currentRow, 0).text().toUtf8()))
        self.rerenderInboxFromLabels()
        self.rerenderSentToLabels()

    def writeNewAddressToTable(self, label, address, streamNumber):
        self.rerenderTabTreeMessages()
        self.rerenderTabTreeSubscriptions()
        self.rerenderTabTreeChans()
        self.rerenderComboBoxSendFrom()
        self.rerenderComboBoxSendFromBroadcast()

    def updateStatusBar(self, data):
        if data != "":
            logger.info('Status bar: ' + data)

        self.statusBar().showMessage(data)

    def initSettings(self):
        QtCore.QCoreApplication.setOrganizationName("PyBitmessage")
        QtCore.QCoreApplication.setOrganizationDomain("bitmessage.org")
        QtCore.QCoreApplication.setApplicationName("pybitmessageqt")
        self.loadSettings()
        for attr, obj in self.ui.__dict__.iteritems():
            if hasattr(obj, "__class__") and isinstance(obj, settingsmixin.SettingsMixin):
                loadMethod = getattr(obj, "loadSettings", None)
                if callable (loadMethod):
                    obj.loadSettings()
       

class helpDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_helpDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.labelHelpURI.setOpenExternalLinks(True)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))
        
class connectDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_connectDialog()
        self.ui.setupUi(self)
        self.parent = parent
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
        self.ui.checkBoxWillinglySendToMobile.setChecked(
            shared.safeConfigGetBoolean('bitmessagesettings', 'willinglysendtomobile'))
        self.ui.checkBoxUseIdenticons.setChecked(
            shared.safeConfigGetBoolean('bitmessagesettings', 'useidenticons'))
        self.ui.checkBoxReplyBelow.setChecked(
            shared.safeConfigGetBoolean('bitmessagesettings', 'replybelow'))
        
        global languages 
        languages = ['system','en','eo','fr','de','es','ru','no','ar','zh_cn','ja','nl','cs','en_pirate','other']
        user_countrycode = str(shared.config.get('bitmessagesettings', 'userlocale'))
        if user_countrycode in languages:
            curr_index = languages.index(user_countrycode)
        else:
            curr_index = languages.index('other')
        self.ui.languageComboBox.setCurrentIndex(curr_index)
        
        if shared.appdata == '':
            self.ui.checkBoxPortableMode.setChecked(True)
        if 'darwin' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.checkBoxStartOnLogon.setText(_translate(
                "MainWindow", "Start-on-login not yet supported on your OS."))
            self.ui.checkBoxMinimizeToTray.setDisabled(True)
            self.ui.checkBoxMinimizeToTray.setText(_translate(
                "MainWindow", "Minimize-to-tray not yet supported on your OS."))
            self.ui.checkBoxShowTrayNotifications.setDisabled(True)
            self.ui.checkBoxShowTrayNotifications.setText(_translate(
                "MainWindow", "Tray notifications not yet supported on your OS."))
        elif 'linux' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.checkBoxStartOnLogon.setText(_translate(
                "MainWindow", "Start-on-login not yet supported on your OS."))
        # On the Network settings tab:
        self.ui.lineEditTCPPort.setText(str(
            shared.config.get('bitmessagesettings', 'port')))
        self.ui.checkBoxUPnP.setChecked(
            shared.safeConfigGetBoolean('bitmessagesettings', 'upnp'))
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
        self.ui.lineEditMaxDownloadRate.setText(str(
            shared.config.get('bitmessagesettings', 'maxdownloadrate')))
        self.ui.lineEditMaxUploadRate.setText(str(
            shared.config.get('bitmessagesettings', 'maxuploadrate')))

        # Demanded difficulty tab
        self.ui.lineEditTotalDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'defaultnoncetrialsperbyte')) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
        self.ui.lineEditSmallMessageDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes')) / shared.networkDefaultPayloadLengthExtraBytes)))

        # Max acceptable difficulty tab
        self.ui.lineEditMaxAcceptableTotalDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'maxacceptablenoncetrialsperbyte')) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)))
        self.ui.lineEditMaxAcceptableSmallMessageDifficulty.setText(str((float(shared.config.getint(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes')) / shared.networkDefaultPayloadLengthExtraBytes)))

        # OpenCL
        if openclpow.has_opencl():
            self.ui.checkBoxOpenCL.setEnabled(True)
        else:
            self.ui.checkBoxOpenCL.setEnabled(False)
        if shared.safeConfigGetBoolean("bitmessagesettings", "opencl"):
            self.ui.checkBoxOpenCL.setChecked(True)
        else:
            self.ui.checkBoxOpenCL.setChecked(False)

        # Namecoin integration tab
        nmctype = shared.config.get('bitmessagesettings', 'namecoinrpctype')
        self.ui.lineEditNamecoinHost.setText(str(
            shared.config.get('bitmessagesettings', 'namecoinrpchost')))
        self.ui.lineEditNamecoinPort.setText(str(
            shared.config.get('bitmessagesettings', 'namecoinrpcport')))
        self.ui.lineEditNamecoinUser.setText(str(
            shared.config.get('bitmessagesettings', 'namecoinrpcuser')))
        self.ui.lineEditNamecoinPassword.setText(str(
            shared.config.get('bitmessagesettings', 'namecoinrpcpassword')))

        if nmctype == "namecoind":
            self.ui.radioButtonNamecoinNamecoind.setChecked(True)
        elif nmctype == "nmcontrol":
            self.ui.radioButtonNamecoinNmcontrol.setChecked(True)
            self.ui.lineEditNamecoinUser.setEnabled(False)
            self.ui.labelNamecoinUser.setEnabled(False)
            self.ui.lineEditNamecoinPassword.setEnabled(False)
            self.ui.labelNamecoinPassword.setEnabled(False)
        else:
            assert False

        QtCore.QObject.connect(self.ui.radioButtonNamecoinNamecoind, QtCore.SIGNAL(
            "toggled(bool)"), self.namecoinTypeChanged)
        QtCore.QObject.connect(self.ui.radioButtonNamecoinNmcontrol, QtCore.SIGNAL(
            "toggled(bool)"), self.namecoinTypeChanged)
        QtCore.QObject.connect(self.ui.pushButtonNamecoinTest, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonNamecoinTest)

        #Message Resend tab
        self.ui.lineEditDays.setText(str(
            shared.config.get('bitmessagesettings', 'stopresendingafterxdays')))
        self.ui.lineEditMonths.setText(str(
            shared.config.get('bitmessagesettings', 'stopresendingafterxmonths')))
        
        
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

    # Check status of namecoin integration radio buttons and translate
    # it to a string as in the options.
    def getNamecoinType(self):
        if self.ui.radioButtonNamecoinNamecoind.isChecked():
            return "namecoind"
        if self.ui.radioButtonNamecoinNmcontrol.isChecked():
            return "nmcontrol"
        assert False

    # Namecoin connection type was changed.
    def namecoinTypeChanged(self, checked):
        nmctype = self.getNamecoinType()
        assert nmctype == "namecoind" or nmctype == "nmcontrol"
            
        isNamecoind = (nmctype == "namecoind")
        self.ui.lineEditNamecoinUser.setEnabled(isNamecoind)
        self.ui.labelNamecoinUser.setEnabled(isNamecoind)
        self.ui.lineEditNamecoinPassword.setEnabled(isNamecoind)
        self.ui.labelNamecoinPassword.setEnabled(isNamecoind)

        if isNamecoind:
            self.ui.lineEditNamecoinPort.setText(shared.namecoinDefaultRpcPort)
        else:
            self.ui.lineEditNamecoinPort.setText("9000")

    # Test the namecoin settings specified in the settings dialog.
    def click_pushButtonNamecoinTest(self):
        self.ui.labelNamecoinTestResult.setText(_translate(
                "MainWindow", "Testing..."))
        options = {}
        options["type"] = self.getNamecoinType()
        options["host"] = self.ui.lineEditNamecoinHost.text()
        options["port"] = self.ui.lineEditNamecoinPort.text()
        options["user"] = self.ui.lineEditNamecoinUser.text()
        options["password"] = self.ui.lineEditNamecoinPassword.text()
        nc = namecoinConnection(options)
        response = nc.test()
        responseStatus = response[0]
        responseText = response[1]
        self.ui.labelNamecoinTestResult.setText(responseText)
        if responseStatus== 'success':
            self.parent.ui.pushButtonFetchNamecoinID.show()


class SpecialAddressBehaviorDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SpecialAddressBehaviorDialog()
        self.ui.setupUi(self)
        self.parent = parent
        addressAtCurrentRow = parent.getCurrentAccount()
        if not shared.safeConfigGetBoolean(addressAtCurrentRow, 'chan'):
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
        else: # if addressAtCurrentRow is a chan address
            self.ui.radioButtonBehaviorMailingList.setDisabled(True)
            self.ui.lineEditMailingListName.setText(_translate(
                "MainWindow", "This is a chan address. You cannot use it as a pseudo-mailing list."))

        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))

class EmailGatewayDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_EmailGatewayDialog()
        self.ui.setupUi(self)
        self.parent = parent
        addressAtCurrentRow = parent.getCurrentAccount()
        acct = accountClass(addressAtCurrentRow)
        if isinstance(acct, GatewayAccount):
            self.ui.radioButtonUnregister.setEnabled(True)
        else:
            self.ui.radioButtonUnregister.setEnabled(False)
        label = shared.config.get(addressAtCurrentRow, 'label')
        if label.find("@mailchuck.com") > -1:
            self.ui.lineEditEmail.setText(label)

        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))


class AddAddressDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AddAddressDialog()
        self.ui.setupUi(self)
        self.parent = parent
        QtCore.QObject.connect(self.ui.lineEditAddress, QtCore.SIGNAL(
            "textChanged(QString)"), self.addressChanged)

    def addressChanged(self, QString):
        status, a, b, c = decodeAddress(str(QString))
        if status == 'missingbm':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address should start with ''BM-''"))
        elif status == 'checksumfailed':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address is not typed or copied correctly (the checksum failed)."))
        elif status == 'versiontoohigh':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The version number of this address is higher than this software can support. Please upgrade Bitmessage."))
        elif status == 'invalidcharacters':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address contains invalid characters."))
        elif status == 'ripetooshort':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too short."))
        elif status == 'ripetoolong':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too long."))
        elif status == 'varintmalformed':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is malformed."))
        elif status == 'success':
            self.ui.labelAddressCheck.setText(
                _translate("MainWindow", "Address is valid."))
            
class NewSubscriptionDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewSubscriptionDialog()
        self.ui.setupUi(self)
        self.parent = parent
        QtCore.QObject.connect(self.ui.lineEditSubscriptionAddress, QtCore.SIGNAL(
            "textChanged(QString)"), self.addressChanged)
        self.ui.checkBoxDisplayMessagesAlreadyInInventory.setText(
            _translate("MainWindow", "Enter an address above."))

    def addressChanged(self, QString):
        self.ui.checkBoxDisplayMessagesAlreadyInInventory.setEnabled(False)
        self.ui.checkBoxDisplayMessagesAlreadyInInventory.setChecked(False)
        status, addressVersion, streamNumber, ripe = decodeAddress(str(QString))
        if status == 'missingbm':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address should start with ''BM-''"))
        elif status == 'checksumfailed':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address is not typed or copied correctly (the checksum failed)."))
        elif status == 'versiontoohigh':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The version number of this address is higher than this software can support. Please upgrade Bitmessage."))
        elif status == 'invalidcharacters':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "The address contains invalid characters."))
        elif status == 'ripetooshort':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too short."))
        elif status == 'ripetoolong':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is too long."))
        elif status == 'varintmalformed':
            self.ui.labelAddressCheck.setText(_translate(
                "MainWindow", "Some data encoded in the address is malformed."))
        elif status == 'success':
            self.ui.labelAddressCheck.setText(
                _translate("MainWindow", "Address is valid."))
            if addressVersion <= 3:
                self.ui.checkBoxDisplayMessagesAlreadyInInventory.setText(
                    _translate("MainWindow", "Address is an old type. We cannot display its past broadcasts."))
            else:
                shared.flushInventory()
                doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                    addressVersion) + encodeVarint(streamNumber) + ripe).digest()).digest()
                tag = doubleHashOfAddressData[32:]
                queryreturn = sqlQuery(
                    '''select hash from inventory where objecttype=3 and tag=?''', tag)
                if len(queryreturn) == 0:
                    self.ui.checkBoxDisplayMessagesAlreadyInInventory.setText(
                        _translate("MainWindow", "There are no recent broadcasts from this address to display."))
                elif len(queryreturn) == 1:
                    self.ui.checkBoxDisplayMessagesAlreadyInInventory.setEnabled(True)
                    self.ui.checkBoxDisplayMessagesAlreadyInInventory.setText(
                        _translate("MainWindow", "Display the %1 recent broadcast from this address.").arg(str(len(queryreturn))))
                else:
                    self.ui.checkBoxDisplayMessagesAlreadyInInventory.setEnabled(True)
                    self.ui.checkBoxDisplayMessagesAlreadyInInventory.setText(
                        _translate("MainWindow", "Display the %1 recent broadcasts from this address.").arg(str(len(queryreturn))))


class NewAddressDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewAddressDialog()
        self.ui.setupUi(self)
        self.parent = parent
        row = 1
        # Let's fill out the 'existing address' combo box with addresses from
        # the 'Your Identities' tab.
        for addressInKeysFile in getSortedAccounts():
            self.ui.radioButtonExisting.click()
            self.ui.comboBoxExisting.addItem(
                addressInKeysFile)
            row += 1
        self.ui.groupBoxDeterministic.setHidden(True)
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))

class newChanDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_newChanDialog()
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

class UISignaler(QThread):

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        while True:
            command, data = shared.UISignalQueue.get()
            if command == 'writeNewAddressToTable':
                label, address, streamNumber = data
                self.emit(SIGNAL(
                    "writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), label, address, str(streamNumber))
            elif command == 'updateStatusBar':
                self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"), data)
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
                self.emit(SIGNAL("updateNetworkStatusTab()"))
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
            elif command == 'rerenderInboxFromLabels':
                self.emit(SIGNAL("rerenderInboxFromLabels()"))
            elif command == 'rerenderSentToLabels':
                self.emit(SIGNAL("rerenderSentToLabels()"))
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
                self.emit(SIGNAL("displayAlert(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), title, text, exitAfterUserClicksOk)
            else:
                sys.stderr.write(
                    'Command sent to UISignaler not recognized: %s\n' % command)


app = None
myapp = None

class MySingleApplication(QApplication):
    """
    Listener to allow our Qt form to get focus when another instance of the
    application is open.

    Based off this nice reimplmentation of MySingleApplication:
    http://stackoverflow.com/a/12712362/2679626
    """

    # Unique identifier for this application
    uuid = '6ec0149b-96e1-4be1-93ab-1465fb3ebf7c'

    def __init__(self, *argv):
        super(MySingleApplication, self).__init__(*argv)
        id = MySingleApplication.uuid

        self.server = None
        self.is_running = False

        socket = QLocalSocket()
        socket.connectToServer(id)
        self.is_running = socket.waitForConnected()

        # Cleanup past crashed servers
        if not self.is_running:
            if socket.error() == QLocalSocket.ConnectionRefusedError:
                socket.disconnectFromServer()
                QLocalServer.removeServer(id)

        socket.abort()

        # Checks if there's an instance of the local server id running
        if self.is_running:
            # This should be ignored, singleton.py will take care of exiting me.
            pass
        else:
            # Nope, create a local server with this id and assign on_new_connection
            # for whenever a second instance tries to run focus the application.
            self.server = QLocalServer()
            self.server.listen(id)
            self.server.newConnection.connect(self.on_new_connection)

    def __del__(self):
        if self.server:
            self.server.close()

    def on_new_connection(self):
        global myapp
        if myapp:
            myapp.appIndicatorShow()

def init():
    global app
    if not app:
        app = MySingleApplication(sys.argv)
    return app

def run():
    global myapp
    app = init()
    change_translation(l10n.getTranslationLanguage())
    app.setStyleSheet("QStatusBar::item { border: 0px solid black }")
    myapp = MyForm()

    myapp.appIndicatorInit(app)
    myapp.ubuntuMessagingMenuInit()
    myapp.notifierInit()
    if shared.safeConfigGetBoolean('bitmessagesettings', 'dontconnect'):
        myapp.showConnectDialog() # ask the user if we may connect
    
#    try:
#        if shared.config.get('bitmessagesettings', 'mailchuck') < 1:
#            myapp.showMigrationWizard(shared.config.get('bitmessagesettings', 'mailchuck'))
#    except:
#        myapp.showMigrationWizard(0)
    
    # only show after wizards and connect dialogs have completed
    if not shared.config.getboolean('bitmessagesettings', 'startintray'):
        myapp.show()

    sys.exit(app.exec_())
