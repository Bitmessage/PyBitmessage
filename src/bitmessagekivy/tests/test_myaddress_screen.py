from time import sleep
from requests.packages.urllib3.util import timeout
from .telenium_process import TeleniumTestProcess
from .common import ordered

data = [
    'BM-2cWmjntZ47WKEUtocrdvs19y5CivpKoi1h',
    'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr'
]

class MyAddressScreen(TeleniumTestProcess):
    """MyAddress Screen Functionality Testing"""

    @ordered
    def test_select_myaddress_list(self):
        """Select Address From List of Address"""
        print("=====================Test -Select Address From List of Address=====================")
        self.cli.sleep(12)
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
        # self.assertExists('//NavigationItem[@text=\"My addresses\"]', timeout=2)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"My addresses\"]', timeout=2)
        # Checking current screen
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=2)

    @ordered
    def test_show_Qrcode(self):
        """Show the Qr code of selected address"""
        print("=====================Test -Show QR code of selected address=====================")
        # Checking current screen
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=2)
        # Click on Address to open popup
        self.cli.wait_click('//MDList[0]/CustomTwoLineAvatarIconListItem[0]', timeout=2)
        # Check the Popup is opened
        self.assertExists('//MyaddDetailPopup//MDLabel[@text=\"Show QR code\"]', timeout=2)
        # Cick on 'Show QR code' button to view QR Code
        self.cli.wait_click('//MyaddDetailPopup//MDLabel[@text=\"Show QR code\"]')
        # Check Current screen is QR Code screen
        self.assertExists("//ShowQRCode[@name~=\"showqrcode\"]", timeout=2)
        # Click on BACK button
        self.cli.wait_click('//MDToolbar//MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=2)
        # Checking current screen(My Address) after BACK press
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=2)

    @ordered
    def test_send_message_from(self):
        """Send Message From Send Message From Button"""
        print("=====================Test -Send Message From Send Message From Button=====================")
        self.cli.sleep(2)
        # Checking current screen
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=2)
        # Click on Address to open popup
        self.cli.wait_click('//MDList[0]/CustomTwoLineAvatarIconListItem[0]', timeout=2)
        # Checking Popup Opened
        self.assertExists('//MyaddDetailPopup//MDLabel[@text=\"Send message from\"]', timeout=2)
        # Click on Send Message Button to redirect Create Screen
        self.cli.wait_click('//MyaddDetailPopup//MDRaisedButton[0]/MDLabel[0]', timeout=2)
        # Checking Current screen(Create)
        self.assertExists("//Create[@name~=\"create\"]", timeout=2)
         # Entering Receiver Address
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", data[1])
        # Checking Receiver Address filled or not
        self.assertNotEqual('//DropDownWidget//MyTextInput[0]', '')
         # ADD SUBJECT
        self.cli.setattr('//DropDownWidget/ScrollView[0]//MyMDTextField[0]', 'text', 'Hey this is Demo Subject')
        # Checking Subject Field is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyMDTextField[0]', '')
         # ADD MESSAGE BODY
        self.cli.setattr('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[0]',
                             'text', 'Hey,i am sending message directly from MyAddress book')
        # Checking Message body is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text]', '')
        # Click on Send Icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=3)
        self.cli.sleep(2) # Send Messages takes 2 seconds to send message so need to user sleep
        # Checking Current screen after Send a message
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=3)

    @ordered
    def test_disable_address(self):
        """Disable Addresses"""
        self.cli.sleep(3)
        # this is for checking current screen
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=4)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=4)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=4)
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=4)
        # self.assertExists('//NavigationItem[@text=\"My addresses\"]', timeout=4)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"My addresses\"]', timeout=4)
        # Checking current screen
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=4)
        # ADDRESS DISABLED
        self.cli.sleep(1)
        self.cli.wait_click('//Thumb', timeout=2)
        # CLICKING ON DISABLE ACCOUNT TO OPEN POPUP
        self.click_on('//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[0]', seconds=2)
        # Checking the pop is Opened
        self.assertExists('//MDDialog[@text=\"Address is not currently active. Please click on Toggle button to active it.\"]', timeout=2)
        # Clicking on 'Ok' Button To Dismiss the pop
        self.click_on('//MDFlatButton[@text=\"Ok\"]', seconds=2)
        self.assertNotExists('//MDDialog[@text=\"Address is not currently active. Please click on Toggle button to active it.\"]', timeout=2)
        # ADDRESS ENABLED
        self.click_on('//Thumb', seconds=2)
        # self.assertExists('//Thumb[@active=\"False\"]', timeout=2)
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=2)
