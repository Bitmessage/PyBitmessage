"""
src/bitmessageqt/foldertree.py
==============================
"""
# pylint: disable=too-many-arguments,bad-super-call,attribute-defined-outside-init

from cgi import escape

from PyQt4 import QtCore, QtGui

from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from settingsmixin import SettingsMixin
from tr import _translate
from utils import avatarize

# for pylupdate
_translate("MainWindow", "inbox")
_translate("MainWindow", "new")
_translate("MainWindow", "sent")
_translate("MainWindow", "trash")


class AccountMixin(object):
    """UI-related functionality for accounts"""
    ALL = 0
    NORMAL = 1
    CHAN = 2
    MAILINGLIST = 3
    SUBSCRIPTION = 4
    BROADCAST = 5

    def account_color(self):
        """QT UI color for an account"""
        if not self.isEnabled:
            return QtGui.QColor(128, 128, 128)
        elif self.type == self.CHAN:
            return QtGui.QColor(216, 119, 0)
        elif self.type in [self.MAILINGLIST, self.SUBSCRIPTION]:
            return QtGui.QColor(137, 4, 177)
        return QtGui.QApplication.palette().text().color()

    def folder_color(self):
        """QT UI color for a folder"""
        if not self.parent().isEnabled:
            return QtGui.QColor(128, 128, 128)
        return QtGui.QApplication.palette().text().color()

    def account_brush(self):
        """Account brush (for QT UI)"""
        brush = QtGui.QBrush(self.account_color())
        brush.setStyle(QtCore.Qt.NoBrush)
        return brush

    def folder_brush(self):
        """Folder brush (for QT UI)"""
        brush = QtGui.QBrush(self.folder_color())
        brush.setStyle(QtCore.Qt.NoBrush)
        return brush

    def account_string(self):
        """Account string suitable for use in To: field: label <address>"""
        label = self._getLabel()
        return (
            self.address if label == self.address
            else '%s <%s>' % (label, self.address)
        )

    def set_address(self, address):
        """Set bitmessage address of the object"""
        self.address = None if address is None else str(address)

    def set_unread_count(self, cnt):
        """Set number of unread messages"""
        try:
            if self.unreadCount == int(cnt):
                return
        except AttributeError:
            pass
        self.unreadCount = int(cnt)
        if isinstance(self, QtGui.QTreeWidgetItem):
            self.emitDataChanged()

    def set_enabled(self, enabled):
        """Set account enabled (QT UI)"""
        self.isEnabled = enabled
        try:
            self.setExpanded(enabled)
        except AttributeError:
            pass
        if isinstance(self, UiAddressWidget):
            for i in range(self.childCount()):
                if isinstance(self.child(i), UiFolderWidget):
                    self.child(i).set_enabled(enabled)
        if isinstance(self, QtGui.QTreeWidgetItem):
            self.emitDataChanged()

    def setType(self):
        """Set account type (QT UI)"""
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        if self.address is None:
            self.type = self.ALL
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        elif BMConfigParser().safeGetBoolean(self.address, 'chan'):
            self.type = self.CHAN
        elif BMConfigParser().safeGetBoolean(self.address, 'mailinglist'):
            self.type = self.MAILINGLIST
        elif sqlQuery(
                '''select label from subscriptions where address=?''', self.address):
            self.type = AccountMixin.SUBSCRIPTION
        else:
            self.type = self.NORMAL

    def default_label(self):
        """Default label (in case no label is set manually)"""
        queryreturn = None
        retval = None
        if self.type in (
                AccountMixin.NORMAL,
                AccountMixin.CHAN, AccountMixin.MAILINGLIST):
            try:
                retval = unicode(
                    BMConfigParser().get(self.address, 'label'), 'utf-8')
            except Exception:
                queryreturn = sqlQuery(
                    '''select label from addressbook where address=?''', self.address)
        elif self.type == AccountMixin.SUBSCRIPTION:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''', self.address)
        if queryreturn is not None:
            if queryreturn:
                for row in queryreturn:
                    retval, = row
                    retval = unicode(retval, 'utf-8')
        elif self.address is None or self.type == AccountMixin.ALL:
            return unicode(
                str(_translate("MainWindow", "All accounts")), 'utf-8')

        return retval or unicode(self.address, 'utf-8')


class BMTreeWidgetItem(QtGui.QTreeWidgetItem, AccountMixin):
    """A common abstract class for Tree widget item"""

    def __init__(self, parent, pos, address, unread_count):
        super(QtGui.QTreeWidgetItem, self).__init__()
        self.set_address(address)
        self.set_unread_count(unread_count)
        self._setup(parent, pos)

    def _get_address_bracket(self, unreadCount=False):
        return " (" + str(self.unreadCount) + ")" if unreadCount else ""

    def data(self, column, role):
        """Override internal QT method for returning object data"""
        if column == 0:
            if role == QtCore.Qt.DisplayRole:
                return self._getLabel() + self._get_address_bracket(
                    self.unreadCount > 0)
            elif role == QtCore.Qt.EditRole:
                return self._getLabel()
            elif role == QtCore.Qt.ToolTipRole:
                return self._getLabel() + self._get_address_bracket(False)
            elif role == QtCore.Qt.FontRole:
                font = QtGui.QFont()
                font.setBold(self.unreadCount > 0)
                return font
        return super(BMTreeWidgetItem, self).data(column, role)


class UiFolderWidget(BMTreeWidgetItem):
    """Item in the account/folder tree representing a folder"""
    folderWeight = {"inbox": 1, "new": 2, "sent": 3, "trash": 4}

    def __init__(
            self, parent, pos=0, address="", folder_name="", unread_count=0):
        self.set_folder_name(folder_name)
        super(UiFolderWidget, self).__init__(
            parent, pos, address, unread_count)

    def _setup(self, parent, pos):
        parent.insertChild(pos, self)

    def _get_label(self):
        return _translate("MainWindow", self.folderName)

    def set_folder_name(self, fname):
        """Set folder name (for QT UI)"""
        self.folderName = str(fname)

    def data(self, column, role):
        """Override internal QT method for returning object data"""
        if column == 0 and role == QtCore.Qt.ForegroundRole:
            return self.folder_brush()
        return super(UiFolderWidget, self).data(column, role)

    # inbox, sent, thrash first, rest alphabetically
    def __lt__(self, other):
        if isinstance(other, UiFolderWidget):
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


class UiAddressWidget(BMTreeWidgetItem, SettingsMixin):
    """Item in the account/folder tree representing an account"""
    def __init__(self, parent, pos=0, address=None, unread_count=0, enabled=True):
        super(UiAddressWidget, self).__init__(
            parent, pos, address, unread_count)
        self.set_enabled(enabled)

    def _setup(self, parent, pos):
        self.setType()
        parent.insertTopLevelItem(pos, self)

    def _get_label(self):
        if self.address is None:
            return unicode(_translate(
                "MainWindow", "All accounts").toUtf8(), 'utf-8', 'ignore')
        else:
            try:
                return unicode(
                    BMConfigParser().get(self.address, 'label'),
                    'utf-8', 'ignore')
            except:
                return unicode(self.address, 'utf-8')

    def _get_address_bracket(self, unread_count=False):
        ret = "" if self.isExpanded() \
            else super(UiAddressWidget, self)._get_address_bracket(unread_count)
        if self.address is not None:
            ret += " (%s)" % self.address
        return ret

    def data(self, column, role):
        """Override internal QT method for returning object data"""
        if column == 0:
            if role == QtCore.Qt.DecorationRole:
                return avatarize(
                    self.address or self._get_label().encode('utf8'))
            elif role == QtCore.Qt.ForegroundRole:
                return self.account_brush()
        return super(UiAddressWidget, self).data(column, role)

    def setData(self, column, role, value):
        """Save account label (if you edit in the the UI, this will be triggered and will save it to keys.dat)"""
        if role == QtCore.Qt.EditRole \
                and self.type != AccountMixin.SUBSCRIPTION:
            BMConfigParser().set(
                str(self.address), 'label',
                str(value.toString().toUtf8())
                if isinstance(value, QtCore.QVariant)
                else value.encode('utf-8')
            )
            BMConfigParser().save()
        return super(UiAddressWidget, self).setData(column, role, value)

    def set_address(self, address):
        """Set address to object (for QT UI)"""
        super(UiAddressWidget, self).set_address(address)
        self.setData(0, QtCore.Qt.UserRole, self.address)

    def _get_sort_rank(self):
        return self.type if self.isEnabled else (self.type + 100)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        # pylint: disable=protected-access
        if isinstance(other, UiAddressWidget):
            reverse = QtCore.Qt.DescendingOrder == \
                self.treeWidget().header().sortIndicatorOrder()
            if self._get_sort_rank() == other._get_sort_rank():
                x = self._get_label().lower()
                y = other._get_label().lower()
                return x < y
            return (
                not reverse
                if self._get_sort_rank() < other._get_sort_rank() else reverse
            )

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)


class UiSubscriptionWidget(UiAddressWidget):
    """Special treating of subscription addresses"""
    # pylint: disable=unused-argument
    def __init__(self, parent, pos=0, address="", unread_count=0, label="", enabled=True):
        super(UiSubscriptionWidget, self).__init__(
            parent, pos, address, unread_count, enabled)

    def _get_label(self):
        queryreturn = sqlQuery(
            '''select label from subscriptions where address=?''', self.address)
        if queryreturn != []:
            for row in queryreturn:
                retval, = row
            return unicode(retval, 'utf-8', 'ignore')
        return unicode(self.address, 'utf-8')

    def setType(self):
        """Set account type"""
        super(UiSubscriptionWidget, self).setType()  # sets it editable
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
        return super(UiSubscriptionWidget, self).setData(column, role, value)


class BMTableWidgetItem(QtGui.QTableWidgetItem, SettingsMixin):
    """A common abstract class for Table widget item"""

    def __init__(self, parent=None, label=None, unread=False):
        super(QtGui.QTableWidgetItem, self).__init__()
        self.set_label(label)
        self.set_unread(unread)
        self._setup()
        if parent is not None:
            parent.append(self)

    def set_label(self, label):
        """Set object label"""
        self.label = label

    def set_unread(self, unread):
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
        self.set_enabled(True)

    def _get_label(self):
        return self.label

    def data(self, role):
        """Return object data (QT UI)"""
        if role == QtCore.Qt.ToolTipRole:
            return self.label + " (" + self.address + ")"
        elif role == QtCore.Qt.DecorationRole:
            if BMConfigParser().safeGetBoolean(
                    'bitmessagesettings', 'useidenticons'):
                return avatarize(self.address or self.label)
        elif role == QtCore.Qt.ForegroundRole:
            return self.account_brush()
        return super(BMAddressWidget, self).data(role)


class MessageListAddressWidget(BMAddressWidget):
    """Address item in a messagelist"""
    def __init__(self, parent, address=None, label=None, unread=False):
        self.set_address(address)
        super(MessageListAddressWidget, self).__init__(parent, label, unread)

    def _setup(self):
        self.isEnabled = True
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setType()

    def set_label(self, label=None):
        """Set label"""
        super(MessageListAddressWidget, self).set_label(label)
        if label is not None:
            return
        new_label = self.address
        queryreturn = None
        if self.type in (
                AccountMixin.NORMAL,
                AccountMixin.CHAN, AccountMixin.MAILINGLIST):
            try:
                new_label = unicode(
                    BMConfigParser().get(self.address, 'label'),
                    'utf-8', 'ignore')
            except:
                queryreturn = sqlQuery(
                    '''select label from addressbook where address=?''', self.address)
        elif self.type == AccountMixin.SUBSCRIPTION:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''', self.address)
        if queryreturn:
            for row in queryreturn:
                new_label = unicode(row[0], 'utf-8', 'ignore')

        self.label = new_label

    def data(self, role):
        """Return object data (QT UI)"""
        if role == QtCore.Qt.UserRole:
            return self.address
        return super(MessageListAddressWidget, self).data(role)

    def setData(self, role, value):
        """Set object data"""
        if role == QtCore.Qt.EditRole:
            self.set_label()
        return super(MessageListAddressWidget, self).setData(role, value)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if isinstance(other, MessageListAddressWidget):
            return self.label.lower() < other.label.lower()
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class MessageListSubjectWidget(BMTableWidgetItem):
    """Message list subject item"""
    def __init__(self, parent, subject=None, label=None, unread=False):
        self.set_subject(subject)
        super(MessageListSubjectWidget, self).__init__(parent, label, unread)

    def _setup(self):
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def set_subject(self, subject):
        """Set subject"""
        self.subject = subject

    def data(self, role):
        """Return object data (QT UI)"""
        if role == QtCore.Qt.UserRole:
            return self.subject
        if role == QtCore.Qt.ToolTipRole:
            return escape(unicode(self.subject, 'utf-8'))
        return super(MessageListSubjectWidget, self).data(role)

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if isinstance(other, MessageListSubjectWidget):
            return self.label.lower() < other.label.lower()
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class UiAddressBookWidgetItem(BMAddressWidget):
    """Addressbook item"""
    # pylint: disable=unused-argument
    def __init__(self, label=None, acc_type=AccountMixin.NORMAL):
        self.type = acc_type
        super(UiAddressBookWidgetItem, self).__init__(label=label)

    def data(self, role):
        """Return object data"""
        if role == QtCore.Qt.UserRole:
            return self.type
        return super(UiAddressBookWidgetItem, self).data(role)

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
                    BMConfigParser().get(self.address, 'label')
                    BMConfigParser().set(self.address, 'label', self.label)
                    BMConfigParser().save()
                except:
                    sqlExecute('''UPDATE addressbook set label=? WHERE address=?''', self.label, self.address)
            elif self.type == AccountMixin.SUBSCRIPTION:
                sqlExecute('''UPDATE subscriptions set label=? WHERE address=?''', self.label, self.address)
            else:
                pass
        return super(UiAddressBookWidgetItem, self).setData(role, value)

    def __lt__(self, other):
        if isinstance(other, UiAddressBookWidgetItem):
            reverse = QtCore.Qt.DescendingOrder == \
                self.tableWidget().horizontalHeader().sortIndicatorOrder()

            if self.type == other.type:
                return self.label.lower() < other.label.lower()
            return not reverse if self.type < other.type else reverse
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class UiAddressBookWidgetItemLabel(UiAddressBookWidgetItem):
    """Addressbook label item"""
    def __init__(self, address, label, acc_type):
        super(UiAddressBookWidgetItemLabel, self).__init__(label, acc_type)
        self.address = address

    def data(self, role):
        """Return object data"""
        self.label = self.default_label()
        return super(UiAddressBookWidgetItemLabel, self).data(role)


class UiAddressBookWidgetItemAddress(UiAddressBookWidgetItem):
    """Addressbook address item"""
    def __init__(self, address, label, acc_type):
        super(UiAddressBookWidgetItemAddress, self).__init__(address, acc_type)
        self.address = address
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def data(self, role):
        """Return object data"""
        if role == QtCore.Qt.ToolTipRole:
            return self.address
        if role == QtCore.Qt.DecorationRole:
            return None
        return super(UiAddressBookWidgetItemAddress, self).data(role)


class AddressBookCompleter(QtGui.QCompleter):
    """Addressbook completer"""

    def __init__(self):
        super(AddressBookCompleter, self).__init__()
        self.cursorPos = -1

    def on_cursor_position_changed(self, oldPos, newPos):  # pylint: disable=unused-argument
        """Callback for cursor position change"""
        if oldPos != self.cursorPos:
            self.cursorPos = -1

    def splitPath(self, path):
        """Split on semicolon"""
        text = unicode(path.toUtf8(), 'utf-8')
        return [text[:self.widget().cursorPosition()].split(';')[-1].strip()]

    def pathFromIndex(self, index):
        """Perform autocompletion (reimplemented QCompleter method)"""
        auto_string = unicode(
            index.data(QtCore.Qt.EditRole).toString().toUtf8(), 'utf-8')
        text = unicode(self.widget().text().toUtf8(), 'utf-8')

        # If cursor position was saved, restore it, else save it
        if self.cursorPos != -1:
            self.widget().setCursorPosition(self.cursorPos)
        else:
            self.cursorPos = self.widget().cursorPosition()

        # Get current prosition
        cur_index = self.widget().cursorPosition()

        # prev_delimiter_index should actually point at final white space
        # AFTER the delimiter
        # Get index of last delimiter before current position
        prev_delimiter_index = text[0:cur_index].rfind(";")
        while text[prev_delimiter_index + 1] == " ":
            prev_delimiter_index += 1

        # Get index of first delimiter after current position
        # (or EOL if no delimiter after cursor)
        next_delimiter_index = text.find(";", cur_index)
        if next_delimiter_index == -1:
            next_delimiter_index = len(text)

        # Get part of string that occurs before cursor
        part1 = text[0:prev_delimiter_index + 1]

        # Get string value from before auto finished string is selected
        # pre = text[prev_delimiter_index + 1:cur_index - 1]

        # Get part of string that occurs AFTER cursor
        part2 = text[next_delimiter_index:]

        return part1 + auto_string + part2
