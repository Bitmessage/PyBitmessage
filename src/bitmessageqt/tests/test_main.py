"""Common definitions for bitmessageqt tests"""
# pylint: disable=import-error
import sys
import unittest

from PyQt4 import QtCore, QtGui
from six.moves import queue

import bitmessageqt
from bitmessageqt import _translate, config, queues


# pylint: disable=too-few-public-methods
class TestApp(QtGui.QApplication):
    """Lightweight QApplication subclass for tests, without the heavy
    BitmessageQtApplication init (QLocalSocket singleton check,
    organisation metadata, etc.)."""

    @staticmethod
    def get_windowstyle():
        """Get window style set in config or default"""
        return config.safeGet(
            'bitmessagesettings', 'windowstyle',
            'Windows' if sys.platform.startswith('win') else 'GTK+'
        )


def get_test_app():
    """Return the existing QApplication or create a TestApp.

    If the running app is a plain QApplication (missing get_windowstyle),
    patch in the required methods from TestApp."""
    app = QtGui.QApplication.instance()
    if app is None:
        return TestApp(sys.argv)
    if not hasattr(app, 'get_windowstyle'):
        # Bolt on the methods the tests expect; this happens when
        # another test already created a bare QApplication.
        app.get_windowstyle = TestApp.get_windowstyle
    return app


class TestBase(unittest.TestCase):
    """Base class for bitmessageqt test case"""

    @classmethod
    def setUpClass(cls):
        """Provide the UI test cases with common settings"""
        cls.config = config
        cls.app = get_test_app()

    def setUp(self):
        self.app = self.__class__.app
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
