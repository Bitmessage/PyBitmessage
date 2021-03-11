import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess
from bmconfigparser import BMConfigParser
from .common import ordered

data = BMConfigParser().addresses()


class AddressBook(TeleniumTestProcess):
    """AddressBook Screen Functionality Testing"""

    @ordered
    def test_save_address(self):
        """Save Address On Address Book Screen/Window"""
        print("=====================Test -Save Address In Address Book=====================")
        self.cli.sleep(6)
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(4)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[6]')
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
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]','text','peter')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(4)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text','sectorAppartment')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(5)
        self.cli.click_on('//GrashofPopup/BoxLayout[0]/MDTextField[1]')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text',data[0])
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text','')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(4)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text','BM-2cX78L9CZpb6GGC3rRVizYiUBwHELMLybd')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(4)

    @ordered
    def test_cancel_address(self):
        """Cancel Address"""
        print("=====================Test -Cancel Address=====================")
        self.cli.sleep(3)
        self.cli.execute('app.addingtoaddressbook()')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[0]','text','prachi')
        self.cli.sleep(3)
        self.cli.setattr('//GrashofPopup/BoxLayout[0]/MDTextField[1]','text',data[0])
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[1]')

    @ordered
    def test_send_message_to_addressbook(self):
        """Directly Send Message To The User"""
        print("=====================Test -Directly Send Message To The User=====================")
        self.cli.sleep(4)
        self.cli.click_on('//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]')
        self.cli.sleep(3)
        self.cli.click_on('//MDRaisedButton[0]')
        self.cli.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        self.cli.sleep(2)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]')
        self.cli.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'Second')
        self.cli.sleep(3)
        random_label=""
        for char in "Hey This is Message From Address Book":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]', 'text', random_label)
            self.cli.sleep(0.2)
        self.cli.click_on('//MDIconButton[2]')
        self.cli.sleep(2)

    @ordered
    def test_delete_address_from_address_contact(self):
        """Delete Address From Address Book"""
        print("=====================Test -Delete Address From Address Book=====================")
        self.cli.sleep(3)
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[6]')
        self.cli.sleep(3)
        self.cli.drag('//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[0]',
            '//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]', 2)
        self.cli.sleep(2)
        self.cli.click_on('//AddressBook/BoxLayout[0]/BoxLayout[0]/ScrollView[0]/MDList[0]/Carousel[0]//Button[0]')
