from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class TrashMessage(TeleniumTestProcess):
    """Trash Screen Functionality Testing"""

    def test_delete_trash_message(self):
        """Delete Trash message permanently from trash message listing"""
        print("=====================Test -Delete Message From Trash Message Listing=====================")
        self.cli.sleep(4)
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(4)
        self.cli.click_on('//NavigationItem[4]')
        self.cli.sleep(4)
        self.cli.drag('//Trash/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[0]',
            '//Trash/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2)
        self.cli.sleep(4)
        self.cli.click_on('//Trash/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//Button[0]')
        self.cli.sleep(2)
        # self.cli.click_on('//MDDialog/MDCard[0]/AnchorLayout[0]/MDBoxLayout[0]/MDFlatButton[0]')
        self.cli.click_on('//MDDialog/DialogFakeCard[0]/AnchorLayout[0]/MDBoxLayout[0]/MDFlatButton[0]')
        self.cli.sleep(4)
