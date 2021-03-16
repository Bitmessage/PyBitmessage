from bitmessagekivy.tests.telenium_process import TeleniumTestProcess
from .common import ordered


class AllMailMessage(TeleniumTestProcess):
    """AllMail Screen Functionality Testing"""

    @ordered
    def test_show_allmail_list(self):
        """Show All Messages on Mail Screen/Window"""
        print("=====================Test -Show Messages Of Mail Screen=====================")
        self.cli.sleep(5)
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(4)
        self.cli.click_on('//NavigationItem[5]')
        self.cli.sleep(4)
    
    @ordered
    def test_delete_message_from_allmail_list(self):
        """Delete Message From Message body of Mail Screen/Window"""
        print("=====================Test -Delete Messages Of Mail Screen=====================")
        self.cli.sleep(4)
        self.cli.click_on('//Allmails[0]/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]')
        self.cli.sleep(5)
        self.cli.click_on('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[1]')
        self.cli.sleep(5)
