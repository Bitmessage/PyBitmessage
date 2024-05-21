from .telenium_process import TeleniumTestProcess
from .common import ordered


class ChatScreen(TeleniumTestProcess):
    """Chat Screen Functionality Testing"""

    @ordered
    def test_open_chat_screen(self):
        """Opening Chat screen"""
        # Checking current Screen(Inbox screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar
        self.open_side_navbar()
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=10)
        # Checking Chat screen label on side nav bar
        self.assertExists('//NavigationItem[@text=\"Chat\"]', timeout=5)
        # this is for opening Chat screen
        self.cli.wait_click('//NavigationItem[@text=\"Chat\"]', timeout=5)
        # Checking navigation bar state
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # Checking current screen
        self.assertExists("//Chat[@name~=\"chat\"]", timeout=5)
