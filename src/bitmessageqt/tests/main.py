"""Common definitions for bitmessageqt tests"""

import Queue
import sys
import unittest

from PyQt4 import QtCore, QtGui

import bitmessageqt
import queues
from tr import _translate


class TestBase(unittest.TestCase):
    """Base class for bitmessageqt test case"""

    def setUp(self):
        self.app = (
            QtGui.QApplication.instance()
            or bitmessageqt.BitmessageQtApplication(sys.argv))
        self.window = self.app.activeWindow()
        if not self.window:
            self.window = bitmessageqt.MyForm()
            self.window.appIndicatorInit(self.app)

    def tearDown(self):
        # self.app.deleteLater()
        while True:
            try:
                thread, exc = queues.excQueue.get(block=False)
            except Queue.Empty:
                return
            if thread == 'tests':
                self.fail('Exception in the main thread: %s' % exc)


class TestMain(unittest.TestCase):
    """Test case for main window - basic features"""

    def test_translate(self):
        """Check the results of _translate() with various args"""
        self.assertIsInstance(
            _translate("MainWindow", "Test"),
            QtCore.QString
        )


class TestUISignaler(TestBase):
    """Test case for UISignalQueue"""

    def test_updateStatusBar(self):
        """Check arguments order of updateStatusBar command"""
        queues.UISignalQueue.put((
            'updateStatusBar', (
                _translate("test", "Testing updateStatusBar..."), 1)
        ))

        QtCore.QTimer.singleShot(60, self.app.quit)
        self.app.exec_()
        # self.app.processEvents(QtCore.QEventLoop.AllEvents, 60)
