from .telenium_process import TeleniumTestProcess


class TrashMessage(TeleniumTestProcess):
    """Trash Screen Functionality Testing"""

    def test_delete_trash_message(self):
        """Delete Trash message permanently from trash message listing"""
        print("=====================Test -Delete Message From Trash Message Listing=====================")
        self.cli.sleep(8)
        # this is for opening Nav drawer
        self.click_on('//MDActionTopAppBarButton[@icon=\"menu\"]')
        # checking state of Nav drawer
        self.assertEqual(self.cli.getattr('//MDNavigationDrawer', 'state'), 'open')
        # this is for opening Trash screen
        self.click_on('//NavigationItem[@text=\"Trash\"]')
        # self.cli.click_on('//NavigationItem[4]')
        self.assertExists("//Trash[@name~=\"trash\"]", timeout=2)
        self.cli.sleep(4)
        # This is for swiping message to activate delete icon.
        self.drag(
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]',
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]')
        self.click_on('//MDList[0]/CutsomSwipeToDeleteItem[0]', seconds=1)
        # clicking on Trash Box icon to delete message.
        self.click_on('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]', seconds=2)
        # Clicking on 'Yes' Button on Popup to confirm delete.
        self.click_on('//MDDialog//MDFlatButton[@text=\"Yes\"]', seconds=1.1)
        # self.cli.click_on('//MDDialog/DialogFakeCard[0]/AnchorLayout[0]/MDBoxLayout[0]/MDFlatButton[0]')
        total_trash_msgs = len(self.cli.select("//CutsomSwipeToDeleteItem"))
        self.assertEqual(total_trash_msgs, 1)
