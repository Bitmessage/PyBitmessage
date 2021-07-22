from tkinter.constants import S
from .telenium_process import TeleniumTestProcess
from .common import ordered

data = [
    'BM-2cWmjntZ47WKEUtocrdvs19y5CivpKoi1h',
    'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr'
]

class AddressBook(TeleniumTestProcess):
    """AddressBook Screen Functionality Testing"""

    @ordered
    def test_save_address(self):
        """Save Address On Address Book Screen/Window"""
        print("=====================Test -Save Address In Address Book=====================")
        self.cli.sleep(3)
        # this is for checking current screen
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=3)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=2)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=3)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"Address Book\"]', timeout=2)
        # Checking current screen
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=2)
        # Click on Account-Plus Icon to opeb popup for add Address
        self.cli.execute('app.addingtoaddressbook()')
        # Click on Label field to check validation
        self.cli.wait_click('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Label\"]', timeout=2)
        # Checking the Label Field shows Validation for empty string
        self.assertExists('//GrashofPopup/BoxLayout[0]/MDTextField[@text=\"\"]', timeout=2)
        # # Click on Address Field
        self.cli.wait_click('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Address\"]', timeout=2)
        # Checking the Address Field shows Validation for empty string
        self.assertExists('//GrashofPopup/BoxLayout[0]/MDTextField[@text=\"\"]', timeout=2)
        # Click On save Button to check Field validation
        self.cli.wait_click('//MDRaisedButton[0]', timeout=2)
        # Add Label to label Field
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Label\"]', 'text', 'test1')
        # Add incorrect Address to Address Field to check validation
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Address\"]', 'text', data[0])
        # Click on Save Button to check the address is correct or not
        self.cli.wait_click('//MDRaisedButton[@text=\"Save\"]')
        # Add Correct Address
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[@hint_text=\"Address\"]', 'text', 'BM-2cX78L9CZpb6GGC3rRVizYiUBwHELMLybd')
        # Click on Save Button
        self.cli.wait_click('//MDRaisedButton[@text=\"Save\"]', timeout=2)
        # Check Current Screen (Address Book)
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=2)
        # Checking Number of addresses increased
        address_book_msgs = len(self.cli.select("//SwipeToDeleteItem"))
        self.assertEqual(address_book_msgs, 1)

    @ordered
    def test_cancel_addressbook_popup(self):
        """Cancel Address"""
        print("=====================Test -Cancel Address Add Popup=====================")
        # Click on Account-Plus Icon to opeb popup for add Address
        self.cli.execute('app.addingtoaddressbook()')
        # Add Label to label Field
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]', 'text', 'test2')
        # Add Address to Address Field
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]', 'text', data[0])
        # Click on Save Button
        self.cli.wait_click('//MDRaisedButton[1]', timeout=2)
        # Check Current Screen (Address Book)
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=2)

    @ordered
    def test_send_message_to_addressbook(self):
        """Directly Send Message To The User"""
        print("=====================Test -Directly Send Message To The User=====================")
        # Check Current Screen (Address Book)
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=2)
        # Click on a Address to show address Details
        self.cli.wait_click(
            '//AddressBook/BoxLayout[0]//SwipeToDeleteItem[0]', timeout=2)
        # Checking the pop us opened
        self.assertNotExists('//AddbookDetailPopup//MDDialog[@state~=\"closed\"]',  timeout=2)
        # Click on the Send to message Button
        self.cli.wait_click('//MDRaisedButton[0]', timeout=2)
        # Redirected to message composer screen(create)
        self.assertExists("//Create[@name~=\"create\"]", timeout=2)
         # Open and select Sender's Address from DropDown
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/MDTextField[0]', 'text', 'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr')
        # Checking the Sender's Field is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/MDTextField[@text]', '')
         # ADD SUBJECT
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'Demo Subject')
        # Checking Subject Field is Entered
        self.assertExists('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[@text=\"Demo Subject\"]', timeout=2)
        # ADD MESSAGE BODY
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[0]',
                             'text', 'Hey,This is draft Message Body from Address Book')
        # Checking Message body is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text]', '')
        # Click on Send Icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=3)
        # After Click send, Screen is redirected to Inbox screen
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=5)

    @ordered
    def test_delete_address_from_address_contact(self):
        """Delete Address From Address Book"""
        print("=====================Test -Delete Address From Address Book=====================")
        # this is for checking current screen
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=3)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=2)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"Address Book\"]', timeout=2)
        # Checking current screen
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=2)
        # Swipe to delete
        self.assertTrue('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'True')
        self.cli.sleep(1)
        self.drag(
            '//MDList[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]',
            '//MDList[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]')
        # Click on trash-can icon
        self.cli.wait_click('//MDList[0]//SwipeToDeleteItem[0]', timeout=3)
        # Checking the trash icon is acrivated
        self.assertTrue('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@disabled]', 'False')
        # Click on trash icon
        self.cli.click_on('//MDList[0]//MDIconButton[@icon=\"delete-forever\"]')
        # Checking current screen
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=2)
