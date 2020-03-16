"""Tests for blackwhitelist"""
from random import choice
from string import ascii_lowercase

from PyQt4 import QtCore, QtGui
from PyQt4.QtTest import QTest

from addresses import addBMIfNotPresent
from bitmessageqt import blacklist
from bitmessageqt.dialogs import AddAddressDialog
from bitmessageqt.utils import avatarize
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from testloader import BitmessageTestCase
from tr import _translate


class BitmessageTest_BlackandWhiteList(BitmessageTestCase):
    """Blacklist and Whitelist address add functionality tests"""

    def test_blackwhitelist(self):
        """Tab switch to blacklist and add the address on blacklist and whitelist"""
        print("=====================Test - Adding Address to Black/WhiteList=====================")
        self.blacklist_obj = blacklist.Blacklist()
        try:
            QTest.qWait(500)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.blackwhitelist)
            QTest.qWait(500)
            self.dialog = AddAddressDialog(self.myapp)
            blacklistcount = len(sqlQuery("Select * from blacklist"))
            self.myapp.ui.blackwhitelist.radioButtonBlacklist.click()
            self.myapp.ui.blackwhitelist.pushButtonAddBlacklist.setStyleSheet(
                "QPushButton {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            self.myapp.ui.blackwhitelist.pushButtonAddBlacklist.setStyleSheet("")
            self.checkblacklist()
            self.myapp.ui.blackwhitelist.radioButtonWhitelist.click()
            self.myapp.ui.blackwhitelist.radioButtonBlacklist.click()
            QTest.qWait(500)
            whitelistcount = len(sqlQuery("Select * from whitelist"))
            self.myapp.ui.blackwhitelist.radioButtonWhitelist.click()
            self.myapp.ui.blackwhitelist.pushButtonAddBlacklist.setStyleSheet(
                "QPushButton {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            self.myapp.ui.blackwhitelist.pushButtonAddBlacklist.setStyleSheet("")
            self.checkblacklist()
            self.myapp.ui.blackwhitelist.radioButtonBlacklist.click()
            self.myapp.ui.blackwhitelist.radioButtonWhitelist.click()
            QTest.qWait(500)
            self.assertEqual(blacklistcount + 1, len(sqlQuery("Select * from blacklist")))
            self.assertEqual(whitelistcount + 1, len(sqlQuery("Select * from whitelist")))
            print("Black/WhiteList Functionality Tested Successfully")
            return 1
        except:
            print("Black/WhiteList Functionality Failed")
            return 0

    def checkblacklist(self):  # pylint: disable=too-many-statements
        """fill blacklist and whitelist fields"""
        try:
            self.dialog.lineEditLabel.setText("")
            self.dialog.lineEditAddress.setText("")
            QTest.qWait(350)
            self.dialog.show()
            QTest.qWait(750)
            random_label = ""
            for _ in range(30):
                random_label += choice(ascii_lowercase)
                self.dialog.lineEditLabel.setText(random_label)
                QTest.qWait(4)
            QTest.qWait(500)
            rand_address = choice(BMConfigParser().addresses())
            random_address = ""
            for i, _ in enumerate(rand_address):
                random_address += rand_address[i]
                self.dialog.lineEditAddress.setText(random_address)
                QTest.qWait(4)
            QTest.qWait(500)
            QtCore.QTimer.singleShot(0, self.dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked)
            if self.dialog.labelAddressCheck.text() == _translate("MainWindow", "Address is valid."):
                address = addBMIfNotPresent(str(self.dialog.lineEditAddress.text()))
                t = (address,)
                if BMConfigParser().get("bitmessagesettings", "blackwhitelist") == "black":
                    sql = """select * from blacklist where address=?"""
                else:
                    sql = """select * from whitelist where address=?"""
                queryreturn = sqlQuery(sql, *t)
                if queryreturn == []:
                    self.blacklist_obj.tableWidgetBlacklist.setSortingEnabled(False)
                    self.blacklist_obj.tableWidgetBlacklist.insertRow(0)
                    newItem = QtGui.QTableWidgetItem(unicode(self.dialog.lineEditLabel.text().toUtf8(), "utf-8"))
                    newItem.setIcon(avatarize(address))
                    self.blacklist_obj.tableWidgetBlacklist.setItem(0, 0, newItem)
                    newItem = QtGui.QTableWidgetItem(address)
                    newItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.blacklist_obj.tableWidgetBlacklist.setItem(0, 1, newItem)
                    self.blacklist_obj.tableWidgetBlacklist.setSortingEnabled(True)
                    t = (str(self.dialog.lineEditLabel.text().toUtf8()), address, True)
                    if BMConfigParser().get("bitmessagesettings", "blackwhitelist") == "black":
                        sql = """INSERT INTO blacklist VALUES (?,?,?)"""
                        sqlExecute(sql, *t)
                        black_list_value = sqlQuery(
                            "Select address from blacklist where label='" + random_label + "'")[0]
                        self.assertEqual(black_list_value[0], random_address)
                        print("Test Pass:--> Address Added to the blacklist")
                        return 1
                    else:
                        sql = """INSERT INTO whitelist VALUES (?,?,?)"""
                        sqlExecute(sql, *t)
                        white_list_value = sqlQuery(
                            "Select address from whitelist where label='" + random_label + "'")[0]
                        self.assertEqual(white_list_value[0], random_address)
                        print("Test Pass:--> Address Added to the whitelist")
                        return 1
                else:
                    print(
                        "Test Fail:--> You cannot add the same address to your list twice."
                        "Perhaps rename the existing one if you want")
                    return 0
            else:
                QTest.qWait(100)
                print("Test Fail:--> The address you entered was invalid. Ignoring it")
                return 0
        except:
            pass
