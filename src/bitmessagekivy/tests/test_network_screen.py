from .telenium_process import TeleniumTestProcess


class NetwrokStatusScreen(TeleniumTestProcess):
    """NetwrokStatus Screen Functionality Testing"""

    def test_network_status(self):
        """Show NetwrokStatus"""
        print("=====================Test -Show Network Status=====================")
        self.cli.sleep(10)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(3)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]", 1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[10]')
        self.cli.sleep(4)
        self.cli.click_on('//NetworkStat/MDTabs[0]/MDTabsBar[0]/MDTabsScrollView[0]/MDGridLayout[0]/MDTabsLabel[1]')
        self.cli.sleep(4)
        self.assertExists("//NetworkStat[@name~=\"networkstat\"]", timeout=2)
