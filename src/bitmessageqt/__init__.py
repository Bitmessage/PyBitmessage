"""
PyQt based UI for bitmessage, the main module
"""

import hashlib
import locale
import os
import random
import string
import subprocess
import sys
import textwrap
import threading
import time
from datetime import datetime, timedelta
from sqlite3 import register_adapter

from PyQt4 import QtCore, QtGui
from PyQt4.QtNetwork import QLocalSocket, QLocalServer

import shared
import state
from debug import logger
from tr import _translate
from addresses import decodeAddress, addBMIfNotPresent
from bitmessageui import Ui_MainWindow
from bmconfigparser import BMConfigParser
import namecoin
from messageview import MessageView
from migrationwizard import Ui_MigrationWizard
from foldertree import (
    AccountMixin, Ui_FolderWidget, Ui_AddressWidget, Ui_SubscriptionWidget,
    MessageList_AddressWidget, MessageList_SubjectWidget,
    Ui_AddressBookWidgetItemLabel, Ui_AddressBookWidgetItemAddress,
    MessageList_TimeWidget)
import settingsmixin
import support
from helper_sql import sqlQuery, sqlExecute, sqlExecuteChunked, sqlStoredProcedure
import helper_search
import l10n
from utils import str_broadcast_subscribers, avatarize
from account import (
    getSortedAccounts, getSortedSubscriptions, accountClass, BMAccount,
    GatewayAccount, MailchuckAccount, AccountColor)
import dialogs
from network.stats import pendingDownload, pendingUpload
from uisignaler import UISignaler
import paths
from proofofwork import getPowType
import queues
import shutdown
from statusbar import BMStatusBar
import sound
# This is needed for tray icon
import bitmessage_icons_rc  # noqa:F401 pylint: disable=unused-import
import helper_sent

try:
    from plugins.plugin import get_plugin, get_plugins
except ImportError:
    get_plugins = False


# TODO: rewrite
def powQueueSize():
    """Returns the size of queues.workerQueue including current unfinished work"""
    queue_len = queues.workerQueue.qsize()
    for thread in threading.enumerate():
        try:
            if thread.name == "singleWorker":
                queue_len += thread.busy
        except Exception as err:
            logger.info('Thread error %s', err)
    return queue_len


def openKeysFile():
    """Open keys file with an external editor"""
    keysfile = os.path.join(state.appdata, 'keys.dat')
    if 'linux' in sys.platform:
        subprocess.call(["xdg-open", keysfile])
    elif sys.platform.startswith('win'):
        os.startfile(keysfile)  # pylint: disable=no-member


class MyForm(settingsmixin.SMainWindow):

    # the maximum frequency of message sounds in seconds
    maxSoundFrequencySec = 60

    REPLY_TYPE_SENDER = 0
    REPLY_TYPE_CHAN = 1
    REPLY_TYPE_UPD = 2

    def change_translation(self, newlocale=None):
        """Change translation language for the application"""
        if newlocale is None:
            newlocale = l10n.getTranslationLanguage()
        try:
            if not self.qmytranslator.isEmpty():
                QtGui.QApplication.removeTranslator(self.qmytranslator)
        except:
            pass
        try:
            if not self.qsystranslator.isEmpty():
                QtGui.QApplication.removeTranslator(self.qsystranslator)
        except:
            pass

        self.qmytranslator = QtCore.QTranslator()
        translationpath = os.path.join(
            paths.codePath(), 'translations', 'bitmessage_' + newlocale)
        self.qmytranslator.load(translationpath)
        QtGui.QApplication.installTranslator(self.qmytranslator)

        self.qsystranslator = QtCore.QTranslator()
        if paths.frozen:
            translationpath = os.path.join(
                paths.codePath(), 'translations', 'qt_' + newlocale)
        else:
            translationpath = os.path.join(
                str(QtCore.QLibraryInfo.location(
                    QtCore.QLibraryInfo.TranslationsPath)), 'qt_' + newlocale)
        self.qsystranslator.load(translationpath)
        QtGui.QApplication.installTranslator(self.qsystranslator)

        lang = locale.normalize(l10n.getTranslationLanguage())
        langs = [
            lang.split(".")[0] + "." + l10n.encoding,
            lang.split(".")[0] + "." + 'UTF-8',
            lang
        ]
        if 'win32' in sys.platform or 'win64' in sys.platform:
            langs = [l10n.getWindowsLocale(lang)]
        for lang in langs:
            try:
                l10n.setlocale(locale.LC_ALL, lang)
                if 'win32' not in sys.platform and 'win64' not in sys.platform:
                    l10n.encoding = locale.nl_langinfo(locale.CODESET)
                else:
                    l10n.encoding = locale.getlocale()[1]
                logger.info("Successfully set locale to %s", lang)
                break
            except:
                logger.error("Failed to set locale to %s", lang, exc_info=True)

    def init_file_menu(self):
        QtCore.QObject.connect(self.ui.actionExit, QtCore.SIGNAL(
            "triggered()"), self.quit)
        QtCore.QObject.connect(self.ui.actionNetworkSwitch, QtCore.SIGNAL(
            "triggered()"), self.network_switch)
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
        QtCore.QObject.connect(self.ui.pushButtonTTL, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonTTL)
        QtCore.QObject.connect(self.ui.pushButtonClear, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonClear)
        QtCore.QObject.connect(self.ui.pushButtonSend, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonSend)
        QtCore.QObject.connect(self.ui.pushButtonFetchNamecoinID, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonFetchNamecoinID)
        QtCore.QObject.connect(self.ui.actionSettings, QtCore.SIGNAL(
            "triggered()"), self.click_actionSettings)
        QtCore.QObject.connect(self.ui.actionAbout, QtCore.SIGNAL(
            "triggered()"), self.click_actionAbout)
        QtCore.QObject.connect(self.ui.actionSupport, QtCore.SIGNAL(
            "triggered()"), self.click_actionSupport)
        QtCore.QObject.connect(self.ui.actionHelp, QtCore.SIGNAL(
            "triggered()"), self.click_actionHelp)

    def init_inbox_popup_menu(self, connectSignal=True):
        # Popup menu for the Inbox tab
        self.ui.inboxContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionReply = self.ui.inboxContextMenuToolbar.addAction(_translate(
            "MainWindow", "Reply to sender"), self.on_action_InboxReply)
        self.actionReplyChan = self.ui.inboxContextMenuToolbar.addAction(_translate(
            "MainWindow", "Reply to channel"), self.on_action_InboxReplyChan)
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
        self.actionMarkAllRead = self.ui.addressContextMenuToolbarYourIdentities.addAction(
            _translate(
                "MainWindow", "Mark all messages as read"),
            self.on_action_MarkAllRead)

        self.ui.treeWidgetYourIdentities.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.treeWidgetYourIdentities, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                self.on_context_menuYourIdentities)

        # load all gui.menu plugins with prefix 'address'
        self.menu_plugins = {'address': []}
        if not get_plugins:
            return
        for plugin in get_plugins('gui.menu', 'address'):
            try:
                handler, title = plugin(self)
            except TypeError:
                continue
            self.menu_plugins['address'].append(
                self.ui.addressContextMenuToolbarYourIdentities.addAction(
                    title, handler
                ))

    def init_chan_popup_menu(self, connectSignal=True):
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
        self.actionSend = self.ui.addressContextMenuToolbar.addAction(
            _translate("MainWindow", "Send message to this chan"),
            self.on_action_Send)
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
        self.actionAddressBookSetSound = \
            self.ui.addressBookContextMenuToolbar.addAction(
                _translate("MainWindow", "Set notification sound..."),
                self.on_action_AddressBookSetSound)
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
        self.actionsubscriptionsSend = self.ui.addressContextMenuToolbar.addAction(
            _translate("MainWindow", "Send message to this address"),
            self.on_action_Send)
        self.ui.treeWidgetSubscriptions.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.ui.treeWidgetSubscriptions, QtCore.SIGNAL(
                'customContextMenuRequested(const QPoint&)'),
                self.on_context_menuSubscriptions)

    def init_sent_popup_menu(self, connectSignal=True):
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
        self.actionSentReply = self.ui.sentContextMenuToolbar.addAction(
            _translate("MainWindow", "Send update"),
            self.on_action_SentReply)
        # self.popMenuSent = QtGui.QMenu( self )
        # self.popMenuSent.addAction( self.actionSentClipboard )
        # self.popMenuSent.addAction( self.actionTrashSentMessage )

    def rerenderTabTreeSubscriptions(self):
        treeWidget = self.ui.treeWidgetSubscriptions
        folders = Ui_FolderWidget.folderWeight.keys()
        folders.remove("new")

        # sort ascending when creating
        if treeWidget.topLevelItemCount() == 0:
            treeWidget.header().setSortIndicator(
                0, QtCore.Qt.AscendingOrder)
        # init dictionary

        db = getSortedSubscriptions(True)
        for address in db:
            for folder in folders:
                if folder not in db[address]:
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

            if toAddress not in db:
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
            treeWidget.header().setSortIndicator(
                0, QtCore.Qt.AscendingOrder)
        # init dictionary
        db = {}
        enabled = {}

        for toAddress in getSortedAccounts():
            isEnabled = BMConfigParser().getboolean(
                toAddress, 'enabled')
            isChan = BMConfigParser().safeGetBoolean(
                toAddress, 'chan')
            isMaillinglist = BMConfigParser().safeGetBoolean(
                toAddress, 'mailinglist')

            if treeWidget == self.ui.treeWidgetYourIdentities:
                if isChan:
                    continue
            elif treeWidget == self.ui.treeWidgetChans:
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
        if treeWidget == self.ui.treeWidgetYourIdentities:
            db[None] = {}
            db[None]["inbox"] = total
            db[None]["new"] = total
            db[None]["sent"] = 0
            db[None]["trash"] = 0
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

            if toAddress not in db:
                treeWidget.takeTopLevelItem(i)
                # no increment
                continue
            unread = 0
            j = 0
            while j < widget.childCount():
                subwidget = widget.child(j)
                try:
                    subwidget.setUnreadCount(
                        db[toAddress][subwidget.folderName])
                    if subwidget.folderName not in ("new", "trash", "sent"):
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
                    if toAddress is not None and tab == 'messages' and folder == "new":
                        continue
                    subwidget = Ui_FolderWidget(widget, j, toAddress, f, c)
                    if subwidget.folderName not in ("new", "trash", "sent"):
                        unread += c
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
                if toAddress is not None and tab == 'messages' and folder == "new":
                    continue
                subwidget = Ui_FolderWidget(widget, j, toAddress, folder, db[toAddress][folder])
                if subwidget.folderName not in ("new", "trash", "sent"):
                    unread += db[toAddress][folder]
                j += 1
            widget.setUnreadCount(unread)
            i += 1

        treeWidget.setSortingEnabled(True)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.qmytranslator = self.qsystranslator = None
        self.indicatorUpdate = None
        self.actionStatus = None

        # the last time that a message arrival sound was played
        self.lastSoundTime = datetime.now() - timedelta(days=1)

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
                    BMConfigParser().remove_section(addressInKeysFile)
                    BMConfigParser().save()

        self.updateStartOnLogon()

        self.change_translation()

        # e.g. for editing labels
        self.recurDepth = 0

        # switch back to this when replying
        self.replyFromTab = None

        # so that quit won't loop
        self.wait = self.quitAccepted = False

        self.init_file_menu()
        self.init_inbox_popup_menu()
        self.init_identities_popup_menu()
        self.init_addressbook_popup_menu()
        self.init_subscriptions_popup_menu()
        self.init_chan_popup_menu()
        self.init_sent_popup_menu()

        # Initialize the user's list of addresses on the 'Chan' tab.
        self.rerenderTabTreeChans()

        # Initialize the user's list of addresses on the 'Messages' tab.
        self.rerenderTabTreeMessages()

        # Set welcome message
        self.ui.textEditInboxMessage.setText(_translate("MainWindow", """
        Welcome to easy and secure Bitmessage
            * send messages to other people
            * send broadcast messages like twitter or
            * discuss in chan(nel)s with other people
        """))

        # Initialize the address book
        self.rerenderAddressBook()

        # Initialize the Subscriptions
        self.rerenderSubscriptions()

        # Initialize the inbox search
        QtCore.QObject.connect(self.ui.inboxSearchLineEdit, QtCore.SIGNAL(
            "returnPressed()"), self.inboxSearchLineEditReturnPressed)
        QtCore.QObject.connect(self.ui.inboxSearchLineEditSubscriptions, QtCore.SIGNAL(
            "returnPressed()"), self.inboxSearchLineEditReturnPressed)
        QtCore.QObject.connect(self.ui.inboxSearchLineEditChans, QtCore.SIGNAL(
            "returnPressed()"), self.inboxSearchLineEditReturnPressed)
        QtCore.QObject.connect(self.ui.inboxSearchLineEdit, QtCore.SIGNAL(
            "textChanged(QString)"), self.inboxSearchLineEditUpdated)
        QtCore.QObject.connect(self.ui.inboxSearchLineEditSubscriptions, QtCore.SIGNAL(
            "textChanged(QString)"), self.inboxSearchLineEditUpdated)
        QtCore.QObject.connect(self.ui.inboxSearchLineEditChans, QtCore.SIGNAL(
            "textChanged(QString)"), self.inboxSearchLineEditUpdated)

        # Initialize addressbook
        QtCore.QObject.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL(
            "itemChanged(QTableWidgetItem *)"), self.tableWidgetAddressBookItemChanged)
        # This is necessary for the completer to work if multiple recipients
        QtCore.QObject.connect(self.ui.lineEditTo, QtCore.SIGNAL(
            "cursorPositionChanged(int, int)"), self.ui.lineEditTo.completer().onCursorPositionChanged)

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
        QtCore.QObject.connect(
            self.ui.tabWidget, QtCore.SIGNAL("currentChanged(int)"),
            self.tabWidgetCurrentChanged
        )

        # Put the colored icon on the status bar
        # self.pushButtonStatusIcon.setIcon(QIcon(":/newPrefix/images/yellowicon.png"))
        self.setStatusBar(BMStatusBar())
        self.statusbar = self.statusBar()

        self.pushButtonStatusIcon = QtGui.QPushButton(self)
        self.pushButtonStatusIcon.setText('')
        self.pushButtonStatusIcon.setIcon(
            QtGui.QIcon(':/newPrefix/images/redicon.png'))
        self.pushButtonStatusIcon.setFlat(True)
        self.statusbar.insertPermanentWidget(0, self.pushButtonStatusIcon)
        QtCore.QObject.connect(self.pushButtonStatusIcon, QtCore.SIGNAL(
            "clicked()"), self.click_pushButtonStatusIcon)

        self.unreadCount = 0

        # Set the icon sizes for the identicons
        identicon_size = 3*7
        self.ui.tableWidgetInbox.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.treeWidgetChans.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.treeWidgetYourIdentities.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.treeWidgetSubscriptions.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        self.ui.tableWidgetAddressBook.setIconSize(QtCore.QSize(identicon_size, identicon_size))
        
        self.UISignalThread = UISignaler.get()
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
            "setStatusIcon(PyQt_PyObject)"), self.setStatusIcon)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "changedInboxUnread(PyQt_PyObject)"), self.changedInboxUnread)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderMessagelistFromLabels()"), self.rerenderMessagelistFromLabels)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderMessgelistToLabels()"), self.rerenderMessagelistToLabels)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderAddressBook()"), self.rerenderAddressBook)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderSubscriptions()"), self.rerenderSubscriptions)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "removeInboxRowByMsgid(PyQt_PyObject)"), self.removeInboxRowByMsgid)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "newVersionAvailable(PyQt_PyObject)"), self.newVersionAvailable)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "displayAlert(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayAlert)
        self.UISignalThread.start()

        # Key press in tree view
        self.ui.treeWidgetYourIdentities.keyPressEvent = self.treeWidgetKeyPressEvent
        self.ui.treeWidgetSubscriptions.keyPressEvent = self.treeWidgetKeyPressEvent
        self.ui.treeWidgetChans.keyPressEvent = self.treeWidgetKeyPressEvent

        # Key press in addressbook
        self.ui.tableWidgetAddressBook.keyPressEvent = self.addressbookKeyPressEvent

        # Key press in messagelist
        self.ui.tableWidgetInbox.keyPressEvent = self.tableWidgetKeyPressEvent
        self.ui.tableWidgetInboxSubscriptions.keyPressEvent = self.tableWidgetKeyPressEvent
        self.ui.tableWidgetInboxChans.keyPressEvent = self.tableWidgetKeyPressEvent

        # Key press in messageview
        self.ui.textEditInboxMessage.keyPressEvent = self.textEditKeyPressEvent
        self.ui.textEditInboxMessageSubscriptions.keyPressEvent = self.textEditKeyPressEvent
        self.ui.textEditInboxMessageChans.keyPressEvent = self.textEditKeyPressEvent

        # Below this point, it would be good if all of the necessary global data
        # structures were initialized.

        self.rerenderComboBoxSendFrom()
        self.rerenderComboBoxSendFromBroadcast()

        # Put the TTL slider in the correct spot
        TTL = BMConfigParser().getint('bitmessagesettings', 'ttl')
        if TTL < 3600: # an hour
            TTL = 3600
        elif TTL > 28*24*60*60: # 28 days
            TTL = 28*24*60*60
        self.ui.horizontalSliderTTL.setSliderPosition((TTL - 3600) ** (1/3.199))
        self.updateHumanFriendlyTTLDescription(TTL)
        
        QtCore.QObject.connect(self.ui.horizontalSliderTTL, QtCore.SIGNAL(
            "valueChanged(int)"), self.updateTTL)

        self.initSettings()
        self.resetNamecoinConnection()
        self.sqlInit()
        self.indicatorInit()
        self.notifierInit()

        self.ui.updateNetworkSwitchMenuLabel()

        self._firstrun = BMConfigParser().safeGetBoolean(
            'bitmessagesettings', 'dontconnect')

        self._contact_selected = None

    def getContactSelected(self):
        """Returns last selected contact once"""
        try:
            return self._contact_selected
        except AttributeError:
            pass
        finally:
            self._contact_selected = None

    def updateStartOnLogon(self):
        # Configure Bitmessage to start on startup (or remove the
        # configuration) based on the setting in the keys.dat file
        if 'win32' in sys.platform or 'win64' in sys.platform:
            # Auto-startup for Windows
            RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            self.settings = QtCore.QSettings(
                RUN_PATH, QtCore.QSettings.NativeFormat)
            # In case the user moves the program and the registry entry is
            # no longer valid, this will delete the old registry entry.
            self.settings.remove("PyBitmessage")
            if BMConfigParser().getboolean(
                    'bitmessagesettings', 'startonlogon'
            ):
                self.settings.setValue("PyBitmessage", sys.argv[0])
        elif 'darwin' in sys.platform:
            # startup for mac
            pass
        elif 'linux' in sys.platform:
            # startup for linux
            pass

    def updateTTL(self, sliderPosition):
        TTL = int(sliderPosition ** 3.199 + 3600)
        self.updateHumanFriendlyTTLDescription(TTL)
        BMConfigParser().set('bitmessagesettings', 'ttl', str(TTL))
        BMConfigParser().save()

    def updateHumanFriendlyTTLDescription(self, TTL):
        numberOfHours = int(round(TTL / (60*60)))
        font = QtGui.QFont()
        stylesheet = ""

        if numberOfHours < 48:
            self.ui.labelHumanFriendlyTTLDescription.setText(
                _translate("MainWindow", "%n hour(s)", None, QtCore.QCoreApplication.CodecForTr, numberOfHours) +
                ", " +
                _translate("MainWindow", "not recommended for chans", None, QtCore.QCoreApplication.CodecForTr)
                )
            stylesheet = "QLabel { color : red; }"
            font.setBold(True)
        else:
            numberOfDays = int(round(TTL / (24*60*60)))
            self.ui.labelHumanFriendlyTTLDescription.setText(_translate("MainWindow", "%n day(s)", None, QtCore.QCoreApplication.CodecForTr, numberOfDays))
            font.setBold(False)
        self.ui.labelHumanFriendlyTTLDescription.setStyleSheet(stylesheet)
        self.ui.labelHumanFriendlyTTLDescription.setFont(font)

    # Show or hide the application window after clicking an item within the
    # tray icon or, on Windows, the try icon itself.
    def appIndicatorShowOrHideWindow(self):
        if not self.actionShow.isChecked():
            self.hide()
        else:
            self.show()
            self.setWindowState(
                self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.raise_()
            self.activateWindow()

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

    def appIndicatorSwitchQuietMode(self):
        BMConfigParser().set(
            'bitmessagesettings', 'showtraynotifications',
            str(not self.actionQuiet.isChecked())
        )

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
    def appIndicatorInbox(self, item=None):
        self.appIndicatorShow()
        # select inbox
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.inbox)
        )
        self.ui.treeWidgetYourIdentities.setCurrentItem(
            self.ui.treeWidgetYourIdentities.topLevelItem(0).child(0)
        )

        if item:
            self.ui.tableWidgetInbox.setCurrentItem(item)
            self.tableWidgetInboxItemClicked()
        else:
            self.ui.tableWidgetInbox.setCurrentCell(0, 0)

    # Show the program window and select send tab
    def appIndicatorSend(self):
        self.appIndicatorShow()
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.send)
        )

    # Show the program window and select subscriptions tab
    def appIndicatorSubscribe(self):
        self.appIndicatorShow()
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.subscriptions)
        )

    # Show the program window and select channels tab
    def appIndicatorChannel(self):
        self.appIndicatorShow()
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.chans)
        )

    def updateUnreadStatus(self, widget, row, msgid, unread=True):
        """
        Switch unread for item of msgid and related items in
        other STableWidgets "All Accounts" and "Chans"
        """
        status = widget.item(row, 0).unread
        if status != unread:
            return

        widgets = [self.ui.tableWidgetInbox, self.ui.tableWidgetInboxChans]
        rrow = None
        try:
            widgets.remove(widget)
            related = widgets.pop()
        except ValueError:
            pass
        else:
            # maybe use instead:
            # rrow = related.row(msgid), msgid should be QTableWidgetItem
            # related = related.findItems(msgid, QtCore.Qt.MatchExactly),
            # returns an empty list
            for rrow in range(related.rowCount()):
                if related.item(rrow, 3).data() == msgid:
                    break

        for col in range(widget.columnCount()):
            widget.item(row, col).setUnread(not status)
            if rrow:
                related.item(rrow, col).setUnread(not status)

    # Here we need to update unread count for:
    # - all widgets if there is no args
    # - All accounts
    # - corresponding account if current is "All accounts"
    # - current account otherwise
    def propagateUnreadCount(self, folder=None, widget=None):
        queryReturn = sqlQuery(
            'SELECT toaddress, folder, COUNT(msgid) AS cnt'
            ' FROM inbox WHERE read = 0 GROUP BY toaddress, folder')
        totalUnread = {}
        normalUnread = {}
        broadcastsUnread = {}
        for addr, fld, count in queryReturn:
            try:
                normalUnread[addr][fld] = count
            except KeyError:
                normalUnread[addr] = {fld: count}
            try:
                totalUnread[fld] += count
            except KeyError:
                totalUnread[fld] = count
        if widget in (
                self.ui.treeWidgetSubscriptions, self.ui.treeWidgetChans):
            widgets = (self.ui.treeWidgetYourIdentities,)
        else:
            widgets = (
                self.ui.treeWidgetYourIdentities,
                self.ui.treeWidgetSubscriptions, self.ui.treeWidgetChans
            )
            queryReturn = sqlQuery(
                'SELECT fromaddress, folder, COUNT(msgid) AS cnt'
                ' FROM inbox WHERE read = 0 AND toaddress = ?'
                ' GROUP BY fromaddress, folder', str_broadcast_subscribers)
            for addr, fld, count in queryReturn:
                try:
                    broadcastsUnread[addr][fld] = count
                except KeyError:
                    broadcastsUnread[addr] = {fld: count}

        for treeWidget in widgets:
            root = treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                addressItem = root.child(i)
                if addressItem.type == AccountMixin.ALL:
                    newCount = sum(totalUnread.itervalues())
                    self.drawTrayIcon(self.currentTrayIconFileName, newCount)
                else:
                    try:
                        newCount = sum((
                            broadcastsUnread
                            if addressItem.type == AccountMixin.SUBSCRIPTION
                            else normalUnread
                        )[addressItem.address].itervalues())
                    except KeyError:
                        newCount = 0
                if newCount != addressItem.unreadCount:
                    addressItem.setUnreadCount(newCount)
                for j in range(addressItem.childCount()):
                    folderItem = addressItem.child(j)
                    folderName = folderItem.folderName
                    if folderName == "new":
                        folderName = "inbox"
                    if folder and folderName != folder:
                        continue
                    if addressItem.type == AccountMixin.ALL:
                        newCount = totalUnread.get(folderName, 0)
                    else:
                        try:
                            newCount = (
                                broadcastsUnread
                                if addressItem.type == AccountMixin.SUBSCRIPTION
                                else normalUnread
                            )[addressItem.address][folderName]
                        except KeyError:
                            newCount = 0
                    if newCount != folderItem.unreadCount:
                        folderItem.setUnreadCount(newCount)

    def addMessageListItem(self, tableWidget, items):
        sortingEnabled = tableWidget.isSortingEnabled()
        if sortingEnabled:
            tableWidget.setSortingEnabled(False)
        tableWidget.insertRow(0)
        for i, item in enumerate(items):
            tableWidget.setItem(0, i, item)
        if sortingEnabled:
            tableWidget.setSortingEnabled(True)

    def addMessageListItemSent(
        self, tableWidget, toAddress, fromAddress, subject,
        status, ackdata, lastactiontime
    ):
        acct = accountClass(fromAddress) or BMAccount(fromAddress)
        acct.parseMessage(toAddress, fromAddress, subject, "")

        if status == 'awaitingpubkey':
            statusText = _translate(
                "MainWindow",
                "Waiting for their encryption key. Will request it again soon."
            )
        elif status == 'doingpowforpubkey':
            statusText = _translate(
                "MainWindow", "Doing work necessary to request encryption key."
            )
        elif status == 'msgqueued':
            statusText = _translate("MainWindow", "Queued.")
        elif status == 'msgsent':
            statusText = _translate(
                "MainWindow",
                "Message sent. Waiting for acknowledgement. Sent at %1"
            ).arg(l10n.formatTimestamp(lastactiontime))
        elif status == 'msgsentnoackexpected':
            statusText = _translate(
                "MainWindow", "Message sent. Sent at %1"
            ).arg(l10n.formatTimestamp(lastactiontime))
        elif status == 'doingmsgpow':
            statusText = _translate(
                "MainWindow", "Doing work necessary to send message.")
        elif status == 'ackreceived':
            statusText = _translate(
                "MainWindow",
                "Acknowledgement of the message received %1"
            ).arg(l10n.formatTimestamp(lastactiontime))
        elif status == 'broadcastqueued':
            statusText = _translate(
                "MainWindow", "Broadcast queued.")
        elif status == 'doingbroadcastpow':
            statusText = _translate(
                "MainWindow", "Doing work necessary to send broadcast.")
        elif status == 'broadcastsent':
            statusText = _translate("MainWindow", "Broadcast on %1").arg(
                l10n.formatTimestamp(lastactiontime))
        elif status == 'toodifficult':
            statusText = _translate(
                "MainWindow",
                "Problem: The work demanded by the recipient is more"
                " difficult than you are willing to do. %1"
            ).arg(l10n.formatTimestamp(lastactiontime))
        elif status == 'badkey':
            statusText = _translate(
                "MainWindow",
                "Problem: The recipient\'s encryption key is no good."
                " Could not encrypt message. %1"
            ).arg(l10n.formatTimestamp(lastactiontime))
        elif status == 'forcepow':
            statusText = _translate(
                "MainWindow",
                "Forced difficulty override. Send should start soon.")
        else:
            statusText = _translate(
                "MainWindow", "Unknown status: %1 %2").arg(status).arg(
                l10n.formatTimestamp(lastactiontime))

        items = [
            MessageList_AddressWidget(
                toAddress, unicode(acct.toLabel, 'utf-8')),
            MessageList_AddressWidget(
                fromAddress, unicode(acct.fromLabel, 'utf-8')),
            MessageList_SubjectWidget(
                str(subject), unicode(acct.subject, 'utf-8', 'replace')),
            MessageList_TimeWidget(
                statusText, False, lastactiontime, ackdata)]
        self.addMessageListItem(tableWidget, items)

        return acct

    def addMessageListItemInbox(
        self, tableWidget, toAddress, fromAddress, subject,
        msgid, received, read
    ):
        if toAddress == str_broadcast_subscribers:
            acct = accountClass(fromAddress)
        else:
            acct = accountClass(toAddress) or accountClass(fromAddress)
        if acct is None:
            acct = BMAccount(fromAddress)
        acct.parseMessage(toAddress, fromAddress, subject, "")

        items = [
            MessageList_AddressWidget(
                toAddress, unicode(acct.toLabel, 'utf-8'), not read),
            MessageList_AddressWidget(
                fromAddress, unicode(acct.fromLabel, 'utf-8'), not read),
            MessageList_SubjectWidget(
                str(subject), unicode(acct.subject, 'utf-8', 'replace'),
                not read),
            MessageList_TimeWidget(
                l10n.formatTimestamp(received), not read, received, msgid)
        ]
        self.addMessageListItem(tableWidget, items)

        return acct

    # Load Sent items from database
    def loadSent(self, tableWidget, account, where="", what=""):
        if tableWidget == self.ui.tableWidgetInboxSubscriptions:
            tableWidget.setColumnHidden(0, True)
            tableWidget.setColumnHidden(1, False)
            xAddress = 'toaddress'
        elif tableWidget == self.ui.tableWidgetInboxChans:
            tableWidget.setColumnHidden(0, False)
            tableWidget.setColumnHidden(1, True)
            xAddress = 'both'
        else:
            tableWidget.setColumnHidden(0, False)
            tableWidget.setColumnHidden(1, bool(account))
            xAddress = 'fromaddress'

        queryreturn = helper_search.search_sql(
            xAddress, account, "sent", where, what, False)

        for row in queryreturn:
            self.addMessageListItemSent(tableWidget, *row)

        tableWidget.horizontalHeader().setSortIndicator(
            3, QtCore.Qt.DescendingOrder)
        tableWidget.setSortingEnabled(True)
        tableWidget.horizontalHeaderItem(3).setText(
            _translate("MainWindow", "Sent"))
        tableWidget.setUpdatesEnabled(True)

    # Load messages from database file
    def loadMessagelist(
        self, tableWidget, account, folder="inbox", where="", what="",
        unreadOnly=False
    ):
        tableWidget.setUpdatesEnabled(False)
        tableWidget.setSortingEnabled(False)
        tableWidget.setRowCount(0)

        if folder == 'sent':
            self.loadSent(tableWidget, account, where, what)
            return

        if tableWidget == self.ui.tableWidgetInboxSubscriptions:
            xAddress = "fromaddress"
            if not what:
                where = _translate("MainWindow", "To")
                what = str_broadcast_subscribers
        else:
            xAddress = "toaddress"
        if account is not None:
            tableWidget.setColumnHidden(0, True)
            tableWidget.setColumnHidden(1, False)
        else:
            tableWidget.setColumnHidden(0, False)
            tableWidget.setColumnHidden(1, False)

        queryreturn = helper_search.search_sql(
            xAddress, account, folder, where, what, unreadOnly)

        for row in queryreturn:
            toAddress, fromAddress, subject, _, msgid, received, read = row
            self.addMessageListItemInbox(
                tableWidget, toAddress, fromAddress, subject,
                msgid, received, read)

        tableWidget.horizontalHeader().setSortIndicator(
            3, QtCore.Qt.DescendingOrder)
        tableWidget.setSortingEnabled(True)
        tableWidget.selectRow(0)
        tableWidget.horizontalHeaderItem(3).setText(
            _translate("MainWindow", "Received"))
        tableWidget.setUpdatesEnabled(True)

    # create application indicator
    def appIndicatorInit(self, app):
        self.initTrayIcon("can-icon-24px-red.png", app)
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"
        QtCore.QObject.connect(self.tray, QtCore.SIGNAL(
            traySignal), self.__icon_activated)

        m = QtGui.QMenu()

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
        self.actionShow.setChecked(not BMConfigParser().getboolean(
            'bitmessagesettings', 'startintray'))
        self.actionShow.triggered.connect(self.appIndicatorShowOrHideWindow)
        if not sys.platform[0:3] == 'win':
            m.addAction(self.actionShow)

        # quiet mode
        self.actionQuiet = QtGui.QAction(_translate(
            "MainWindow", "Quiet Mode"), m, checkable=True)
        self.actionQuiet.setChecked(not BMConfigParser().getboolean(
            'bitmessagesettings', 'showtraynotifications'))
        self.actionQuiet.triggered.connect(self.appIndicatorSwitchQuietMode)
        m.addAction(self.actionQuiet)

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

    # returns the number of unread messages and subscriptions
    def getUnread(self):
        counters = [0, 0]

        queryreturn = sqlQuery('''
        SELECT msgid, toaddress, read FROM inbox where folder='inbox'
        ''')
        for msgid, toAddress, read in queryreturn:

            if not read:
                # increment the unread subscriptions if True (1)
                # else messages (0)
                counters[toAddress == str_broadcast_subscribers] += 1

        return counters

    # play a sound
    def playSound(self, category, label):
        # filename of the sound to be played
        soundFilename = None

        def _choose_ext(basename):
            for ext in sound.extensions:
                if os.path.isfile(os.extsep.join([basename, ext])):
                    return os.extsep + ext

        # if the address had a known label in the address book
        if label:
            # Does a sound file exist for this particular contact?
            soundFilename = state.appdata + 'sounds/' + label
            ext = _choose_ext(soundFilename)
            if not ext:
                category = sound.SOUND_KNOWN
                soundFilename = None

        if soundFilename is None:
            # Avoid making sounds more frequently than the threshold.
            # This suppresses playing sounds repeatedly when there
            # are many new messages
            if not sound.is_connection_sound(category):
                # elapsed time since the last sound was played
                dt = datetime.now() - self.lastSoundTime
                # suppress sounds which are more frequent than the threshold
                if dt.total_seconds() < self.maxSoundFrequencySec:
                    return

            # the sound is for an address which exists in the address book
            if category is sound.SOUND_KNOWN:
                soundFilename = state.appdata + 'sounds/known'
            # the sound is for an unknown address
            elif category is sound.SOUND_UNKNOWN:
                soundFilename = state.appdata + 'sounds/unknown'
            # initial connection sound
            elif category is sound.SOUND_CONNECTED:
                soundFilename = state.appdata + 'sounds/connected'
            # disconnected sound
            elif category is sound.SOUND_DISCONNECTED:
                soundFilename = state.appdata + 'sounds/disconnected'
            # sound when the connection status becomes green
            elif category is sound.SOUND_CONNECTION_GREEN:
                soundFilename = state.appdata + 'sounds/green'

        if soundFilename is None:
            logger.warning("Probably wrong category number in playSound()")
            return

        if not sound.is_connection_sound(category):
            # record the last time that a received message sound was played
            self.lastSoundTime = datetime.now()

        try:  # try already known format
            soundFilename += ext
        except (TypeError, NameError):
            ext = _choose_ext(soundFilename)
            if not ext:
                try:  # if no user sound file found try to play from theme
                    return self._theme_player(category, label)
                except TypeError:
                    return

            soundFilename += ext

        self._player(soundFilename)

    # Adapters and converters for QT <-> sqlite
    def sqlInit(self):
        register_adapter(QtCore.QByteArray, str)

    # Try init the distro specific appindicator,
    # for example the Ubuntu MessagingMenu
    def indicatorInit(self):
        def _noop_update(*args, **kwargs):
            pass

        try:
            self.indicatorUpdate = get_plugin('indicator')(self)
        except (NameError, TypeError):
            logger.warning("No indicator plugin found")
            self.indicatorUpdate = _noop_update

    # initialise the message notifier
    def notifierInit(self):
        def _simple_notify(
                title, subtitle, category, label=None, icon=None):
            self.tray.showMessage(title, subtitle, 1, 2000)

        self._notifier = _simple_notify
        # does nothing if isAvailable returns false
        self._player = QtGui.QSound.play

        if not get_plugins:
            return

        _plugin = get_plugin('notification.message')
        if _plugin:
            self._notifier = _plugin
        else:
            logger.warning("No notification.message plugin found")

        self._theme_player = get_plugin('notification.sound', 'theme')

        if not QtGui.QSound.isAvailable():
            _plugin = get_plugin(
                'notification.sound', 'file', fallback='file.fallback')
            if _plugin:
                self._player = _plugin
            else:
                logger.warning("No notification.sound plugin found")

    def notifierShow(
            self, title, subtitle, category, label=None, icon=None):
        self.playSound(category, label)
        self._notifier(
            unicode(title), unicode(subtitle), category, label, icon)

    # tree
    def treeWidgetKeyPressEvent(self, event):
        return self.handleKeyPress(event, self.getCurrentTreeWidget())

    # addressbook
    def addressbookKeyPressEvent(self, event):
        """Handle keypress event in addressbook widget"""
        if event.key() == QtCore.Qt.Key_Delete:
            self.on_action_AddressBookDelete()
        else:
            return QtGui.QTableWidget.keyPressEvent(
                self.ui.tableWidgetAddressBook, event)

    # inbox / sent
    def tableWidgetKeyPressEvent(self, event):
        return self.handleKeyPress(event, self.getCurrentMessagelist())

    # messageview
    def textEditKeyPressEvent(self, event):
        return self.handleKeyPress(event, self.getCurrentMessageTextedit())

    def handleKeyPress(self, event, focus=None):
        """This method handles keypress events for all widgets on MyForm"""
        messagelist = self.getCurrentMessagelist()
        if event.key() == QtCore.Qt.Key_Delete:
            if isinstance(focus, (MessageView, QtGui.QTableWidget)):
                folder = self.getCurrentFolder()
                if folder == "sent":
                    self.on_action_SentTrash()
                else:
                    self.on_action_InboxTrash()
            event.ignore()
        elif QtGui.QApplication.queryKeyboardModifiers() == QtCore.Qt.NoModifier:
            if event.key() == QtCore.Qt.Key_N:
                currentRow = messagelist.currentRow()
                if currentRow < messagelist.rowCount() - 1:
                    messagelist.selectRow(currentRow + 1)
                event.ignore()
            elif event.key() == QtCore.Qt.Key_P:
                currentRow = messagelist.currentRow()
                if currentRow > 0:
                    messagelist.selectRow(currentRow - 1)
                event.ignore()
            elif event.key() == QtCore.Qt.Key_R:
                if messagelist == self.ui.tableWidgetInboxChans:
                    self.on_action_InboxReplyChan()
                else:
                    self.on_action_InboxReply()
                event.ignore()
            elif event.key() == QtCore.Qt.Key_C:
                currentAddress = self.getCurrentAccount()
                if currentAddress:
                    self.setSendFromComboBox(currentAddress)
                self.ui.tabWidgetSend.setCurrentIndex(
                    self.ui.tabWidgetSend.indexOf(self.ui.sendDirect)
                )
                self.ui.tabWidget.setCurrentIndex(
                    self.ui.tabWidget.indexOf(self.ui.send)
                )
                self.ui.lineEditTo.setFocus()
                event.ignore()
            elif event.key() == QtCore.Qt.Key_F:
                try:
                    self.getCurrentSearchLine(retObj=True).setFocus()
                except AttributeError:
                    pass
                event.ignore()
        if not event.isAccepted():
            return
        if isinstance(focus, MessageView):
            return MessageView.keyPressEvent(focus, event)
        if isinstance(focus, QtGui.QTableWidget):
            return QtGui.QTableWidget.keyPressEvent(focus, event)
        if isinstance(focus, QtGui.QTreeWidget):
            return QtGui.QTreeWidget.keyPressEvent(focus, event)

    # menu button 'manage keys'
    def click_actionManageKeys(self):
        if 'darwin' in sys.platform or 'linux' in sys.platform:
            if state.appdata == '':
                # reply = QtGui.QMessageBox.information(self, 'keys.dat?','You
                # may manage your keys by editing the keys.dat file stored in
                # the same directory as this program. It is important that you
                # back up this file.', QMessageBox.Ok)
                reply = QtGui.QMessageBox.information(self, 'keys.dat?', _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file."), QtGui.QMessageBox.Ok)

            else:
                QtGui.QMessageBox.information(self, 'keys.dat?', _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in\n %1 \nIt is important that you back up this file.").arg(state.appdata), QtGui.QMessageBox.Ok)
        elif sys.platform == 'win32' or sys.platform == 'win64':
            if state.appdata == '':
                reply = QtGui.QMessageBox.question(self, _translate("MainWindow", "Open keys.dat?"), _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)"), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            else:
                reply = QtGui.QMessageBox.question(self, _translate("MainWindow", "Open keys.dat?"), _translate(
                    "MainWindow", "You may manage your keys by editing the keys.dat file stored in\n %1 \nIt is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)").arg(state.appdata), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                openKeysFile()

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

    # menu button 'regenerate deterministic addresses'
    def click_actionRegenerateDeterministicAddresses(self):
        dialog = dialogs.RegenerateAddressesDialog(self)
        if dialog.exec_():
            if dialog.lineEditPassphrase.text() == "":
                QtGui.QMessageBox.about(
                    self, _translate("MainWindow", "bad passphrase"),
                    _translate(
                        "MainWindow",
                        "You must type your passphrase. If you don\'t"
                        " have one then this is not the form for you."
                    ))
                return
            streamNumberForAddress = int(dialog.lineEditStreamNumber.text())
            try:
                addressVersionNumber = int(
                    dialog.lineEditAddressVersionNumber.text())
            except:
                QtGui.QMessageBox.about(
                    self,
                    _translate("MainWindow", "Bad address version number"),
                    _translate(
                        "MainWindow",
                        "Your address version number must be a number:"
                        " either 3 or 4."
                    ))
                return
            if addressVersionNumber < 3 or addressVersionNumber > 4:
                QtGui.QMessageBox.about(
                    self,
                    _translate("MainWindow", "Bad address version number"),
                    _translate(
                        "MainWindow",
                        "Your address version number must be either 3 or 4."
                    ))
                return
            queues.addressGeneratorQueue.put((
                'createDeterministicAddresses',
                addressVersionNumber, streamNumberForAddress,
                "regenerated deterministic address",
                dialog.spinBoxNumberOfAddressesToMake.value(),
                dialog.lineEditPassphrase.text().toUtf8(),
                dialog.checkBoxEighteenByteRipe.isChecked()
            ))
            self.ui.tabWidget.setCurrentIndex(
                self.ui.tabWidget.indexOf(self.ui.chans)
            )

    # opens 'join chan' dialog
    def click_actionJoinChan(self):
        dialogs.NewChanDialog(self)

    def showConnectDialog(self):
        dialog = dialogs.ConnectDialog(self)
        if dialog.exec_():
            if dialog.radioButtonConnectNow.isChecked():
                self.ui.updateNetworkSwitchMenuLabel(False)
                BMConfigParser().remove_option(
                    'bitmessagesettings', 'dontconnect')
                BMConfigParser().save()
            elif dialog.radioButtonConfigureNetwork.isChecked():
                self.click_actionSettings()
            else:
                self._firstrun = False

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
            self.init_identities_popup_menu(False)
            self.init_chan_popup_menu(False)
            self.init_addressbook_popup_menu(False)
            self.init_subscriptions_popup_menu(False)
            self.init_sent_popup_menu(False)
            self.ui.blackwhitelist.init_blacklist_popup_menu(False)
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                if BMConfigParser().getboolean('bitmessagesettings', 'minimizetotray') and not 'darwin' in sys.platform:
                    QtCore.QTimer.singleShot(0, self.appIndicatorHide)
            elif event.oldState() & QtCore.Qt.WindowMinimized:
                # The window state has just been changed to
                # Normal/Maximised/FullScreen
                pass

    def __icon_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.actionShow.setChecked(not self.actionShow.isChecked())
            self.appIndicatorShowOrHideWindow()

    # Indicates whether or not there is a connection to the Bitmessage network
    connected = False

    def setStatusIcon(self, color):
        # print 'setting status icon color'
        _notifications_enabled = not BMConfigParser().getboolean(
            'bitmessagesettings', 'hidetrayconnectionnotifications')
        if color == 'red':
            self.pushButtonStatusIcon.setIcon(
                QtGui.QIcon(":/newPrefix/images/redicon.png"))
            state.statusIconColor = 'red'
            # if the connection is lost then show a notification
            if self.connected and _notifications_enabled:
                self.notifierShow(
                    'Bitmessage',
                    _translate("MainWindow", "Connection lost"),
                    sound.SOUND_DISCONNECTED)
            if not BMConfigParser().safeGetBoolean('bitmessagesettings', 'upnp') and \
                BMConfigParser().get('bitmessagesettings', 'socksproxytype') == "none":
                self.updateStatusBar(
                    _translate(
                        "MainWindow",
                        "Problems connecting? Try enabling UPnP in the Network"
                        " Settings"
                    ))
            self.connected = False

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Not Connected"))
                self.setTrayIconFile("can-icon-24px-red.png")
        if color == 'yellow':
            if self.statusbar.currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusbar.clearMessage()
            self.pushButtonStatusIcon.setIcon(
                QtGui.QIcon(":/newPrefix/images/yellowicon.png"))
            state.statusIconColor = 'yellow'
            # if a new connection has been established then show a notification
            if not self.connected and _notifications_enabled:
                self.notifierShow(
                    'Bitmessage',
                    _translate("MainWindow", "Connected"),
                    sound.SOUND_CONNECTED)
            self.connected = True

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Connected"))
                self.setTrayIconFile("can-icon-24px-yellow.png")
        if color == 'green':
            if self.statusbar.currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusbar.clearMessage()
            self.pushButtonStatusIcon.setIcon(
                QtGui.QIcon(":/newPrefix/images/greenicon.png"))
            state.statusIconColor = 'green'
            if not self.connected and _notifications_enabled:
                self.notifierShow(
                    'Bitmessage',
                    _translate("MainWindow", "Connected"),
                    sound.SOUND_CONNECTION_GREEN)
            self.connected = True

            if self.actionStatus is not None:
                self.actionStatus.setText(_translate(
                    "MainWindow", "Connected"))
                self.setTrayIconFile("can-icon-24px-green.png")

    def initTrayIcon(self, iconFileName, app):
        self.currentTrayIconFileName = iconFileName
        self.tray = QtGui.QSystemTrayIcon(
            self.calcTrayIcon(iconFileName, self.findInboxUnreadCount()), app)

    def setTrayIconFile(self, iconFileName):
        self.currentTrayIconFileName = iconFileName
        self.drawTrayIcon(iconFileName, self.findInboxUnreadCount())

    def calcTrayIcon(self, iconFileName, inboxUnreadCount):
        pixmap = QtGui.QPixmap(":/newPrefix/images/" + iconFileName)
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
            # it looks like -2 is also ok due to the error of metric
            marginY = 0
            # if it renders too wide we need to change it to a plus symbol
            if rect.width() > 20:
                txt = "+"
                fontSize = 15
                font = QtGui.QFont(fontName, fontSize, QtGui.QFont.Bold)
                fontMetrics = QtGui.QFontMetrics(font)
                rect = fontMetrics.boundingRect(txt)
            # draw text
            painter = QtGui.QPainter()
            painter.begin(pixmap)
            painter.setPen(
                QtGui.QPen(QtGui.QColor(255, 0, 0), QtCore.Qt.SolidPattern))
            painter.setFont(font)
            painter.drawText(24-rect.right()-marginX, -rect.top()+marginY, txt)
            painter.end()
        return QtGui.QIcon(pixmap)

    def drawTrayIcon(self, iconFileName, inboxUnreadCount):
        self.tray.setIcon(self.calcTrayIcon(iconFileName, inboxUnreadCount))

    def changedInboxUnread(self, row=None):
        self.drawTrayIcon(
            self.currentTrayIconFileName, self.findInboxUnreadCount())
        self.rerenderTabTreeMessages()
        self.rerenderTabTreeSubscriptions()
        self.rerenderTabTreeChans()

    def findInboxUnreadCount(self, count=None):
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
        for sent in (
            self.ui.tableWidgetInbox,
            self.ui.tableWidgetInboxSubscriptions,
            self.ui.tableWidgetInboxChans
        ):
            treeWidget = self.widgetConvert(sent)
            if self.getCurrentFolder(treeWidget) != "sent":
                continue
            if treeWidget in (
                self.ui.treeWidgetSubscriptions,
                self.ui.treeWidgetChans
            ) and self.getCurrentAccount(treeWidget) != toAddress:
                continue

            for i in range(sent.rowCount()):
                rowAddress = sent.item(i, 0).data(QtCore.Qt.UserRole)
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
        if type(ackdata) is str:
            ackdata = QtCore.QByteArray(ackdata)
        for sent in (
            self.ui.tableWidgetInbox,
            self.ui.tableWidgetInboxSubscriptions,
            self.ui.tableWidgetInboxChans
        ):
            treeWidget = self.widgetConvert(sent)
            if self.getCurrentFolder(treeWidget) != "sent":
                continue
            for i in range(sent.rowCount()):
                toAddress = sent.item(i, 0).data(QtCore.Qt.UserRole)
                tableAckdata = sent.item(i, 3).data()
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

    def removeInboxRowByMsgid(self, msgid):
        # msgid and inventoryHash are the same thing
        for inbox in (
            self.ui.tableWidgetInbox,
            self.ui.tableWidgetInboxSubscriptions,
            self.ui.tableWidgetInboxChans
        ):
            i = None
            for i in range(inbox.rowCount()):
                if msgid == inbox.item(i, 3).data():
                    break
            else:
                continue
            self.updateStatusBar(_translate("MainWindow", "Message trashed"))
            treeWidget = self.widgetConvert(inbox)
            self.propagateUnreadCount(
                # wrong assumption about current folder here:
                self.getCurrentFolder(treeWidget), treeWidget
            )
            if i:
                inbox.removeRow(i)

    def newVersionAvailable(self, version):
        self.notifiedNewVersion = ".".join(str(n) for n in version)
        self.updateStatusBar(_translate(
            "MainWindow",
            "New version of PyBitmessage is available: %1. Download it"
            " from https://github.com/Bitmessage/PyBitmessage/releases/latest"
            ).arg(self.notifiedNewVersion)
        )

    def displayAlert(self, title, text, exitAfterUserClicksOk):
        self.updateStatusBar(text)
        QtGui.QMessageBox.critical(self, title, text, QtGui.QMessageBox.Ok)
        if exitAfterUserClicksOk:
            os._exit(0)

    def rerenderMessagelistFromLabels(self):
        for messagelist in (self.ui.tableWidgetInbox, self.ui.tableWidgetInboxChans, self.ui.tableWidgetInboxSubscriptions):
            for i in range(messagelist.rowCount()):
                messagelist.item(i, 1).setLabel()

    def rerenderMessagelistToLabels(self):
        for messagelist in (self.ui.tableWidgetInbox, self.ui.tableWidgetInboxChans, self.ui.tableWidgetInboxSubscriptions):
            for i in range(messagelist.rowCount()):
                messagelist.item(i, 0).setLabel()

    def rerenderAddressBook(self):
        def addRow (address, label, type):
            self.ui.tableWidgetAddressBook.insertRow(0)
            newItem = Ui_AddressBookWidgetItemLabel(address, unicode(label, 'utf-8'), type)
            self.ui.tableWidgetAddressBook.setItem(0, 0, newItem)
            newItem = Ui_AddressBookWidgetItemAddress(address, unicode(label, 'utf-8'), type)
            self.ui.tableWidgetAddressBook.setItem(0, 1, newItem)

        oldRows = {}
        for i in range(self.ui.tableWidgetAddressBook.rowCount()):
            item = self.ui.tableWidgetAddressBook.item(i, 0)
            oldRows[item.address] = [item.label, item.type, i]

        if self.ui.tableWidgetAddressBook.rowCount() == 0:
            self.ui.tableWidgetAddressBook.horizontalHeader().setSortIndicator(0, QtCore.Qt.AscendingOrder)
        if self.ui.tableWidgetAddressBook.isSortingEnabled():
            self.ui.tableWidgetAddressBook.setSortingEnabled(False)

        newRows = {}
        # subscriptions
        queryreturn = sqlQuery('SELECT label, address FROM subscriptions WHERE enabled = 1')
        for row in queryreturn:
            label, address = row
            newRows[address] = [label, AccountMixin.SUBSCRIPTION]
        # chans
        addresses = getSortedAccounts()
        for address in addresses:
            account = accountClass(address)
            if (account.type == AccountMixin.CHAN and BMConfigParser().safeGetBoolean(address, 'enabled')):
                newRows[address] = [account.getLabel(), AccountMixin.CHAN]
        # normal accounts
        queryreturn = sqlQuery('SELECT * FROM addressbook')
        for row in queryreturn:
            label, address = row
            newRows[address] = [label, AccountMixin.NORMAL]

        completerList = []
        for address in sorted(
            oldRows, key=lambda x: oldRows[x][2], reverse=True
        ):
            try:
                completerList.append(
                    newRows.pop(address)[0] + " <" + address + ">")
            except KeyError:
                self.ui.tableWidgetAddressBook.removeRow(oldRows[address][2])
        for address in newRows:
            addRow(address, newRows[address][0], newRows[address][1])
            completerList.append(unicode(newRows[address][0], encoding="UTF-8") + " <" + address + ">")

        # sort
        self.ui.tableWidgetAddressBook.sortByColumn(
            0, QtCore.Qt.AscendingOrder)
        self.ui.tableWidgetAddressBook.setSortingEnabled(True)
        self.ui.lineEditTo.completer().model().setStringList(completerList)

    def rerenderSubscriptions(self):
        self.rerenderTabTreeSubscriptions()

    def click_pushButtonTTL(self):
        QtGui.QMessageBox.information(self, 'Time To Live', _translate(
            "MainWindow", """The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate."""), QtGui.QMessageBox.Ok)

    def click_pushButtonClear(self):
        self.ui.lineEditSubject.setText("")
        self.ui.lineEditTo.setText("")
        self.ui.textEditMessage.reset()
        self.ui.comboBoxSendFrom.setCurrentIndex(0)

    def click_pushButtonSend(self):
        encoding = 3 if QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ShiftModifier else 2

        self.statusbar.clearMessage()

        if self.ui.tabWidgetSend.currentIndex() == \
                self.ui.tabWidgetSend.indexOf(self.ui.sendDirect):
            # message to specific people
            sendMessageToPeople = True
            fromAddress = str(self.ui.comboBoxSendFrom.itemData(
                self.ui.comboBoxSendFrom.currentIndex(),
                QtCore.Qt.UserRole).toString())
            toAddresses = str(self.ui.lineEditTo.text().toUtf8())
            subject = str(self.ui.lineEditSubject.text().toUtf8())
            message = str(
                self.ui.textEditMessage.document().toPlainText().toUtf8())
        else:
            # broadcast message
            sendMessageToPeople = False
            fromAddress = str(self.ui.comboBoxSendFromBroadcast.itemData(
                self.ui.comboBoxSendFromBroadcast.currentIndex(),
                QtCore.Qt.UserRole).toString())
            subject = str(self.ui.lineEditSubjectBroadcast.text().toUtf8())
            message = str(
                self.ui.textEditMessageBroadcast.document().toPlainText().toUtf8())
        """
        The whole network message must fit in 2^18 bytes.
        Let's assume 500 bytes of overhead. If someone wants to get that
        too an exact number you are welcome to but I think that it would
        be a better use of time to support message continuation so that
        users can send messages of any length.
        """
        if len(message) > (2 ** 18 - 500):
            QtGui.QMessageBox.about(
                self, _translate("MainWindow", "Message too long"),
                _translate(
                    "MainWindow",
                    "The message that you are trying to send is too long"
                    " by %1 bytes. (The maximum is 261644 bytes). Please"
                    " cut it down before sending."
                ).arg(len(message) - (2 ** 18 - 500)))
            return

        acct = accountClass(fromAddress)

        # To send a message to specific people (rather than broadcast)
        if sendMessageToPeople:
            toAddressesList = set([
                s.strip() for s in toAddresses.replace(',', ';').split(';')
            ])
            # remove duplicate addresses. If the user has one address
            # with a BM- and the same address without the BM-, this will
            # not catch it. They'll send the message to the person twice.
            for toAddress in toAddressesList:
                if toAddress != '':
                    # label plus address
                    if "<" in toAddress and ">" in toAddress:
                        toAddress = toAddress.split('<')[1].split('>')[0]
                    # email address
                    if toAddress.find("@") >= 0:
                        if isinstance(acct, GatewayAccount):
                            acct.createMessage(toAddress, fromAddress, subject, message)
                            subject = acct.subject
                            toAddress = acct.toAddress
                        else:
                            if QtGui.QMessageBox.question(self, "Sending an email?", _translate("MainWindow", 
                                "You are trying to send an email instead of a bitmessage. This requires registering with a gateway. Attempt to register?"),
                                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                                continue
                            email = acct.getLabel()
                            if email[-14:] != "@mailchuck.com": #attempt register
                                # 12 character random email address
                                email = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(12)) + "@mailchuck.com"
                            acct = MailchuckAccount(fromAddress)
                            acct.register(email)
                            BMConfigParser().set(fromAddress, 'label', email)
                            BMConfigParser().set(fromAddress, 'gateway', 'mailchuck')
                            BMConfigParser().save()
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: Your account wasn't registered at"
                                " an email gateway. Sending registration"
                                " now as %1, please wait for the registration"
                                " to be processed before retrying sending."
                                ).arg(email)
                            )
                            return
                    status, addressVersionNumber, streamNumber = decodeAddress(toAddress)[:3]
                    if status != 'success':
                        try:
                            toAddress = unicode(toAddress, 'utf-8', 'ignore')
                        except:
                            pass
                        logger.error('Error: Could not decode recipient address ' + toAddress + ':' + status)

                        if status == 'missingbm':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: Bitmessage addresses start with"
                                " BM-   Please check the recipient address %1"
                                ).arg(toAddress))
                        elif status == 'checksumfailed':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: The recipient address %1 is not"
                                " typed or copied correctly. Please check it."
                                ).arg(toAddress))
                        elif status == 'invalidcharacters':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: The recipient address %1 contains"
                                " invalid characters. Please check it."
                                ).arg(toAddress))
                        elif status == 'versiontoohigh':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: The version of the recipient address"
                                " %1 is too high. Either you need to upgrade"
                                " your Bitmessage software or your"
                                " acquaintance is being clever."
                                ).arg(toAddress))
                        elif status == 'ripetooshort':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: Some data encoded in the recipient"
                                " address %1 is too short. There might be"
                                " something wrong with the software of"
                                " your acquaintance."
                                ).arg(toAddress))
                        elif status == 'ripetoolong':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: Some data encoded in the recipient"
                                " address %1 is too long. There might be"
                                " something wrong with the software of"
                                " your acquaintance."
                                ).arg(toAddress))
                        elif status == 'varintmalformed':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: Some data encoded in the recipient"
                                " address %1 is malformed. There might be"
                                " something wrong with the software of"
                                " your acquaintance."
                                ).arg(toAddress))
                        else:
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Error: Something is wrong with the"
                                " recipient address %1."
                                ).arg(toAddress))
                    elif fromAddress == '':
                        self.updateStatusBar(_translate(
                            "MainWindow",
                            "Error: You must specify a From address. If you"
                            " don\'t have one, go to the"
                            " \'Your Identities\' tab.")
                        )
                    else:
                        toAddress = addBMIfNotPresent(toAddress)

                        if addressVersionNumber > 4 or addressVersionNumber <= 1:
                            QtGui.QMessageBox.about(self, _translate("MainWindow", "Address version number"), _translate(
                                "MainWindow", "Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.").arg(toAddress).arg(str(addressVersionNumber)))
                            continue
                        if streamNumber > 1 or streamNumber == 0:
                            QtGui.QMessageBox.about(self, _translate("MainWindow", "Stream number"), _translate(
                                "MainWindow", "Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.").arg(toAddress).arg(str(streamNumber)))
                            continue
                        self.statusbar.clearMessage()
                        if state.statusIconColor == 'red':
                            self.updateStatusBar(_translate(
                                "MainWindow",
                                "Warning: You are currently not connected."
                                " Bitmessage will do the work necessary to"
                                " send the message but it won\'t send until"
                                " you connect.")
                            )
                        ackdata = helper_sent.insert(
                            toAddress=toAddress, fromAddress=fromAddress,
                            subject=subject, message=message, encoding=encoding)
                        toLabel = ''
                        queryreturn = sqlQuery('''select label from addressbook where address=?''',
                                               toAddress)
                        if queryreturn != []:
                            for row in queryreturn:
                                toLabel, = row

                        self.displayNewSentMessage(
                            toAddress, toLabel, fromAddress, subject, message, ackdata)
                        queues.workerQueue.put(('sendmessage', toAddress))

                        self.click_pushButtonClear()
                        if self.replyFromTab is not None:
                            self.ui.tabWidget.setCurrentIndex(self.replyFromTab)
                            self.replyFromTab = None
                        self.updateStatusBar(_translate(
                            "MainWindow", "Message queued."))
                        # self.ui.tableWidgetInbox.setCurrentCell(0, 0)
                else:
                    self.updateStatusBar(_translate(
                        "MainWindow", "Your \'To\' field is empty."))
        else:  # User selected 'Broadcast'
            if fromAddress == '':
                self.updateStatusBar(_translate(
                    "MainWindow",
                    "Error: You must specify a From address. If you don\'t"
                    " have one, go to the \'Your Identities\' tab."
                ))
            else:
                self.statusbar.clearMessage()
                # We don't actually need the ackdata for acknowledgement since
                # this is a broadcast message, but we can use it to update the
                # user interface when the POW is done generating.
                toAddress = str_broadcast_subscribers

                # msgid. We don't know what this will be until the POW is done.
                ackdata = helper_sent.insert(
                    fromAddress=fromAddress,
                    subject=subject, message=message,
                    status='broadcastqueued', encoding=encoding)

                toLabel = str_broadcast_subscribers

                self.displayNewSentMessage(
                    toAddress, toLabel, fromAddress, subject, message, ackdata)

                queues.workerQueue.put(('sendbroadcast', ''))

                self.ui.comboBoxSendFromBroadcast.setCurrentIndex(0)
                self.ui.lineEditSubjectBroadcast.setText('')
                self.ui.textEditMessageBroadcast.reset()
                self.ui.tabWidget.setCurrentIndex(
                    self.ui.tabWidget.indexOf(self.ui.send)
                )
                self.ui.tableWidgetInboxSubscriptions.setCurrentCell(0, 0)
                self.updateStatusBar(_translate(
                    "MainWindow", "Broadcast queued."))

    def click_pushButtonLoadFromAddressBook(self):
        self.ui.tabWidget.setCurrentIndex(5)
        for i in range(4):
            time.sleep(0.1)
            self.statusbar.clearMessage()
            time.sleep(0.1)
            self.updateStatusBar(_translate(
                "MainWindow",
                "Right click one or more entries in your address book and"
                " select \'Send message to this address\'."
            ))

    def click_pushButtonFetchNamecoinID(self):
        identities = str(self.ui.lineEditTo.text().toUtf8()).split(";")
        err, addr = self.namecoin.query(identities[-1].strip())
        if err is not None:
            self.updateStatusBar(
                _translate("MainWindow", "Error: %1").arg(err))
        else:
            identities[-1] = addr
            self.ui.lineEditTo.setText("; ".join(identities))
            self.updateStatusBar(_translate(
                "MainWindow", "Fetched address from namecoin identity."))

    def setBroadcastEnablementDependingOnWhetherThisIsAMailingListAddress(self, address):
        # If this is a chan then don't let people broadcast because no one
        # should subscribe to chan addresses.
        self.ui.tabWidgetSend.setCurrentIndex(
            self.ui.tabWidgetSend.indexOf(
                self.ui.sendBroadcast
                if BMConfigParser().safeGetBoolean(str(address), 'mailinglist')
                else self.ui.sendDirect
            ))

    def rerenderComboBoxSendFrom(self):
        self.ui.comboBoxSendFrom.clear()
        for addressInKeysFile in getSortedAccounts():
            isEnabled = BMConfigParser().getboolean(
                addressInKeysFile, 'enabled')  # I realize that this is poor programming practice but I don't care. It's easier for others to read.
            isMaillinglist = BMConfigParser().safeGetBoolean(addressInKeysFile, 'mailinglist')
            if isEnabled and not isMaillinglist:
                label = unicode(BMConfigParser().get(addressInKeysFile, 'label'), 'utf-8', 'ignore').strip()
                if label == "":
                    label = addressInKeysFile
                self.ui.comboBoxSendFrom.addItem(avatarize(addressInKeysFile), label, addressInKeysFile)
#        self.ui.comboBoxSendFrom.model().sort(1, Qt.AscendingOrder)
        for i in range(self.ui.comboBoxSendFrom.count()):
            address = str(self.ui.comboBoxSendFrom.itemData(
                i, QtCore.Qt.UserRole).toString())
            self.ui.comboBoxSendFrom.setItemData(
                i, AccountColor(address).accountColor(),
                QtCore.Qt.ForegroundRole)
        self.ui.comboBoxSendFrom.insertItem(0, '', '')
        if(self.ui.comboBoxSendFrom.count() == 2):
            self.ui.comboBoxSendFrom.setCurrentIndex(1)
        else:
            self.ui.comboBoxSendFrom.setCurrentIndex(0)

    def rerenderComboBoxSendFromBroadcast(self):
        self.ui.comboBoxSendFromBroadcast.clear()
        for addressInKeysFile in getSortedAccounts():
            isEnabled = BMConfigParser().getboolean(
                addressInKeysFile, 'enabled')  # I realize that this is poor programming practice but I don't care. It's easier for others to read.
            isChan = BMConfigParser().safeGetBoolean(addressInKeysFile, 'chan')
            if isEnabled and not isChan:
                label = unicode(BMConfigParser().get(addressInKeysFile, 'label'), 'utf-8', 'ignore').strip()
                if label == "":
                    label = addressInKeysFile
                self.ui.comboBoxSendFromBroadcast.addItem(avatarize(addressInKeysFile), label, addressInKeysFile)
        for i in range(self.ui.comboBoxSendFromBroadcast.count()):
            address = str(self.ui.comboBoxSendFromBroadcast.itemData(
                i, QtCore.Qt.UserRole).toString())
            self.ui.comboBoxSendFromBroadcast.setItemData(
                i, AccountColor(address).accountColor(),
                QtCore.Qt.ForegroundRole)
        self.ui.comboBoxSendFromBroadcast.insertItem(0, '', '')
        if(self.ui.comboBoxSendFromBroadcast.count() == 2):
            self.ui.comboBoxSendFromBroadcast.setCurrentIndex(1)
        else:
            self.ui.comboBoxSendFromBroadcast.setCurrentIndex(0)

    # This function is called by the processmsg function when that function
    # receives a message to an address that is acting as a
    # pseudo-mailing-list. The message will be broadcast out. This function
    # puts the message on the 'Sent' tab.
    def displayNewSentMessage(
            self, toAddress, toLabel, fromAddress, subject,
            message, ackdata):
        acct = accountClass(fromAddress)
        acct.parseMessage(toAddress, fromAddress, subject, message)
        tab = -1
        for sent in (
            self.ui.tableWidgetInbox,
            self.ui.tableWidgetInboxSubscriptions,
            self.ui.tableWidgetInboxChans
        ):
            tab += 1
            if tab == 1:
                tab = 2
            treeWidget = self.widgetConvert(sent)
            if self.getCurrentFolder(treeWidget) != "sent":
                continue
            if treeWidget == self.ui.treeWidgetYourIdentities \
                and self.getCurrentAccount(treeWidget) not in (
                    fromAddress, None, False):
                continue
            elif treeWidget in (
                self.ui.treeWidgetSubscriptions,
                self.ui.treeWidgetChans
            ) and self.getCurrentAccount(treeWidget) != toAddress:
                continue
            elif not helper_search.check_match(
                toAddress, fromAddress, subject, message,
                self.getCurrentSearchOption(tab),
                self.getCurrentSearchLine(tab)
            ):
                continue

            self.addMessageListItemSent(
                sent, toAddress, fromAddress, subject,
                "msgqueued", ackdata, time.time())
            self.getAccountTextedit(acct).setPlainText(message)
            sent.setCurrentCell(0, 0)

    def displayNewInboxMessage(
            self, inventoryHash, toAddress, fromAddress, subject, message):
        acct = accountClass(
            fromAddress if toAddress == str_broadcast_subscribers
            else toAddress
        )
        inbox = self.getAccountMessagelist(acct)
        ret = treeWidget = None
        tab = -1
        for treeWidget in (
            self.ui.treeWidgetYourIdentities,
            self.ui.treeWidgetSubscriptions,
            self.ui.treeWidgetChans
        ):
            tab += 1
            if tab == 1:
                tab = 2
            if not helper_search.check_match(
                toAddress, fromAddress, subject, message,
                self.getCurrentSearchOption(tab),
                self.getCurrentSearchLine(tab)
            ):
                continue
            tableWidget = self.widgetConvert(treeWidget)
            current_account = self.getCurrentAccount(treeWidget)
            current_folder = self.getCurrentFolder(treeWidget)
            # pylint: disable=too-many-boolean-expressions
            if ((tableWidget == inbox
                 and current_account == acct.address
                 and current_folder in ("inbox", None))
                or (treeWidget == self.ui.treeWidgetYourIdentities
                    and current_account is None
                    and current_folder in ("inbox", "new", None))):
                ret = self.addMessageListItemInbox(
                    tableWidget, toAddress, fromAddress, subject,
                    inventoryHash, time.time(), False)

        if ret is None:
            acct.parseMessage(toAddress, fromAddress, subject, "")
        else:
            acct = ret
        self.propagateUnreadCount(widget=treeWidget if ret else None)
        if BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'showtraynotifications'):
            self.notifierShow(
                _translate("MainWindow", "New Message"),
                _translate("MainWindow", "From %1").arg(
                    unicode(acct.fromLabel, 'utf-8')),
                sound.SOUND_UNKNOWN
            )
        if self.getCurrentAccount() is not None and (
                (self.getCurrentFolder(treeWidget) != "inbox"
                 and self.getCurrentFolder(treeWidget) is not None)
                or self.getCurrentAccount(treeWidget) != acct.address):
            # Ubuntu should notify of new message irrespective of
            # whether it's in current message list or not
            self.indicatorUpdate(True, to_label=acct.toLabel)

        try:
            if acct.feedback != GatewayAccount.ALL_OK:
                if acct.feedback == GatewayAccount.REGISTRATION_DENIED:
                    dialogs.EmailGatewayDialog(
                        self, BMConfigParser(), acct).exec_()
                # possible other branches?
        except AttributeError:
            pass

    def click_pushButtonAddAddressBook(self, dialog=None):
        if not dialog:
            dialog = dialogs.AddAddressDialog(self)
        dialog.exec_()
        try:
            address, label = dialog.data
        except AttributeError:
            return

        # First we must check to see if the address is already in the
        # address book. The user cannot add it again or else it will
        # cause problems when updating and deleting the entry.
        if shared.isAddressInMyAddressBook(address):
            self.updateStatusBar(_translate(
                "MainWindow",
                "Error: You cannot add the same address to your"
                " address book twice. Try renaming the existing one"
                " if you want."
            ))
            return

        self.addEntryToAddressBook(address, label)

    def addEntryToAddressBook(self, address, label):
        if shared.isAddressInMyAddressBook(address):
            return
        sqlExecute('''INSERT INTO addressbook VALUES (?,?)''', label, address)
        self.rerenderMessagelistFromLabels()
        self.rerenderMessagelistToLabels()
        self.rerenderAddressBook()

    def addSubscription(self, address, label):
        # This should be handled outside of this function, for error displaying
        # and such, but it must also be checked here.
        if shared.isAddressInMySubscriptionsList(address):
            return
        # Add to database (perhaps this should be separated from the MyForm class)
        sqlExecute(
            '''INSERT INTO subscriptions VALUES (?,?,?)''',
            label, address, True
        )
        self.rerenderMessagelistFromLabels()
        shared.reloadBroadcastSendersForWhichImWatching()
        self.rerenderAddressBook()
        self.rerenderTabTreeSubscriptions()

    def click_pushButtonAddSubscription(self):
        dialog = dialogs.NewSubscriptionDialog(self)
        dialog.exec_()
        try:
            address, label = dialog.data
        except AttributeError:
            return

        # We must check to see if the address is already in the
        # subscriptions list. The user cannot add it again or else it
        # will cause problems when updating and deleting the entry.
        if shared.isAddressInMySubscriptionsList(address):
            self.updateStatusBar(_translate(
                "MainWindow",
                "Error: You cannot add the same address to your"
                " subscriptions twice. Perhaps rename the existing one"
                " if you want."
            ))
            return

        self.addSubscription(address, label)
        # Now, if the user wants to display old broadcasts, let's get
        # them out of the inventory and put them
        # to the objectProcessorQueue to be processed
        if dialog.checkBoxDisplayMessagesAlreadyInInventory.isChecked():
            for value in dialog.recent:
                queues.objectProcessorQueue.put((
                    value.type, value.payload
                ))

    def click_pushButtonStatusIcon(self):
        dialogs.IconGlossaryDialog(self, config=BMConfigParser()).exec_()

    def click_actionHelp(self):
        dialogs.HelpDialog(self).exec_()

    def click_actionSupport(self):
        support.createSupportMessage(self)

    def click_actionAbout(self):
        dialogs.AboutDialog(self).exec_()

    def click_actionSettings(self):
        dialogs.SettingsDialog(self, firstrun=self._firstrun).exec_()

    def on_action_Send(self):
        """Send message to current selected address"""
        self.click_pushButtonClear()
        account_item = self.getCurrentItem()
        if not account_item:
            return
        self.ui.lineEditTo.setText(account_item.accountString())
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.send)
        )

    def on_action_SpecialAddressBehaviorDialog(self):
        """Show SpecialAddressBehaviorDialog"""
        dialogs.SpecialAddressBehaviorDialog(self, BMConfigParser())

    def on_action_EmailGatewayDialog(self):
        dialog = dialogs.EmailGatewayDialog(self, config=BMConfigParser())
        # For Modal dialogs
        dialog.exec_()
        try:
            acct = dialog.data
        except AttributeError:
            return

        # Only settings remain here
        acct.settings()
        for i in range(self.ui.comboBoxSendFrom.count()):
            if str(self.ui.comboBoxSendFrom.itemData(i).toPyObject()) \
                    == acct.fromAddress:
                self.ui.comboBoxSendFrom.setCurrentIndex(i)
                break
        else:
            self.ui.comboBoxSendFrom.setCurrentIndex(0)

        self.ui.lineEditTo.setText(acct.toAddress)
        self.ui.lineEditSubject.setText(acct.subject)
        self.ui.textEditMessage.setText(acct.message)
        self.ui.tabWidgetSend.setCurrentIndex(
            self.ui.tabWidgetSend.indexOf(self.ui.sendDirect)
        )
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.send)
        )
        self.ui.textEditMessage.setFocus()

    def on_action_MarkAllRead(self):
        if QtGui.QMessageBox.question(
                self, "Marking all messages as read?",
                _translate(
                    "MainWindow",
                    "Are you sure you would like to mark all messages read?"
                ), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        ) != QtGui.QMessageBox.Yes:
            return
        tableWidget = self.getCurrentMessagelist()

        idCount = tableWidget.rowCount()
        if idCount == 0:
            return

        msgids = []
        for i in range(0, idCount):
            msgids.append(tableWidget.item(i, 3).data())
            for col in xrange(tableWidget.columnCount()):
                tableWidget.item(i, col).setUnread(False)

        markread = sqlExecuteChunked(
            "UPDATE inbox SET read = 1 WHERE msgid IN({0}) AND read=0",
            idCount, *msgids
        )

        if markread > 0:
            self.propagateUnreadCount()

    def click_NewAddressDialog(self):
        dialogs.NewAddressDialog(self)

    def network_switch(self):
        dontconnect_option = not BMConfigParser().safeGetBoolean(
            'bitmessagesettings', 'dontconnect')
        reply = QtGui.QMessageBox.question(
            self, _translate("MainWindow", "Disconnecting")
            if dontconnect_option else _translate("MainWindow", "Connecting"),
            _translate(
                "MainWindow",
                "Bitmessage will now drop all connections. Are you sure?"
            ) if dontconnect_option else _translate(
                "MainWindow",
                "Bitmessage will now start connecting to network. Are you sure?"
            ), QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel)
        if reply != QtGui.QMessageBox.Yes:
            return
        BMConfigParser().set(
            'bitmessagesettings', 'dontconnect', str(dontconnect_option))
        BMConfigParser().save()
        self.ui.updateNetworkSwitchMenuLabel(dontconnect_option)

        self.ui.pushButtonFetchNamecoinID.setHidden(
            dontconnect_option or self.namecoin.test()[0] == 'failed'
        )

    # Quit selected from menu or application indicator
    def quit(self):
        """Quit the bitmessageqt application"""
        if self.quitAccepted and not self.wait:
            return

        self.show()
        self.raise_()
        self.activateWindow()

        waitForPow = True
        waitForConnection = False
        waitForSync = False

        # C PoW currently doesn't support interrupting and OpenCL is untested
        if getPowType() == "python" and (powQueueSize() > 0 or pendingUpload() > 0):
            reply = QtGui.QMessageBox.question(
                self, _translate("MainWindow", "Proof of work pending"),
                _translate(
                    "MainWindow",
                    "%n object(s) pending proof of work", None,
                    QtCore.QCoreApplication.CodecForTr, powQueueSize()
                ) + ", " +
                _translate(
                    "MainWindow",
                    "%n object(s) waiting to be distributed", None,
                    QtCore.QCoreApplication.CodecForTr, pendingUpload()
                ) + "\n\n" +
                _translate(
                    "MainWindow", "Wait until these tasks finish?"),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.No:
                waitForPow = False
            elif reply == QtGui.QMessageBox.Cancel:
                return

        if pendingDownload() > 0:
            reply = QtGui.QMessageBox.question(
                self, _translate("MainWindow", "Synchronisation pending"),
                _translate(
                    "MainWindow",
                    "Bitmessage hasn't synchronised with the network,"
                    " %n object(s) to be downloaded. If you quit now,"
                    " it may cause delivery delays. Wait until the"
                    " synchronisation finishes?", None,
                    QtCore.QCoreApplication.CodecForTr, pendingDownload()
                ),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Yes:
                self.wait = waitForSync = True
            elif reply == QtGui.QMessageBox.Cancel:
                return

        if state.statusIconColor == 'red' and not BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'dontconnect'):
            reply = QtGui.QMessageBox.question(
                self, _translate("MainWindow", "Not connected"),
                _translate(
                    "MainWindow",
                    "Bitmessage isn't connected to the network. If you"
                    " quit now, it may cause delivery delays. Wait until"
                    " connected and the synchronisation finishes?"
                ),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Yes:
                waitForConnection = True
                self.wait = waitForSync = True
            elif reply == QtGui.QMessageBox.Cancel:
                return

        self.quitAccepted = True

        self.updateStatusBar(_translate(
            "MainWindow", "Shutting down PyBitmessage... %1%").arg(0))

        if waitForConnection:
            self.updateStatusBar(_translate(
                "MainWindow", "Waiting for network connection..."))
            while state.statusIconColor == 'red':
                time.sleep(0.5)
                QtCore.QCoreApplication.processEvents(
                    QtCore.QEventLoop.AllEvents, 1000
                )

        # this probably will not work correctly, because there is a delay
        # between the status icon turning red and inventory exchange,
        # but it's better than nothing.
        if waitForSync:
            self.updateStatusBar(_translate(
                "MainWindow", "Waiting for finishing synchronisation..."))
            while pendingDownload() > 0:
                time.sleep(0.5)
                QtCore.QCoreApplication.processEvents(
                    QtCore.QEventLoop.AllEvents, 1000
                )

        if waitForPow:
            # check if PoW queue empty
            maxWorkerQueue = 0
            curWorkerQueue = powQueueSize()
            while curWorkerQueue > 0:
                # worker queue size
                curWorkerQueue = powQueueSize()
                if curWorkerQueue > maxWorkerQueue:
                    maxWorkerQueue = curWorkerQueue
                if curWorkerQueue > 0:
                    self.updateStatusBar(_translate(
                        "MainWindow", "Waiting for PoW to finish... %1%"
                    ).arg(50 * (maxWorkerQueue - curWorkerQueue) /
                          maxWorkerQueue))
                    time.sleep(0.5)
                    QtCore.QCoreApplication.processEvents(
                        QtCore.QEventLoop.AllEvents, 1000
                    )

            self.updateStatusBar(_translate(
                "MainWindow", "Shutting down Pybitmessage... %1%").arg(50))

            QtCore.QCoreApplication.processEvents(
                QtCore.QEventLoop.AllEvents, 1000
            )
            if maxWorkerQueue > 0:
                # a bit of time so that the hashHolder is populated
                time.sleep(0.5)
            QtCore.QCoreApplication.processEvents(
                QtCore.QEventLoop.AllEvents, 1000
            )

            # check if upload (of objects created locally) pending
            self.updateStatusBar(_translate(
                "MainWindow", "Waiting for objects to be sent... %1%").arg(50))
            maxPendingUpload = max(1, pendingUpload())

            while pendingUpload() > 1:
                self.updateStatusBar(_translate(
                    "MainWindow",
                    "Waiting for objects to be sent... %1%"
                ).arg(int(50 + 20 * (pendingUpload() / maxPendingUpload))))
                time.sleep(0.5)
                QtCore.QCoreApplication.processEvents(
                    QtCore.QEventLoop.AllEvents, 1000
                )

            QtCore.QCoreApplication.processEvents(
                QtCore.QEventLoop.AllEvents, 1000
            )
        QtCore.QCoreApplication.processEvents(
            QtCore.QEventLoop.AllEvents, 1000
        )

        # save state and geometry self and all widgets
        self.updateStatusBar(_translate(
            "MainWindow", "Saving settings... %1%").arg(70))
        QtCore.QCoreApplication.processEvents(
            QtCore.QEventLoop.AllEvents, 1000
        )
        self.saveSettings()
        for attr, obj in self.ui.__dict__.iteritems():
            if hasattr(obj, "__class__") \
                    and isinstance(obj, settingsmixin.SettingsMixin):
                saveMethod = getattr(obj, "saveSettings", None)
                if callable(saveMethod):
                    obj.saveSettings()

        self.updateStatusBar(_translate(
            "MainWindow", "Shutting down core... %1%").arg(80))
        QtCore.QCoreApplication.processEvents(
            QtCore.QEventLoop.AllEvents, 1000
        )
        shutdown.doCleanShutdown()

        self.updateStatusBar(_translate(
            "MainWindow", "Stopping notifications... %1%").arg(90))
        self.tray.hide()

        self.updateStatusBar(_translate(
            "MainWindow", "Shutdown imminent... %1%").arg(100))

        logger.info("Shutdown complete")
        self.close()
        # FIXME: rewrite loops with timer instead
        if self.wait:
            self.destroy()
        app.quit()

    def closeEvent(self, event):
        """window close event"""
        event.ignore()
        trayonclose = BMConfigParser().safeGetBoolean(
            'bitmessagesettings', 'trayonclose')
        if trayonclose:
            self.appIndicatorHide()
        else:
            # custom quit method
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

        msgids = set()
        # modified = 0
        for row in tableWidget.selectedIndexes():
            currentRow = row.row()
            msgid = tableWidget.item(currentRow, 3).data()
            msgids.add(msgid)
            # if not tableWidget.item(currentRow, 0).unread:
            #     modified += 1
            self.updateUnreadStatus(tableWidget, currentRow, msgid, False)

        # for 1081
        idCount = len(msgids)
        # rowcount =
        sqlExecuteChunked(
            '''UPDATE inbox SET read=0 WHERE msgid IN ({0}) AND read=1''',
            idCount, *msgids
        )

        self.propagateUnreadCount()
        # tableWidget.selectRow(currentRow + 1)
        # This doesn't de-select the last message if you try to mark it
        # unread, but that doesn't interfere. Might not be necessary.
        # We could also select upwards, but then our problem would be
        # with the topmost message.
        # tableWidget.clearSelection() manages to mark the message
        # as read again.

    # Format predefined text on message reply.
    def quoted_text(self, message):
        if not BMConfigParser().safeGetBoolean('bitmessagesettings', 'replybelow'):
            return '\n\n------------------------------------------------------\n' + message

        quoteWrapper = textwrap.TextWrapper(
            replace_whitespace=False, initial_indent='> ',
            subsequent_indent='> ', break_long_words=False,
            break_on_hyphens=False)

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

    def setSendFromComboBox(self, address=None):
        if address is None:
            messagelist = self.getCurrentMessagelist()
            if not messagelist:
                return
            currentInboxRow = messagelist.currentRow()
            address = messagelist.item(currentInboxRow, 0).address
        for box in (
            self.ui.comboBoxSendFrom, self.ui.comboBoxSendFromBroadcast
        ):
            for i in range(box.count()):
                if str(box.itemData(i).toPyObject()) == address:
                    box.setCurrentIndex(i)
                    break
            else:
                box.setCurrentIndex(0)

    def on_action_InboxReplyChan(self):
        self.on_action_InboxReply(self.REPLY_TYPE_CHAN)

    def on_action_SentReply(self):
        self.on_action_InboxReply(self.REPLY_TYPE_UPD)

    def on_action_InboxReply(self, reply_type=None):
        """Handle any reply action depending on reply_type"""
        # pylint: disable=too-many-locals
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return

        if reply_type is None:
            reply_type = self.REPLY_TYPE_SENDER

        # save this to return back after reply is done
        self.replyFromTab = self.ui.tabWidget.currentIndex()

        column_to = 1 if reply_type == self.REPLY_TYPE_UPD else 0
        column_from = 0 if reply_type == self.REPLY_TYPE_UPD else 1

        currentInboxRow = tableWidget.currentRow()
        toAddressAtCurrentInboxRow = tableWidget.item(
            currentInboxRow, column_to).address
        acct = accountClass(toAddressAtCurrentInboxRow)
        fromAddressAtCurrentInboxRow = tableWidget.item(
            currentInboxRow, column_from).address
        msgid = tableWidget.item(currentInboxRow, 3).data()
        queryreturn = sqlQuery(
            "SELECT message FROM inbox WHERE msgid=?", msgid
        ) or sqlQuery("SELECT message FROM sent WHERE ackdata=?", msgid)
        if queryreturn != []:
            for row in queryreturn:
                messageAtCurrentInboxRow, = row
        acct.parseMessage(
            toAddressAtCurrentInboxRow, fromAddressAtCurrentInboxRow,
            tableWidget.item(currentInboxRow, 2).subject,
            messageAtCurrentInboxRow)
        widget = {
            'subject': self.ui.lineEditSubject,
            'from': self.ui.comboBoxSendFrom,
            'message': self.ui.textEditMessage
        }

        if toAddressAtCurrentInboxRow == str_broadcast_subscribers:
            self.ui.tabWidgetSend.setCurrentIndex(
                self.ui.tabWidgetSend.indexOf(self.ui.sendDirect)
            )
#            toAddressAtCurrentInboxRow = fromAddressAtCurrentInboxRow
        elif not BMConfigParser().has_section(toAddressAtCurrentInboxRow):
            QtGui.QMessageBox.information(
                self, _translate("MainWindow", "Address is gone"),
                _translate(
                    "MainWindow",
                    "Bitmessage cannot find your address %1. Perhaps you"
                    " removed it?"
                ).arg(toAddressAtCurrentInboxRow), QtGui.QMessageBox.Ok)
        elif not BMConfigParser().getboolean(
                toAddressAtCurrentInboxRow, 'enabled'):
            QtGui.QMessageBox.information(
                self, _translate("MainWindow", "Address disabled"),
                _translate(
                    "MainWindow",
                    "Error: The address from which you are trying to send"
                    " is disabled. You\'ll have to enable it on the"
                    " \'Your Identities\' tab before using it."
                ), QtGui.QMessageBox.Ok)
        else:
            self.setBroadcastEnablementDependingOnWhetherThisIsAMailingListAddress(toAddressAtCurrentInboxRow)
            broadcast_tab_index = self.ui.tabWidgetSend.indexOf(
                self.ui.sendBroadcast
            )
            if self.ui.tabWidgetSend.currentIndex() == broadcast_tab_index:
                widget = {
                    'subject': self.ui.lineEditSubjectBroadcast,
                    'from': self.ui.comboBoxSendFromBroadcast,
                    'message': self.ui.textEditMessageBroadcast
                }
                self.ui.tabWidgetSend.setCurrentIndex(broadcast_tab_index)
                toAddressAtCurrentInboxRow = fromAddressAtCurrentInboxRow
        if fromAddressAtCurrentInboxRow == \
            tableWidget.item(currentInboxRow, column_from).label or (
                isinstance(acct, GatewayAccount) and
                fromAddressAtCurrentInboxRow == acct.relayAddress):
            self.ui.lineEditTo.setText(str(acct.fromAddress))
        else:
            self.ui.lineEditTo.setText(
                tableWidget.item(currentInboxRow, column_from).accountString()
            )

        # If the previous message was to a chan then we should send our
        # reply to the chan rather than to the particular person who sent
        # the message.
        if acct.type == AccountMixin.CHAN and reply_type == self.REPLY_TYPE_CHAN:
            logger.debug(
                'Original sent to a chan. Setting the to address in the'
                ' reply to the chan address.')
            if toAddressAtCurrentInboxRow == \
                    tableWidget.item(currentInboxRow, column_to).label:
                self.ui.lineEditTo.setText(str(toAddressAtCurrentInboxRow))
            else:
                self.ui.lineEditTo.setText(
                    tableWidget.item(currentInboxRow, column_to).accountString()
                )

        self.setSendFromComboBox(toAddressAtCurrentInboxRow)

        quotedText = self.quoted_text(
            unicode(messageAtCurrentInboxRow, 'utf-8', 'replace'))
        widget['message'].setPlainText(quotedText)
        if acct.subject[0:3] in ('Re:', 'RE:'):
            widget['subject'].setText(
                tableWidget.item(currentInboxRow, 2).label)
        else:
            widget['subject'].setText(
                'Re: ' + tableWidget.item(currentInboxRow, 2).label)
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.send)
        )
        widget['message'].setFocus()

    def on_action_InboxAddSenderToAddressBook(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentInboxRow = tableWidget.currentRow()
        addressAtCurrentInboxRow = tableWidget.item(
            currentInboxRow, 1).data(QtCore.Qt.UserRole)
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.send)
        )
        self.click_pushButtonAddAddressBook(
            dialogs.AddAddressDialog(self, addressAtCurrentInboxRow))

    def on_action_InboxAddSenderToBlackList(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentInboxRow = tableWidget.currentRow()
        addressAtCurrentInboxRow = tableWidget.item(
            currentInboxRow, 1).data(QtCore.Qt.UserRole)
        recipientAddress = tableWidget.item(
            currentInboxRow, 0).data(QtCore.Qt.UserRole)
        # Let's make sure that it isn't already in the address book
        queryreturn = sqlQuery('''select * from blacklist where address=?''',
                               addressAtCurrentInboxRow)
        if queryreturn == []:
            label = "\"" + tableWidget.item(currentInboxRow, 2).subject + "\" in " + BMConfigParser().get(recipientAddress, "label")
            sqlExecute('''INSERT INTO blacklist VALUES (?,?, ?)''',
                       label,
                       addressAtCurrentInboxRow, True)
            self.ui.blackwhitelist.rerenderBlackWhiteList()
            self.updateStatusBar(_translate(
                "MainWindow",
                "Entry added to the blacklist. Edit the label to your liking.")
            )
        else:
            self.updateStatusBar(_translate(
                "MainWindow",
                "Error: You cannot add the same address to your blacklist"
                " twice. Try renaming the existing one if you want."))

    def deleteRowFromMessagelist(
        self, row=None, inventoryHash=None, ackData=None, messageLists=None
    ):
        if messageLists is None:
            messageLists = (
                self.ui.tableWidgetInbox,
                self.ui.tableWidgetInboxChans,
                self.ui.tableWidgetInboxSubscriptions
            )
        elif type(messageLists) not in (list, tuple):
            messageLists = (messageLists,)
        for messageList in messageLists:
            if row is not None:
                inventoryHash = messageList.item(row, 3).data()
                messageList.removeRow(row)
            elif inventoryHash is not None:
                for i in range(messageList.rowCount() - 1, -1, -1):
                    if messageList.item(i, 3).data() == inventoryHash:
                        messageList.removeRow(i)
            elif ackData is not None:
                for i in range(messageList.rowCount() - 1, -1, -1):
                    if messageList.item(i, 3).data() == ackData:
                        messageList.removeRow(i)

    # Send item on the Inbox tab to trash
    def on_action_InboxTrash(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentRow = 0
        folder = self.getCurrentFolder()
        shifted = QtGui.QApplication.queryKeyboardModifiers() \
            & QtCore.Qt.ShiftModifier
        tableWidget.setUpdatesEnabled(False)
        inventoryHashesToTrash = set()
        # ranges in reversed order
        for r in sorted(
            tableWidget.selectedRanges(), key=lambda r: r.topRow()
        )[::-1]:
            for i in range(r.bottomRow() - r.topRow() + 1):
                inventoryHashesToTrash.add(
                    tableWidget.item(r.topRow() + i, 3).data())
            currentRow = r.topRow()
            self.getCurrentMessageTextedit().setText("")
            tableWidget.model().removeRows(
                r.topRow(), r.bottomRow() - r.topRow() + 1)
        idCount = len(inventoryHashesToTrash)
        sqlExecuteChunked(
            ("DELETE FROM inbox" if folder == "trash" or shifted else
             "UPDATE inbox SET folder='trash', read=1") +
            " WHERE msgid IN ({0})", idCount, *inventoryHashesToTrash)
        tableWidget.selectRow(0 if currentRow == 0 else currentRow - 1)
        tableWidget.setUpdatesEnabled(True)
        self.propagateUnreadCount(folder)
        self.updateStatusBar(_translate("MainWindow", "Moved items to trash."))

    def on_action_TrashUndelete(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentRow = 0
        tableWidget.setUpdatesEnabled(False)
        inventoryHashesToTrash = set()
        # ranges in reversed order
        for r in sorted(
            tableWidget.selectedRanges(), key=lambda r: r.topRow()
        )[::-1]:
            for i in range(r.bottomRow() - r.topRow() + 1):
                inventoryHashesToTrash.add(
                    tableWidget.item(r.topRow() + i, 3).data())
            currentRow = r.topRow()
            self.getCurrentMessageTextedit().setText("")
            tableWidget.model().removeRows(
                r.topRow(), r.bottomRow() - r.topRow() + 1)
        tableWidget.selectRow(0 if currentRow == 0 else currentRow - 1)
        idCount = len(inventoryHashesToTrash)
        sqlExecuteChunked(
            "UPDATE inbox SET folder='inbox' WHERE msgid IN({0})",
            idCount, *inventoryHashesToTrash)
        tableWidget.selectRow(0 if currentRow == 0 else currentRow - 1)
        tableWidget.setUpdatesEnabled(True)
        self.propagateUnreadCount()
        self.updateStatusBar(_translate("MainWindow", "Undeleted item."))

    def on_action_InboxSaveMessageAs(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        currentInboxRow = tableWidget.currentRow()
        try:
            subjectAtCurrentInboxRow = str(tableWidget.item(
                currentInboxRow, 2).data(QtCore.Qt.UserRole))
        except:
            subjectAtCurrentInboxRow = ''

        # Retrieve the message data out of the SQL database
        msgid = tableWidget.item(currentInboxRow, 3).data()
        queryreturn = sqlQuery(
            '''select message from inbox where msgid=?''', msgid)
        if queryreturn != []:
            for row in queryreturn:
                message, = row

        defaultFilename = "".join(x for x in subjectAtCurrentInboxRow if x.isalnum()) + '.txt'
        filename = QtGui.QFileDialog.getSaveFileName(self, _translate("MainWindow","Save As..."), defaultFilename, "Text files (*.txt);;All files (*.*)")
        if filename == '':
            return
        try:
            f = open(filename, 'w')
            f.write(message)
            f.close()
        except Exception:
            logger.exception('Message not saved', exc_info=True)
            self.updateStatusBar(_translate("MainWindow", "Write error."))

    # Send item on the Sent tab to trash
    def on_action_SentTrash(self):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return
        folder = self.getCurrentFolder()
        shifted = QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ShiftModifier
        while tableWidget.selectedIndexes() != []:
            currentRow = tableWidget.selectedIndexes()[0].row()
            ackdataToTrash = tableWidget.item(currentRow, 3).data()
            sqlExecute(
                "DELETE FROM sent" if folder == "trash" or shifted else
                "UPDATE sent SET folder='trash'"
                " WHERE ackdata = ?", ackdataToTrash
            )
            self.getCurrentMessageTextedit().setPlainText("")
            tableWidget.removeRow(currentRow)
            self.updateStatusBar(_translate(
                "MainWindow", "Moved items to trash."))

        self.ui.tableWidgetInbox.selectRow(
            currentRow if currentRow == 0 else currentRow - 1)

    def on_action_ForceSend(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetInbox.item(
            currentRow, 0).data(QtCore.Qt.UserRole)
        toRipe = decodeAddress(addressAtCurrentRow)[3]
        sqlExecute(
            '''UPDATE sent SET status='forcepow' WHERE toripe=? AND status='toodifficult' and folder='sent' ''',
            toRipe)
        queryreturn = sqlQuery('''select ackdata FROM sent WHERE status='forcepow' ''')
        for row in queryreturn:
            ackdata, = row
            queues.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                ackdata, 'Overriding maximum-difficulty setting. Work queued.')))
        queues.workerQueue.put(('sendmessage', ''))

    def on_action_SentClipboard(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetInbox.item(
            currentRow, 0).data(QtCore.Qt.UserRole)
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))

    # Group of functions for the Address Book dialog box
    def on_action_AddressBookNew(self):
        self.click_pushButtonAddAddressBook()

    def on_action_AddressBookDelete(self):
        while self.ui.tableWidgetAddressBook.selectedIndexes() != []:
            currentRow = self.ui.tableWidgetAddressBook.selectedIndexes()[
                0].row()
            item = self.ui.tableWidgetAddressBook.item(currentRow, 0)
            sqlExecute(
                'DELETE FROM addressbook WHERE address=?', item.address)
            self.ui.tableWidgetAddressBook.removeRow(currentRow)
        self.rerenderMessagelistFromLabels()
        self.rerenderMessagelistToLabels()

    def on_action_AddressBookClipboard(self):
        addresses_string = ''
        for item in self.getAddressbookSelectedItems():
            if addresses_string == '':
                addresses_string = item.address
            else:
                addresses_string += ', ' + item.address
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(addresses_string)

    def on_action_AddressBookSend(self):
        selected_items = self.getAddressbookSelectedItems()

        if not selected_items:  # FIXME: impossible
            return self.updateStatusBar(_translate(
                "MainWindow", "No addresses selected."))

        addresses_string = unicode(
            self.ui.lineEditTo.text().toUtf8(), 'utf-8')
        for item in selected_items:
            address_string = item.accountString()
            if not addresses_string:
                addresses_string = address_string
            else:
                addresses_string += '; ' + address_string

        self.ui.lineEditTo.setText(addresses_string)
        self.statusbar.clearMessage()
        self.ui.tabWidget.setCurrentIndex(
            self.ui.tabWidget.indexOf(self.ui.send)
        )

    def on_action_AddressBookSubscribe(self):
        for item in self.getAddressbookSelectedItems():
            # Then subscribe to it...
            # provided it's not already in the address book
            if shared.isAddressInMySubscriptionsList(item.address):
                self.updateStatusBar(_translate(
                    "MainWindow",
                    "Error: You cannot add the same address to your"
                    " subscriptions twice. Perhaps rename the existing"
                    " one if you want."))
                continue
            self.addSubscription(item.address, item.label)
            self.ui.tabWidget.setCurrentIndex(
                self.ui.tabWidget.indexOf(self.ui.subscriptions)
            )

    def on_context_menuAddressBook(self, point):
        self.popMenuAddressBook = QtGui.QMenu(self)
        self.popMenuAddressBook.addAction(self.actionAddressBookSend)
        self.popMenuAddressBook.addAction(self.actionAddressBookClipboard)
        self.popMenuAddressBook.addAction(self.actionAddressBookSubscribe)
        self.popMenuAddressBook.addAction(self.actionAddressBookSetAvatar)
        self.popMenuAddressBook.addAction(self.actionAddressBookSetSound)
        self.popMenuAddressBook.addSeparator()
        self.popMenuAddressBook.addAction(self.actionAddressBookNew)
        normal = True
        selected_items = self.getAddressbookSelectedItems()
        for item in selected_items:
            if item.type != AccountMixin.NORMAL:
                normal = False
                break
        if normal:
            # only if all selected addressbook items are normal, allow delete
            self.popMenuAddressBook.addAction(self.actionAddressBookDelete)
        if len(selected_items) == 1:
            self._contact_selected = selected_items.pop()
            self.popMenuAddressBook.addSeparator()
            for plugin in self.menu_plugins['address']:
                self.popMenuAddressBook.addAction(plugin)
        self.popMenuAddressBook.exec_(
            self.ui.tableWidgetAddressBook.mapToGlobal(point))

    # Group of functions for the Subscriptions dialog box
    def on_action_SubscriptionsNew(self):
        self.click_pushButtonAddSubscription()

    def on_action_SubscriptionsDelete(self):
        if QtGui.QMessageBox.question(
                self, "Delete subscription?",
                _translate(
                    "MainWindow",
                    "If you delete the subscription, messages that you"
                    " already received will become inaccessible. Maybe"
                    " you can consider disabling the subscription instead."
                    " Disabled subscriptions will not receive new"
                    " messages, but you can still view messages you"
                    " already received.\n\nAre you sure you want to"
                    " delete the subscription?"
                ), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        ) != QtGui.QMessageBox.Yes:
            return
        address = self.getCurrentAccount()
        sqlExecute('''DELETE FROM subscriptions WHERE address=?''',
                   address)
        self.rerenderTabTreeSubscriptions()
        self.rerenderMessagelistFromLabels()
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
        currentItem = self.getCurrentItem()
        self.popMenuSubscriptions = QtGui.QMenu(self)
        if isinstance(currentItem, Ui_AddressWidget):
            self.popMenuSubscriptions.addAction(self.actionsubscriptionsNew)
            self.popMenuSubscriptions.addAction(self.actionsubscriptionsDelete)
            self.popMenuSubscriptions.addSeparator()
            if currentItem.isEnabled:
                self.popMenuSubscriptions.addAction(self.actionsubscriptionsDisable)
            else:
                self.popMenuSubscriptions.addAction(self.actionsubscriptionsEnable)
            self.popMenuSubscriptions.addAction(self.actionsubscriptionsSetAvatar)
            self.popMenuSubscriptions.addSeparator()
            self.popMenuSubscriptions.addAction(self.actionsubscriptionsClipboard)
            self.popMenuSubscriptions.addAction(self.actionsubscriptionsSend)
            self.popMenuSubscriptions.addSeparator()

            self._contact_selected = currentItem
            # preloaded gui.menu plugins with prefix 'address'
            for plugin in self.menu_plugins['address']:
                self.popMenuSubscriptions.addAction(plugin)
            self.popMenuSubscriptions.addSeparator()
        if self.getCurrentFolder() != 'sent':
            self.popMenuSubscriptions.addAction(self.actionMarkAllRead)
        if self.popMenuSubscriptions.isEmpty():
            return
        self.popMenuSubscriptions.exec_(
            self.ui.treeWidgetSubscriptions.mapToGlobal(point))

    def widgetConvert(self, widget):
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
        currentIndex = self.ui.tabWidget.currentIndex()
        treeWidgetList = (
            self.ui.treeWidgetYourIdentities,
            False,
            self.ui.treeWidgetSubscriptions,
            self.ui.treeWidgetChans
        )
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
        currentIndex = self.ui.tabWidget.currentIndex()
        messagelistList = (
            self.ui.tableWidgetInbox,
            False,
            self.ui.tableWidgetInboxSubscriptions,
            self.ui.tableWidgetInboxChans,
        )
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return messagelistList[currentIndex]

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
                return messagelist.item(currentRow, 3).data()

    def getCurrentMessageTextedit(self):
        currentIndex = self.ui.tabWidget.currentIndex()
        messagelistList = (
            self.ui.textEditInboxMessage,
            False,
            self.ui.textEditInboxMessageSubscriptions,
            self.ui.textEditInboxMessageChans,
        )
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return messagelistList[currentIndex]

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

    def getCurrentSearchLine(self, currentIndex=None, retObj=False):
        if currentIndex is None:
            currentIndex = self.ui.tabWidget.currentIndex()
        messagelistList = (
            self.ui.inboxSearchLineEdit,
            False,
            self.ui.inboxSearchLineEditSubscriptions,
            self.ui.inboxSearchLineEditChans,
        )
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return (
                messagelistList[currentIndex] if retObj
                else messagelistList[currentIndex].text().toUtf8().data())

    def getCurrentSearchOption(self, currentIndex=None):
        if currentIndex is None:
            currentIndex = self.ui.tabWidget.currentIndex()
        messagelistList = (
            self.ui.inboxSearchOption,
            False,
            self.ui.inboxSearchOptionSubscriptions,
            self.ui.inboxSearchOptionChans,
        )
        if currentIndex >= 0 and currentIndex < len(messagelistList):
            return messagelistList[currentIndex].currentText()

    # Group of functions for the Your Identities dialog box
    def getCurrentItem(self, treeWidget=None):
        if treeWidget is None:
            treeWidget = self.getCurrentTreeWidget()
        if treeWidget:
            return treeWidget.currentItem()

    def getCurrentAccount(self, treeWidget=None):
        currentItem = self.getCurrentItem(treeWidget)
        if currentItem:
            return currentItem.address

    def getCurrentFolder(self, treeWidget=None):
        currentItem = self.getCurrentItem(treeWidget)
        try:
            return currentItem.folderName
        except AttributeError:
            pass

    def setCurrentItemColor(self, color):
        currentItem = self.getCurrentItem()
        if currentItem:
            brush = QtGui.QBrush()
            brush.setStyle(QtCore.Qt.NoBrush)
            brush.setColor(color)
            currentItem.setForeground(0, brush)

    def getAddressbookSelectedItems(self):
        return [
            self.ui.tableWidgetAddressBook.item(i.row(), 0)
            for i in self.ui.tableWidgetAddressBook.selectedIndexes()
            if i.column() == 0
        ]

    def on_action_YourIdentitiesNew(self):
        self.click_NewAddressDialog()

    def on_action_YourIdentitiesDelete(self):
        account = self.getCurrentItem()
        if account.type == AccountMixin.NORMAL:
            return  # maybe in the future
        elif account.type == AccountMixin.CHAN:
            if QtGui.QMessageBox.question(
                    self, "Delete channel?",
                    _translate(
                        "MainWindow",
                        "If you delete the channel, messages that you"
                        " already received will become inaccessible."
                        " Maybe you can consider disabling the channel"
                        " instead. Disabled channels will not receive new"
                        " messages, but you can still view messages you"
                        " already received.\n\nAre you sure you want to"
                        " delete the channel?"
                    ), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            ) == QtGui.QMessageBox.Yes:
                BMConfigParser().remove_section(str(account.address))
            else:
                return
        else:
            return
        BMConfigParser().save()
        shared.reloadMyAddressHashes()
        self.rerenderAddressBook()
        self.rerenderComboBoxSendFrom()
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
        BMConfigParser().set(address, 'enabled', 'true')
        BMConfigParser().save()
        shared.reloadMyAddressHashes()
        self.rerenderAddressBook()

    def on_action_Disable(self):
        address = self.getCurrentAccount()
        self.disableIdentity(address)
        account = self.getCurrentItem()
        account.setEnabled(False)

    def disableIdentity(self, address):
        BMConfigParser().set(str(address), 'enabled', 'false')
        BMConfigParser().save()
        shared.reloadMyAddressHashes()
        self.rerenderAddressBook()

    def on_action_Clipboard(self):
        address = self.getCurrentAccount()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(address))

    def on_action_ClipboardMessagelist(self):
        tableWidget = self.getCurrentMessagelist()
        currentColumn = tableWidget.currentColumn()
        currentRow = tableWidget.currentRow()
        currentFolder = self.getCurrentFolder()
        if currentColumn not in (0, 1, 2):  # to, from, subject
            currentColumn = 0 if currentFolder == "sent" else 1

        if currentFolder == "sent":
            myAddress = tableWidget.item(currentRow, 1).data(QtCore.Qt.UserRole)
            otherAddress = tableWidget.item(currentRow, 0).data(QtCore.Qt.UserRole)
        else:
            myAddress = tableWidget.item(currentRow, 0).data(QtCore.Qt.UserRole)
            otherAddress = tableWidget.item(currentRow, 1).data(QtCore.Qt.UserRole)
        account = accountClass(myAddress)
        if isinstance(account, GatewayAccount) and otherAddress == account.relayAddress and (
            (currentColumn in [0, 2] and self.getCurrentFolder() == "sent") or
            (currentColumn in [1, 2] and self.getCurrentFolder() != "sent")):
            text = str(tableWidget.item(currentRow, currentColumn).label)
        else:
            text = tableWidget.item(currentRow, currentColumn).data(QtCore.Qt.UserRole)

        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(text)

    # set avatar functions
    def on_action_TreeWidgetSetAvatar(self):
        address = self.getCurrentAccount()
        self.setAvatar(address)

    def on_action_AddressBookSetAvatar(self):
        self.on_action_SetAvatar(self.ui.tableWidgetAddressBook)

    def on_action_SetAvatar(self, thisTableWidget):
        currentRow = thisTableWidget.currentRow()
        addressAtCurrentRow = thisTableWidget.item(
            currentRow, 1).text()
        setToIdenticon = not self.setAvatar(addressAtCurrentRow)
        if setToIdenticon:
            thisTableWidget.item(
                currentRow, 0).setIcon(avatarize(addressAtCurrentRow))

    # TODO: reuse utils
    def setAvatar(self, addressAtCurrentRow):
        if not os.path.exists(state.appdata + 'avatars/'):
            os.makedirs(state.appdata + 'avatars/')
        hash = hashlib.md5(addBMIfNotPresent(addressAtCurrentRow)).hexdigest()
        extensions = [
            'PNG', 'GIF', 'JPG', 'JPEG', 'SVG', 'BMP', 'MNG', 'PBM',
            'PGM', 'PPM', 'TIFF', 'XBM', 'XPM', 'TGA']

        names = {
            'BMP': 'Windows Bitmap',
            'GIF': 'Graphic Interchange Format',
            'JPG': 'Joint Photographic Experts Group',
            'JPEG': 'Joint Photographic Experts Group',
            'MNG': 'Multiple-image Network Graphics',
            'PNG': 'Portable Network Graphics',
            'PBM': 'Portable Bitmap',
            'PGM': 'Portable Graymap',
            'PPM': 'Portable Pixmap',
            'TIFF': 'Tagged Image File Format',
            'XBM': 'X11 Bitmap',
            'XPM': 'X11 Pixmap',
            'SVG': 'Scalable Vector Graphics',
            'TGA': 'Targa Image Format'}
        filters = []
        all_images_filter = []
        current_files = []
        for ext in extensions:
            filters += [names[ext] + ' (*.' + ext.lower() + ')']
            all_images_filter += ['*.' + ext.lower()]
            upper = state.appdata + 'avatars/' + hash + '.' + ext.upper()
            lower = state.appdata + 'avatars/' + hash + '.' + ext.lower()
            if os.path.isfile(lower):
                current_files += [lower]
            elif os.path.isfile(upper):
                current_files += [upper]
        filters[0:0] = ['Image files (' + ' '.join(all_images_filter) + ')']
        filters[1:1] = ['All files (*.*)']
        sourcefile = QtGui.QFileDialog.getOpenFileName(
            self, _translate("MainWindow", "Set avatar..."),
            filter=';;'.join(filters)
        )
        # determine the correct filename (note that avatars don't use the suffix)
        destination = state.appdata + 'avatars/' + hash + '.' + sourcefile.split('.')[-1]
        exists = QtCore.QFile.exists(destination)
        if sourcefile == '':
            # ask for removal of avatar
            if exists | (len(current_files) > 0):
                displayMsg = _translate(
                    "MainWindow", "Do you really want to remove this avatar?")
                overwrite = QtGui.QMessageBox.question(
                    self, 'Message', displayMsg,
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            else:
                overwrite = QtGui.QMessageBox.No
        else:
            # ask whether to overwrite old avatar
            if exists | (len(current_files) > 0):
                displayMsg = _translate(
                    "MainWindow",
                    "You have already set an avatar for this address."
                    " Do you really want to overwrite it?")
                overwrite = QtGui.QMessageBox.question(
                    self, 'Message', displayMsg,
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
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
            self.rerenderMessagelistFromLabels()
            self.rerenderMessagelistToLabels()
            self.ui.blackwhitelist.rerenderBlackWhiteList()
            # generate identicon
            return False

        return True

    def on_action_AddressBookSetSound(self):
        widget = self.ui.tableWidgetAddressBook
        self.setAddressSound(widget.item(widget.currentRow(), 0).text())

    def setAddressSound(self, addr):
        filters = [unicode(_translate(
            "MainWindow", "Sound files (%s)" %
            ' '.join(['*%s%s' % (os.extsep, ext) for ext in sound.extensions])
        ))]
        sourcefile = unicode(QtGui.QFileDialog.getOpenFileName(
            self, _translate("MainWindow", "Set notification sound..."),
            filter=';;'.join(filters)
        ))

        if not sourcefile:
            return

        destdir = os.path.join(state.appdata, 'sounds')
        destfile = unicode(addr) + os.path.splitext(sourcefile)[-1]
        destination = os.path.join(destdir, destfile)

        if sourcefile == destination:
            return

        pattern = destfile.lower()
        for item in os.listdir(destdir):
            if item.lower() == pattern:
                overwrite = QtGui.QMessageBox.question(
                    self, _translate("MainWindow", "Message"),
                    _translate(
                        "MainWindow",
                        "You have already set a notification sound"
                        " for this address book entry."
                        " Do you really want to overwrite it?"),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No
                ) == QtGui.QMessageBox.Yes
                if overwrite:
                    QtCore.QFile.remove(os.path.join(destdir, item))
                break

        if not QtCore.QFile.copy(sourcefile, destination):
            logger.error(
                'couldn\'t copy %s to %s', sourcefile, destination)

    def on_context_menuYourIdentities(self, point):
        currentItem = self.getCurrentItem()
        self.popMenuYourIdentities = QtGui.QMenu(self)
        if isinstance(currentItem, Ui_AddressWidget):
            self.popMenuYourIdentities.addAction(self.actionNewYourIdentities)
            self.popMenuYourIdentities.addSeparator()
            self.popMenuYourIdentities.addAction(self.actionClipboardYourIdentities)
            self.popMenuYourIdentities.addSeparator()
            if currentItem.isEnabled:
                self.popMenuYourIdentities.addAction(self.actionDisableYourIdentities)
            else:
                self.popMenuYourIdentities.addAction(self.actionEnableYourIdentities)
            self.popMenuYourIdentities.addAction(self.actionSetAvatarYourIdentities)
            self.popMenuYourIdentities.addAction(self.actionSpecialAddressBehaviorYourIdentities)
            self.popMenuYourIdentities.addAction(self.actionEmailGateway)
            self.popMenuYourIdentities.addSeparator()
            if currentItem.type != AccountMixin.ALL:
                self._contact_selected = currentItem
                # preloaded gui.menu plugins with prefix 'address'
                for plugin in self.menu_plugins['address']:
                    self.popMenuYourIdentities.addAction(plugin)
            self.popMenuYourIdentities.addSeparator()
        if self.getCurrentFolder() != 'sent':
            self.popMenuYourIdentities.addAction(self.actionMarkAllRead)
        if self.popMenuYourIdentities.isEmpty():
            return
        self.popMenuYourIdentities.exec_(
            self.ui.treeWidgetYourIdentities.mapToGlobal(point))

    # TODO make one popMenu
    def on_context_menuChan(self, point):
        currentItem = self.getCurrentItem()
        self.popMenu = QtGui.QMenu(self)
        if isinstance(currentItem, Ui_AddressWidget):
            self.popMenu.addAction(self.actionNew)
            self.popMenu.addAction(self.actionDelete)
            self.popMenu.addSeparator()
            if currentItem.isEnabled:
                self.popMenu.addAction(self.actionDisable)
            else:
                self.popMenu.addAction(self.actionEnable)
            self.popMenu.addAction(self.actionSetAvatar)
            self.popMenu.addSeparator()
            self.popMenu.addAction(self.actionClipboard)
            self.popMenu.addAction(self.actionSend)
            self.popMenu.addSeparator()
            self._contact_selected = currentItem
            # preloaded gui.menu plugins with prefix 'address'
            for plugin in self.menu_plugins['address']:
                self.popMenu.addAction(plugin)
            self.popMenu.addSeparator()
        if self.getCurrentFolder() != 'sent':
            self.popMenu.addAction(self.actionMarkAllRead)
        if self.popMenu.isEmpty():
            return
        self.popMenu.exec_(
            self.ui.treeWidgetChans.mapToGlobal(point))

    def on_context_menuInbox(self, point):
        tableWidget = self.getCurrentMessagelist()
        if not tableWidget:
            return

        currentFolder = self.getCurrentFolder()
        if currentFolder == 'sent':
            self.on_context_menuSent(point)
            return

        self.popMenuInbox = QtGui.QMenu(self)
        self.popMenuInbox.addAction(self.actionForceHtml)
        self.popMenuInbox.addAction(self.actionMarkUnread)
        self.popMenuInbox.addSeparator()
        currentRow = tableWidget.currentRow()
        account = accountClass(
            tableWidget.item(currentRow, 0).data(QtCore.Qt.UserRole))

        if account.type == AccountMixin.CHAN:
            self.popMenuInbox.addAction(self.actionReplyChan)
        self.popMenuInbox.addAction(self.actionReply)
        self.popMenuInbox.addAction(self.actionAddSenderToAddressBook)
        self.actionClipboardMessagelist = self.ui.inboxContextMenuToolbar.addAction(
            _translate("MainWindow", "Copy subject to clipboard")
            if tableWidget.currentColumn() == 2 else
            _translate("MainWindow", "Copy address to clipboard"),
            self.on_action_ClipboardMessagelist)
        self.popMenuInbox.addAction(self.actionClipboardMessagelist)
        # pylint: disable=no-member
        self._contact_selected = tableWidget.item(currentRow, 1)
        # preloaded gui.menu plugins with prefix 'address'
        for plugin in self.menu_plugins['address']:
            self.popMenuInbox.addAction(plugin)
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
        currentRow = self.ui.tableWidgetInbox.currentRow()
        self.popMenuSent = QtGui.QMenu(self)
        self.popMenuSent.addAction(self.actionSentClipboard)
        self._contact_selected = self.ui.tableWidgetInbox.item(currentRow, 0)
        # preloaded gui.menu plugins with prefix 'address'
        for plugin in self.menu_plugins['address']:
            self.popMenuSent.addAction(plugin)
        self.popMenuSent.addSeparator()
        self.popMenuSent.addAction(self.actionTrashSentMessage)
        self.popMenuSent.addAction(self.actionSentReply)

        # Check to see if this item is toodifficult and display an additional
        # menu option (Force Send) if it is.
        if currentRow >= 0:
            ackData = self.ui.tableWidgetInbox.item(currentRow, 3).data()
            queryreturn = sqlQuery('''SELECT status FROM sent where ackdata=?''', ackData)
            for row in queryreturn:
                status, = row
            if status == 'toodifficult':
                self.popMenuSent.addAction(self.actionForceSend)

        self.popMenuSent.exec_(self.ui.tableWidgetInbox.mapToGlobal(point))

    def inboxSearchLineEditUpdated(self, text):
        # dynamic search for too short text is slow
        text = text.toUtf8()
        if 0 < len(text) < 3:
            return
        messagelist = self.getCurrentMessagelist()
        if messagelist:
            searchOption = self.getCurrentSearchOption()
            account = self.getCurrentAccount()
            folder = self.getCurrentFolder()
            self.loadMessagelist(
                messagelist, account, folder, searchOption, text)

    def inboxSearchLineEditReturnPressed(self):
        logger.debug("Search return pressed")
        searchLine = self.getCurrentSearchLine()
        messagelist = self.getCurrentMessagelist()
        if messagelist and len(str(searchLine)) < 3:
            searchOption = self.getCurrentSearchOption()
            account = self.getCurrentAccount()
            folder = self.getCurrentFolder()
            self.loadMessagelist(
                messagelist, account, folder, searchOption, searchLine)
            messagelist.setFocus()

    def treeWidgetItemClicked(self):
        messagelist = self.getCurrentMessagelist()
        if not messagelist:
            return
        messageTextedit = self.getCurrentMessageTextedit()
        if messageTextedit:
            messageTextedit.setPlainText("")
        account = self.getCurrentAccount()
        folder = self.getCurrentFolder()
        # refresh count indicator
        self.propagateUnreadCount(folder)
        self.loadMessagelist(
            messagelist, account, folder,
            self.getCurrentSearchOption(), self.getCurrentSearchLine())

    def treeWidgetItemChanged(self, item, column):
        # only for manual edits. automatic edits (setText) are ignored
        if column != 0:
            return
        # only account names of normal addresses (no chans/mailinglists)
        if (not isinstance(item, Ui_AddressWidget)) or (not self.getCurrentTreeWidget()) or self.getCurrentTreeWidget().currentItem() is None:
            return
        # not visible
        if (not self.getCurrentItem()) or (not isinstance(self.getCurrentItem(), Ui_AddressWidget)):
            return
        # only currently selected item
        if item.address != self.getCurrentAccount():
            return
        # "All accounts" can't be renamed
        if item.type == AccountMixin.ALL:
            return

        newLabel = unicode(item.text(0), 'utf-8', 'ignore')
        oldLabel = item.defaultLabel()

        # unchanged, do not do anything either
        if newLabel == oldLabel:
            return

        # recursion prevention
        if self.recurDepth > 0:
            return

        self.recurDepth += 1
        if item.type == AccountMixin.NORMAL or item.type == AccountMixin.MAILINGLIST:
            self.rerenderComboBoxSendFromBroadcast()
        if item.type == AccountMixin.NORMAL or item.type == AccountMixin.CHAN:
            self.rerenderComboBoxSendFrom()
        self.rerenderMessagelistFromLabels()
        if item.type != AccountMixin.SUBSCRIPTION:
            self.rerenderMessagelistToLabels()
        if item.type in (AccountMixin.NORMAL, AccountMixin.CHAN, AccountMixin.SUBSCRIPTION):
            self.rerenderAddressBook()
        self.recurDepth -= 1

    def tableWidgetInboxItemClicked(self):
        messageTextedit = self.getCurrentMessageTextedit()
        if not messageTextedit:
            return

        msgid = self.getCurrentMessageId()
        folder = self.getCurrentFolder()
        if msgid:
            queryreturn = sqlQuery(
                '''SELECT message FROM %s WHERE %s=?''' % (
                    ('sent', 'ackdata') if folder == 'sent'
                    else ('inbox', 'msgid')
                ), msgid
            )

        try:
            message = queryreturn[-1][0]
        except NameError:
            message = ""
        except IndexError:
            message = _translate(
                "MainWindow",
                "Error occurred: could not load message from disk."
            )
        else:
            tableWidget = self.getCurrentMessagelist()
            currentRow = tableWidget.currentRow()
            # refresh
            if tableWidget.item(currentRow, 0).unread is True:
                self.updateUnreadStatus(tableWidget, currentRow, msgid)
            # propagate
            if folder != 'sent' and sqlExecute(
                '''UPDATE inbox SET read=1 WHERE msgid=? AND read=0''',
                msgid
            ) > 0:
                self.propagateUnreadCount()

        messageTextedit.setCurrentFont(QtGui.QFont())
        messageTextedit.setTextColor(QtGui.QColor())
        messageTextedit.setContent(message)

    def tableWidgetAddressBookItemChanged(self, item):
        if item.type == AccountMixin.CHAN:
            self.rerenderComboBoxSendFrom()
        self.rerenderMessagelistFromLabels()
        self.rerenderMessagelistToLabels()
        completerList = self.ui.lineEditTo.completer().model().stringList()
        for i in range(len(completerList)):
            if unicode(completerList[i]).endswith(" <" + item.address + ">"):
                completerList[i] = item.label + " <" + item.address + ">"
        self.ui.lineEditTo.completer().model().setStringList(completerList)

    def tabWidgetCurrentChanged(self, n):
        if n == self.ui.tabWidget.indexOf(self.ui.networkstatus):
            self.ui.networkstatus.startUpdate()
        else:
            self.ui.networkstatus.stopUpdate()

    def writeNewAddressToTable(self, label, address, streamNumber):
        self.rerenderTabTreeMessages()
        self.rerenderTabTreeSubscriptions()
        self.rerenderTabTreeChans()
        self.rerenderComboBoxSendFrom()
        self.rerenderComboBoxSendFromBroadcast()
        self.rerenderAddressBook()

    def updateStatusBar(self, data):
        try:
            message, option = data
        except ValueError:
            option = 0
            message = data
        except TypeError:
            logger.debug(
                'Invalid argument for updateStatusBar!', exc_info=True)

        if message != "":
            logger.info('Status bar: ' + message)

        if option == 1:
            self.statusbar.addImportant(message)
        else:
            self.statusbar.showMessage(message, 10000)

    def resetNamecoinConnection(self):
        namecoin.ensureNamecoinOptions()
        self.namecoin = namecoin.namecoinConnection()

        # Check to see whether we can connect to namecoin.
        # Hide the 'Fetch Namecoin ID' button if we can't.
        if BMConfigParser().safeGetBoolean(
            'bitmessagesettings', 'dontconnect'
        ) or self.namecoin.test()[0] == 'failed':
            logger.warning(
                'There was a problem testing for a Namecoin daemon.'
                ' Hiding the Fetch Namecoin ID button')
            self.ui.pushButtonFetchNamecoinID.hide()
        else:
            self.ui.pushButtonFetchNamecoinID.show()

    def initSettings(self):
        self.loadSettings()
        for attr, obj in self.ui.__dict__.iteritems():
            if hasattr(obj, "__class__") and \
                    isinstance(obj, settingsmixin.SettingsMixin):
                loadMethod = getattr(obj, "loadSettings", None)
                if callable(loadMethod):
                    obj.loadSettings()


app = None
myapp = None


class BitmessageQtApplication(QtGui.QApplication):
    """
    Listener to allow our Qt form to get focus when another instance of the
    application is open.

    Based off this nice reimplmentation of MySingleApplication:
    http://stackoverflow.com/a/12712362/2679626
    """

    # Unique identifier for this application
    uuid = '6ec0149b-96e1-4be1-93ab-1465fb3ebf7c'

    def __init__(self, *argv):
        super(BitmessageQtApplication, self).__init__(*argv)
        id = BitmessageQtApplication.uuid

        QtCore.QCoreApplication.setOrganizationName("PyBitmessage")
        QtCore.QCoreApplication.setOrganizationDomain("bitmessage.org")
        QtCore.QCoreApplication.setApplicationName("pybitmessageqt")

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
            # This should be ignored, singleinstance.py will take care of exiting me.
            pass
        else:
            # Nope, create a local server with this id and assign on_new_connection
            # for whenever a second instance tries to run focus the application.
            self.server = QLocalServer()
            self.server.listen(id)
            self.server.newConnection.connect(self.on_new_connection)

        self.setStyleSheet("QStatusBar::item { border: 0px solid black }")

    def __del__(self):
        if self.server:
            self.server.close()

    def on_new_connection(self):
        if myapp:
            myapp.appIndicatorShow()


def init():
    global app
    if not app:
        app = BitmessageQtApplication(sys.argv)
    return app


def run():
    global myapp
    app = init()
    myapp = MyForm()

    myapp.appIndicatorInit(app)

    if myapp._firstrun:
        myapp.showConnectDialog()  # ask the user if we may connect

#    try:
#        if BMConfigParser().get('bitmessagesettings', 'mailchuck') < 1:
#            myapp.showMigrationWizard(BMConfigParser().get('bitmessagesettings', 'mailchuck'))
#    except:
#        myapp.showMigrationWizard(0)

    # only show after wizards and connect dialogs have completed
    if not BMConfigParser().getboolean('bitmessagesettings', 'startintray'):
        myapp.show()

    app.exec_()
