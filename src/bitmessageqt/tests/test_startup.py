"""
Smoke test: verify the main window can be created and shut down.

This test requires the full bitmessage backend to be running
(it is designed to run via ``bitmessagemain.py -t`` or from
``src/tests/core.py``).  It also needs a display (Xvfb is fine).
"""
import sys
import unittest

try:
    from PyQt4 import QtCore, QtGui
    has_qt = True
except ImportError:
    has_qt = False


@unittest.skipUnless(has_qt, "requires PyQt4")
class TestStartup(unittest.TestCase):
    """Verify the main window starts and has expected structure"""

    def setUp(self):
        import bitmessageqt
        self.app = (
            QtGui.QApplication.instance()
            or bitmessageqt.BitmessageQtApplication(sys.argv))
        self.window = self.app.activeWindow()
        if not self.window:
            self.window = bitmessageqt.MyForm()
            self.window.appIndicatorInit(self.app)

    def test_window_exists(self):
        """The main window should be created successfully"""
        self.assertIsNotNone(self.window)
        self.assertIsNotNone(self.window.ui)

    def test_window_has_tabs(self):
        """The main window should have the expected tab widget"""
        tabs = self.window.ui.tabWidget
        self.assertIsNotNone(tabs)
        self.assertGreater(tabs.count(), 0)

    def test_window_title(self):
        """The main window should have a non-empty title"""
        self.assertTrue(len(self.window.windowTitle()) > 0)

    def test_status_bar(self):
        """The main window should have a status bar"""
        self.assertIsNotNone(self.window.statusBar())

    def test_quit_cycle(self):
        """The event loop should start and stop without crashing"""
        QtCore.QTimer.singleShot(50, self.app.quit)
        self.app.exec_()
