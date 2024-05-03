"""Tests for PyBitmessage settings"""
import threading
import time

from main import TestBase
from bmconfigparser import config
from bitmessageqt import settings


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
        self.assertEqual(style_control.currentText(), 'GTK+')
        style_count = style_control.count()
        self.assertGreater(style_count, 1)
        for i in range(style_count):
            if i != style_control.currentIndex():
                style_control.setCurrentIndex(i)
                break
        self.dialog.accept()
        self.assertEqual(
            config.safeGet('bitmessagesettings', 'windowstyle'),
            style_control.currentText())
