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
    # pylint: disable= no-else-return

    def test_msgsend(self):
        """Auto-fill senders address, receivers address, subject and message and sends the message"""
        print(
            "=====================Test - Message Send/Receive Functionality=====================")
        try:
            if BMConfigParser().addresses():
                inbox_length = len(sqlQuery("Select msgid from inbox"))
                QTest.qWait(500)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.send)
                QTest.qWait(500)
                rand_address = choice(BMConfigParser().addresses())
                random_address = ""
                for i, _ in enumerate(rand_address):
                    random_address += rand_address[i]
                    self.myapp.ui.lineEditTo.setText(random_address)
                    QTest.qWait(4)
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
                QTest.qWait(400)
                randinteger = random.randrange(1, len(BMConfigParser().addresses()) + 1)
                self.myapp.ui.comboBoxSendFrom.setCurrentIndex(randinteger)
                QTest.qWait(1000)
                QTest.mouseClick(self.myapp.ui.pushButtonSend, Qt.LeftButton)
                QTest.qWait(350)
                self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
                print(" Waiting For Message .......................... ")
                for x in range(5):
                    QTest.qWait(4000)
                    print("  waiting " + x * ".")
                new_inbox = sqlQuery("Select msgid,toaddress,subject from inbox")
                self.assertEqual(new_inbox[-1][1], rand_address)
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
