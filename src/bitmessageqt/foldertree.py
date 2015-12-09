from PyQt4 import QtCore, QtGui

from helper_sql import *
from utils import *
import shared
from settingsmixin import SettingsMixin

class AccountMixin (object):
    ALL = 0
    NORMAL = 1
    CHAN = 2
    MAILINGLIST = 3
    SUBSCRIPTION = 4
    BROADCAST = 5

    def accountColor (self):
        if not self.isEnabled:
            return QtGui.QColor(128, 128, 128)
        elif self.type == self.CHAN:
            return QtGui.QColor(216, 119, 0)
        elif self.type in [self.MAILINGLIST, self.SUBSCRIPTION]:
            return QtGui.QColor(137, 04, 177)
        else:
            return QtGui.QApplication.palette().text().color()
            
    def folderColor (self):
        if not self.parent.isEnabled:
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
        self.updateText()
    
    def setUnreadCount(self, cnt):
        self.unreadCount = int(cnt)
        self.updateText()

    def setEnabled(self, enabled):
        self.isEnabled = enabled
        if hasattr(self, "setExpanded"):
            self.setExpanded(enabled)
        if isinstance(self, Ui_AddressWidget):
            for i in range(self.childCount()):
                if isinstance(self.child(i), Ui_FolderWidget):
                    self.child(i).setEnabled(enabled)
        self.updateText()

    def setType(self):
        if self.address is None:
            self.type = self.ALL
        elif shared.safeConfigGetBoolean(self.address, 'chan'):
            self.type = self.CHAN
        elif shared.safeConfigGetBoolean(self.address, 'mailinglist'):
            self.type = self.MAILINGLIST
        else:
            self.type = self.NORMAL
    
    def updateText(self):
        pass


class Ui_FolderWidget(QtGui.QTreeWidgetItem, AccountMixin):
    folderWeight = {"inbox": 1, "new": 2, "sent": 3, "trash": 4}
    def __init__(self, parent, pos = 0, address = "", folderName = "", unreadCount = 0):
        super(QtGui.QTreeWidgetItem, self).__init__()
        self.initialised = False
        self.setAddress(address)
        self.setFolderName(folderName)
        self.setUnreadCount(unreadCount)
        self.parent = parent
        self.initialised = True
        self.updateText()
        parent.insertChild(pos, self)

    def setFolderName(self, fname):
        self.folderName = str(fname)
        self.setData(0, QtCore.Qt.UserRole, self.folderName)
        self.updateText()
        
    def updateText(self):
        if not self.initialised:
            return
        text = QtGui.QApplication.translate("MainWindow", self.folderName)
        font = QtGui.QFont()
        if self.unreadCount > 0:
            text += " (" + str(self.unreadCount) + ")"
            font.setBold(True)
        else:
            font.setBold(False)
        self.setFont(0, font)
        self.setForeground(0, self.folderBrush())
        self.setText(0, text)
        self.setToolTip(0, text)
 #       self.setData(0, QtCore.Qt.UserRole, [self.address, self.folderName])

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
            if self.treeWidget().header().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if x == y:
                return self.folderName < other.folderName
            else:
                return (x >= y if reverse else x < y)

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)
    

class Ui_AddressWidget(QtGui.QTreeWidgetItem, AccountMixin, SettingsMixin):
    def __init__(self, parent, pos = 0, address = None, unreadCount = 0, enabled = True):
        super(QtGui.QTreeWidgetItem, self).__init__()
        parent.insertTopLevelItem(pos, self)
        # only set default when creating
        #super(QtGui.QTreeWidgetItem, self).setExpanded(shared.config.getboolean(self.address, 'enabled'))
        self.initialised = False
        self.setAddress(address)
        self.setEnabled(enabled)
        self.setUnreadCount(unreadCount)
        self.initialised = True
        self.setType() # does updateText
        
    def _getLabel(self):
        if self.address is None:
            return unicode(str(QtGui.QApplication.translate("MainWindow", "All accounts")), 'utf-8')
        else:
            try:
                return unicode(shared.config.get(self.address, 'label'), 'utf-8)')
            except:
                return unicode(self.address, 'utf-8')
    
    def _getAddressBracket(self, unreadCount = False):
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
                    return avatarize(self._getLabel())
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
        if role == QtCore.Qt.EditRole:
            shared.config.set(str(self.address), 'label', str(value.toString()))
            shared.writeKeysFile()
            return
        return super(Ui_AddressWidget, self).setData(column, role, value)
        
    def setAddress(self, address):
        super(Ui_AddressWidget, self).setAddress(address)
        self.setData(0, QtCore.Qt.UserRole, self.address)
    
    def updateText(self):
        if not self.initialised:
            return
        self.emitDataChanged()
    
    def setExpanded(self, expand):
        super(Ui_AddressWidget, self).setExpanded(expand)
        self.updateText()
    
    def _getSortRank(self):
        ret = self.type
        if not self.isEnabled:
            ret += 100
        return ret

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if (isinstance(other, Ui_AddressWidget)):
            reverse = False
            if self.treeWidget().header().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if self._getSortRank() == other._getSortRank():
                x = self._getLabel().decode('utf-8').lower()
                y = other._getLabel().decode('utf-8').lower()
                return x < y
            return (not reverse if self._getSortRank() < other._getSortRank() else reverse)

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)

        
class Ui_SubscriptionWidget(Ui_AddressWidget, AccountMixin):
    def __init__(self, parent, pos = 0, address = "", unreadCount = 0, label = "", enabled = True):
        super(QtGui.QTreeWidgetItem, self).__init__()
        parent.insertTopLevelItem(pos, self)
        # only set default when creating
        #super(QtGui.QTreeWidgetItem, self).setExpanded(shared.config.getboolean(self.address, 'enabled'))
        self.initialised = False
        self.setAddress(address)
        self.setEnabled(enabled)
        self.setType()
        self.setLabel(label)
        self.initialised = True
        self.setUnreadCount (unreadCount) # does updateText
    
    def setLabel(self, label):
        self.label = label
    
    def _getLabel(self):
        return unicode(self.label, 'utf-8)')
        
    def setType(self):
        self.type = self.SUBSCRIPTION
        
    def setData(self, column, role, value):
        if role == QtCore.Qt.EditRole:
            self.setLabel(str(value.toString()))
            sqlExecute(
                '''UPDATE subscriptions SET label=? WHERE address=?''',
                self.label, self.address)
            return
        return super(Ui_SubscriptionWidget, self).setData(column, role, value)
    
    def updateText(self):
        if not self.initialised:
            return
        self.emitDataChanged()
        
        
class Ui_AddressBookWidgetItem(QtGui.QTableWidgetItem, AccountMixin):
    def __init__ (self, text, type = AccountMixin.NORMAL):
        super(QtGui.QTableWidgetItem, self).__init__(text)
        self.label = text
        self.type = type
        self.setEnabled(True)
        self.setForeground(self.accountBrush())

    def __lt__ (self, other):
        if (isinstance(other, Ui_AddressBookWidgetItem)):
            reverse = False
            if self.tableWidget().horizontalHeader().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if self.type == other.type:
                return self.label.decode('utf-8').lower() < other.label.decode('utf-8').lower()
            else:
                return (not reverse if self.type < other.type else reverse)
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class Ui_AddressBookWidgetItemLabel(Ui_AddressBookWidgetItem):
    def __init__ (self, address, label, type):
        Ui_AddressBookWidgetItem.__init__(self, label, type)
        self.address = address
        self.label = label
        self.setIcon(avatarize(address))
        self.setToolTip(label + " (" + address + ")")

    def setLabel(self, label):
        self.label = label
        self.setToolTip(self.label + " (" + self.address + ")")


class Ui_AddressBookWidgetItemAddress(Ui_AddressBookWidgetItem):
    def __init__ (self, address, label, type):
        Ui_AddressBookWidgetItem.__init__(self, address, type)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setToolTip(label + " (" + address + ")")