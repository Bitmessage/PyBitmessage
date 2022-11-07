from .telenium_process import TeleniumTestProcess
from .common import ordered


class TrashMessage(TeleniumTestProcess):
    """Trash Screen Functionality Testing"""

    @ordered
    def test_delete_trash_message(self):
        """Delete Trash message permanently from trash message listing"""
        # Checking current Screen(Inbox screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar
        self.open_side_navbar()
        # this is for opening Trash screen
        self.cli.wait_click('//NavigationItem[@text=\"Trash\"]', timeout=2)
        # Checking the drawer is in 'closed' state
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # Checking Trash Screen
        self.assertExists("//ScreenManager[@current=\"trash\"]", timeout=5)
