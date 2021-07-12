from .telenium_process import TeleniumTestProcess
from .common import ordered


class AllMailMessage(TeleniumTestProcess):
    """AllMail Screen Functionality Testing"""

    @ordered
    def test_show_allmail_list(self):
        """Show All Messages on Mail Screen/Window"""
        print("=====================Test -Show Messages Of Mail Screen=====================")
        self.cli.sleep(10)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(4)
        self.cli.click_on('//NavigationItem[5]')
        self.cli.sleep(4)
        self.assertExists("//Allmails[@name~=\"allmails\"]", timeout=2)

    @ordered
    def test_delete_message_from_allmail_list(self):
        """Delete Message From Message body of Mail Screen/Window"""
        print("=====================Test -Delete Messages Of Mail Screen=====================")
        self.cli.sleep(4)
        self.cli.click_on(
            '//Allmails[0]/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/CutsomSwipeToDeleteItem[0]')
        self.assertExists("//MailDetail[@name~=\"mailDetail\"]", timeout=0)
        self.cli.sleep(5)
        self.cli.click_on('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[1]')
        self.cli.sleep(5)
        self.assertExists("//Allmails[@name~=\"allmails\"]", timeout=0)
