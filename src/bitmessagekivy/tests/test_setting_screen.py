from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class SettingScreen(TeleniumTestProcess):
    """Setting Screen Functionality Testing"""

    def test_setting_screen(self):
        """Show Setting Screen"""
        print("=====================Test -Show Setting Screen=====================")
        self.cli.sleep(3)
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(3)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]", 1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[7]')
        self.cli.sleep(4)
