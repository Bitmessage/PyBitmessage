"""Test for message send"""
import random
from random import choice
from string import ascii_lowercase

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from bmconfigparser import BMConfigParser
from helper_sql import sqlQuery
from testloader import BitmessageTestCase


class BitmessageTest_MessageTesting(BitmessageTestCase):
    """Test Message Sending functionality"""

    def test_msgsend(self):
        """Auto-fill senders address, receivers address, subject and message and sends the message"""
        try:
            if BMConfigParser().addresses():
                QTest.qWait(500)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
                QTest.qWait(500)

                self.myapp.ui.comboBoxSendFrom.setCurrentIndex(
                    random.randrange(1, len(BMConfigParser().addresses()) + 1)
                )
                QTest.qWait(1000)

                rand_address = choice(BMConfigParser().addresses())
                random_address = ""
                for x in range(len(rand_address)):
                    random_address += rand_address[x]
                    self.myapp.ui.lineEditTo.setText(random_address)
                    QTest.qWait(1)
                QTest.qWait(800)

                random_subject = ""
                for x in range(40):
                    random_subject += choice(ascii_lowercase)
                    self.myapp.ui.lineEditSubject.setText(random_subject)
                    QTest.qWait(1)
                QTest.qWait(800)

                random_message = ""
                for x in range(200):
                    random_message += choice(ascii_lowercase)
                    self.myapp.ui.textEditMessage.setText(random_message)
                    QTest.qWait(1)
                QTest.qWait(800)

                inbox_length = len(sqlQuery("Select msgid from inbox"))
                QTest.mouseClick(self.myapp.ui.pushButtonSend, Qt.LeftButton)
                QTest.qWait(600)

                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
                print(" .......................... waiting for message .......................... ")

                for x in range(5):
                    QTest.qWait(5000)
                    print("  waiting " + x * ".")
                self.assertEqual(sqlQuery("Select toaddress,subject from inbox")[-1], (rand_address, random_subject))

                if len(sqlQuery("Select msgid from inbox")) == inbox_length + 1:
                    QTest.qWait(100)
                    print("\n Test Pass :--> Message Received Successfully \n")
                    self.assertTrue(True, " Test Pass :--> Message Received Successfully")
                    return 1
                else:
                    QTest.qWait(100)
                    print("\n Test Fail :--> Doesn't Receive Any Message!! \n")
                    self.assertTrue(False, " \n Test Fail :--> Doesn't Receive Any Message!!")
                    return 0
            else:
                QTest.qWait(100)
                print("\n Test Fail :--> No Address Found!! \n")
                self.assertTrue(False, " \n Test Fail :--> No Address Found!!")
                return 0
        except:
            QTest.qWait(100)
            print("\n Test Fail :--> Message Sending Test Fail!! \n")
            self.assertTrue(False, " \n Test Fail :--> Message Sending Test Fail!!")
            return 0
