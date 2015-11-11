from PyQt4 import QtCore, QtGui

from utils import *
import shared
from settingsmixin import SettingsMixin

class AccountMixin (object):
    def accountColor (self):
        if not self.isEnabled:
            return QtGui.QColor(128, 128, 128)
        elif self.type == "chan":
            return QtGui.QColor(216, 119, 0)
        elif self.type == "mailinglist" or self.type == "subscription":
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
        if shared.safeConfigGetBoolean(self.address, 'chan'):
            self.type = "chan"
        elif shared.safeConfigGetBoolean(self.address, 'mailinglist'):
            self.type = "mailinglist"
        else:
            self.type = "normal"
    
    def updateText(self):
        pass


class Ui_FolderWidget(QtGui.QTreeWidgetItem, AccountMixin):
    folderWeight = {"inbox": 1, "sent": 2, "trash": 3}
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
                x = 4
            if other.folderName in self.folderWeight:
                y = self.folderWeight[other.folderName]
            else:
                y = 4
            reverse = False
            if self.treeWidget().header().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if x == y:
                return self.folderName < other.folderName
            else:
                return (x >= y if reverse else x < y)

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)
    

class Ui_AddressWidget(QtGui.QTreeWidgetItem, AccountMixin, SettingsMixin):
    def __init__(self, parent, pos = 0, address = "", unreadCount = 0, enabled = True):
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
        
    def setAddress(self, address):
        super(Ui_AddressWidget, self).setAddress(address)
        self.setData(0, QtCore.Qt.UserRole, self.address)
    
    def updateText(self):
        if not self.initialised:
            return
        text = unicode(shared.config.get(self.address, 'label'), 'utf-8)') + ' (' + self.address + ')'
        
        font = QtGui.QFont()
        if self.unreadCount > 0:
            # only show message count if the child doesn't show
            if not self.isExpanded():
                text += " (" + str(self.unreadCount) + ")"
            font.setBold(True)
        else:
            font.setBold(False)
        self.setFont(0, font)
            
        #set text color
        self.setForeground(0, self.accountBrush())

        self.setIcon(0, avatarize(self.address))
        self.setText(0, text)
        self.setToolTip(0, text)
#        self.setData(0, QtCore.Qt.UserRole, [self.address, "inbox"])
    
    def setExpanded(self, expand):
        super(Ui_AddressWidget, self).setExpanded(expand)
        self.updateText()

    def edit(self):
        self.setText(0, shared.config.get(self.address, 'label'))
        super(QtGui.QAbstractItemView, self).edit()

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if (isinstance(other, Ui_AddressWidget)):
            reverse = False
            if self.treeWidget().header().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if self.isEnabled == other.isEnabled:
                if self.type == other.type:
                    if shared.config.get(self.address, 'label'):
                        x = shared.config.get(self.address, 'label').decode('utf-8').lower()
                    else:
                        x = self.address.decode('utf-8').lower()
                    if shared.config.get(other.address, 'label'):
                        y = shared.config.get(other.address, 'label').decode('utf-8').lower()
                    else:
                        y = other.address.decode('utf-8').lower()
                    return x < y
                else:
                    return (reverse if self.type == "mailinglist" else not reverse)
#            else:
            return (not reverse if self.isEnabled else reverse)

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
        
    def setType(self):
        self.type = "subscription"
        
    def edit(self):
        self.setText(0, self.label)
        super(QtGui.QAbstractItemView, self).edit()
    
    def updateText(self):
        if not self.initialised:
            return
        text = unicode(self.label, 'utf-8)') + ' (' + self.address + ')'
        
        font = QtGui.QFont()
        if self.unreadCount > 0:
            # only show message count if the child doesn't show
            if not self.isExpanded():
                text += " (" + str(self.unreadCount) + ")"
            font.setBold(True)
        else:
            font.setBold(False)
        self.setFont(0, font)
            
        #set text color
        self.setForeground(0, self.accountBrush())

        self.setIcon(0, avatarize(self.address))
        self.setText(0, text)
        self.setToolTip(0, text)
#        self.setData(0, QtCore.Qt.UserRole, [self.address, "inbox"])
    
    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if (isinstance(other, Ui_SubscriptionWidget)):
            reverse = False
            if self.treeWidget().header().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if self.isEnabled == other.isEnabled:
                if self.label:
                    x = self.label.decode('utf-8').lower()
                else:
                    x = self.address.decode('utf-8').lower()
                if other.label:
                    y = other.label.decode('utf-8').lower()
                else:
                    y = other.address.decode('utf-8').lower()
                return x < y
#            else:
            return (not reverse if self.isEnabled else reverse)

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)
        
class Ui_AddressBookWidgetItem(QtGui.QTableWidgetItem, AccountMixin):
    _types = {'normal': 0, 'chan': 1, 'subscription': 2}

    def __init__ (self, text, type = 'normal'):
        super(QtGui.QTableWidgetItem, self).__init__(text)
        self.label = text
        self.type = type
        try:
            self.typeNum = self._types[self.type]
        except:
            self.type = 0
        self.setEnabled(True)
        self.setForeground(self.accountBrush())

    def __lt__ (self, other):
        if (isinstance(other, Ui_AddressBookWidgetItem)):
            reverse = False
            if self.tableWidget().horizontalHeader().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if self.typeNum == other.typeNum:
                return self.label.decode('utf-8').lower() < other.label.decode('utf-8').lower()
            else:
                return (not reverse if self.typeNum < other.typeNum else reverse)
        return super(QtGui.QTableWidgetItem, self).__lt__(other)


class Ui_AddressBookWidgetItemLabel(Ui_AddressBookWidgetItem):
    def __init__ (self, address, label, type):
        Ui_AddressBookWidgetItem.__init__(self, label, type)
        self.setIcon(avatarize(address))
        self.setToolTip(label + " (" + address + ")")


class Ui_AddressBookWidgetItemAddress(Ui_AddressBookWidgetItem):
    def __init__ (self, address, label, type):
        Ui_AddressBookWidgetItem.__init__(self, address, type)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setToolTip(label + " (" + address + ")")