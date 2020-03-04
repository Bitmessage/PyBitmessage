"""Add address in the subscription list"""
from random import choice
from string import ascii_lowercase

from PyQt4 import QtCore, QtGui
from PyQt4.QtTest import QTest

import shared
from bitmessageqt import dialogs
from bmconfigparser import BMConfigParser
from helper_sql import sqlQuery
from testloader import BitmessageTestCase


class BitmessageTest_AddSubscription(BitmessageTestCase):
    """Add address to list"""

    def test_subscription(self):
        """Test for subscription functionality"""
        try:
            if BMConfigParser().addresses():
                QTest.qWait(500)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.subscriptions)
                QTest.qWait(500)

                self.dialog = dialogs.NewSubscriptionDialog(self.myapp)
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

                try:
                    QTest.qWait(800)
                    address, label = self.dialog.data
                except AttributeError:
                    QTest.qWait(500)
                    print("\n Test Fail :--> Error, While Creating subscription list. \n")
                    return 0

                if shared.isAddressInMySubscriptionsList(address):
                    print(
                        "\n Test Fail :--> You cannot add the same address to your subscriptions twice."
                        " Perhaps rename the existing one if you want. \n"
                    )
                    QTest.qWait(500)
                    return 0

                self.myapp.addSubscription(address, label)
                sub_add = sqlQuery("select address from subscriptions where label='" + random_label + "'")[0]
                self.assertEqual(random_address, sub_add[0])
                print("\n Test Pass :-->  Subscription Done Successfully! \n")
                QTest.qWait(100)
                self.assertTrue(True, " \n Test Pass :-->  Subscription Done Successfully!")
                return 1
            else:
                QTest.qWait(100)
                print("\n Test Fail :--> No Address Found! \n")
                self.assertTrue(False, " \n Test Fail :-->   No Address Found!")
                return 0
        except:
            QTest.qWait(100)
            print("\n Test Fail :--> Error Occured while adding address to subscription list! \n")
            self.assertTrue(False, " \n Test Fail :--> Error Occured while adding address to subscription list! ")
            return 0
