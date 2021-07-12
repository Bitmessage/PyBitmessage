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
        self.cli.sleep(12)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(4)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]", 1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[6]')
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=0)
        self.cli.sleep(4)
        self.cli.execute('app.addingtoaddressbook()')
        self.cli.sleep(3)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[0]')
        self.cli.sleep(4)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        self.cli.sleep(4)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(4)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[0]')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]', 'text', 'test1')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(4)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]', 'text', 'sectorAppartment')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(5)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]', 'text', data[0])
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]', 'text', '')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(4)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]', 'text', 'BM-2cX78L9CZpb6GGC3rRVizYiUBwHELMLybd')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(4)
        address_book_msgs = len(self.cli.select("//SwipeToDeleteItem"))
        self.assertEqual(address_book_msgs, 1)

    @ordered
    def test_cancel_addressbook_popup(self):
        """Cancel Address"""
        print("=====================Test -Cancel Address Add Popup=====================")
        self.cli.sleep(3)
        self.cli.execute('app.addingtoaddressbook()')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]', 'text', 'test2')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]', 'text', data[0])
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[1]')
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=1)

    @ordered
    def test_send_message_to_addressbook(self):
        """Directly Send Message To The User"""
        print("=====================Test -Directly Send Message To The User=====================")
        self.cli.sleep(4)
        self.cli.click_on(
            '//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/SwipeToDeleteItem[0]')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.assertExists("//Create[@name~=\"create\"]", timeout=1)
        self.cli.sleep(3)
        self.cli.click_on(
            '//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        self.cli.sleep(5)
        # self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]')
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/RelativeLayout[0]/BoxLayout[0]/MyTextInput')
        self.cli.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'Second')
        self.cli.sleep(3)
        random_label = ""
        for char in "Hey This is Message From Address Book":
            random_label += char
            self.cli.setattr(
                '//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[0]', 'text', random_label)
            self.cli.sleep(0.2)
        self.cli.click_on('//MDActionTopAppBarButton[2]')
        self.cli.sleep(4)
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=1)

    @ordered
    def test_delete_address_from_address_contact(self):
        """Delete Address From Address Book"""
        print("=====================Test -Delete Address From Address Book=====================")
        self.cli.sleep(2)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[6]')
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=1)
        self.cli.sleep(3)
        self.cli.drag(
            '//MDList[0]/SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]',
            '//MDList[0]/SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 1)
        self.cli.click_on('//MDList[0]/SwipeToDeleteItem[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MDList[0]/SwipeToDeleteItem[0]//MDIconButton[0]')
        self.assertExists("//AddressBook[@name~=\"addressbook\"]", timeout=2)
