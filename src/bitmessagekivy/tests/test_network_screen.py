# pylint: disable=too-few-public-methods
"""
    Kivy Networkstat UI test
"""

from .telenium_process import TeleniumTestProcess


class NetworkStatusScreen(TeleniumTestProcess):
    """NetworkStatus Screen Functionality Testing"""

    def test_network_status(self):
        """Show NetworkStatus"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar
        # due to rapid transition effect, it doesn't click on menu-bar
        self.open_side_navbar()
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=5)
        # Clicking on Network Status tab
        self.cli.wait_click('//NavigationItem[@text=\"Network status\"]', timeout=2)
        # Checking the drawer is in 'closed' state
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # Checking for current screen (Network Status)
        self.assertExists("//NetworkStat[@name~=\"networkstat\"]", timeout=2)
        # Checking state of Total Connections tab
        self.assertExists(
            '//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Total connections\"][@state=\"down\"]', timeout=5
        )
        # Getting the value of total connections
        total_connection_text = self.cli.getattr('//NetworkStat//MDRaisedButton[@text]', 'text')
        # Splitting the string from total connection numbers
        number_of_connections = int(total_connection_text.split(' ')[-1])
        # Checking Total connections
        self.assertGreaterEqual(number_of_connections, 1)
        # Checking the state of Process tab
        self.assertExists(
            '//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"][@state=\"normal\"]', timeout=5
        )
        # Clicking on Processes Tab
        self.cli.wait_click(
            '//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"]', timeout=1
        )
        # Checking the state of Process tab
        self.assertExists(
            '//NetworkStat/MDTabs[0]//MDTabsLabel[@text=\"Processes\"][@state=\"down\"]', timeout=5
        )
