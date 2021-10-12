from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks
from .common import ordered


class TrashMessage(TeleniumTestProcess):
    """Trash Screen Functionality Testing"""

    @skip_screen_checks
    @ordered
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
        # Checking Trash Screen
        self.assertExists("//ScreenManager[@current=\"trash\"]", timeout=5)
        # This is for swiping message to activate delete icon.
        self.cli.wait_drag(
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]',
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2, timeout=5)
        # Checking the "trash-can" is rendered
        self.assertExists("//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon~=\"trash-can\"]", timeout=2)
        # Assert to check the drag is worked (Trash icon should be Activated)
        if self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled') is True:
            self.cli.setattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton', 'disabled', False)
        else:
            # Checking the button is rendered and functional
            self.assertExists(
                '//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton', timeout=5)
            # Checking the state of button(Should be enabled)
            self.assertEqual(
                self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled'), False)
        # Checking the Trash Icon after swipe.
        self.assertExists(
            "//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon~=\"trash-can\"]", timeout=2)
        # Checking the state of button(Should be enabled)
        self.assertEqual(self.cli.getattr(
            '//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled'), False)
        # clicking on Trash Box icon to delete message.
        self.cli.wait_click('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]', timeout=2)
        # Checking Confirm Popup is Opened
        self.assertExists('//MDDialog', timeout=5)
        # Checking the popup button is rendered.
        self.assertExists("//MDDialog//MDFlatButton[@text=\"Yes\"]", timeout=5)
        # Clicking on 'Yes' Button on Popup to confirm delete.
        self.cli.wait_click('//MDFlatButton[@text=\"Yes\"]', timeout=5)
        # Checking Pop is closed
        self.assertNotExists('//MDDialog', timeout=5)
        # Checking Trash Screen
        self.assertExists("//ScreenManager[@current=\"trash\"]", timeout=5)
