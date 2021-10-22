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
        # Method to open side navbar
        self.open_side_navbar()
        # this is for opening Trash screen
        self.cli.wait_click('//NavigationItem[@text=\"Trash\"]', timeout=2)
        # Checking Trash Screen
        self.assertExists("//ScreenManager[@current=\"trash\"]", timeout=5)
        # This is for swiping message to activate delete icon.
        self.cli.wait_drag(
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]',
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2, timeout=5)
        # Checking the "trash-can" is rendered
        self.assertExists(
            "//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon~=\"trash-can\"]", timeout=2)
        # Delete icon is enabled
        self.cli.setattr('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton', 'disabled', False)
        # Checking the Dialog popup is closed
        self.assertNotExists('//MDDialog[@open]', timeout=5)
        # Checking the delete icon is rendered and functional
        self.assertExists('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # Click on the delete icon to delete the current message
        self.cli.wait_click('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # Checking Confirm Popup is Opened
        self.assertExists('//MDDialog[@open]', timeout=5)
        # Checking the popup's 'Yes' button is rendered.
        self.assertExists("//MDDialog//MDFlatButton[@text=\"Yes\"]", timeout=5)
        # Clicking on 'Yes' Button on Popup to confirm delete.
        self.cli.wait_click('//MDFlatButton[@text=\"Yes\"]', timeout=5)
        # Checking the Dialog is closed on click "Yes" button
        self.assertNotExists('//MDDialog[@open]', timeout=5)
        # Checking the message is rendered on Trash screen
        self.assertExists('//MDList[0]/CutsomSwipeToDeleteItem[0]', timeout=5)
        # Checking Current screen is Trash Screen
        self.assertExists("//ScreenManager[@current=\"trash\"]", timeout=5)
