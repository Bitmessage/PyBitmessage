"""Tests for PyBitmessage settings"""
import threading
import time

from PyQt4 import QtCore, QtGui, QtTest

from bmconfigparser import config
from bitmessageqt import settings

from .main import TestBase


class TestSettings(TestBase):
    """A test case for the "Settings" dialog"""
    def setUp(self):
        super(TestSettings, self).setUp()
        self.dialog = settings.SettingsDialog(self.window)

    def test_udp(self):
        """Test the effect of checkBoxUDP"""
        udp_setting = config.safeGetBoolean('bitmessagesettings', 'udp')
        self.assertEqual(udp_setting, self.dialog.checkBoxUDP.isChecked())
        self.dialog.checkBoxUDP.setChecked(not udp_setting)
        self.dialog.accept()
        self.assertEqual(
            not udp_setting,
            config.safeGetBoolean('bitmessagesettings', 'udp'))
        time.sleep(5)
        for thread in threading.enumerate():
            if thread.name == 'Announcer':  # find Announcer thread
                if udp_setting:
                    self.fail(
                        'Announcer thread is running while udp set to False')
                break
        else:
            if not udp_setting:
                self.fail('No Announcer thread found while udp set to True')

    def test_styling(self):
        """Test custom windows style and font"""
        style_setting = config.safeGet('bitmessagesettings', 'windowstyle')
        font_setting = config.safeGet('bitmessagesettings', 'font')
        self.assertIs(style_setting, None)
        self.assertIs(font_setting, None)
        style_control = self.dialog.comboBoxStyle
        self.assertEqual(
            style_control.currentText(), self.app.get_windowstyle())

        def call_font_dialog():
            """A function to get the open font dialog and accept it"""
            font_dialog = QtGui.QApplication.activeModalWidget()
            self.assertTrue(isinstance(font_dialog, QtGui.QFontDialog))
            selected_font = font_dialog.currentFont()
            self.assertEqual(
                config.safeGet('bitmessagesettings', 'font'), '{},{}'.format(
                    selected_font.family(), selected_font.pointSize()))

            font_dialog.accept()
            self.dialog.accept()
            self.assertEqual(
                config.safeGet('bitmessagesettings', 'windowstyle'),
                style_control.currentText())

        def click_font_button():
            """Use QtTest to click the button"""
            QtTest.QTest.mouseClick(
                self.dialog.buttonFont, QtCore.Qt.LeftButton)

        style_count = style_control.count()
        self.assertGreater(style_count, 1)
        for i in range(style_count):
            if i != style_control.currentIndex():
                style_control.setCurrentIndex(i)
                break

        QtCore.QTimer.singleShot(30, click_font_button)
        QtCore.QTimer.singleShot(60, call_font_dialog)
        time.sleep(2)
