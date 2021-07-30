from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks
from .common import ordered


class AllMailMessage(TeleniumTestProcess):
    """AllMail Screen Functionality Testing"""

    @skip_screen_checks
    @ordered
    def test_show_allmail_list(self):
        """Show All Messages on Mail Screen/Window"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # This is for checking the Side nav Bar id closed
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # This is for checking the menu button is appeared
        self.assertExists('//MDActionTopAppBarButton[@icon~=\"menu\"]', timeout=5)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # this is for opening All Mail screen
        self.cli.wait_click('//NavigationItem[@text=\"All Mails\"]', timeout=5)
        # Assert for checking Current Screen(All mail)
        self.assertExists("//ScreenManager[@current=\"allmails\"]", timeout=5)

    @skip_screen_checks
    @ordered
    def test_delete_message_from_allmail_list(self):
        """Delete Message From Message body of Mail Screen/Window"""
        # click on a Message to get message details screen
        self.cli.wait_click(
            '//MDList[0]/CustomSwipeToDeleteItem[0]', timeout=3)
        # Assert for checking Current Screen(Mail Detail)
        self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=5)
        # CLicking on Trash-Can icon to delete Message
        self.cli.wait_click('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[@icon=\"delete-forever\"]', timeout=5)
        # After deleting msg, screen is redirected to All mail screen
        self.assertExists("//ScreenManager[@current=\"allmails\"]", timeout=5)
