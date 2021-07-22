from time import time
from .telenium_process import TeleniumTestProcess
from .common import ordered

data = [
    'BM-2cWmjntZ47WKEUtocrdvs19y5CivpKoi1h',
    'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr'
]

class SendMessage(TeleniumTestProcess):
    """Sent Screen Functionality Testing"""

    @ordered
    def test_send_message_and_validation(self):
        """
            Sending Message From Inbox Screen
            opens a pop-up(screen)which send message from sender to reciever
        """
        print("=======Test - Sending Message From Inbox Screen with validation Checks=======")
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
        # Checking State of Sender's Address Input Field (Empty)
        self.assertExists('//DropDownWidget/ScrollView[0]//MDTextField[@text=\"\"]', timeout=3)
        # Click on Receiver's Address Field to check validation
        self.cli.wait_click('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=4)
        # Checking State of Receiver's Address Input Field (Empty)
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=2)
        # Click on Subject Field to check validation
        self.cli.wait_click('//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"\"]', timeout=2)
        # Checking State of Subject Input Field (Empty)
        self.assertExists('//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"\"]', timeout=2)
        # Click on Send Icon to check validation working
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=2)
        # Checking validation Pop up is Opened
        self.assertExists('//MDDialog[@text=\"Please fill the form completely\"]', timeout=2)
        # Click on 'Ok' to dismiss the Popup
        self.cli.wait_click('//MDFlatButton[0]', timeout=2)
        # Checking Pop up is closed
        self.assertExists("//Create[@name~=\"create\"]", timeout=4)
        # ADD SENDER'S ADDRESS
        # Checking State of Sender's Address Input Field (Empty)
        self.assertExists('//DropDownWidget/ScrollView[0]//MDTextField[@text=\"\"]', timeout=2)
        # Open Sender's Address DropDown
        self.cli.wait_click(
            '//Create//CustomSpinner[0]/ArrowImg[0]', timeout=3)
        # Due to animation and transition effect, it needed some halt otherwise it fails
        self.cli.sleep(2)
        # Checking the Address Dropdown is in open State
        self.assertTrue('//Create//CustomSpinner[@is_open]', 'True')
        # Select Sender's Address from Dropdown
        self.cli.wait_click('//ComposerSpinnerOption[0]', timeout=3)
        # Checking the Address Dropdown is in open State
        self.assertTrue('//Create//CustomSpinner[@is_open]', 'False')
        # Assert to check Sender's address dropdown open or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MDTextField[0]', '')
        # ADD SUBJECT
        self.cli.setattr('//DropDownWidget/ScrollView[0]//MyMDTextField[0]', 'text', 'heyyyyyy')
        # Checking Subject Field is Entered
        self.assertExists('//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"heyyyyyy\"]', timeout=2)
        # Checking BODY Field(EMPTY)
        self.assertExists('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text=\"\"]', timeout=2)
        # ADD BODY
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[0]',
                             'text', 'how are you this is message body')
        # Checking BODY is Entered
        self.assertExists(
            '//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text=\"how are you this is message body\"]', timeout=2)
        # click on send icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=2)
        # Checking validation so Pop up is Opened
        self.assertExists('//MDDialog[@text=\"Please fill the form completely\"]', timeout=2)
        # Pop clicked on ok
        self.cli.wait_click('//MDFlatButton[0]', timeout=2)
        # ADD RECEIVER ADDRESS
        # Checking Receiver Address Field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=2)
        # Entering Receiver Address
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", data[0])
        # Checking Receiver Address filled or not
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyTextInput[0]', '')
        # Clicking on send icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=4)
        # Checking screen(Inbox) after sending message
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=4)

    @ordered
    def test_sent_box(self):
        """
            Checking Message in Sent Screen after sending a Message.
        """
        print("=======Test - Checking Message in Sent Screen after sending a Message=======")
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # Clicking on Sent Tab
        self.cli.wait_click('//NavigationItem[@text=\"Sent\"]', timeout=3)
        # Checking current screen; Sent
        self.assertExists("//Sent[@name~=\"sent\"]", timeout=3)
        # It takes time to reload sent messages so used sleep method
        self.cli.sleep(1)
        # Checking number of Sent messages
        total_sent_msgs = len(self.cli.select("//SwipeToDeleteItem"))
        self.assertEqual(total_sent_msgs, 2)
