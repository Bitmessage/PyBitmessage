import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class TrashMessage(TeleniumTestProcess):
    """Trash Screen Functionality Testing"""

    def test_delete_trash_message(self):
        """Delete Message From List of Message Permanently Of Trash Screen/Window"""
        print("=====================Test -Delete Messages Of Trash Screen=====================")
        time.sleep(6)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(4)
        self.cli.click_on('//NavigationItem[4]')
        time.sleep(4)
        self.cli.drag('//Trash/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[0]',
            '//Trash/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2)
        time.sleep(4)
        self.cli.click_on('//Trash/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//Button[0]')
        time.sleep(2)
        self.cli.click_on('//MDDialog/MDCard[0]/AnchorLayout[0]/MDBoxLayout[0]/MDFlatButton[0]')
        time.sleep(4)
