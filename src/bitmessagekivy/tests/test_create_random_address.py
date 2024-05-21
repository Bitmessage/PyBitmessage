"""
    Test for creating new identity
"""

from random import choice
from string import ascii_lowercase
from .telenium_process import TeleniumTestProcess
from .common import ordered


class CreateRandomAddress(TeleniumTestProcess):
    """This is for testing randrom address creation"""
    @staticmethod
    def populate_test_data():
        pass

    @ordered
    # This method tests the landing screen when the app runs first time and
    # the landing screen should be "login" where we can create new address
    def test_landing_screen(self):
        """Click on Proceed Button to Proceed to Next Screen."""
        # Checking current Screen(Login screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='login')
        # Dragging from sent to PROS: to NOTE:
        self.drag(
            '''//Login//Screen//ContentHead[1][@section_name=\"PROS:\"]''',
            '''//Login//Screen//ContentHead[0][@section_name=\"NOTE:\"]'''
        )
        # Assert the checkbox is rendered
        self.assertExists(
            '//Login//Screen[@name=\"check_screen\"]//AnchorLayout[1]/Check[@active=false]', timeout=5
        )
        # Clicking on the checkbox
        self.cli.wait_click(
            '//Login//Screen[@name=\"check_screen\"]//AnchorLayout[1]/Check', timeout=5
        )
        # Checking Status of checkbox after click
        self.assertExists(
            '//Login//Screen[@name=\"check_screen\"]//AnchorLayout[1]/Check[@active=true]', timeout=5
        )
        # Checking the Proceed Next button is rendered or not
        self.assertExists(
            '''//Login//Screen[@name=\"check_screen\"]'''
            '''//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]''', timeout=5
        )
        # Clicking on Proceed Next Button to redirect to "random" screen
        self.cli.wait_click(
            '''//Login//Screen[@name=\"check_screen\"]'''
            '''//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]''', timeout=5
        )
        self.assertExists("//ScreenManager[@current=\"random\"]", timeout=5)

    @ordered
    def test_generate_random_address_label(self):
        """Creating New Adress For New User."""
        # Checking the Button is rendered
        self.assertExists(
            '//Random//RandomBoxlayout//MDTextField[@hint_text=\"Label\"]', timeout=5)
        # Click on Label Text Field to give address Label
        self.cli.wait_click(
            '//Random//RandomBoxlayout//MDTextField[@hint_text=\"Label\"]', timeout=5)
        # Enter a Label Randomly
        random_label = ""
        for _ in range(10):
            random_label += choice(ascii_lowercase)
            self.cli.setattr('//Random//MDTextField[0]', "text", random_label)
            self.cli.sleep(0.1)
        # Checking the Button is rendered
        self.assertExists(
            '//Random//RandomBoxlayout//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
        # Click on Proceed Next button to generate random Address
        self.cli.wait_click(
            '//Random//RandomBoxlayout//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
        # Checking "My Address" Screen after creating a address
        self.assertExists("//ScreenManager[@current=\"myaddress\"]", timeout=5)
        # Checking the new address is created
        self.assertExists('//MyAddress//MDList[0]/CustomTwoLineAvatarIconListItem', timeout=10)

    @ordered
    def test_set_default_address(self):
        """Select First Address From Drawer-Box"""
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"myaddress\"]", timeout=5)
        # This is for opening side navbar
        self.open_side_navbar()
        # Click to open Address Dropdown
        self.assertExists('//NavigationItem[0][@text=\"dropdown_nav_item\"]', timeout=5)
        self.assertExists(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"]', timeout=5
        )
        self.assertExists(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@is_open=false]', timeout=5
        )
        self.cli.wait(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@state=\"normal\"]', timeout=5
        )
        # Click to open Address Dropdown
        self.cli.wait_click(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"]', timeout=5
        )
        self.cli.wait(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@state=\"normal\"]', timeout=5
        )
        # Check the state of dropdown.
        self.assertExists(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@is_open=true]', timeout=5
        )
        # List of addresses
        addresses_in_dropdown = self.cli.getattr(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]/IdentitySpinner[@values]', 'values'
        )
        # Checking the dropdown options are exists
        self.assertGreaterEqual(len(self.cli.getattr(
            '//MySpinnerOption[@text]', 'text')), len(addresses_in_dropdown)
        )
        # Selection of an address to set as a default address.
        self.cli.wait_click('//MySpinnerOption[0]', timeout=5)

        self.assertExists(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@is_open=false]', timeout=5
        )
        self.cli.sleep(0.5)
