"""Add address in the subscription list"""
from random import choice
from string import ascii_lowercase

from PyQt4 import QtGui
from PyQt4.QtCore import QTimer
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
        print("=====================Test - Subscribe Address=====================")
        try:
            if BMConfigParser().addresses():
                QTest.qWait(500)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.subscriptions)
                QTest.qWait(500)
                self.myapp.ui.pushButtonAddSubscription.setStyleSheet(
                    "QPushButton {background-color: #FF5733; color: white;}")
                QTest.qWait(50)
                self.myapp.ui.pushButtonAddSubscription.setStyleSheet("")
                dialog = dialogs.NewSubscriptionDialog(self.myapp)
                dialog.show()
                QTest.qWait(750)

                random_label = ""
                for _ in range(30):
                    random_label += choice(ascii_lowercase)
                    dialog.lineEditLabel.setText(random_label)
                    QTest.qWait(4)
                QTest.qWait(500)
                rand_address = choice(BMConfigParser().addresses())
                random_address = ""
                for i, _ in enumerate(rand_address):
                    random_address += rand_address[i]
                    dialog.lineEditAddress.setText(random_address)
                    QTest.qWait(4)
                QTest.qWait(500)
                QTimer.singleShot(0, dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked)

                try:
                    QTest.qWait(800)
                    address, label = dialog.data
                except:
                    print("Test Fail:--> Error, While Creating subscription list")
                    QTest.qWait(500)
                    return 0
                if shared.isAddressInMySubscriptionsList(address):
                    print(
                        "Test Fail:--> You cannot add the same address to your subscriptions twice."
                        " Perhaps rename the existing one if you want")
                    QTest.qWait(500)
                    return 0
                self.myapp.addSubscription(address, label)
                sub_add = sqlQuery(
                    "select address from subscriptions where label='" + random_label + "'")[0]
                self.assertEqual(random_address, sub_add[0])
                print("Test Pass:-->  Subscription Done Successfully")
                return 1
            else:
                print("Test Fail:--> No Address Found")
                return 0
        except:
            print("Test Fail:--> Error Occured while adding address to subscription list")
            return 0
