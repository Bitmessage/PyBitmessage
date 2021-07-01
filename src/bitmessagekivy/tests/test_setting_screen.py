from .telenium_process import TeleniumTestProcess


class SettingScreen(TeleniumTestProcess):
    """Setting Screen Functionality Testing"""

    def test_setting_screen(self):
        """Show Setting Screen"""
        print("=====================Test -Show Setting Screen=====================")
        self.cli.sleep(3)
        # self.cli.wait_click("//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]", timeout=20)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(3)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]", 1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[7]')
        self.cli.sleep(2)
        self.assertExists("//Setting[@name~=\"set\"]", timeout=2)
