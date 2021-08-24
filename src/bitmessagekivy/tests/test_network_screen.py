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
        # This is for checking the Side nav Bar id closed
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # This is for checking the menu button is appeared
        self.assertExists('//MDActionTopAppBarButton[@icon~=\"menu\"]', timeout=5)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=5)
        # Clicking on Network Status tab
        self.cli.wait_click('//NavigationItem[@text=\"Network status\"]', timeout=5)
        # checking current screen
        self.assertExists("//ScreenManager[@current=\"networkstat\"]", timeout=5)
        # Clicking on Processes Tab
        self.cli.wait_click('//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"]', timeout=3)
        # this is for checking current screen
        self.assertTrue('//NetworkStat/MDTabs[@disabled]', 'False')
