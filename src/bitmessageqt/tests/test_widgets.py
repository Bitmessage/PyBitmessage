"""
Unit tests for individual bitmessageqt widgets.

These tests need a display (real or virtual via Xvfb/xvfb-run) and PyQt4,
but do NOT require the full bitmessage backend, database, or network.
Each test creates only the minimal widget under test.
"""
import sys
import unittest

# pylint: disable=import-outside-toplevel,unused-import
try:
    from PyQt4 import QtCore, QtGui, QtTest
    has_qt = True
except ImportError:
    has_qt = False


def get_app():
    """Return existing QApplication or create a new one"""
    return QtGui.QApplication.instance() or QtGui.QApplication(sys.argv)


@unittest.skipUnless(has_qt, "requires PyQt4")
class TestSafeHTMLParser(unittest.TestCase):
    """Test the SafeHTMLParser used for message rendering"""

    def test_sanitise(self):
        """Check that dangerous HTML is stripped"""
        from bitmessageqt.safehtmlparser import SafeHTMLParser
        parser = SafeHTMLParser()
        parser.reset()
        parser.reset_safe()
        parser.feed("<b>hello</b> <script/>alert('x')</script> &amp; world")
        self.assertIn("hello", parser.sanitised)
        self.assertNotIn("<script", parser.sanitised)


@unittest.skipUnless(has_qt, "requires PyQt4")
class TestMessageView(unittest.TestCase):
    """Test the MessageView widget in isolation"""

    def setUp(self):
        self.app = get_app()

    def test_create_messageview(self):
        """MessageView widget can be instantiated"""
        from bitmessageqt.messageview import MessageView
        widget = MessageView(None)
        self.assertIsNotNone(widget)

    def test_messageview_set_content(self):
        """MessageView.setContent renders the given text"""
        from bitmessageqt.messageview import MessageView
        widget = MessageView(None)
        widget.setContent("Hello, this is a <b>test</b> message.")
        self.assertIn("test", widget.toPlainText())


@unittest.skipUnless(has_qt, "requires PyQt4")
class TestAddressValidator(unittest.TestCase):
    """Test the AddressValidator"""

    def setUp(self):
        self.app = get_app()

    def test_create_validator(self):
        """AddressValidator can be instantiated with a buttonBox"""
        from bitmessageqt.addressvalidator import AddressValidator
        line_edit = QtGui.QLineEdit()
        # AddressValidator.setParams() reads the Ok button label on init,
        # so a real QDialogButtonBox is the simplest way to satisfy that.
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        validator = AddressValidator(
            line_edit, buttonBox=button_box)
        self.assertIsNotNone(validator)
        self.assertFalse(validator.isValid)


@unittest.skipUnless(has_qt, "requires PyQt4")
class TestLanguageBox(unittest.TestCase):
    """Test the language selection combobox"""

    def setUp(self):
        self.app = get_app()

    def test_create_languagebox(self):
        """LanguageBox can be instantiated"""
        from bitmessageqt.languagebox import LanguageBox
        parent = QtGui.QWidget()
        combo = LanguageBox(parent)
        self.assertIsNotNone(combo)
        self.assertGreater(combo.count(), 0)
