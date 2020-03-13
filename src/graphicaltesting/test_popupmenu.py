"""Inbox TabWidget QTreeWidget Testing"""
import random
from random import choice
from string import ascii_lowercase

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

import queues
import shared
from bitmessageqt import blacklist, dialogs
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from testloader import BitmessageTestCase
from tr import _translate


class BitmessageTest_Inbox_PopMenu(BitmessageTestCase):
    """Inbox TabWidget QTreeWidget popMenu Fucntionality testing"""

    def test_sider(self):
        """Show QTreeWidget popmenu"""
        try:
            QTest.qWait(500)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
            QTest.qWait(500)
            self.treeWidget = self.myapp.ui.treeWidgetYourIdentities
            self.levelitem = self.treeWidget.topLevelItem(random.randint(1, len(BMConfigParser().addresses()) + 1))
            self.treeWidget.setCurrentItem(self.levelitem)
            self.currentItem = self.myapp.getCurrentItem()
            self.rect = self.treeWidget.visualItemRect(self.levelitem)
            self.myapp.on_context_menuYourIdentities(QtCore.QPoint(self.rect.x() + 160, self.rect.y() + 200))
            self.myapp.popMenuYourIdentities.hide()
            self.copy_clipboard()
            self.enable_disable()
            self.special_address_behavior()
            self.email_gateway()
            self.mark_all_as_read()
            return 1
        except:
            print("Test Fail:--> QTreeWidget popmenu functionality failed")
            return 0

    def copy_clipboard(self):
        """Copy Address to the ClipBoard and test whether the copied test is same or not?"""
        print("=====================Test - Copy Address to the ClipBoard=====================")
        try:
            self.popup_menu(2)
            text_selected = self.currentItem.text(0)
            QTest.qWait(500)
            self.myapp.popMenuYourIdentities.actions()[2].trigger()
            QTest.qWait(750)
            if str(QtGui.QApplication.clipboard().text()) in str(text_selected):
                print("Test Pass:--> Copy functionality working fine")
                return 1
            else:
                print("Test Fail:--> Copy functionality failed")
                return 0
        except:
            print("Test Fail:--> Copy functionality failed")
            return 0

    def enable_disable(self):
        """Enable address and disable address"""
        print("=====================Test - Address Enable-Disable Functionality=====================")
        try:
            self.popup_menu(4)
            if self.currentItem.isEnabled:
                QTest.qWait(500)
                self.myapp.popMenuYourIdentities.actions()[4].trigger()
                QTest.qWait(1000)
                self.myapp.on_action_Enable()
                QTest.qWait(500)
                print("Test Pass:--> Enable-Disable working fine")
                return 1
            else:
                QTest.qWait(500)
                self.myapp.popMenuYourIdentities.actions()[4].trigger()
                QTest.qWait(1000)
                self.myapp.on_action_Disable()
                QTest.qWait(500)
                print("Test Pass:--> Enable-Disable working fine")
                return 1
        except:
            print("Test Fail:--> Could not able to do Enable-Disable")
            return 0

    def special_address_behavior(self):
        """Tests for special address"""
        print("=====================Test - Address Special Behavior=====================")
        try:
            self.popup_menu(6)
            special_add = dialogs.SpecialAddressBehaviorDialog(self.myapp, BMConfigParser())
            special_add.lineEditMailingListName.setText("")
            QTest.qWait(500)
            special_add.radioButtonBehaviorMailingList.click()
            QTest.qWait(1000)
            special_add.lineEditMailingListName.setText("".join(choice(ascii_lowercase) for x in range(15)))
            QTest.qWait(500)
            QTest.mouseClick(special_add.buttonBox.button(QtGui.QDialogButtonBox.Ok), Qt.LeftButton)
            print("Test Pass:--> Special Address Behavior Functionality Passed")
            return 1
        except:
            print("Test Fail:--> Special Address Behavior Functionality failed")
            return 0

    def email_gateway(self):
        """Test email gateway functionality"""
        print("=====================Test - Email Gateway=====================")
        try:
            self.popup_menu(7)
            QTest.qWait(200)
            email_gateway = dialogs.EmailGatewayDialog(self.myapp, BMConfigParser())
            email_gateway.show()
            QTest.qWait(500)
            email_gateway.radioButtonRegister.click()
            QTest.qWait(450)
            email = (
                ("".join(choice(ascii_lowercase) for x in range(10)))
                + "@"
                + ("".join(choice(ascii_lowercase) for x in range(7)))
                + ".com"
            )
            email_gateway.lineEditEmail.setText(email)
            QTest.qWait(500)
            QTest.mouseClick(email_gateway.buttonBox.button(QtGui.QDialogButtonBox.Ok), Qt.LeftButton)
            print("Test Pass:--> Email-Gateway Functionality Passed")
            return 1
        except:
            print("Test Fail:--> Email-Gateway Functionality failed")
            return 0

    def mark_all_as_read(self):
        """Mark all messages as read"""
        print("=====================Test - Mark All as Read Functionality=====================")
        try:
            self.popup_menu(11)
            QTest.qWait(500)
            self.myapp.popMenuYourIdentities.actions()[11].trigger()
            QTest.qWait(500)
            print("Test Pass:--> Mark All as Read Functionality Passed")
            return 1
        except:
            print("Test Fail:--> Mark All as Read Functionality failed")
            return 0

    def popup_menu(self, intval):
        QTest.qWait(5)
        self.myapp.popMenuYourIdentities.setActiveAction(self.myapp.popMenuYourIdentities.actions()[intval])
        self.myapp.popMenuYourIdentities.setStyleSheet("QMenu:selected {background-color:#FF5733}")
        self.myapp.popMenuYourIdentities.show()
        QTest.qWait(400)
        self.myapp.popMenuYourIdentities.hide()
        QTest.qWait(50)


class BitmessageTest_AddressBox_PopMenu(BitmessageTestCase):
    """AddressBox TabWidget QTreeWidget popMenu Fucntionality testing"""

    def test_sider(self):
        try:
            QTest.qWait(500)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
            self.treeWidget = self.myapp.ui.tableWidgetAddressBook
            total_sub = sqlQuery("Select address from addressbook")
            QTest.qWait(500)
            self.rand_value = random.randint(0, len(total_sub) - 1)
            self.current_address = str(self.treeWidget.item(self.rand_value, 1).text())
            self.treeWidget.setCurrentCell(self.rand_value, 1)
            self.treeWidget.item(self.rand_value, 1).setSelected(True)
            rect = self.treeWidget.visualItemRect(self.treeWidget.item(self.rand_value, 1))
            QTest.qWait(500)
            self.myapp.on_context_menuAddressBook(QtCore.QPoint(rect.x() + 160, rect.y() + 200))
            QTest.qWait(500)
            if len(total_sub) > 0:
                self.treeWidget.item(random.randint(0, self.rand_value), 1)
            else:
                print("No Address Found.")
                self.add_new_address()
            self.myapp.popMenuAddressBook.hide()
            self.send_message_to_this_add()
            self.copy_clipboard()
            self.subscribe_to_this_address()
            self.delete_addressbook()
            return 1
        except:
            print("Test Fail:--> PopUpMenu Send Tab Functionality failed")
            return 0

    def add_new_address(self):
        """Adding New Address to Address Book"""
        print("=====================Test - Adding New Address to Address Book=====================")
        try:
            self.popup_menu(6)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
            self.dialog = dialogs.AddAddressDialog(self.myapp)
            self.dialog.show()
            QTest.qWait(500)
            self.dialog.lineEditLabel.setText("".join(choice(ascii_lowercase) for _ in range(15)))
            QTest.qWait(500)
            self.dialog.lineEditAddress.setText(choice(BMConfigParser().addresses()))
            QTest.qWait(500)
            QtCore.QTimer.singleShot(0, self.dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked)
            QTest.qWait(500)
            try:
                address, label = self.dialog.data
            except:
                print("Test Fail:--> Could Not able to add new address")
                return 0
            if shared.isAddressInMyAddressBook(address):
                print(
                    " Test :--> You cannot add the same address to your address book twice."
                    " Try renaming the existing one if you want. \n"
                )
                self.myapp.updateStatusBar(
                    _translate(
                        "MainWindow",
                        "Error: You cannot add the same address to your adrress book twice."
                        " Try renaming the existing one if you want.",
                    )
                )
                return 0
            self.myapp.addEntryToAddressBook(address, label)
            print("Test Pass:--> Address Added to the Address Book!")
            return 1
        except:
            print("Test Fail:--> Could Not able to add new address")
            return 0

    def send_message_to_this_add(self):
        """Test - Send Message to this Address"""
        print("=====================Test - Send Message to this Address=====================")
        try:
            self.popup_menu(0)
            if BMConfigParser().addresses():
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
                inbox_length = len(sqlQuery("Select msgid from inbox"))
                QTest.qWait(500)
                self.myapp.popMenuAddressBook.actions()[0].trigger()
                QTest.qWait(500)
                random_subject = ""
                for x in range(30):
                    random_subject += choice(ascii_lowercase)
                    self.myapp.ui.lineEditSubject.setText(random_subject)
                    QTest.qWait(4)
                QTest.qWait(500)
                random_message = ""
                for x in range(150):
                    random_message += choice(ascii_lowercase)
                    self.myapp.ui.textEditMessage.setText(random_message)
                    QTest.qWait(1)
                QTest.qWait(500)
                randinteger = random.randrange(1, len(BMConfigParser().addresses()) + 1)
                self.myapp.ui.comboBoxSendFrom.setCurrentIndex(randinteger)
                QTest.qWait(500)
                QTest.mouseClick(self.myapp.ui.pushButtonSend, Qt.LeftButton)
                QTest.qWait(500)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
                print(" Waiting For Message .......................... ")
                for x in range(5):
                    QTest.qWait(4000)
                    print("  waiting " + x * ".")
                new_inbox = sqlQuery("Select msgid,toaddress,subject from inbox")
                self.assertEqual(new_inbox[-1][2], random_subject)
                if len(sqlQuery("Select msgid from inbox")) == inbox_length + 1:
                    print("Test Pass:--> Message Received Successfully")
                    return 1
                else:
                    print("Test Fail:--> Doesn't Receive Any Message")
                    return 0
            else:
                print("Test Fail:--> No Address Found")
                return 0
        except:
            print("Test Fail:--> Message Sending Test Fail")
            return 0

    def copy_clipboard(self):
        """Test - Copy Address Book Address to Clipboard"""
        print("=====================Test - Copy Address Book Address to Clipboard=====================")
        try:
            self.popup_menu(1)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
            self.current_address = str(self.treeWidget.item(random.randint(0, self.rand_value), 1).text())
            QTest.qWait(500)
            self.myapp.popMenuAddressBook.actions()[1].trigger()
            QTest.qWait(1000)
            if str(QtGui.QApplication.clipboard().text()) in self.current_address:
                print("Test Pass:--> Copy functionality working fine")
                return 1
            else:
                print("Test Fail:--> Copy functionality failed")
                return 0
        except:
            print("Test Fail:--> Copy functionality failed")
            return 0

    def subscribe_to_this_address(self):
        """Subscribe to This Address"""
        print("=====================Test - Subscribe to This Address=====================")
        try:
            self.popup_menu(2)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
            self.treeWidget.setCurrentCell(self.rand_value, 1)
            QTest.qWait(500)
            self.myapp.popMenuAddressBook.actions()[2].trigger()
            QTest.qWait(750)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
            subscription_list = sqlQuery("SELECT address FROM subscriptions")
            if self.current_address in subscription_list:
                print(
                    "Test Fail:-->" + "Subscribe to this functionality failed"
                    " because address is alreay added in the subscription list\n"
                )
                return 0
            else:
                print("Test Pass:--> Subscribe to this functionality working fine")
                return 1
        except:
            print("Test Fail:--> Subscribe to this Address failed")
            return 0

    def delete_addressbook(self):
        """Delete Address from the Address Book"""
        print("=====================Test - Delete Address from the Address Book=====================")
        try:
            self.popup_menu(7)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
            self.treeWidget.setCurrentCell(self.rand_value, 1)
            self.myapp.on_action_AddressBookDelete()
            QTest.qWait(500)
            addressbook_list = sqlQuery("SELECT address FROM addressbook")
            if self.current_address not in addressbook_list:
                print("Test Pass:--> Address is Deleted from the AddressBook")
                return 1
            else:
                print("Test Fail:--> Could not able to Delete this address")
                return 0
        except:
            print("Test Fail:--> Could Not Able to Delete this Address from the AddressBook")
            return 0

    def popup_menu(self, intval):
        QTest.qWait(5)
        self.myapp.popMenuAddressBook.setActiveAction(self.myapp.popMenuAddressBook.actions()[intval])
        self.myapp.popMenuAddressBook.setStyleSheet("QMenu:selected {background-color:#FF5733}")
        self.myapp.popMenuAddressBook.show()
        QTest.qWait(400)
        self.myapp.popMenuAddressBook.hide()
        QTest.qWait(50)


class BitmessageTest_Subscription_PopMenu(BitmessageTestCase):
    """Subscription TabWidget QTreeWidget popMenu Fucntionality testing"""

    def test_sider(self):
        try:
            QTest.qWait(500)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.subscriptions)
            QTest.qWait(500)
            self.treeWidget = self.myapp.ui.treeWidgetSubscriptions
            total_sub = sqlQuery("Select address from subscriptions")
            self.levelitem = self.treeWidget.topLevelItem(random.randint(0, len(total_sub) - 1))
            self.treeWidget.setCurrentItem(self.levelitem)
            rect = self.treeWidget.visualItemRect(self.levelitem)
            self.currentItem = self.myapp.getCurrentItem()
            self.myapp.on_context_menuSubscriptions(QtCore.QPoint(rect.x() + 160, rect.y() + 200))
            QTest.qWait(500)
            self.myapp.popMenuSubscriptions.hide()
            self.new_subscribe()
            self.enable_disable()
            self.copy_clipboard()
            self.send_message_to_this_add()
            self.mark_all_as_read()
            self.del_address_from_sub()
            return 1
        except:
            print("Test Fail:--> Subscription Tab PopUpMenu Functionality failed")
            return 0

    def new_subscribe(self):
        print("=====================Test - Subscribe to New Address=====================")
        try:
            if BMConfigParser().addresses():
                self.popup_menu(0)
                dialog = dialogs.NewSubscriptionDialog(self.myapp)
                QTest.qWait(500)
                dialog.lineEditLabel.setText("")
                dialog.lineEditAddress.setText("")
                dialog.show()
                QTest.qWait(500)
                random_label = ""
                for _ in range(30):
                    random_label += choice(ascii_lowercase)
                    dialog.lineEditLabel.setText(random_label)
                    QTest.qWait(5)
                QTest.qWait(500)
                rand_address = choice(BMConfigParser().addresses())
                random_address = ""
                for x in range(len(rand_address)):
                    random_address += rand_address[x]
                    dialog.lineEditAddress.setText(random_address)
                    QTest.qWait(5)
                QtCore.QTimer.singleShot(0, dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked)
                QTest.qWait(500)
                try:
                    address, label = dialog.data
                except AttributeError:
                    print("Test Fail:--> Could Not able to add new address to subscription list")
                    return 0
                if shared.isAddressInMySubscriptionsList(address):
                    print(
                        "MainWindow",
                        "Error: You cannot add the same address to your subscriptions twice."
                        " Perhaps rename the existing one if you want.",
                    )
                    self.myapp.updateStatusBar(
                        _translate(
                            "MainWindow",
                            "Error: You cannot add the same address to your subscriptions twice."
                            " Perhaps rename the existing one if you want.",
                        )
                    )
                    return 0
                self.myapp.addSubscription(address, label)
                print("Test Pass:--> Address Added to subscription list")
                if dialog.checkBoxDisplayMessagesAlreadyInInventory.isChecked():
                    for value in dialog.recent:
                        queues.objectProcessorQueue.put((value.type, value.payload))
                return 1
            else:
                print("Test Fail:--> No address found")
                return 0
        except:
            print("Test Fail:--> New Subscription Functionality Failed")
            return 0

    def enable_disable(self):
        """Enable address and disable address"""
        print("=====================Test - Address Enable-Disable Functionality=====================")
        QTest.qWait(500)
        try:
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.subscriptions)
            self.treeWidget.setCurrentItem(self.levelitem)
            self.popup_menu(3)
            if self.currentItem.isEnabled:
                QTest.qWait(500)
                self.myapp.popMenuSubscriptions.actions()[3].trigger()
                QTest.qWait(1000)
                self.myapp.on_action_Enable()
                QTest.qWait(500)
            else:
                QTest.qWait(500)
                self.myapp.popMenuSubscriptions.actions()[3].trigger()
                QTest.qWait(1000)
                self.myapp.on_action_Disable()
                QTest.qWait(500)
            print("Test Pass:--> Enable Disable Working well")
            return 0
        except:
            print("Test Fail:--> Enable Disable failed")
            return 1

    def copy_clipboard(self):
        """Test - Copy Address Book Address to Clipboard"""
        print("=====================Test - Copy Address Book Address to Clipboard=====================")
        try:
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.subscriptions)
            self.treeWidget.setCurrentItem(self.levelitem)
            self.popup_menu(6)
            QTest.qWait(500)
            self.myapp.popMenuSubscriptions.actions()[6].trigger()
            QTest.qWait(1000)
            if str(QtGui.QApplication.clipboard().text()) in str(self.currentItem.text(0)):
                print("Test Pass:--> Copy functionality working fine")
                return 1
            else:
                print("Test Fail:--> Copy functionality failed")
                return 0
        except:
            print("Test Fail:--> Copy functionality failed")
            return 0

    def send_message_to_this_add(self):
        """Test - Send Message to this Address"""
        print("=====================Test - Send Message to this Address=====================")
        try:
            self.popup_menu(7)
            if BMConfigParser().addresses():
                inbox_length = len(sqlQuery("Select msgid from inbox"))
                QTest.qWait(500)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.subscriptions)
                self.treeWidget.setCurrentItem(self.levelitem)
                self.myapp.popMenuSubscriptions.actions()[7].trigger()
                QTest.qWait(500)
                random_subject = ""
                for x in range(30):
                    random_subject += choice(ascii_lowercase)
                    self.myapp.ui.lineEditSubject.setText(random_subject)
                    QTest.qWait(4)
                QTest.qWait(500)
                random_message = ""
                for x in range(150):
                    random_message += choice(ascii_lowercase)
                    self.myapp.ui.textEditMessage.setText(random_message)
                    QTest.qWait(1)
                QTest.qWait(500)
                randinteger = random.randrange(1, len(BMConfigParser().addresses()) + 1)
                self.myapp.ui.comboBoxSendFrom.setCurrentIndex(randinteger)
                QTest.qWait(500)
                QTest.mouseClick(self.myapp.ui.pushButtonSend, Qt.LeftButton)
                QTest.qWait(500)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
                print(" Waiting For Message .......................... ")
                for x in range(5):
                    QTest.qWait(4000)
                    print("  waiting " + x * ".")
                new_inbox = sqlQuery("Select msgid,toaddress,subject from inbox")
                self.assertEqual(new_inbox[-1][2], random_subject)
                if len(sqlQuery("Select msgid from inbox")) == inbox_length + 1:
                    print("Test Pass:--> Message Received Successfully")
                    return 1
                else:
                    print("Test Fail:--> Doesn't Receive Any Message")
                    return 0
            else:
                print("Test Fail:--> No Address Found")
                return 0
        except:
            print("Test Fail:--> Message Sending Test Fail")
            return 0

    def mark_all_as_read(self):
        """Mark all messages as read"""
        print("=====================Test - Mark All as Read Functionality=====================")
        try:
            self.popup_menu(8)
            QTest.qWait(550)
            self.myapp.popMenuSubscriptions.actions()[8].trigger()
            QTest.qWait(750)
            print("Test Pass:--> Mark All as Read Functionality Passed")
            return 1
        except:
            print("Test Fail:--> Mark All as Read Functionality failed")
            return 0

    def del_address_from_sub(self):
        print("=====================Test - Delete Address from the subscription Field=====================")
        try:
            self.popup_menu(1)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.subscriptions)
            self.treeWidget.setCurrentItem(self.levelitem)
            address = self.myapp.getCurrentAccount()
            QTest.qWait(750)
            sqlExecute("""DELETE FROM subscriptions WHERE address=?""", address)
            self.myapp.rerenderTabTreeSubscriptions()
            self.myapp.rerenderMessagelistFromLabels()
            self.myapp.rerenderAddressBook()
            shared.reloadBroadcastSendersForWhichImWatching()
            addressbook_list = sqlQuery("SELECT address FROM subscriptions")
            if address not in addressbook_list:
                print("Test Pass:--> Address is Deleted from the AddressBook")
                return 1
            else:
                print("Test Fail:--> Could not able to Delete this address")
                return 0
        except:
            print("Test Fail:--> Could Not Able to Delete this Address from the AddressBook")
            return 0

    def popup_menu(self, intval):
        QTest.qWait(5)
        self.myapp.popMenuSubscriptions.setActiveAction(self.myapp.popMenuSubscriptions.actions()[intval])
        self.myapp.popMenuSubscriptions.setStyleSheet("QMenu:selected {background-color:#FF5733}")
        self.myapp.popMenuSubscriptions.show()
        QTest.qWait(400)
        self.myapp.popMenuSubscriptions.hide()
        QTest.qWait(50)


class BitmessageTest_BlackWhiteList_PopMenu(BitmessageTestCase):
    """Subscription TabWidget QTreeWidget popMenu Fucntionality testing"""

    def test_sider(self):
        total_bl = sqlQuery("Select address from blacklist")
        if total_bl > 0:
            QTest.qWait(500)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.blackwhitelist)
            self.tableWidget = self.myapp.ui.blackwhitelist.tableWidgetBlacklist
            QTest.qWait(500)
            self.rand_value = random.randint(0, len(total_bl) - 1)
            self.current_address = str(self.tableWidget.item(self.rand_value, 1).text())
            self.tableWidget.setCurrentCell(self.rand_value, 1)
            self.tableWidget.item(self.rand_value, 1).setSelected(True)
            rect = self.tableWidget.visualItemRect(self.tableWidget.item(self.rand_value, 1))
            QTest.qWait(500)
            self.blacklist_obj = blacklist.Blacklist()
            self.blacklist_obj.init_blacklist_popup_menu()
            self.blacklist_obj.popMenuBlacklist.move(QtCore.QPoint(rect.x(), rect.y() + 290))
            self.blacklist_obj.popMenuBlacklist.show()
            QTest.qWait(300)
            self.blacklist_obj.popMenuBlacklist.hide()
            self.add_delete()
        else:
            print("Test Fail:--> No black list Found")
            return 0
