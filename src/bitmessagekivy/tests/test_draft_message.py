from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks
from .common import ordered

test_address = {
    'receiver': 'BM-2cVWtdUzPwF7UNGDrZftWuHWiJ6xxBpiSP'
}


class DraftMessage(TeleniumTestProcess):
    """Draft Screen Functionality Testing"""
    test_subject = 'Test Subject text'
    test_body = 'Hey, This is draft Message Body'

    @skip_screen_checks
    @ordered
    def test_save_message_to_draft(self):
        """
            Saving a message to draft box when click on back button
        """
        # Checking current Screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=10, value='inbox')
        # Click on Composer Icon(Plus icon)
        self.cli.wait_click('//ComposerButton[0]/MDFloatingActionButton[@icon=\"plus\"]', timeout=5)
        # Checking Message Composer Screen(Create)
        self.assertExists("//ScreenManager[@current=\"create\"]", timeout=5)
        # ADD SUBJECT
        self.cli.setattr('//DropDownWidget/ScrollView[0]//MyMDTextField[0]', 'text', self.test_subject)
        # Checking Subject Field is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyMDTextField[@text]', '')
        # ADD MESSAGE BODY
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text]',
            'text', self.test_body)
        # Checking Message body is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text]', '')
        # Click on Send Icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=5)
        # Checking validation Pop up is Opened
        self.assertExists('//MDDialog', timeout=5)
        # Click "OK" button to dismiss the Popup
        self.cli.wait_click('//MDFlatButton[@text=\"Ok\"]', timeout=5)
        # RECEIVER FIELD
        # Checking Receiver Address Field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=5)
        # Entering Receiver Address
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", test_address['receiver'])
        # Checking Receiver Address filled or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyTextInput[@text]', '')
        # Assert to check Sender's address dropdown open or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MDTextField[@text]', '')
        is_open = self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open')
        self.assertEqual(is_open, False)
        # Open Sender's Address DropDown
        self.cli.wait_click('//Create//CustomSpinner[0]/ArrowImg[0]', timeout=5)
        # Select Sender's Address from Dropdown
        self.cli.wait_click('//ComposerSpinnerOption[0]', timeout=5)
        # Assert to check Sender's address dropdown closed
        is_open = self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open')
        self.assertEqual(is_open, False)
        # CLICK BACK-BUTTON
        self.cli.wait_click(
            '//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=5)
        # Checking current screen(Login) after BACK Press
        self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=5)

    @skip_screen_checks
    @ordered
    def test_edit_and_resend_draft_messgae(self):
        """Select A Message From Draft Messages Then
            make changes and sending it."""
        # OPEN NAVIGATION-DRAWER
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # Click to open Draft Screen
        self.cli.wait_click('//NavigationItem[@text=\"Draft\"]', timeout=5)
        # Checking Draft Screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=5)

        # Checking messages in draft box
        self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem', timeout=5)
        self.cli.sleep(1)
        # Click on a drafted msg to show details
        self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # Checking current screen Mail Detail
        self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=5)
        # CLICK on EDIT BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[@icon=\"pencil\"]', timeout=5)
        # Checking Current Screen 'Create'; composer screen.
        self.assertExists("//ScreenManager[@current=\"create\"]", timeout=5)
        # Click on Send Icon to send msg
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=5)
        # Redirected to the inbox screen
        self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=5)

    @skip_screen_checks
    @ordered
    def test_delete_draft_message(self):
        """Deleting a Drafted Message"""
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=5)
        # Saving a msg to draft to perform delete operation
        self.test_save_message_to_draft()
        # OPEN NAVIGATION-DRAWER
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # Click to open Draft Screen
        self.cli.wait_click('//NavigationItem[@text=\"Draft\"]', timeout=5)
        # Checking Draft Screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=5)
        self.cli.sleep(1)  # TODO: Remove sleep(), need to wait to render the msg  # pylint: disable=W0511
        # Click on a message to show msg details
        self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # Checking Current screen is Mail Detail
        self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=5)
        # Click on trash-can icon to delete
        self.cli.wait_click('//MDToolbar//MDActionTopAppBarButton[@icon=\"delete-forever\"]', timeout=5)
        # After Deleting, Screen is redirected to Draft screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=10)
