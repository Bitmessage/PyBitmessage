from .telenium_process import TeleniumTestProcess
from .common import ordered


class DraftMessage(TeleniumTestProcess):
    """Draft Screen Functionality Testing"""

    @ordered
    def test_save_draft_message(self):
        """Select A Draft Screen From Navigaion-Drawer-Box Then
           Send a drafted message """
        print("=====================Test - Select A Draft Screen From Navigaion-Drawer-Box=====================")
        self.cli.sleep(8)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # Click to open Inbox
        self.cli.wait_click('//NavigationItem[@text=\"Inbox\"]', timeout=2)
        # Checking Inbox Screen
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=2)
        # Due to animation and transition effect, it needed some halt otherwise it fails
        self.cli.sleep(1)
        # Click on Composer Icon(Plus icon)
        self.cli.wait_click('//ComposerButton[0]/MDFloatingActionButton[@icon=\"plus\"]', timeout=2)
        # Checking Message Composer Screen(Create)
        self.assertExists("//Create[@name~=\"create\"]", timeout=4)
        # ADD SENDER'S ADDRESS
        # Checking State of Sender's Address Input Field (Empty)
        self.assertExists('//DropDownWidget/ScrollView[0]//MDTextField[@text=\"\"]', timeout=2)
        # Open Sender's Address DropDown
        self.cli.wait_click(
            '//DropDownWidget/ScrollView[0]//BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]', timeout=2)
        # Due to animation and transition effect, it needed some halt otherwise it fails
        self.cli.sleep(2)
        # SENDER FIELD
        # Select Sender's Address from Dropdown
        self.cli.wait_click(
            '//DropDownWidget/ScrollView[0]//BoxLayout[0]/CustomSpinner[0]', timeout=2)
        self.cli.click_on('//ComposerSpinnerOption[0]')
        # Assert to check Sender's address dropdown open or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MDTextField[@text]', '')
        # RECEIVER FIELD
        # Checking Receiver Address Field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=2)
        # Entering Receiver Address
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", 'BM-2cSsuH1bUWBski8bvdqnK2DivMqQCeQA1J')
        # Checking Receiver Address filled or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyTextInput[@text]', '')
        # CLICK BACK-BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=2)
        # Checking current screen(Login) after BACK Press
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=2)
        self.cli.sleep(0.5)
        # Click on Composer Icon(Plus icon)
        self.cli.wait_click('//ComposerButton[0]/MDFloatingActionButton[@icon=\"plus\"]', timeout=2)
        # Checking Message Composer Screen(Create)
        self.assertExists("//Create[@name~=\"create\"]", timeout=4)
        # ADD SENDER'S ADDRESS
        # Checking State of Sender's Address Input Field (Empty)
        self.assertExists('//DropDownWidget/ScrollView[0]//MDTextField[@text=\"\"]', timeout=2)
        
        # Open Sender's Address DropDown
        self.cli.wait_click(
            '//Create//CustomSpinner[0]/ArrowImg[0]', timeout=2)
        # Due to animation and transition effect, it needed some halt otherwise it fails
        self.cli.sleep(2)
        # Select Sender's Address from Dropdown
        self.cli.wait_click(
            '//DropDownWidget/ScrollView[0]//CustomSpinner[0]', timeout=2)
        self.cli.click_on('//ComposerSpinnerOption[0]')
        # Assert to check Sender's address dropdown open or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MDTextField[@text]', '')
        
        # RECEIVER FIELD
        # Checking Receiver Address Field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=2)
        # Entering Receiver Address
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", 'BM-2cSsuH1bUWBski8bvdqnK2DivMqQCeQA1J')
        # Checking Receiver Address filled or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyTextInput[@text]', '')
         # ADD SUBJECT
        self.cli.setattr('//DropDownWidget/ScrollView[0]//MyMDTextField[0]', 'text', 'Another Draft message')
        # Checking Subject Field is Entered
        self.assertExists('//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"Another Draft message\"]', timeout=2)
        # CLICK BACK-BUTTON
        self.cli.wait_click('//MDToolbar//MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=2)
        # Checking current screen(Login) after BACK Press
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=2)

    @ordered
    def test_edit_and_resend_draft_messgae(self):
        """Select A Message From List of Messages Then
            make changes and send it."""
        print("=====================Test - Edit A Message From Draft Screen=====================")
        # OPEN NAVIGATION-DRAWER
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # Click to open Draft Screen
        self.cli.wait_click('//NavigationItem[@text=\"Draft\"]', timeout=2)
        # Checking Draft Screen
        self.assertExists("//Draft[@name~=\"draft\"]", timeout=2)
        # Due to animation and transition effect, it needed some halt otherwise it fails
        self.cli.sleep(1)
        # SHOW DRAFT MESSAGE AND SELECT FIRST MESSAGE
        self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=2)
        # Checking current screen Mail Detail
        self.assertExists("//MailDetail[@name~=\"mailDetail\"]", timeout=2)
        # CLICK EDIT BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[@icon=\"pencil\"]', timeout=2)
        # Checking Current Screen 'Create'
        self.assertExists("//Create[@name~=\"create\"]", timeout=2)
        # ADD MESSAGE BODY
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text]',
                             'text', 'Hey,This is draft Message Body')
        # Checking Message body is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text]', '')
        # Click on Send Icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=3)
        # After Click send, Screen is redirected to Inbox screen
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=5)

    @ordered
    def test_delete_draft_message(self):
        """Delete A Message From List of Messages"""
        print("=====================Test - Delete A Message From List of Messages=====================")
        self.cli.sleep(2)
         # OPEN NAVIGATION-DRAWER
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # Click to open Draft Screen
        self.cli.wait_click('//NavigationItem[@text=\"Draft\"]', timeout=2)
        # Checking Draft Screen
        self.assertExists("//Draft[@name~=\"draft\"]", timeout=2)
        self.cli.sleep(1)
        self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        # Checking Current screen is Mail Detail
        self.assertExists("//MailDetail[@name~=\"mailDetail\"]", timeout=3)
        # Click on trash-can icon to delete
        self.cli.wait_click('//MDToolbar//MDActionTopAppBarButton[@icon=\"delete-forever\"]', timeout=2)
        # After Deleting, Screen is redirected to Draft screen
        self.assertExists("//Draft[@name~=\"draft\"]", timeout=1)
