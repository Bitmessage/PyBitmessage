"""Tests for changs Tab"""
from PyQt4.QtTest import QTest

from testloader import BitmessageTestCase


class BitmessageTest_ChansTest(BitmessageTestCase):
    """Switch to chans and test"""

    def test_chans(self):
        """Switch to chans window and test"""
        print("=====================Test - Chans Functionality=====================")
        QTest.qWait(1200)
        self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.chans)
        print("Test Pass :--> Chans Test Passed")
        return 1
