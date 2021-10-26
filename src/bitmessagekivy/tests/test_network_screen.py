# pylint: disable=too-few-public-methods

from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks


class NetworkStatusScreen(TeleniumTestProcess):
    """NetworkStatus Screen Functionality Testing"""

    @skip_screen_checks
    def test_network_status(self):
        """Show NetworkStatus"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar
        self.open_side_navbar()
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=5)
        # Clicking on Network Status tab
        self.cli.wait_click('//NavigationItem[@text=\"Network status\"]', timeout=5)
        # checking current screen
        self.assertExists("//ScreenManager[@current=\"networkstat\"]", timeout=5)
        # Checking the state of "Total Connection" tab
        self.assertExists(
            '//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Total connections\"][@state=\"down\"]', timeout=3)
        # Checking the state of "Processes" tab
        self.assertExists('//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"][@state=\"normal\"]', timeout=3)
        # Checking the "Tab" is rendered
        self.assertExists('//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"]', timeout=4)
        # Clicking on Processes Tab
        self.cli.wait_click('//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"]', timeout=4)
        # Checking the state of "Processes" tab
        self.assertExists('//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"][@state=\"normal\"]', timeout=3)
