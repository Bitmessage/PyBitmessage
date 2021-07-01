from .telenium_process import TeleniumTestProcess


class TrashMessage(TeleniumTestProcess):
    """Trash Screen Functionality Testing"""

    def test_delete_trash_message(self):
        """Delete Trash message permanently from trash message listing"""
        print("=====================Test -Delete Message From Trash Message Listing=====================")
        self.cli.sleep(4)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(4)
        self.cli.click_on('//NavigationItem[4]')
        self.assertExists("//Trash[@name~=\"trash\"]", timeout=2)
        self.cli.sleep(4)
        self.cli.drag(
            '//MDList[0]/CutsomSwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]',
            '//MDList[0]/CutsomSwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 1)
        self.cli.click_on('//MDList[0]/CutsomSwipeToDeleteItem[0]')
        self.cli.sleep(4)
        self.cli.click_on('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MDDialog/MDCard[0]/AnchorLayout[0]/MDBoxLayout[0]/MDFlatButton[0]')
        # self.cli.click_on('//MDDialog/DialogFakeCard[0]/AnchorLayout[0]/MDBoxLayout[0]/MDFlatButton[0]')
        self.cli.sleep(2)
        total_trash_msgs = len(self.cli.select("//CutsomSwipeToDeleteItem"))
        self.assertEqual(total_trash_msgs, 1)
