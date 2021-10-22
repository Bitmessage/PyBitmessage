from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks
from .common import ordered

test_address = {
    'invalid_address': 'BM-2cWmjntZ47WKEUtocrdvs19y5CivpKoi1',
    'autoresponder_address': 'BM-2cVWtdUzPwF7UNGDrZftWuHWiJ6xxBpiSP',
    'recipient': 'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr',
    'sender': 'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr'
}


class AddressBook(TeleniumTestProcess):
    """AddressBook Screen Functionality Testing"""
    test_label = 'Auto Responder'
    test_subject = 'Test Subject'
    test_body = 'Hey,This is draft Message Body from Address Book'

    @skip_screen_checks
    @ordered
    def test_save_address(self):
        """Saving a new Address On Address Book Screen/Window"""
        # Checking current Screen(Inbox screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar (written in telenium_process.py)
        self.open_side_navbar()
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=5)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"Address Book\"]', timeout=5)
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"addressbook\"]", timeout=5)
        # This is for checking the Side nav Bar is closed
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # Check for rendered button
        self.assertExists('//MDActionTopAppBarButton[@icon=\"account-plus\"]', timeout=5)
        # Click on "Account-Plus' Icon to open popup to save a new Address
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"account-plus\"]', timeout=5)
        # Checking the Label Field shows Validation for empty string
        self.assertExists('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Label\"][@text=\"\"]', timeout=5)
        # Checking the Address Field shows Validation for empty string
        self.assertExists('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Address\"][@text=\"\"]', timeout=5)
        # Click On save Button to check Field validation
        self.cli.wait_click('//MDRaisedButton[@text=\"Save\"]', timeout=5)
        # Add an address Label to label Field
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Label\"]', 'text', self.test_label)
        # Checking the Label Field should not be empty
        self.assertExists(
            '//GrashofPopup/BoxLayout[0]/MDTextField[0][@text=\"{}\"]'.format(self.test_label), timeout=2)
        # Add incorrect Address to Address Field to check validation
        self.cli.setattr(
            '//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Address\"]',
            'text', test_address['invalid_address'])
        # Checking the Address Field should not be empty
        self.assertExists(
            '//GrashofPopup/BoxLayout[0]/MDTextField[1][@text=\"{}\"]'.format(test_address['invalid_address']),
            timeout=2)
        # Add Correct Address
        self.cli.setattr(
            '//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Address\"]', 'text',
            test_address['autoresponder_address'])
        # Checking the Address Field contains correct address
        self.assertEqual(
            self.cli.getattr('//GrashofPopup/BoxLayout[0]/MDTextField[1][@text]', 'text'),
            test_address['autoresponder_address'])
        # Validating the Label field
        self.assertExists(
            '//GrashofPopup/BoxLayout[0]/MDTextField[0][@text=\"{}\"]'.format(self.test_label), timeout=2)
        # Validating the Valid Address is entered
        self.assertExists(
            '//GrashofPopup/BoxLayout[0]/MDTextField[1][@text=\"{}\"]'.format(
                test_address['autoresponder_address']), timeout=3)
        # Click on Save Button to save the address in address book
        self.cli.wait_click('//MDRaisedButton[@text=\"Save\"]', timeout=2)
        # Check Current Screen (Address Book)
        self.assertExists("//ScreenManager[@current=\"addressbook\"]", timeout=5)
        # Checking new address should be added
        self.assertExists('//SwipeToDeleteItem', timeout=5)

    @skip_screen_checks
    @ordered
    def test_dismiss_addressbook_popup(self):
        """This method is to perform Dismiss add Address popup"""
        # Checking the "Address saving" Popup is not opened
        self.assertNotExists('//GrashofPopup', timeout=5)
        # Checking the "Add account" Button is rendered
        self.assertExists('//MDActionTopAppBarButton[@icon=\"account-plus\"]', timeout=6)
        # Click on Account-Plus Icon to open popup for add Address
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"account-plus\"]', timeout=5)
        # Add Label to label Field
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]', 'text', 'test_label2')
        # Checking the Label Field should not be empty
        self.assertExists(
            '//GrashofPopup/BoxLayout[0]/MDTextField[0][@text=\"{}\"]'.format('test_label2'), timeout=2)
        # Add Address to Address Field
        self.cli.setattr(
            '//GrashofPopup/BoxLayout[0]/MDTextField[1]', 'text', test_address['recipient'])
        # Checking the Address Field should not be empty
        self.assertExists(
            '//GrashofPopup/BoxLayout[0]/MDTextField[1][@text=\"{}\"]'.format(test_address['recipient']),
            timeout=2)
        # Checking for "Cancel" button is rendered
        self.assertExists('//MDRaisedButton[@text=\"Cancel\"]', timeout=5)
        # Click on 'Cancel' Button to dismiss the popup
        self.cli.wait_click('//MDRaisedButton[@text=\"Cancel\"]', timeout=2)
        # Check Current Screen (Address Book)
        self.assertExists("//ScreenManager[@current=\"addressbook\"]", timeout=5)

    @skip_screen_checks
    @ordered
    def test_send_message_to_saved_address(self):
        """This method is to send msg to the saved address from addressbook"""
        # Checking the Message detail Dialog box is not opened
        self.assertNotExists('//MDDialog', timeout=3)
        # Checking the saved address is rendered
        self.assertExists('//AddressBook/BoxLayout[0]//SwipeToDeleteItem[0]', timeout=5)
        # Click on a Address to open address Details popup
        self.cli.wait_click('//AddressBook/BoxLayout[0]//SwipeToDeleteItem[0]', timeout=5)
        # Checking the Message detail Dialog is opened
        self.assertExists('//MDDialog', timeout=3)
        # Checking the buttons are rendered
        self.assertExists('//MDRaisedButton', timeout=5)
        # Click on the Send to message Button
        self.cli.wait_click('//MDRaisedButton[0]', timeout=5)
        # Redirected to message composer screen(create)
        self.assertExists("//ScreenManager[@current=\"create\"]", timeout=5)
        # Checking the Address is populated to recipient field when we try to send message to saved address.
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//MyTextInput[@text="{}"]'.format(
                test_address['autoresponder_address']), timeout=5)
        # CLICK BACK-BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=5)
        # After Back press, redirected to 'inbox' screen
        self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=8)

    @skip_screen_checks
    @ordered
    def test_delete_address_from_saved_address(self):
        """Delete a saved Address from Address Book"""
        # Method to open side navbar (written in telenium_process.py)
        self.open_side_navbar()
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"Address Book\"]', timeout=2)
        # checking state of Nav drawer(closed)
        self.assertExists("//MDNavigationDrawer[@state~=\"close\"]", timeout=2)
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"addressbook\"]", timeout=8)
        # Checking the Address is rendered
        self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem', timeout=5)
        # Waiting for the trash icon to be rendered
        self.cli.wait('//MDList[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # Enable the trash icon
        self.cli.setattr('//MDList[0]//MDIconButton[@disabled]', 'disabled', False)
        # Swiping over the Address to delete
        self.cli.wait_drag('//MDList[0]//AvatarSampleWidget', '//MDList[0]//TimeTagRightSampleWidget', 2, timeout=5)
        # Click on trash icon to delete the Address.
        self.cli.wait_click('//MDList[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # Checking the deleted Address is disappeared
        self.assertNotExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem', timeout=5)
        # Address count should be zero
        self.assertEqual(len(self.cli.select('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]')), 0)
        # After Deleting, Screen is redirected to Address Book screen
        self.assertExists("//ScreenManager[@current=\"addressbook\"]", timeout=8)
