from .telenium_process import TeleniumTestProcess


class SettingScreen(TeleniumTestProcess):
    """Setting Screen Functionality Testing"""

    def test_setting_screen(self):
        """Show Setting Screen"""
        print("=====================Test -Show Setting Screen=====================")
        self.cli.sleep(3)
        # this is for opening Nav drawer
        self.click_on('//MDActionTopAppBarButton[@icon=\"menu\"]')
        # checking state of Nav drawer
        self.assertEqual(self.cli.getattr('//MDNavigationDrawer', 'state'), 'open')
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll funcation
        scroll_distance = self.cli.getattr('//ContentNavigationDrawer//ScrollView[0]', 'scroll_y')
        self.assertLessEqual(scroll_distance, -0.0)
        # this is for opening setting screen
        self.click_on('//NavigationItem[@text=\"Settings\"]')
        # Checking current screen
        self.assertExists("//Setting[@name~=\"set\"]", timeout=2)
