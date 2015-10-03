from PyQt4 import QtCore, QtGui

from utils import *
import shared

class Ui_FolderWidget(QtGui.QTreeWidgetItem):
    folderWeight = {"inbox": 1, "sent": 2, "trash": 3}
    def __init__(self, parent, pos = 0, address = "", folderName = "", unreadCount = 0):
        super(QtGui.QTreeWidgetItem, self).__init__()
        self.address = address
        self.folderName = folderName
        self.unreadCount = unreadCount
        parent.insertChild(pos, self)
        self.updateText()

    def setAddress(self, address):
        self.address = str(address)
        self.updateText()
    
    def setUnreadCount(self, cnt):
        self.unreadCount = int(cnt)
        self.updateText()

    def setFolderName(self, fname):
        self.folderName = str(fname)
        self.updateText()
        
    def updateText(self):
        text = QtGui.QApplication.translate("MainWindow", self.folderName)
        font = QtGui.QFont()
        if self.unreadCount > 0:
            text += " (" + str(self.unreadCount) + ")"
            font.setBold(True)
        else:
            font.setBold(False)
        self.setFont(0, font)
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
    

class Ui_AddressWidget(QtGui.QTreeWidgetItem):
    def __init__(self, parent, pos = 0, address = "", unreadCount = 0):
        super(QtGui.QTreeWidgetItem, self).__init__()
        self.address = address
        self.unreadCount = unreadCount
        parent.insertTopLevelItem(pos, self)
        # only set default when creating
        #super(QtGui.QTreeWidgetItem, self).setExpanded(shared.config.getboolean(self.address, 'enabled'))
        self.setExpanded(shared.safeConfigGetBoolean(self.address, 'enabled'))
        self.updateText()
    
    def setAddress(self, address):
        self.address = str(address)
        self.updateText()

    def setUnreadCount(self, cnt):
        self.unreadCount = int(cnt)
        self.updateText()
        
    def updateText(self):
        text = QtGui.QApplication.translate("MainWindow",
            unicode(shared.config.get(self.address, 'label'), 'utf-8)')
                + ' (' + self.address + ')')
        
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
        if shared.safeConfigGetBoolean(self.address, 'enabled'):
            if shared.safeConfigGetBoolean(self.address, 'mailinglist'):
                brush = QtGui.QBrush(QtGui.QColor(137, 04, 177))
            else:
                brush = QtGui.QBrush(QtGui.QApplication.palette().text().color())
            #self.setExpanded(True)        
        else:
            brush = QtGui.QBrush(QtGui.QColor(128, 128, 128))
            #self.setExpanded(False)
        brush.setStyle(QtCore.Qt.NoBrush)
        self.setForeground(0, brush)

        self.setIcon(0, avatarize(self.address))
        self.setText(0, text)
        self.setToolTip(0, text)
#        self.setData(0, QtCore.Qt.UserRole, [self.address, "inbox"])
    
    def setExpanded(self, expand):
        super(Ui_AddressWidget, self).setExpanded(expand)
        self.updateText()

    # label (or address) alphabetically, disabled at the end
    def __lt__(self, other):
        if (isinstance(other, Ui_AddressWidget)):
            reverse = False
            if self.treeWidget().header().sortIndicatorOrder() == QtCore.Qt.DescendingOrder:
                reverse = True
            if shared.config.getboolean(self.address, 'enabled') == shared.config.getboolean(other.address, 'enabled'):
                if shared.config.get(self.address, 'label'):
                    x = shared.config.get(self.address, 'label').decode('utf-8').lower()
                else:
                    x = self.address.decode('utf-8').lower()
                if shared.config.get(other.address, 'label'):
                    y = shared.config.get(other.address, 'label').decode('utf-8').lower()
                else:
                    y = other.address.decode('utf-8').lower()
                return x < y
#            else:
            return (not reverse if shared.config.getboolean(self.address, 'enabled') else reverse)

        return super(QtGui.QTreeWidgetItem, self).__lt__(other)
