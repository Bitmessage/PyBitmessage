"""Common definitions for bitmessageqt tests"""

import sys
import unittest

from qtpy import QtCore, QtWidgets
from six import string_types
from six.moves import queue

import bitmessageqt
from bitmessageqt import _translate, config, queues


class TestBase(unittest.TestCase):
    """Base class for bitmessageqt test case"""

    @classmethod
    def setUpClass(cls):
        """Provide the UI test cases with common settings"""
        cls.config = config

    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance()
            or bitmessageqt.BitmessageQtApplication(sys.argv))
        self.window = self.app.activeWindow()
        if not self.window:
            self.window = bitmessageqt.MyForm()
            self.window.appIndicatorInit(self.app)

    def tearDown(self):
        """Search for exceptions in closures called by timer and fail if any"""
        # self.app.deleteLater()
        concerning = []
        while True:
            try:
                thread, exc = queues.excQueue.get(block=False)
            except queue.Empty:
                break
            if thread == 'tests':
                concerning.append(exc)
        if concerning:
            self.fail(
                'Exceptions found in the main thread:\n%s' % '\n'.join((
                    str(e) for e in concerning
                )))


class TestMain(unittest.TestCase):
    """Test case for main window - basic features"""

    def test_translate(self):
        """Check the results of _translate() with various args"""
        self.assertIsInstance(_translate("MainWindow", "Test"), string_types)


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
