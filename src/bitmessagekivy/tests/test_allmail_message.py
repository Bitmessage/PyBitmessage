from .telenium_process import TeleniumTestProcess
from .common import ordered


class AllMailMessage(TeleniumTestProcess):
    """AllMail Screen Functionality Testing"""

    @ordered
    def test_show_allmail_list(self):
        """Show All Messages on Mail Screen/Window"""
        print("=====================Test -Show Messages Of Mail Screen=====================")
        self.cli.sleep(8)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # this is for opening All Mail screen
        self.cli.wait_click('//NavigationItem[@text=\"All Mails\"]', timeout=2)
        self.cli.sleep(3)
        # Assert for checking Current Screen(All mail)
        self.assertExists("//Allmails[@name~=\"allmails\"]", timeout=2)

    @ordered
    def test_delete_message_from_allmail_list(self):
        """Delete Message From Message body of Mail Screen/Window"""
        print("=====================Test -Delete Messages Of Mail Screen=====================")
        # Assert for checking Current Screen(All mail)
        self.assertExists("//Allmails[@name~=\"allmails\"]", timeout=2)
        # click on a Message to get message details screen
        self.cli.wait_click(
            '//MDList[0]/CutsomSwipeToDeleteItem[0]', timeout=2)
        # Assert for checking Current Screen(Mail Detail)
        self.assertExists("//MailDetail[@name~=\"mailDetail\"]", timeout=2)
        # CLicking on Trash-Can icon to delete Message
        self.cli.wait_click('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[1]', timeout=2)
        # After deleting msg, screen is redirected to All mail screen
        self.assertExists("//Allmails[@name~=\"allmails\"]", timeout=0)
