from .telenium_process import TeleniumTestProcess


class SettingScreen(TeleniumTestProcess):
    """Setting Screen Functionality Testing"""

    def test_setting_screen(self):
        """Show Setting Screen"""
        print("=====================Test -Show Setting Screen=====================")
        self.cli.sleep(3)
        # this is for checking current screen
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=2)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=2)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll funcation
        scroll_distance = self.cli.getattr('//ContentNavigationDrawer//ScrollView[0]', 'scroll_y')
        self.assertCheckScrollDown(scroll_distance, -0.0, timeout=1)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"Settings\"]', timeout=1)
        # Checking current screen
        self.assertExists("//Setting[@name~=\"set\"]", timeout=2)
