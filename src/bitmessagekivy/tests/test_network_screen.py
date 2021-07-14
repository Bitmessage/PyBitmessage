from requests.packages.urllib3.util import timeout
from .telenium_process import TeleniumTestProcess


class NetwrokStatusScreen(TeleniumTestProcess):
    """NetwrokStatus Screen Functionality Testing"""

    def test_network_status(self):
        """Show NetwrokStatus"""
        print("=====================Test -Show NetwrokStatus=====================")
        self.cli.sleep(8)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=2)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # Assert for checking scroller run till Network tab.
        self.assertExists("//NavigationItem[@text=\"Network status\"]", timeout=2)
        # assert for checking scroll function
        scroll_distance = self.cli.getattr('//ContentNavigationDrawer//ScrollView[0]', 'scroll_y')
        self.assertCheckScrollDown(scroll_distance, -0.0, timeout=2)
        # Clicking on Network Status tab
        self.click_on('//NavigationItem[@text=\"Network status\"]', seconds=1)
        # Checking for current screen (Network Status)
        self.assertExists("//NetworkStat[@name~=\"networkstat\"]", timeout=2)
        # Clicking on Processes Tab
        self.cli.wait_click('//NetworkStat/MDTabs[0]//MDTabsLabel[1]', timeout=1)
        # Checking for current screen (Network Status)
        self.assertExists("//NetworkStat[@name~=\"networkstat\"]", timeout=2)

