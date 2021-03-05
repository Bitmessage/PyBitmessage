import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class MyAddressScreen(TeleniumTestProcess):
    """MyAddress Screen Functionality Testing"""

    def test_select_myaddress_list(self):
        """Select Address From List of Address"""
        print("=====================Test -Select Address From List of Address=====================")
        time.sleep(4)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(3)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        time.sleep(3)
        self.cli.click_on('//NavigationItem[11]')
        time.sleep(4)

    def test_show_Qrcode(self):
        """Show the Qr code of selected address"""
        print("=====================Test -Show QR code of selected address=====================")
        time.sleep(4)
        self.cli.click_on('//MyAddress/BoxLayout[0]/FloatLayout[0]/MDScrollViewRefreshLayout[0]/MDList[0]/CustomTwoLineAvatarIconListItem[0]')
        time.sleep(3)
        self.cli.click_on('//MyaddDetailPopup/BoxLayout[1]/MDRaisedButton[1]/MDLabel[0]')
        time.sleep(3)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDIconButton[0]')
        time.sleep(3)

    def test_send_message_from(self):
        """Send Message From Send Message From Button"""
        print("=====================Test -Send Message From Send Message From Button=====================")
        time.sleep(4)
        self.cli.click_on('//MyAddress/BoxLayout[0]/FloatLayout[0]/MDScrollViewRefreshLayout[0]/MDList[0]/CustomTwoLineAvatarIconListItem[0]')
        time.sleep(4)
        self.cli.click_on('//MyaddDetailPopup/BoxLayout[1]/MDRaisedButton[0]/MDLabel[0]')
        time.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput', "text", data[1])
        time.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'Hey')
        time.sleep(3)
        random_label=""
        for char in "Hey,i am sending message directly from MyAddress book":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]', 'text', random_label)
            time.sleep(0.2)
        time.sleep(2)
        self.cli.click_on('//MDIconButton[2]')
        time.sleep(2)


if __name__ == '__main__':
    """Start Application"""
    obj = MyAddressScreen()
    obj.setUpClass()
    obj.test_select_myaddress_list()
    obj.test_show_Qrcode()
    obj.test_send_message_from()
