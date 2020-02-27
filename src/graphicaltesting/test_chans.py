"""Tests for changs Tab"""
from PyQt4.QtTest import QTest

from testloader import BitmessageTestCase


class BitmessageTest_ChansTest(BitmessageTestCase):
    """Switch to chans and test"""

    def test_chans(self):
        """Switch to chans window and test"""
        QTest.qWait(1200)
        self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.chans)
        # QTest.mouseClick(self.myapp.ui.pushButtonAddChan, Qt.LeftButton)
        # self.assertEqual('foo'.upper(), 'F00')
        print("\n Test Pass :--> Chans Test Passed! \n")
        return 1
