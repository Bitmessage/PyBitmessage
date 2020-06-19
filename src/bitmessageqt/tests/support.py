# from PyQt4 import QtTest

import sys

from shared import isAddressInMyAddressBook

from main import TestBase


class TestSupport(TestBase):
    """A test case for support module"""
    SUPPORT_ADDRESS = 'BM-2cUdgkDDAahwPAU6oD2A7DnjqZz3hgY832'
    SUPPORT_SUBJECT = 'Support request'

    def test(self):
        """trigger menu action "Contact Support" and check the result"""
        ui = self.window.ui
        self.assertEqual(ui.lineEditTo.text(), '')
        self.assertEqual(ui.lineEditSubject.text(), '')

        ui.actionSupport.trigger()

        self.assertTrue(
            isAddressInMyAddressBook(self.SUPPORT_ADDRESS))

        self.assertEqual(
            ui.tabWidget.currentIndex(), ui.tabWidget.indexOf(ui.send))
        self.assertEqual(
            ui.lineEditTo.text(), self.SUPPORT_ADDRESS)
        self.assertEqual(
            ui.lineEditSubject.text(), self.SUPPORT_SUBJECT)
        self.assertIn(
            sys.version, ui.textEditMessage.toPlainText())
