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
        try:
            QTest.qWait(500)
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.blackwhitelist)
            QTest.qWait(500)

            self.blacklist_obj = blacklist.Blacklist()
            self.dialog = AddAddressDialog(self.myapp)
            blacklistcount = len(sqlQuery("Select * from blacklist"))

            self.myapp.ui.blackwhitelist.radioButtonBlacklist.click()
            self.checkblacklist(self.myapp)
            QTest.qWait(500)
            self.assertEqual(blacklistcount + 1, len(sqlQuery("Select * from blacklist")))
            whitelistcount = len(sqlQuery("Select * from whitelist"))

            self.myapp.ui.blackwhitelist.radioButtonWhitelist.click()
            self.checkblacklist(self.myapp)
            QTest.qWait(500)
            self.assertEqual(whitelistcount + 1, len(sqlQuery("Select * from whitelist")))
            self.assertTrue(True, " \n Test Pass :-->  Black/WhiteList Functionality Tested Successfully!")
        except:
            self.assertTrue(False, " \n Test Fail :--> Black/WhiteList Functionality Failed!.")

    def checkblacklist(self, myapp):
        """fill blacklist and whitelist fields"""
        # pylint: disable=too-many-statements
        QTest.qWait(1000)
        self.dialog.lineEditLabel.setText("")
        self.dialog.lineEditAddress.setText("")
        self.dialog.show()
        QTest.qWait(800)
        random_label = ""
        for _ in range(30):
            random_label += choice(ascii_lowercase)
            self.dialog.lineEditLabel.setText(random_label)
            QTest.qWait(5)
        QTest.qWait(500)
        rand_address = choice(BMConfigParser().addresses())
        random_address = ""
        for x in range(len(rand_address)):
            random_address += rand_address[x]
            self.dialog.lineEditAddress.setText(random_address)
            QTest.qWait(5)
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
                    black_list_value = sqlQuery("Select address from blacklist where label='" + random_label + "'")[0]
                    print("\n Test Pass :--> Address Added to the blacklist! \n")
                    self.assertEqual(black_list_value[0], random_address)
                    return
                else:
                    sql = """INSERT INTO whitelist VALUES (?,?,?)"""
                    sqlExecute(sql, *t)
                    white_list_value = sqlQuery("Select address from whitelist where label='" + random_label + "'")[0]
                    print("\n Test Pass :--> Address Added to the whitelist! \n")
                    self.assertEqual(white_list_value[0], random_address)
                    return
            else:
                QTest.qWait(100)
                print(
                    "\n Test Fail :--> You cannot add the same address to your list twice."
                    " Perhaps rename the existing one if you want. \n"
                )
                self.assertTrue(
                    False,
                    "\n Test Fail :--> You cannot add the same address to your list twice."
                    " Perhaps rename the existing one if you want.",
                )
                return 0
        else:
            QTest.qWait(100)
            print("\n Test Fail :--> The address you entered was invalid. Ignoring it. \n")
            self.assertTrue(False, " \n Test Fail :--> The address you entered was invalid. Ignoring it.")
            return 0
