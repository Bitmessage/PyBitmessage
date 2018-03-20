from PyQt4 import QtCore, QtGui
from string import find, rfind, rstrip, lstrip

from tr import _translate
from bmconfigparser import BMConfigParser
from helper_sql import *
from utils import *
from settingsmixin import SettingsMixin

# for pylupdate
_translate("MainWindow", "inbox")
_translate("MainWindow", "new")
_translate("MainWindow", "sent")
_translate("MainWindow", "trash")


class AccountMixin(object):
    ALL = 0
    NORMAL = 1
    CHAN = 2
    MAILINGLIST = 3
    SUBSCRIPTION = 4
    BROADCAST = 5

    def accountColor(self):
        if not self.isEnabled:
            return QtGui.QColor(128, 128, 128)
        elif self.type == self.CHAN:
            return QtGui.QColor(216, 119, 0)
        elif self.type in [self.MAILINGLIST, self.SUBSCRIPTION]:
            return QtGui.QColor(137, 04, 177)
        else:
            return QtGui.QApplication.palette().text().color()

    def folderColor(self):
        if not self.parent().isEnabled:
            return QtGui.QColor(128, 128, 128)
        else:
            return QtGui.QApplication.palette().text().color()

    def accountBrush(self):
        brush = QtGui.QBrush(self.accountColor())
        brush.setStyle(QtCore.Qt.NoBrush)
        return brush

    def folderBrush(self):
        brush = QtGui.QBrush(self.folderColor())
        brush.setStyle(QtCore.Qt.NoBrush)
        return brush

    def setAddress(self, address):
        if address is None:
            self.address = None
        else:
            self.address = str(address)

    def setUnreadCount(self, cnt):
        if hasattr(self, "unreadCount") and self.unreadCount == int(cnt):
            return
        self.unreadCount = int(cnt)
        if isinstance(self, QtGui.QTreeWidgetItem):
            self.emitDataChanged()

    def setEnabled(self, enabled):
        self.isEnabled = enabled
        if hasattr(self, "setExpanded"):
            self.setExpanded(enabled)
        if isinstance(self, Ui_AddressWidget):
            for i in range(self.childCount()):
                if isinstance(self.child(i), Ui_FolderWidget):
                    self.child(i).setEnabled(enabled)
        if isinstance(self, QtGui.QTreeWidgetItem):
            self.emitDataChanged()

    def setType(self):
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        if self.address is None:
            self.type = self.ALL
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        elif BMConfigParser().safeGetBoolean(self.address, 'chan'):
            self.type = self.CHAN
        elif BMConfigParser().safeGetBoolean(self.address, 'mailinglist'):
            self.type = self.MAILINGLIST
        elif sqlQuery(
                '''select label from subscriptions\
                where address=?''', self.address):
            self.type = AccountMixin.SUBSCRIPTION
        else:
            self.type = self.NORMAL

    def defaultLabel(self):
        queryreturn = None
        retval = None
        if self.type in (
                AccountMixin.NORMAL,
                AccountMixin.CHAN,
                AccountMixin.MAILINGLIST):
            try:
                retval = unicode(
                    BMConfigParser().get(
                        self.address, 'label'), 'utf-8')
            except Exception:
                queryreturn = sqlQuery(
                    '''select label from addressbook\
                    where address=?''', self.address)
        elif self.type == AccountMixin.SUBSCRIPTION:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''',
                self.address)
        if queryreturn is not None:
            if queryreturn != []:
                for row in queryreturn:
                    retval, = row
                    retval = unicode(retval, 'utf-8')
        elif self.address is None or self.type == AccountMixin.ALL:
            return unicode(
                str(_translate("MainWindow", "All accounts")), 'utf-8')
        if retval is None:
            return unicode(self.address, 'utf-8')
        else:
            return retval


class Ui_FolderWidget(QtGui.QTreeWidgetItem, AccountMixin):
    folderWeight = {"inbox": 1, "new": 2, "sent": 3, "trash": 4}

    def __init__(
            self,
            parent,
            pos=0,
            address="",
            folderName="",
            unreadCount=0):
        super(QtGui.QTreeWidgetItem, self).__init__()
        self.setAddress(address)
        self.setFolderName(folderName)
        self.setUnreadCount(unreadCount)
        parent.insertChild(pos, self)

    def setFolderName(self, fname):
        self.folderName = str(fname)

    def data(self, column, role):
        if column == 0:
            if role == QtCore.Qt.DisplayRole:
                return _translate("MainWindow", self.folderName) + (
                    " (" + str(self.unreadCount) + ")"
                    if self.unreadCount > 0 else ""
                )
            elif role in (QtCore.Qt.EditRole, QtCore.Qt.ToolTipRole):
                return _translate("MainWindow", self.folderName)
            elif role == QtCore.Qt.FontRole:
                font = QtGui.QFont()
                font.setBold(self.unreadCount > 0)
                return font
            elif role == QtCore.Qt.ForegroundRole:
                return self.folderBrush()
        return super(Ui_FolderWidget, self).data(column, role)

    # inbox, sent, thrash first, rest alphabetically
    def __lt__(self, other):
        if (isinstance(other, Ui_FolderWidget)):
            if self.folderName in self.folderWeight:
                x = self.folderWeight[self.folderName]
            else:
                x = 99
            if other.folderName in self.folderWeight:
                y = self.folderWeight[other.folderName]
            else:
                y = 99
            reverse = False
            if self.treeWidget() \
                    .header() \
                    .sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if x == y:
                return self.folderName < other.folderName
            else:
                return (x >= y if reverse else x < y)

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)


class Ui_AddressWidget(QtGui.QTreeWidgetItem, AccountMixin, SettingsMixin):
    def __init__(
            self,
            parent,
            pos=0,
            address=None,
            unreadCount=0,
            enabled=True):
        super(QtGui.QTreeWidgetItem, self).__init__()
        parent.insertTopLevelItem(pos, self)
        # only set default when creating
        # super(QtGui.QTreeWidgetItem, self).setExpanded(BMConfigParser().
        # getboolean(self.address, 'enabled'))
        self.setAddress(address)
        self.setEnabled(enabled)
        self.setUnreadCount(unreadCount)
        self.setType()

    def _getLabel(self):
        if self.address is None:
            return unicode(_translate(
                "MainWindow", "All accounts").toUtf8(), 'utf-8', 'ignore')
        else:
            try:
                return unicode(
                    BMConfigParser().get(self.address, 'label'),
                    'utf-8', 'ignore')
            except BaseException:
                return unicode(self.address, 'utf-8')

    def _getAddressBracket(self, unreadCount=False):
        ret = ""
        if unreadCount:
            ret += " (" + str(self.unreadCount) + ")"
        if self.address is not None:
            ret += " (" + self.address + ")"
        return ret

    def data(self, column, role):
        if column == 0:
            if role == QtCore.Qt.DisplayRole:
                if self.unreadCount > 0 and not self.isExpanded():
                    return self._getLabel() + self._getAddressBracket(True)
                else:
                    return self._getLabel() + self._getAddressBracket(False)
            elif role == QtCore.Qt.EditRole:
                return self._getLabel()
            elif role == QtCore.Qt.ToolTipRole:
                return self._getLabel() + self._getAddressBracket(False)
            elif role == QtCore.Qt.DecorationRole:
                if self.address is None:
                    return avatarize(self._getLabel().encode('utf8'))
                else:
                    return avatarize(self.address)
            elif role == QtCore.Qt.FontRole:
                font = QtGui.QFont()
                font.setBold(self.unreadCount > 0)
                return font
            elif role == QtCore.Qt.ForegroundRole:
                return self.accountBrush()
        return super(Ui_AddressWidget, self).data(column, role)

    def setData(self, column, role, value):
        if role == QtCore.Qt \
                .EditRole and self.type != AccountMixin.SUBSCRIPTION:
            if isinstance(value, QtCore.QVariant):
                BMConfigParser() \
                    .set(str(
                        self.address), 'label',
                    str(value.toString().toUtf8()))
            else:
                BMConfigParser().set(str(self.address), 'label', str(value))
            BMConfigParser().save()
        return super(Ui_AddressWidget, self).setData(column, role, value)

    def setAddress(self, address):
        super(Ui_AddressWidget, self).setAddress(address)
        self.setData(0, QtCore.Qt.UserRole, self.address)

    def setExpanded(self, expand):
        super(Ui_AddressWidget, self).setExpanded(expand)

    def _getSortRank(self):
        ret = self.type
        if not self.isEnabled:
            ret += 100
        return ret

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if (isinstance(other, Ui_AddressWidget)):
            reverse = False
            if self.treeWidget() \
                    .header() \
                    .sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if self._getSortRank() == other._getSortRank():
                x = self._getLabel().lower()
                y = other._getLabel().lower()
                return x < y
            return (not reverse if self._getSortRank() <
                    other._getSortRank() else reverse)

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)


class Ui_SubscriptionWidget(Ui_AddressWidget, AccountMixin):
    def __init__(
            self,
            parent,
            pos=0,
            address="",
            unreadCount=0,
            label="",
            enabled=True):
        super(QtGui.QTreeWidgetItem, self).__init__()
        parent.insertTopLevelItem(pos, self)
        # only set default when creating
        # super(QtGui.QTreeWidgetItem, self).
        # setExpanded(BMConfigParser().
        # getboolean(self.address, 'enabled'))
        self.setAddress(address)
        self.setEnabled(enabled)
        self.setType()
        self.setUnreadCount(unreadCount)

    def _getLabel(self):
        queryreturn = sqlQuery(
            '''select label from subscriptions where address=?''',
            self.address)
        if queryreturn != []:
            for row in queryreturn:
                retval, = row
            return unicode(retval, 'utf-8', 'ignore')
        return unicode(self.address, 'utf-8')

    def setType(self):
        super(Ui_SubscriptionWidget, self).setType()  # sets it editable
        self.type = AccountMixin.SUBSCRIPTION  # overrides type

    def setData(self, column, role, value):
        if role == QtCore.Qt.EditRole:
            from debug import logger
            if isinstance(value, QtCore.QVariant):
                label = str(
                    value.toString().toUtf8()).decode(
                    'utf-8', 'ignore')
            else:
                label = unicode(value, 'utf-8', 'ignore')
            sqlExecute(
                '''UPDATE subscriptions SET label=? WHERE address=?''',
                label, self.address)
        return super(Ui_SubscriptionWidget, self).setData(column, role, value)


class MessageList_AddressWidget(
        QtGui.QTableWidgetItem,
        AccountMixin,
        SettingsMixin):
    def __init__(self, parent, address=None, label=None, unread=False):
        super(QtGui.QTableWidgetItem, self).__init__()
        # parent.insertTopLevelItem(pos, self)
        # only set default when creating
        # super(QtGui.QTreeWidgetItem, self).setExpanded(
        # BMConfigParser().getboolean(self.address, 'enabled'))
        self.isEnabled = True
        self.setAddress(address)
        self.setLabel(label)
        self.setUnread(unread)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setType()
        parent.append(self)

    def setLabel(self, label=None):
        newLabel = self.address
        if label is None:
            queryreturn = None
            if self.type in (
                    AccountMixin.NORMAL,
                    AccountMixin.CHAN,
                    AccountMixin.MAILINGLIST):
                try:
                    newLabel = unicode(
                        BMConfigParser().get(
                            self.address,
                            'label'),
                        'utf-8',
                        'ignore')
                except BaseException:
                    queryreturn = sqlQuery(
                        '''select label from addressbook\
                         where address=?''', self.address)
            elif self.type == AccountMixin.SUBSCRIPTION:
                queryreturn = sqlQuery(
                    '''select label from subscriptions where address=?''',
                    self.address)
            if queryreturn is not None:
                if queryreturn != []:
                    for row in queryreturn:
                        newLabel = unicode(row[0], 'utf-8', 'ignore')
        else:
            newLabel = label
        if hasattr(self, 'label') and newLabel == self.label:
            return
        self.label = newLabel

    def setUnread(self, unread):
        self.unread = unread

    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return self.label
        elif role == QtCore.Qt.EditRole:
            return self.label
        elif role == QtCore.Qt.ToolTipRole:
            return self.label + " (" + self.address + ")"
        elif role == QtCore.Qt.DecorationRole:
            if BMConfigParser() \
                    .safeGetBoolean('bitmessagesettings', 'useidenticons'):
                if self.address is None:
                    return avatarize(self.label)
                else:
                    return avatarize(self.address)
        elif role == QtCore.Qt.FontRole:
            font = QtGui.QFont()
            font.setBold(self.unread)
            return font
        elif role == QtCore.Qt.ForegroundRole:
            return self.accountBrush()
        elif role == QtCore.Qt.UserRole:
            return self.address
        return super(MessageList_AddressWidget, self).data(role)

    def setData(self, role, value):
        if role == QtCore.Qt.EditRole:
            self.setLabel()
        return super(MessageList_AddressWidget, self).setData(role, value)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if (isinstance(other, MessageList_AddressWidget)):
            return self.label.lower() < other.label.lower()
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class MessageList_SubjectWidget(QtGui.QTableWidgetItem, SettingsMixin):
    def __init__(self, parent, subject=None, label=None, unread=False):
        super(QtGui.QTableWidgetItem, self).__init__()
        # parent.insertTopLevelItem(pos, self)
        # only set default when creating
        # super(QtGui.QTreeWidgetItem, self)
        # .setExpanded(BMConfigParser().
        # getboolean(self.address, 'enabled'))
        self.setSubject(subject)
        self.setLabel(label)
        self.setUnread(unread)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        parent.append(self)

    def setLabel(self, label):
        self.label = label

    def setSubject(self, subject):
        self.subject = subject

    def setUnread(self, unread):
        self.unread = unread

    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return self.label
        elif role == QtCore.Qt.EditRole:
            return self.label
        elif role == QtCore.Qt.ToolTipRole:
            return self.label
        elif role == QtCore.Qt.FontRole:
            font = QtGui.QFont()
            font.setBold(self.unread)
            return font
        elif role == QtCore.Qt.UserRole:
            return self.subject
        return super(MessageList_SubjectWidget, self).data(role)

    def setData(self, role, value):
        return super(MessageList_SubjectWidget, self).setData(role, value)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if (isinstance(other, MessageList_SubjectWidget)):
            return self.label.lower() < other.label.lower()
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class Ui_AddressBookWidgetItem(QtGui.QTableWidgetItem, AccountMixin):
    def __init__(self, text, type=AccountMixin.NORMAL):
        super(QtGui.QTableWidgetItem, self).__init__(text)
        self.label = text
        self.type = type
        self.setEnabled(True)

    def data(self, role):
        if role == QtCore.Qt.DisplayRole:
            return self.label
        elif role == QtCore.Qt.EditRole:
            return self.label
        elif role == QtCore.Qt.ToolTipRole:
            return self.label + " (" + self.address + ")"
        elif role == QtCore.Qt.DecorationRole:
            if BMConfigParser() \
                    .safeGetBoolean('bitmessagesettings', 'useidenticons'):
                if self.address is None:
                    return avatarize(self.label)
                else:
                    return avatarize(self.address)
        elif role == QtCore.Qt.FontRole:
            font = QtGui.QFont()
            return font
        elif role == QtCore.Qt.ForegroundRole:
            return self.accountBrush()
        elif role == QtCore.Qt.UserRole:
            return self.type
        return super(Ui_AddressBookWidgetItem, self).data(role)

    def setData(self, role, value):
        if role == QtCore.Qt.EditRole:
            if isinstance(value, QtCore.QVariant):
                self.label = str(value.toString().toUtf8())
            else:
                self.label = str(value)
            if self.type in (
                    AccountMixin.NORMAL,
                    AccountMixin.MAILINGLIST,
                    AccountMixin.CHAN):
                try:
                    # a = BMConfigParser().get(self.address, 'label')
                    BMConfigParser().set(self.address, 'label', self.label)
                    BMConfigParser().save()
                except BaseException:
                    sqlExecute(
                        '''UPDATE addressbook set label=? WHERE address=?''',
                        self.label,
                        self.address)
            elif self.type == AccountMixin.SUBSCRIPTION:
                from debug import logger
                sqlExecute(
                    '''UPDATE subscriptions set label=? WHERE address=?''',
                    self.label,
                    self.address)
            else:
                pass
        return super(Ui_AddressBookWidgetItem, self).setData(role, value)

    def __lt__(self, other):
        if (isinstance(other, Ui_AddressBookWidgetItem)):
            reverse = False
            if self.tableWidget().horizontalHeader(
            ).sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if self.type == other.type:
                return self.label.lower() < other.label.lower()
            else:
                return (not reverse if self.type < other.type else reverse)
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class Ui_AddressBookWidgetItemLabel(Ui_AddressBookWidgetItem):
    def __init__(self, address, label, type):
        Ui_AddressBookWidgetItem.__init__(self, label, type)
        self.address = address
        self.label = label

    def data(self, role):
        self.label = self.defaultLabel()
        return super(Ui_AddressBookWidgetItemLabel, self).data(role)


class Ui_AddressBookWidgetItemAddress(Ui_AddressBookWidgetItem):
    def __init__(self, address, label, type):
        Ui_AddressBookWidgetItem.__init__(self, address, type)
        self.address = address
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def data(self, role):
        if role == QtCore.Qt.ToolTipRole:
            return self.address
        if role == QtCore.Qt.DecorationRole:
            return
        return super(Ui_AddressBookWidgetItemAddress, self).data(role)


class AddressBookCompleter(QtGui.QCompleter):
    def __init__(self):
        super(QtGui.QCompleter, self).__init__()
        self.cursorPos = -1

    def onCursorPositionChanged(self, oldPos, newPos):
        if oldPos != self.cursorPos:
            self.cursorPos = -1

    def splitPath(self, path):
        stringList = []
        text = unicode(path.toUtf8(), encoding="UTF-8")
        splitIndex = rfind(text[0:self.widget().cursorPosition()], ";") + 1
        str = text[splitIndex:self.widget().cursorPosition()]
        str = rstrip(lstrip(str))
        stringList.append(str)
        return stringList

    def pathFromIndex(self, index):
        autoString = unicode(
            index.data(
                QtCore.Qt.EditRole).toString().toUtf8(),
            encoding="UTF-8")
        text = unicode(self.widget().text().toUtf8(), encoding="UTF-8")

        # If cursor position was saved, restore it, else save it
        if self.cursorPos != -1:
            self.widget().setCursorPosition(self.cursorPos)
        else:
            self.cursorPos = self.widget().cursorPosition()

        # Get current prosition
        curIndex = self.widget().cursorPosition()

        # prev_delimiter_index should actually point at
        # final white space AFTER the delimiter
        # Get index of last delimiter before current position
        prevDelimiterIndex = rfind(text[0:curIndex], ";")
        while text[prevDelimiterIndex + 1] == " ":
            prevDelimiterIndex += 1

        # Get index of first delimiter after current position (or EOL if no
        # delimiter after cursor)
        nextDelimiterIndex = find(text, ";", curIndex)
        if nextDelimiterIndex == -1:
            nextDelimiterIndex = len(text)

        # Get part of string that occurs before cursor
        part1 = text[0:prevDelimiterIndex + 1]

        # Get string value from before auto finished string is selected
        # pre = text[prevDelimiterIndex + 1:curIndex - 1]

        # Get part of string that occurs AFTER cursor
        part2 = text[nextDelimiterIndex:]

        return part1 + autoString + part2
