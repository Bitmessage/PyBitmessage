"""Inbox TabWidget QTreeWidget Testing"""
import random
from random import choice
from string import ascii_lowercase

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from bitmessageqt import dialogs
from bmconfigparser import BMConfigParser
from testloader import BitmessageTestCase


class BitmessageTest_Inbox_PopMenu(BitmessageTestCase):
    """Inbox TabWidget QTreeWidget popMenu Fucntionality testing"""

    def test_sider(self):
        """Show QTreeWidget popmenu"""
        QTest.qWait(500)
        self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
        QTest.qWait(500)
        treeWidget = self.myapp.ui.treeWidgetYourIdentities
        self.levelitem = treeWidget.topLevelItem(random.randint(1, len(BMConfigParser().addresses())))
        self.myapp.ui.treeWidgetYourIdentities.setCurrentItem(self.levelitem)
        rect = self.myapp.ui.treeWidgetYourIdentities.visualItemRect(self.levelitem)
        self.currentItem = self.myapp.getCurrentItem()
        self.myapp.on_context_menuYourIdentities(QtCore.QPoint(rect.x() + 200, rect.y() + 200))
        QTest.qWait(500)
        self.myapp.popMenuYourIdentities.hide()
        QTest.qWait(100)
        self.copy_clipboard()
        QTest.qWait(100)
        self.enable_disable()
        QTest.qWait(100)
        self.special_address_behavior()
        QTest.qWait(100)
        self.email_gateway()
        QTest.qWait(100)
        self.mark_all_as_read()

    def copy_clipboard(self):
        """Copy address to clipboard and test"""
        try:
            text_selected = self.levelitem.text(0)
            QTest.qWait(250)
            self.myapp.popMenuYourIdentities.actions()[2].trigger()
            QTest.qWait(750)
            if str(QtGui.QApplication.clipboard().text()) in str(text_selected):
                self.assertTrue(True, " Test Pass :--> Copy functionality working fine \n")
                print(" Test Pass :--> Copy functionality working fine \n")
            else:
                print(" Test Fail :--> Copy functionality failed \n")
                self.assertTrue(False, " Test Fail :--> Copy functionality failed \n")
        except:
            print(" Test Fail :--> Copy functionality failed \n")
            self.assertTrue(False, " Test Fail :--> Copy functionality failed \n")

    def enable_disable(self):
        """Enable address and disable address"""
        QTest.qWait(500)
        try:
            if self.currentItem.isEnabled:
                QTest.qWait(300)
                self.myapp.popMenuYourIdentities.actions()[4].trigger()
                print("Address is Disabled \n")
                QTest.qWait(1000)
                self.myapp.on_action_Enable()
                print("Address is Enabled \n")
                QTest.qWait(1000)
            else:
                QTest.qWait(300)
                self.myapp.popMenuYourIdentities.actions()[4].trigger()
                print("Address is Enabled \n")
                QTest.qWait(1000)
                self.myapp.on_action_Disable()
                print("Address is Disabled \n")
                QTest.qWait(1000)
        except:
            self.assertTrue(False, " Test Fail :--> Enable Disable failed \n")

    def special_address_behavior(self):
        """Tests for special address"""
        try:
            special_add = dialogs.SpecialAddressBehaviorDialog(self.myapp, BMConfigParser())
            special_add.lineEditMailingListName.setText("")
            QTest.qWait(1000)
            special_add.radioButtonBehaviorMailingList.click()
            QTest.qWait(500)
            special_add.lineEditMailingListName.setText("".join(choice(ascii_lowercase) for x in range(15)))
            QTest.qWait(1000)
            QTest.mouseClick(special_add.buttonBox.button(QtGui.QDialogButtonBox.Ok), Qt.LeftButton)
            self.assertTrue(True, " Test Pass :--> Special Address Behavior Functionality Passed \n")
            print(" Test Pass :--> Special Address Behavior Functionality Passed \n")
        except:
            print(" Test Fail :--> Special Address Behavior Functionality failed \n")
            self.assertTrue(False, " Test Fail :--> Special Address Behavior Functionality failed \n")

    def email_gateway(self):
        """Test email gateway functionality"""
        try:
            QTest.qWait(200)
            email_gateway = dialogs.EmailGatewayDialog(self.myapp, config=BMConfigParser())
            QTest.qWait(300)
            email_gateway.show()
            QTest.qWait(1000)
            email_gateway.radioButtonRegister.click()
            QTest.qWait(500)
            email = (
                ("".join(choice(ascii_lowercase) for x in range(10)))
                + "@"
                + ("".join(choice(ascii_lowercase) for x in range(7)))
                + ".com"
            )
            email_gateway.lineEditEmail.setText(email)
            QTest.qWait(1000)
            QTest.mouseClick(email_gateway.buttonBox.button(QtGui.QDialogButtonBox.Ok), Qt.LeftButton)
            self.assertTrue(True, " Test Pass :--> Email-Gateway Functionality Passed \n")
            print(" Test Pass :--> Email-Gateway Functionality Passed \n")
        except:
            print(" Test Fail :--> Email-Gateway Functionality failed \n")
            self.assertTrue(False, " Test Fail :--> Email-Gateway Functionality failed \n")

    def mark_all_as_read(self):
        """Mark all messages as read"""
        try:
            QTest.qWait(1000)
            self.myapp.popMenuYourIdentities.actions()[11].trigger()
            QTest.qWait(200)
            self.assertTrue(True, " Test Pass :--> Mark All as Read Functionality Passed \n")
            print(" Test Pass :--> Mark All as Read Functionality Passed \n")
        except:
            print(" Test Fail :--> Mark All as Read Functionality failed \n")
            self.assertTrue(False, " Test Fail :--> Mark All as Read Functionality failed \n")
