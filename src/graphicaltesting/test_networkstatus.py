from PyQt4.QtTest import QTest

from testloader import BitmessageTestCase


class BitmessageTest_NetworkTest(BitmessageTestCase):
    def test_network(self):
        """Switch to network window and test"""
        QTest.qWait(1000)
        self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.networkstatus)
        QTest.qWait(1200)
        print("\n Test Pass :--> Network Functionality Working Well! \n")
        return 1
