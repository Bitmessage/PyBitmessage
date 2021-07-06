from .telenium_process import TeleniumTestProcess


class SettingScreen(TeleniumTestProcess):
    """Setting Screen Functionality Testing"""

    def test_setting_screen(self):
        """Show Setting Screen"""
        print("=====================Test -Show Setting Screen=====================")
        self.cli.sleep(3)
        # this is for opening Nav drawer
        self.cli.click_on('//MDActionTopAppBarButton[@icon=\"menu\"]')
        self.cli.sleep(3)
        # this is for scrolling Nav drawer
        self.cli.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]", 1)
        self.cli.sleep(3)
        # this is for opening setting screen
        self.cli.click_on('//NavigationItem[@text=\"Settings\"]')
        self.cli.sleep(2)
        # Checking current screen
        self.assertExists("//Setting[@name~=\"set\"]", timeout=2)
