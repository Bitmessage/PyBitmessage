from PyQt4 import QtCore, QtGui

import widgets
from addresses import addBMIfNotPresent
from bmconfigparser import config
from dialogs import AddAddressDialog
from helper_sql import sqlExecute, sqlQuery
from queues import UISignalQueue
from retranslateui import RetranslateMixin
from tr import _translate
from uisignaler import UISignaler
from utils import avatarize


class Blacklist(QtGui.QWidget, RetranslateMixin):
    def __init__(self, parent=None):
        super(Blacklist, self).__init__(parent)
        widgets.load('blacklist.ui', self)

        QtCore.QObject.connect(self.radioButtonBlacklist, QtCore.SIGNAL(
            "clicked()"), self.click_radioButtonBlacklist)
        QtCore.QObject.connect(self.radioButtonWhitelist, QtCore.SIGNAL(
            "clicked()"), self.click_radioButtonWhitelist)
        QtCore.QObject.connect(self.pushButtonAddBlacklist, QtCore.SIGNAL(
        "clicked()"), self.click_pushButtonAddBlacklist)

        self.init_blacklist_popup_menu()

        # Initialize blacklist
        QtCore.QObject.connect(self.tableWidgetBlacklist, QtCore.SIGNAL(
            "itemChanged(QTableWidgetItem *)"), self.tableWidgetBlacklistItemChanged)

        # Set the icon sizes for the identicons
        identicon_size = 3*7
        self.tableWidgetBlacklist.setIconSize(QtCore.QSize(identicon_size, identicon_size))

        self.UISignalThread = UISignaler.get()
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "rerenderBlackWhiteList()"), self.rerenderBlackWhiteList)

    def click_radioButtonBlacklist(self):
        if config.get('bitmessagesettings', 'blackwhitelist') == 'white':
            config.set('bitmessagesettings', 'blackwhitelist', 'black')
            config.save()
            # self.tableWidgetBlacklist.clearContents()
            self.tableWidgetBlacklist.setRowCount(0)
            self.rerenderBlackWhiteList()

    def click_radioButtonWhitelist(self):
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            config.set('bitmessagesettings', 'blackwhitelist', 'white')
            config.save()
            # self.tableWidgetBlacklist.clearContents()
            self.tableWidgetBlacklist.setRowCount(0)
            self.rerenderBlackWhiteList()

    def click_pushButtonAddBlacklist(self):
        self.NewBlacklistDialogInstance = AddAddressDialog(self)
        if self.NewBlacklistDialogInstance.exec_():
            if self.NewBlacklistDialogInstance.labelAddressCheck.text() == \
                    _translate("MainWindow", "Address is valid."):
                address = addBMIfNotPresent(str(
                    self.NewBlacklistDialogInstance.lineEditAddress.text()))
                # First we must check to see if the address is already in the
                # address book. The user cannot add it again or else it will
                # cause problems when updating and deleting the entry.
                t = (address,)
                if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                    sql = '''select * from blacklist where address=?'''
                else:
                    sql = '''select * from whitelist where address=?'''
                queryreturn = sqlQuery(sql,*t)
                if queryreturn == []:
                    self.tableWidgetBlacklist.setSortingEnabled(False)
                    self.tableWidgetBlacklist.insertRow(0)
                    newItem = QtGui.QTableWidgetItem(unicode(
                        self.NewBlacklistDialogInstance.lineEditLabel.text().toUtf8(), 'utf-8'))
                    newItem.setIcon(avatarize(address))
                    self.tableWidgetBlacklist.setItem(0, 0, newItem)
                    newItem = QtGui.QTableWidgetItem(address)
                    newItem.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.tableWidgetBlacklist.setItem(0, 1, newItem)
                    self.tableWidgetBlacklist.setSortingEnabled(True)
                    t = (str(self.NewBlacklistDialogInstance.lineEditLabel.text().toUtf8()), address, True)
                    if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                        sql = '''INSERT INTO blacklist VALUES (?,?,?)'''
                    else:
                        sql = '''INSERT INTO whitelist VALUES (?,?,?)'''
                    sqlExecute(sql, *t)
                else:
                    UISignalQueue.put((
                        'updateStatusBar',
                        _translate(
                            "MainWindow",
                            "Error: You cannot add the same address to your"
                            " list twice. Perhaps rename the existing one"
                            " if you want.")
                    ))
            else:
                UISignalQueue.put((
                    'updateStatusBar',
                    _translate(
                        "MainWindow",
                        "The address you entered was invalid. Ignoring it.")
                ))

    def tableWidgetBlacklistItemChanged(self, item):
        if item.column() == 0:
            addressitem = self.tableWidgetBlacklist.item(item.row(), 1)
            if isinstance(addressitem, QtGui.QTableWidgetItem):
                if self.radioButtonBlacklist.isChecked():
                    sqlExecute('''UPDATE blacklist SET label=? WHERE address=?''',
                            str(item.text()), str(addressitem.text()))
                else:
                    sqlExecute('''UPDATE whitelist SET label=? WHERE address=?''',
                            str(item.text()), str(addressitem.text()))

    def init_blacklist_popup_menu(self, connectSignal=True):
        # Popup menu for the Blacklist page
        self.blacklistContextMenuToolbar = QtGui.QToolBar()
        # Actions
        self.actionBlacklistNew = self.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Add new entry"), self.on_action_BlacklistNew)
        self.actionBlacklistDelete = self.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Delete"), self.on_action_BlacklistDelete)
        self.actionBlacklistClipboard = self.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Copy address to clipboard"),
            self.on_action_BlacklistClipboard)
        self.actionBlacklistEnable = self.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Enable"), self.on_action_BlacklistEnable)
        self.actionBlacklistDisable = self.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Disable"), self.on_action_BlacklistDisable)
        self.actionBlacklistSetAvatar = self.blacklistContextMenuToolbar.addAction(
            _translate(
                "MainWindow", "Set avatar..."),
            self.on_action_BlacklistSetAvatar)
        self.tableWidgetBlacklist.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        if connectSignal:
            self.connect(self.tableWidgetBlacklist, QtCore.SIGNAL(
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

    def rerenderBlackWhiteList(self):
        tabs = self.parent().parent()
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            tabs.setTabText(tabs.indexOf(self), _translate('blacklist', 'Blacklist'))
        else:
            tabs.setTabText(tabs.indexOf(self), _translate('blacklist', 'Whitelist'))
        self.tableWidgetBlacklist.setRowCount(0)
        listType = config.get('bitmessagesettings', 'blackwhitelist')
        if listType == 'black':
            queryreturn = sqlQuery('''SELECT label, address, enabled FROM blacklist''')
        else:
            queryreturn = sqlQuery('''SELECT label, address, enabled FROM whitelist''')
        self.tableWidgetBlacklist.setSortingEnabled(False)
        for row in queryreturn:
            label, address, enabled = row
            self.tableWidgetBlacklist.insertRow(0)
            newItem = QtGui.QTableWidgetItem(unicode(label, 'utf-8'))
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            newItem.setIcon(avatarize(address))
            self.tableWidgetBlacklist.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(address)
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128, 128, 128))
            self.tableWidgetBlacklist.setItem(0, 1, newItem)
        self.tableWidgetBlacklist.setSortingEnabled(True)

    # Group of functions for the Blacklist dialog box
    def on_action_BlacklistNew(self):
        self.click_pushButtonAddBlacklist()

    def on_action_BlacklistDelete(self):
        currentRow = self.tableWidgetBlacklist.currentRow()
        labelAtCurrentRow = self.tableWidgetBlacklist.item(
            currentRow, 0).text().toUtf8()
        addressAtCurrentRow = self.tableWidgetBlacklist.item(
            currentRow, 1).text()
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlExecute(
                '''DELETE FROM blacklist WHERE label=? AND address=?''',
                str(labelAtCurrentRow), str(addressAtCurrentRow))
        else:
            sqlExecute(
                '''DELETE FROM whitelist WHERE label=? AND address=?''',
                str(labelAtCurrentRow), str(addressAtCurrentRow))
        self.tableWidgetBlacklist.removeRow(currentRow)

    def on_action_BlacklistClipboard(self):
        currentRow = self.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.tableWidgetBlacklist.item(
            currentRow, 1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))

    def on_context_menuBlacklist(self, point):
        self.popMenuBlacklist.exec_(
            self.tableWidgetBlacklist.mapToGlobal(point))

    def on_action_BlacklistEnable(self):
        currentRow = self.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.tableWidgetBlacklist.item(
            currentRow, 1).text()
        self.tableWidgetBlacklist.item(
            currentRow, 0).setTextColor(QtGui.QApplication.palette().text().color())
        self.tableWidgetBlacklist.item(
            currentRow, 1).setTextColor(QtGui.QApplication.palette().text().color())
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlExecute(
                '''UPDATE blacklist SET enabled=1 WHERE address=?''',
                str(addressAtCurrentRow))
        else:
            sqlExecute(
                '''UPDATE whitelist SET enabled=1 WHERE address=?''',
                str(addressAtCurrentRow))

    def on_action_BlacklistDisable(self):
        currentRow = self.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.tableWidgetBlacklist.item(
            currentRow, 1).text()
        self.tableWidgetBlacklist.item(
            currentRow, 0).setTextColor(QtGui.QColor(128, 128, 128))
        self.tableWidgetBlacklist.item(
            currentRow, 1).setTextColor(QtGui.QColor(128, 128, 128))
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlExecute(
                '''UPDATE blacklist SET enabled=0 WHERE address=?''', str(addressAtCurrentRow))
        else:
            sqlExecute(
                '''UPDATE whitelist SET enabled=0 WHERE address=?''', str(addressAtCurrentRow))

    def on_action_BlacklistSetAvatar(self):
        self.window().on_action_SetAvatar(self.tableWidgetBlacklist)
