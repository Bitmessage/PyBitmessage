"""
Folder tree and messagelist widgets definitions.
"""
# pylint: disable=too-many-arguments,bad-super-call
# pylint: disable=attribute-defined-outside-init

from cgi import escape

from PyQt4 import QtCore, QtGui

from bmconfigparser import config
from helper_sql import sqlExecute, sqlQuery
from settingsmixin import SettingsMixin
from tr import _translate
from utils import avatarize

# for pylupdate
_translate("MainWindow", "inbox")
_translate("MainWindow", "new")
_translate("MainWindow", "sent")
_translate("MainWindow", "trash")

TimestampRole = QtCore.Qt.UserRole + 1


class AccountMixin(object):
    """UI-related functionality for accounts"""
    ALL = 0
    NORMAL = 1
    CHAN = 2
    MAILINGLIST = 3
    SUBSCRIPTION = 4
    BROADCAST = 5

    def accountColor(self):
        """QT UI color for an account"""
        if not self.isEnabled:
            return QtGui.QColor(128, 128, 128)
        elif self.type == self.CHAN:
            return QtGui.QColor(216, 119, 0)
        elif self.type in [self.MAILINGLIST, self.SUBSCRIPTION]:
            return QtGui.QColor(137, 4, 177)
        return QtGui.QApplication.palette().text().color()

    def folderColor(self):
        """QT UI color for a folder"""
        if not self.parent().isEnabled:
            return QtGui.QColor(128, 128, 128)
        return QtGui.QApplication.palette().text().color()

    def accountBrush(self):
        """Account brush (for QT UI)"""
        brush = QtGui.QBrush(self.accountColor())
        brush.setStyle(QtCore.Qt.NoBrush)
        return brush

    def folderBrush(self):
        """Folder brush (for QT UI)"""
        brush = QtGui.QBrush(self.folderColor())
        brush.setStyle(QtCore.Qt.NoBrush)
        return brush

    def accountString(self):
        """Account string suitable for use in To: field: label <address>"""
        label = self._getLabel()
        return (
            self.address if label == self.address
            else '%s <%s>' % (label, self.address)
        )

    def setAddress(self, address):
        """Set bitmessage address of the object"""
        if address is None:
            self.address = None
        else:
            self.address = str(address)

    def setUnreadCount(self, cnt):
        """Set number of unread messages"""
        try:
            if self.unreadCount == int(cnt):
                return
        except AttributeError:
            pass
        self.unreadCount = int(cnt)
        if isinstance(self, QtGui.QTreeWidgetItem):
            self.emitDataChanged()

    def setEnabled(self, enabled):
        """Set account enabled (QT UI)"""
        self.isEnabled = enabled
        try:
            self.setExpanded(enabled)
        except AttributeError:
            pass
        if isinstance(self, Ui_AddressWidget):
            for i in range(self.childCount()):
                if isinstance(self.child(i), Ui_FolderWidget):
                    self.child(i).setEnabled(enabled)
        if isinstance(self, QtGui.QTreeWidgetItem):
            self.emitDataChanged()

    def setType(self):
        """Set account type (QT UI)"""
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        if self.address is None:
            self.type = self.ALL
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        elif config.safeGetBoolean(self.address, 'chan'):
            self.type = self.CHAN
        elif config.safeGetBoolean(self.address, 'mailinglist'):
            self.type = self.MAILINGLIST
        elif sqlQuery(
                '''select label from subscriptions where address=?''', self.address):
            self.type = AccountMixin.SUBSCRIPTION
        else:
            self.type = self.NORMAL

    def defaultLabel(self):
        """Default label (in case no label is set manually)"""
        queryreturn = None
        retval = None
        if self.type in (
                AccountMixin.NORMAL,
                AccountMixin.CHAN, AccountMixin.MAILINGLIST):
            try:
                retval = unicode(
                    config.get(self.address, 'label'), 'utf-8')
            except Exception:
                queryreturn = sqlQuery(
                    '''select label from addressbook where address=?''', self.address)
        elif self.type == AccountMixin.SUBSCRIPTION:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''', self.address)
        if queryreturn is not None:
            if queryreturn != []:
                for row in queryreturn:
                    retval, = row
                    retval = unicode(retval, 'utf-8')
        elif self.address is None or self.type == AccountMixin.ALL:
            return unicode(
                str(_translate("MainWindow", "All accounts")), 'utf-8')

        return retval or unicode(self.address, 'utf-8')


class BMTreeWidgetItem(QtGui.QTreeWidgetItem, AccountMixin):
    """A common abstract class for Tree widget item"""

    def __init__(self, parent, pos, address, unreadCount):
        super(QtGui.QTreeWidgetItem, self).__init__()
        self.setAddress(address)
        self.setUnreadCount(unreadCount)
        self._setup(parent, pos)

    def _getAddressBracket(self, unreadCount=False):
        return " (" + str(self.unreadCount) + ")" if unreadCount else ""

    def data(self, column, role):
        """Override internal QT method for returning object data"""
        if column == 0:
            if role == QtCore.Qt.DisplayRole:
                return self._getLabel() + self._getAddressBracket(
                    self.unreadCount > 0)
            elif role == QtCore.Qt.EditRole:
                return self._getLabel()
            elif role == QtCore.Qt.ToolTipRole:
                return self._getLabel() + self._getAddressBracket(False)
            elif role == QtCore.Qt.FontRole:
                font = QtGui.QFont()
                font.setBold(self.unreadCount > 0)
                return font
        return super(BMTreeWidgetItem, self).data(column, role)


class Ui_FolderWidget(BMTreeWidgetItem):
    """Item in the account/folder tree representing a folder"""
    folderWeight = {"inbox": 1, "new": 2, "sent": 3, "trash": 4}

    def __init__(
            self, parent, pos=0, address="", folderName="", unreadCount=0):
        self.setFolderName(folderName)
        super(Ui_FolderWidget, self).__init__(
            parent, pos, address, unreadCount)

    def _setup(self, parent, pos):
        parent.insertChild(pos, self)

    def _getLabel(self):
        return _translate("MainWindow", self.folderName)

    def setFolderName(self, fname):
        """Set folder name (for QT UI)"""
        self.folderName = str(fname)

    def data(self, column, role):
        """Override internal QT method for returning object data"""
        if column == 0 and role == QtCore.Qt.ForegroundRole:
            return self.folderBrush()
        return super(Ui_FolderWidget, self).data(column, role)

    # inbox, sent, thrash first, rest alphabetically
    def __lt__(self, other):
        if isinstance(other, Ui_FolderWidget):
            if self.folderName in self.folderWeight:
                x = self.folderWeight[self.folderName]
            else:
                x = 99
            if other.folderName in self.folderWeight:
                y = self.folderWeight[other.folderName]
            else:
                y = 99
            reverse = QtCore.Qt.DescendingOrder == \
                self.treeWidget().header().sortIndicatorOrder()
            if x == y:
                return self.folderName < other.folderName
            return x >= y if reverse else x < y

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)


class Ui_AddressWidget(BMTreeWidgetItem, SettingsMixin):
    """Item in the account/folder tree representing an account"""
    def __init__(self, parent, pos=0, address=None, unreadCount=0, enabled=True):
        super(Ui_AddressWidget, self).__init__(
            parent, pos, address, unreadCount)
        self.setEnabled(enabled)

    def _setup(self, parent, pos):
        self.setType()
        parent.insertTopLevelItem(pos, self)

    def _getLabel(self):
        if self.address is None:
            return unicode(_translate(
                "MainWindow", "All accounts").toUtf8(), 'utf-8', 'ignore')
        else:
            try:
                return unicode(
                    config.get(self.address, 'label'),
                    'utf-8', 'ignore')
            except:
                return unicode(self.address, 'utf-8')

    def _getAddressBracket(self, unreadCount=False):
        ret = "" if self.isExpanded() \
            else super(Ui_AddressWidget, self)._getAddressBracket(unreadCount)
        if self.address is not None:
            ret += " (" + self.address + ")"
        return ret

    def data(self, column, role):
        """Override internal QT method for returning object data"""
        if column == 0:
            if role == QtCore.Qt.DecorationRole:
                return avatarize(
                    self.address or self._getLabel().encode('utf8'))
            elif role == QtCore.Qt.ForegroundRole:
                return self.accountBrush()
        return super(Ui_AddressWidget, self).data(column, role)

    def setData(self, column, role, value):
        """Save account label (if you edit in the the UI, this will be triggered and will save it to keys.dat)"""
        if role == QtCore.Qt.EditRole \
                and self.type != AccountMixin.SUBSCRIPTION:
            config.set(
                str(self.address), 'label',
                str(value.toString().toUtf8())
                if isinstance(value, QtCore.QVariant)
                else value.encode('utf-8')
            )
            config.save()
        return super(Ui_AddressWidget, self).setData(column, role, value)

    def setAddress(self, address):
        """Set address to object (for QT UI)"""
        super(Ui_AddressWidget, self).setAddress(address)
        self.setData(0, QtCore.Qt.UserRole, self.address)

    def _getSortRank(self):
        return self.type if self.isEnabled else (self.type + 100)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        # pylint: disable=protected-access
        if isinstance(other, Ui_AddressWidget):
            reverse = QtCore.Qt.DescendingOrder == \
                self.treeWidget().header().sortIndicatorOrder()
            if self._getSortRank() == other._getSortRank():
                x = self._getLabel().lower()
                y = other._getLabel().lower()
                return x < y
            return (
                not reverse
                if self._getSortRank() < other._getSortRank() else reverse
            )

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)


class Ui_SubscriptionWidget(Ui_AddressWidget):
    """Special treating of subscription addresses"""
    # pylint: disable=unused-argument
    def __init__(self, parent, pos=0, address="", unreadCount=0, label="", enabled=True):
        super(Ui_SubscriptionWidget, self).__init__(
            parent, pos, address, unreadCount, enabled)

    def _getLabel(self):
        queryreturn = sqlQuery(
            '''select label from subscriptions where address=?''', self.address)
        if queryreturn != []:
            for row in queryreturn:
                retval, = row
            return unicode(retval, 'utf-8', 'ignore')
        return unicode(self.address, 'utf-8')

    def setType(self):
        """Set account type"""
        super(Ui_SubscriptionWidget, self).setType()  # sets it editable
        self.type = AccountMixin.SUBSCRIPTION  # overrides type

    def setData(self, column, role, value):
        """Save subscription label to database"""
        if role == QtCore.Qt.EditRole:
            if isinstance(value, QtCore.QVariant):
                label = str(
                    value.toString().toUtf8()).decode('utf-8', 'ignore')
            else:
                label = unicode(value, 'utf-8', 'ignore')
            sqlExecute(
                '''UPDATE subscriptions SET label=? WHERE address=?''',
                label, self.address)
        return super(Ui_SubscriptionWidget, self).setData(column, role, value)


class BMTableWidgetItem(QtGui.QTableWidgetItem, SettingsMixin):
    """A common abstract class for Table widget item"""

    def __init__(self, label=None, unread=False):
        super(QtGui.QTableWidgetItem, self).__init__()
        self.setLabel(label)
        self.setUnread(unread)
        self._setup()

    def _setup(self):
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def setLabel(self, label):
        """Set object label"""
        self.label = label

    def setUnread(self, unread):
        """Set/unset read state of an item"""
        self.unread = unread

    def data(self, role):
        """Return object data (QT UI)"""
        if role in (
            QtCore.Qt.DisplayRole, QtCore.Qt.EditRole, QtCore.Qt.ToolTipRole
        ):
            return self.label
        elif role == QtCore.Qt.FontRole:
            font = QtGui.QFont()
            font.setBold(self.unread)
            return font
        return super(BMTableWidgetItem, self).data(role)


class BMAddressWidget(BMTableWidgetItem, AccountMixin):
    """A common class for Table widget item with account"""

    def _setup(self):
        super(BMAddressWidget, self)._setup()
        self.setEnabled(True)
        self.setType()

    def _getLabel(self):
        return self.label

    def data(self, role):
        """Return object data (QT UI)"""
        if role == QtCore.Qt.ToolTipRole:
            return self.label + " (" + self.address + ")"
        elif role == QtCore.Qt.DecorationRole:
            if config.safeGetBoolean(
                    'bitmessagesettings', 'useidenticons'):
                return avatarize(self.address or self.label)
        elif role == QtCore.Qt.ForegroundRole:
            return self.accountBrush()
        return super(BMAddressWidget, self).data(role)


class MessageList_AddressWidget(BMAddressWidget):
    """Address item in a messagelist"""
    def __init__(self, address=None, label=None, unread=False):
        self.setAddress(address)
        super(MessageList_AddressWidget, self).__init__(label, unread)

    def setLabel(self, label=None):
        """Set label"""
        super(MessageList_AddressWidget, self).setLabel(label)
        if label is not None:
            return
        newLabel = self.address
        queryreturn = None
        if self.type in (
                AccountMixin.NORMAL,
                AccountMixin.CHAN, AccountMixin.MAILINGLIST):
            try:
                newLabel = unicode(
                    config.get(self.address, 'label'),
                    'utf-8', 'ignore')
            except:
                queryreturn = sqlQuery(
                    '''select label from addressbook where address=?''', self.address)
        elif self.type == AccountMixin.SUBSCRIPTION:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''', self.address)
        if queryreturn:
            for row in queryreturn:
                newLabel = unicode(row[0], 'utf-8', 'ignore')

        self.label = newLabel

    def data(self, role):
        """Return object data (QT UI)"""
        if role == QtCore.Qt.UserRole:
            return self.address
        return super(MessageList_AddressWidget, self).data(role)

    def setData(self, role, value):
        """Set object data"""
        if role == QtCore.Qt.EditRole:
            self.setLabel()
        return super(MessageList_AddressWidget, self).setData(role, value)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if isinstance(other, MessageList_AddressWidget):
            return self.label.lower() < other.label.lower()
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class MessageList_SubjectWidget(BMTableWidgetItem):
    """Message list subject item"""
    def __init__(self, subject=None, label=None, unread=False):
        self.setSubject(subject)
        super(MessageList_SubjectWidget, self).__init__(label, unread)

    def setSubject(self, subject):
        """Set subject"""
        self.subject = subject

    def data(self, role):
        """Return object data (QT UI)"""
        if role == QtCore.Qt.UserRole:
            return self.subject
        if role == QtCore.Qt.ToolTipRole:
            return escape(unicode(self.subject, 'utf-8'))
        return super(MessageList_SubjectWidget, self).data(role)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if isinstance(other, MessageList_SubjectWidget):
            return self.label.lower() < other.label.lower()
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


# In order for the time columns on the Inbox and Sent tabs to be sorted
# correctly (rather than alphabetically), we need to overload the <
# operator and use this class instead of QTableWidgetItem.
class MessageList_TimeWidget(BMTableWidgetItem):
    """
    A subclass of QTableWidgetItem for received (lastactiontime) field.
    '<' operator is overloaded to sort by TimestampRole == 33
    msgid is available by QtCore.Qt.UserRole
    """

    def __init__(self, label=None, unread=False, timestamp=None, msgid=''):
        super(MessageList_TimeWidget, self).__init__(label, unread)
        self.setData(QtCore.Qt.UserRole, QtCore.QByteArray(msgid))
        self.setData(TimestampRole, int(timestamp))

    def __lt__(self, other):
        return self.data(TimestampRole) < other.data(TimestampRole)

    def data(self, role=QtCore.Qt.UserRole):
        """
        Returns expected python types for QtCore.Qt.UserRole and TimestampRole
        custom roles and super for any Qt role
        """
        data = super(MessageList_TimeWidget, self).data(role)
        if role == TimestampRole:
            return int(data.toPyObject())
        if role == QtCore.Qt.UserRole:
            return str(data.toPyObject())
        return data


class Ui_AddressBookWidgetItem(BMAddressWidget):
    """Addressbook item"""
    # pylint: disable=unused-argument
    def __init__(self, label=None, acc_type=AccountMixin.NORMAL):
        self.type = acc_type
        super(Ui_AddressBookWidgetItem, self).__init__(label=label)

    def data(self, role):
        """Return object data"""
        if role == QtCore.Qt.UserRole:
            return self.type
        return super(Ui_AddressBookWidgetItem, self).data(role)

    def setData(self, role, value):
        """Set data"""
        if role == QtCore.Qt.EditRole:
            self.label = str(
                value.toString().toUtf8()
                if isinstance(value, QtCore.QVariant) else value
            )
            if self.type in (
                    AccountMixin.NORMAL,
                    AccountMixin.MAILINGLIST, AccountMixin.CHAN):
                try:
                    config.get(self.address, 'label')
                    config.set(self.address, 'label', self.label)
                    config.save()
                except:
                    sqlExecute('''UPDATE addressbook set label=? WHERE address=?''', self.label, self.address)
            elif self.type == AccountMixin.SUBSCRIPTION:
                sqlExecute('''UPDATE subscriptions set label=? WHERE address=?''', self.label, self.address)
            else:
                pass
        return super(Ui_AddressBookWidgetItem, self).setData(role, value)

    def __lt__(self, other):
        if isinstance(other, Ui_AddressBookWidgetItem):
            reverse = QtCore.Qt.DescendingOrder == \
                self.tableWidget().horizontalHeader().sortIndicatorOrder()

            if self.type == other.type:
                return self.label.lower() < other.label.lower()
            return not reverse if self.type < other.type else reverse
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class Ui_AddressBookWidgetItemLabel(Ui_AddressBookWidgetItem):
    """Addressbook label item"""
    def __init__(self, address, label, acc_type):
        self.address = address
        super(Ui_AddressBookWidgetItemLabel, self).__init__(label, acc_type)

    def data(self, role):
        """Return object data"""
        self.label = self.defaultLabel()
        return super(Ui_AddressBookWidgetItemLabel, self).data(role)


class Ui_AddressBookWidgetItemAddress(Ui_AddressBookWidgetItem):
    """Addressbook address item"""
    def __init__(self, address, label, acc_type):
        self.address = address
        super(Ui_AddressBookWidgetItemAddress, self).__init__(address, acc_type)

    def data(self, role):
        """Return object data"""
        if role == QtCore.Qt.ToolTipRole:
            return self.address
        if role == QtCore.Qt.DecorationRole:
            return None
        return super(Ui_AddressBookWidgetItemAddress, self).data(role)


class AddressBookCompleter(QtGui.QCompleter):
    """Addressbook completer"""

    def __init__(self):
        super(AddressBookCompleter, self).__init__()
        self.cursorPos = -1

    def onCursorPositionChanged(self, oldPos, newPos):  # pylint: disable=unused-argument
        """Callback for cursor position change"""
        if oldPos != self.cursorPos:
            self.cursorPos = -1

    def splitPath(self, path):
        """Split on semicolon"""
        text = unicode(path.toUtf8(), 'utf-8')
        return [text[:self.widget().cursorPosition()].split(';')[-1].strip()]

    def pathFromIndex(self, index):
        """Perform autocompletion (reimplemented QCompleter method)"""
        autoString = unicode(
            index.data(QtCore.Qt.EditRole).toString().toUtf8(), 'utf-8')
        text = unicode(self.widget().text().toUtf8(), 'utf-8')

        # If cursor position was saved, restore it, else save it
        if self.cursorPos != -1:
            self.widget().setCursorPosition(self.cursorPos)
        else:
            self.cursorPos = self.widget().cursorPosition()

        # Get current prosition
        curIndex = self.widget().cursorPosition()

        # prev_delimiter_index should actually point at final white space
        # AFTER the delimiter
        # Get index of last delimiter before current position
        prevDelimiterIndex = text[0:curIndex].rfind(";")
        while text[prevDelimiterIndex + 1] == " ":
            prevDelimiterIndex += 1

        # Get index of first delimiter after current position
        # (or EOL if no delimiter after cursor)
        nextDelimiterIndex = text.find(";", curIndex)
        if nextDelimiterIndex == -1:
            nextDelimiterIndex = len(text)

        # Get part of string that occurs before cursor
        part1 = text[0:prevDelimiterIndex + 1]

        # Get string value from before auto finished string is selected
        # pre = text[prevDelimiterIndex + 1:curIndex - 1]

        # Get part of string that occurs AFTER cursor
        part2 = text[nextDelimiterIndex:]

        return part1 + autoString + part2
