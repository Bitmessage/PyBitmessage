# pylint: disable=too-few-public-methods

from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks


class SettingScreen(TeleniumTestProcess):
    """Setting Screen Functionality Testing"""

    @skip_screen_checks
    def test_setting_screen(self):
        """Show Setting Screen"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar
        self.open_side_navbar()
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=5)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"Settings\"]', timeout=3)
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"set\"]", timeout=3)
        # Scrolling down currrent screen
        self.cli.wait_drag(
            '//MDTabs[0]//MDLabel[@text=\"Close to tray\"]',
            '//MDTabs[0]//MDLabel[@text=\"Minimize to tray\"]', 1, timeout=5)
        # Checking state of 'Network Settings' sub tab should be 'normal'(inactive)
        self.assertExists('//MDTabs[0]//MDTabsLabel[@text=\"Network Settings\"][@state=\"normal\"]', timeout=5)
        # Click on "Network Settings" subtab
        self.cli.wait_click('//MDTabs[0]//MDTabsLabel[@text=\"Network Settings\"]', timeout=5)
        # Checking state of 'Network Settings' sub tab should be 'down'(active)
        self.assertExists('//MDTabs[0]//MDTabsLabel[@text=\"Network Settings\"][@state=\"down\"]', timeout=5)
        # Scrolling down currrent screen
        self.cli.wait_drag(
            '//MDTabs[0]//MDLabel[@text=\"Username:\"]', '//MDTabs[0]//MDLabel[@text=\"Port:\"]', 1, timeout=5)
        # Checking state of 'Resends Expire' sub tab should be 'normal'(inactive)
        self.assertExists('//MDTabs[0]//MDTabsLabel[@text=\"Resends Expire\"][@state=\"normal\"]', timeout=5)
        # Scrolling down currrent screen
        self.cli.wait_click('//MDTabs[0]//MDTabsLabel[@text=\"Resends Expire\"]', timeout=5)
        # Checking state of 'Resends Expire' sub tab should be 'down'(active)
        self.assertExists('//MDTabs[0]//MDTabsLabel[@text=\"Resends Expire\"][@state=\"down\"]', timeout=5)
