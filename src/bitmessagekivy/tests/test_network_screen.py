import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class NetwrokStatusScreen(TeleniumTestProcess):
    """NetwrokStatus Screen Functionality Testing"""

    def test_network_status(self):
        """Show NetwrokStatus"""
        print("=====================Test -Show NetwrokStatus=====================")
        time.sleep(4)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(3)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        time.sleep(3)
        self.cli.click_on('//NavigationItem[10]')
        time.sleep(4)
        self.cli.click_on('//NetworkStat/MDTabs[0]/MDTabsBar[0]/MDTabsScrollView[0]/MDGridLayout[0]/MDTabsLabel[1]')
        time.sleep(4)
