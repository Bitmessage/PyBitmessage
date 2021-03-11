import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class SettingScreen(TeleniumTestProcess):
    """Setting Screen Functionality Testing"""
    
    # @classmethod
    # def setUpClass(cls):
    #     super(SettingScreen, cls).setUpClass()

    def test_setting_screen(self):
        """Show Setting Screen"""
        print("=====================Test -Show Setting Screen=====================")
        time.sleep(4)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(3)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        time.sleep(3)
        self.cli.click_on('//NavigationItem[7]')
        time.sleep(2)
