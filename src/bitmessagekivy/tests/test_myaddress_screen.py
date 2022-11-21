from .telenium_process import TeleniumTestProcess
from .common import ordered


data = [
    'BM-2cWmjntZ47WKEUtocrdvs19y5CivpKoi1h',
    'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr'
]


class MyAddressScreen(TeleniumTestProcess):
    """MyAddress Screen Functionality Testing"""
    @ordered
    def test_myaddress_screen(self):
        """Open MyAddress Screen"""
        # Checking current Screen(Inbox screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar
        self.open_side_navbar()
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=10)
        # Checking My address label on side nav bar
        self.assertExists('//NavigationItem[@text=\"My addresses\"]', timeout=5)
        # this is for opening setting screen
        self.cli.wait_click('//NavigationItem[@text=\"My addresses\"]', timeout=5)
        # Checking current screen
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=5)

    @ordered
    def test_disable_address(self):
        """Disable Addresses"""
        # Dragging for loading addreses
        self.drag(
            '//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[@text=\"test2\"]',
            '//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[@text=\"test1\"]'
        )
        # Checking list of Addresses
        self.assertExists("//MyAddress//CustomTwoLineAvatarIconListItem", timeout=5)
        # Checking the Toggle button is rendered on addresses
        self.assertExists("//MyAddress//CustomTwoLineAvatarIconListItem//ToggleBtn", timeout=5)
        # Clicking on the Toggle button of first address to make it disable
        self.assertExists(
            "//MyAddress//CustomTwoLineAvatarIconListItem[@text=\"test2\"]//ToggleBtn[@active=true]",
            timeout=5
        )
        # Clicking on Toggle button of first address
        self.cli.wait_click(
            "//MyAddress//CustomTwoLineAvatarIconListItem[@text=\"test2\"]//ToggleBtn/Thumb",
            timeout=5
        )
        # Checking the address is disabled
        self.assertExists(
            "//MyAddress//CustomTwoLineAvatarIconListItem[@text=\"test2\"]//ToggleBtn[@active=false]",
            timeout=5
        )
        # CLICKING ON DISABLE ACCOUNT TO OPEN POPUP
        self.cli.wait_click("//MyAddress//CustomTwoLineAvatarIconListItem[@text=\"test2\"]", timeout=5)
        # Checking the popup is Opened
        self.assertExists(
            '//MDDialog[@text=\"Address is not currently active. Please click on Toggle button to active it.\"]',
            timeout=5
        )
        # Clicking on 'Ok' Button To Dismiss the popup
        self.cli.wait_click('//MDFlatButton[@text=\"Ok\"]', timeout=5)
        # Clicking on toggle button to enable the address
        self.cli.wait_click(
            "//MyAddress//CustomTwoLineAvatarIconListItem[@text=\"test2\"]//ToggleBtn/Thumb",
            timeout=5
        )
        # Checking the address is enabled
        self.assertExists(
            "//MyAddress//CustomTwoLineAvatarIconListItem[@text=\"test2\"]//ToggleBtn[@active=true]",
            timeout=5
        )
        # Checking the current screen is MyAddress
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=5)

    @ordered
    def test_show_Qrcode(self):
        """Show the Qr code of selected address"""
        # Checking labels from addresss list
        first_label = self.cli.getattr('//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[1][@text]', 'text')
        second_label = self.cli.getattr('//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[0][@text]', 'text')
        # Checking first label
        self.assertEqual(first_label, 'test1')
        # Checking second label
        self.assertEqual(second_label, 'test2')
        # Click on Address to open popup
        self.cli.wait_click('//MDList[0]/CustomTwoLineAvatarIconListItem[@text=\"test1\"]', timeout=5)
        # Check the Popup is opened
        self.assertExists('//MyaddDetailPopup//MDLabel[@text=\"Show QR code\"]', timeout=5)
        # Cick on 'Show QR code' button to view QR Code
        self.cli.wait_click('//MyaddDetailPopup//MDLabel[@text=\"Show QR code\"]')
        # Check Current screen is QR Code screen
        self.assertExists("//ShowQRCode[@name~=\"showqrcode\"]", timeout=2)
        # Check BACK button
        self.assertExists('//ActionTopAppBarButton[@icon~=\"arrow-left\"]', timeout=5)
        # Click on BACK button
        self.cli.wait_click('//ActionTopAppBarButton[@icon~=\"arrow-left\"]', timeout=5)
        # Checking current screen(My Address) after BACK press
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=5)

    @ordered
    def test_send_message_from(self):
        """Send Message From Send Message From Button"""
        # this is for scrolling Myaddress screen
        self.drag(
            '//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[@text=\"test2\"]',
            '//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[@text=\"test1\"]'
        )
        # Checking the addresses
        self.assertExists(
            '//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem[@text=\"test1\"]',
            timeout=5
        )
        # Click on Address to open popup
        self.cli.wait_click('//MDList[0]/CustomTwoLineAvatarIconListItem[@text=\"test1\"]', timeout=5)
        # Checking Popup Opened
        self.assertExists('//MyaddDetailPopup//MDLabel[@text=\"Send message from\"]', timeout=5)
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
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[0]',
            'text', 'Hey,i am sending message directly from MyAddress book'
        )
        # Checking Message body is Entered
        self.assertNotEqual('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text]', '')
