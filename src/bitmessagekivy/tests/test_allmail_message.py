import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class AllMailMessage(TeleniumTestProcess):
    """AllMail Screen Functionality Testing"""

    def test_select_all_mails(self):
        """Show All Messages on Mail Screen/Window"""
        print("=====================Test -Show Messages Of Mail Screen=====================")
        time.sleep(5)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(4)
        self.cli.click_on('//NavigationItem[5]')
        time.sleep(4)
      
    def test_delete_message_from_draft(self):
        """Delete Message From Message body of Mail Screen/Window"""
        print("=====================Test -Delete Messages Of Mail Screen=====================")
        time.sleep(4)
        self.cli.click_on('//Allmails[0]/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]')
        time.sleep(5)
        self.cli.click_on('//MDToolbar/BoxLayout[2]/MDIconButton[1]')
        time.sleep(3)


if __name__ == '__main__':
    """Start Application"""
    obj = AllMailMessage()
    obj.setUpClass()
    obj.test_select_all_mails()
    obj.test_delete_message_from_draft()
