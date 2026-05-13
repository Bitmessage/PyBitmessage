"""
Smoke tests: verify that bitmessageqt modules can be imported.

These tests require PyQt4 to be installed but do NOT need a running
X server, database, or any bitmessage backend threads.
"""
import unittest


# pylint: disable=import-error,unused-variable
class TestImports(unittest.TestCase):
    """Verify that key bitmessageqt modules are importable"""

    @staticmethod
    def test_import_bitmessageqt():
        """The main bitmessageqt package should be importable"""
        import bitmessageqt

    @staticmethod
    def test_import_bitmessageui():
        """The generated UI module should be importable"""
        from bitmessageqt import bitmessageui

    @staticmethod
    def test_import_settings():
        """The settings dialog module should be importable"""
        from bitmessageqt import settings

    @staticmethod
    def test_import_address_dialogs():
        """The address dialogs module should be importable"""
        from bitmessageqt import address_dialogs

    @staticmethod
    def test_import_networkstatus():
        """The network status module should be importable"""
        from bitmessageqt import networkstatus

    @staticmethod
    def test_import_safehtmlparser():
        """safehtmlparser should be importable"""
        from bitmessageqt import safehtmlparser

    @staticmethod
    def test_import_support():
        """The support module should be importable"""
        from bitmessageqt import support

    @staticmethod
    def test_import_foldertree():
        """The foldertree module should be importable"""
        from bitmessageqt import foldertree

    @staticmethod
    def test_import_messageview():
        """The messageview module should be importable"""
        from bitmessageqt import messageview

    @staticmethod
    def test_import_utils():
        """The utils module should be importable"""
        from bitmessageqt import utils

    @staticmethod
    def test_import_account():
        """The account module should be importable"""
        from bitmessageqt import account
