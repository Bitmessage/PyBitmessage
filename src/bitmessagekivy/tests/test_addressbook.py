import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class AddressBook(TeleniumTestProcess):
    """AddressBook Screen Functionality Testing"""

    def test_save_address(self):
        """Save Address On Address Book Screen/Window"""
        print("=====================Test -Save Address In Address Book=====================")
        time.sleep(6)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(4)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        time.sleep(3)
        self.cli.click_on('//NavigationItem[6]')
        time.sleep(4)
        self.cli.execute('app.addingtoaddressbook()')
        time.sleep(3)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[0]')
        time.sleep(4)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        time.sleep(4)
        self.cli.click_on('//MDRaisedButton[0]')
        time.sleep(4)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[0]')
        time.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]','text','peter')
        time.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        time.sleep(4)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        time.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text','sectorAppartment')
        time.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        time.sleep(5)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        time.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text',data[0])
        time.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text','')
        time.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        time.sleep(4)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text','BM-2cX78L9CZpb6GGC3rRVizYiUBwHELMLybd')
        time.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        time.sleep(4)

    def test_cancel_address(self):
        """Cancel Address"""
        print("=====================Test -Cancel Address=====================")
        time.sleep(3)
        self.cli.execute('app.addingtoaddressbook()')
        time.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]','text','prachi')
        time.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text',data[0])
        time.sleep(3)
        self.cli.click_on('//MDRaisedButton[1]')

    def test_send_message_to_addressbook(self):
        """Directly Send Message To The User"""
        print("=====================Test -Directly Send Message To The User=====================")
        time.sleep(4)
        self.cli.click_on('//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]')
        time.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        time.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        time.sleep(2)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]')
        time.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'Second')
        time.sleep(3)
        random_label=""
        for char in "Hey This is Message From Address Book":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]', 'text', random_label)
            time.sleep(0.2)
        self.cli.click_on('//MDIconButton[2]')
        time.sleep(2)

    def test_delete_address_from_address_contact(self):
        """Delete Address From Address Book"""
        print("=====================Test -Delete Address From Address Book=====================")
        time.sleep(3)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(3)
        self.cli.click_on('//NavigationItem[6]')
        time.sleep(3)
        self.cli.drag('//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[0]',
            '//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2)
        time.sleep(2)
        self.cli.click_on('//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//Button[0]')

    def test_all_address_book_method(self):
        self.test_save_address()
        self.test_cancel_address()
        self.test_send_message_to_addressbook()
        self.test_delete_address_from_address_contact()


if __name__ == '__main__':
    """Start Application"""
    obj = AddressBook()
    obj.setUpClass()
    obj.test_all_address_book_method()
