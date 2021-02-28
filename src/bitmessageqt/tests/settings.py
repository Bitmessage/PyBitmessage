import threading
import time

from main import TestBase
from bmconfigparser import BMConfigParser
from bitmessageqt import settings


class TestSettings(TestBase):
    """A test case for the "Settings" dialog"""
    def setUp(self):
        super(TestSettings, self).setUp()
        self.dialog = settings.SettingsDialog(self.window)

    def test_udp(self):
        """Test the effect of checkBoxUDP"""
        udp_setting = BMConfigParser().safeGetBoolean(
            'bitmessagesettings', 'udp')
        self.assertEqual(udp_setting, self.dialog.checkBoxUDP.isChecked())
        self.dialog.checkBoxUDP.setChecked(not udp_setting)
        self.dialog.accept()
        self.assertEqual(
            not udp_setting,
            BMConfigParser().safeGetBoolean('bitmessagesettings', 'udp'))
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
