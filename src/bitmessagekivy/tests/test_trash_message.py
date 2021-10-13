import pdb
from .telenium_process import TeleniumTestProcess

class TrashMessage(TeleniumTestProcess):
    """Trash Screen Functionality Testing"""

    def test_delete_trash_message(self):
        """Delete Trash message permanently from trash message listing"""
        # Checking current Screen(Inbox screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Checking "Menu" is rendered
        self.assertExists('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # this is for opening Trash screen
        self.cli.wait_click('//NavigationItem[@text=\"Trash\"]', timeout=2)
        # self.cli.click_on('//NavigationItem[4]')
        # Checking Trash Screen
        self.assertExists("//ScreenManager[@current=\"trash\"]", timeout=5)
        # import pdb; pdb.set_trace()
        # Checking Trash Icon is in disable state
        # self.assertEqual(self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled'), True)
        # This is for swiping message to activate delete icon.
        self.cli.wait_drag('//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]', '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2, timeout=5)
        # self.assertExists('//Trash[0]//TwoLineAvatarIconListItem', timeout=3)
        # self.cli.wait_drag('//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]', '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2, timeout=5)
        # self.cli.wait(self.cli.wait_click('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', timeout=2))
        # Assert to check the drag is worked (Trash icon should be Activated)
        # self.cli.wait('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon~=\"trash-can\"]', timeout=5)
        # self.cli.setattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton', 'disabled', False)
        # self.assertEqual(self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled'), False)
        self.assertExists("//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon~=\"trash-can\"]", timeout=2)
        self.cli.setattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]', 'disabled', False)

        # if self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled') is True:
        #     self.cli.setattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton', 'disabled', False)
        # else:
        #     self.assertExists('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton', timeout=5)
        #     self.assertEqual(self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled'), False)

        # Checking the Trash Icon after swipe.
        # self.assertExists("//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon~=\"trash-can\"]", timeout=2)
        # self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon]', 'disabled')
        # self.assertEqual(self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled'), False)
        self.assertNotExists('//MDDialog[@open]', timeout=5)
        self.assertExists('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]', timeout=5)
        import pdb; pdb.set_trace()
        # clicking on Trash Box icon to delete message.
        self.cli.wait_click('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]', timeout=5)
        # Checking Confirm Popup is Opened
        self.assertExists('//MDDialog[@open]', timeout=5)
        # Checking the popup button is rendered.
        self.assertExists("//MDDialog//MDFlatButton[@text=\"Yes\"]", timeout=5)
        # Clicking on 'Yes' Button on Popup to confirm delete.
        self.cli.wait_click('//MDFlatButton[@text=\"Yes\"]', timeout=5)
        # self.cli.wait('//Trash[0]//TwoLineAvatarIconListItem', timeout=5)
        # Checking Pop is closed
        self.assertNotExists('//MDDialog[@open]', timeout=5)
        # self.assertExists('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]', timeout=5)
        self.assertExists('//MDList[0]/CutsomSwipeToDeleteItem[0]', timeout=5)
        # self.assertNotExists('//MDDialog', timeout=5)
        # self.assertExists('//Trash[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        # Checking Trash Screen
        self.assertExists("//ScreenManager[@current=\"trash\"]", timeout=5)
        # print(len(self.cli.select("//Trash[0]//CutsomSwipeToDeleteItem")),'__________________-------')
        # total_trash_msgs = len(self.cli.select("//CutsomSwipeToDeleteItem"))
        # Checking the message count of messages of draft screen after delete.
        # self.assertEqual(len(self.cli.select("//Trash[0]//CutsomSwipeToDeleteItem")), 1)
        # self.cli.sleep(5)
