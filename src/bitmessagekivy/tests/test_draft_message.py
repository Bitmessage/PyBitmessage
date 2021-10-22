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
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"{}\"]'.format(self.test_subject), timeout=5)
        # ADD MESSAGE BODY
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text]',
            'text', self.test_body)
        # Checking Message body is Entered
        self.assertExists(
            '//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text=\"{}\"]'.format(
                self.test_body), timeout=5)
        # Click on "Send" Icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=5)
        # Checking validation Pop up is Opened
        self.assertExists('//MDDialog[@open]', timeout=5)
        # checking the button is rendered
        self.assertExists('//MDFlatButton[@text=\"Ok\"]', timeout=5)
        # Click "OK" button to dismiss the Popup
        self.cli.wait_click('//MDFlatButton[@text=\"Ok\"]', timeout=5)
        # Checking validation Pop up is Closed
        self.assertNotExists('//MDDialog[@open]', timeout=5)
        # RECEIVER FIELD
        # Checking Receiver Address Field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=5)
        # Entering Receiver Address
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", test_address['auto_responder'])
        # Checking Receiver Address filled or not
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"{}\"]'.format(test_address['auto_responder']),
            timeout=2)
        # Checking the sender's Field is empty
        self.assertExists('//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text=\"\"]', timeout=3)
        # Assert to check Sender's address dropdown open or not
        self.assertEqual(self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open'), False)
        # Open Sender's Address DropDown
        self.cli.wait_click('//Create//CustomSpinner[0]/ArrowImg[0]', timeout=5)
        # Checking the status of dropdown
        self.assertEqual(self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open'), False)
        # Checking the dropdown option is rendered
        self.assertExists('//ComposerSpinnerOption[0]', timeout=5)
        # Select Sender's Address from Dropdown options
        self.cli.wait_click('//ComposerSpinnerOption[0]', timeout=5)
        # Assert to check Sender address dropdown closed
        self.assertEqual(self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open'), False)
        # Checking sender address is selected
        sender_address = self.cli.getattr('//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text]', 'text')
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text=\"{}\"]'.format(sender_address), timeout=3)
        # CLICK BACK-BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=5)
        # Checking current screen(Login) after "BACK" Press
        self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=5)

    @skip_screen_checks
    @ordered
    def test_edit_and_resend_draft_messgae(self):
        """Click on a Drafted message to send message"""
        # OPEN NAVIGATION-DRAWER
        # this is for opening Nav drawer
        self.open_side_navbar()
        # Checking messages in draft box
        self.assertEqual(len(self.cli.select('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem')), 1)
        # Wait to render the widget
        self.cli.wait('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        # Click on a Message to view its details (Message Detail screen)
        self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # Checking current screen Mail Detail
        self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=3)

        # CLICK on EDIT(Pencil) BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[@icon=\"pencil\"]', timeout=5)
        # Checking Current Screen 'Create'; composer screen.
        self.assertExists("//ScreenManager[@current=\"create\"]", timeout=10)
        # Checking the recipient is in the receiver field
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"{}\"]'.format(test_address['auto_responder']),
            timeout=2)
        # Checking the sender address is in the sender field
        sender_address = self.cli.getattr('//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text]', 'text')
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text=\"{}\"]'.format(sender_address), timeout=3)
        # Checking the subject text is in the subject field
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"{}\"]'.format(self.test_subject), timeout=5)
        # Checking the Body text is in the Body field
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text=\"{}\"]'.format(self.test_body),
            timeout=5)
        # CLICK BACK-BUTTON to autosave msg in draft screen
        self.cli.wait_click('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=5)
        # Checking current screen(Login) after BACK Press
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=5)

    @skip_screen_checks
    @ordered
    def test_delete_draft_message(self):
        """Deleting a Drafted Message"""
        # Checking current screen is Draft Screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=5)
        # Cheking the Message is rendered
        self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # Enable the trash icon
        self.cli.setattr('//MDList[0]//MDIconButton[@disabled]', 'disabled', False)
        # Waiting for the trash icon to be rendered
        self.cli.wait('//MDList[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # Swiping over the message to delete
        self.cli.wait_drag('//MDList[0]//AvatarSampleWidget', '//MDList[0]//TimeTagRightSampleWidget', 2, timeout=5)
        # Click on trash icon to delete the message.
        self.cli.wait_click('//MDList[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # Checking the deleted message is disappeared
        self.assertNotExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem', timeout=5)
        # Message count should be zero
        self.assertEqual(len(self.cli.select('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]')), 0)
        # After Deleting, Screen is redirected to Draft screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=8)
