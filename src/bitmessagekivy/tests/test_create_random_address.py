from time import time
from random import choice
from string import ascii_lowercase
from telenium.client import TeleniumHttpException
from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks
from .common import ordered


class CreateRandomAddress(TeleniumTestProcess):
    """This is for testing randrom address creation"""

    @staticmethod
    def populate_test_data():
        pass

    @skip_screen_checks
    @ordered
    # This method tests the landing screen when the app runs first time and
    # the landing screen should be "login" where we can create new address
    def test_landing_screen(self):
        """Click on Proceed Button to Proceed to Next Screen."""
        # Checking current Screen(Login screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='login')
        # Click on "Proceed Next" Button to "generate random label for address" screen
        # Some widgets cannot renders suddenly and become not functional so we used loop with a timeout.
        start = time()
        deadline = start + 2
        while time() < deadline:
            try:
                # Clicking on Proceed Next Button to redirect to "random" screen
                self.cli.wait_click('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
            except TeleniumHttpException:
                # Checking Current Screen(Random Screen) after Clicking on "Proceed Next" Button
                self.assertExists("//ScreenManager[@current=\"random\"]", timeout=5)
        self.assertExists("//ScreenManager[@current=\"random\"]", timeout=5)

    @skip_screen_checks
    @ordered
    def test_generate_random_address_label(self):
        """Creating New Adress For New User."""
        # Checking the Button is rendered
        self.assertExists(
            '//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[@hint_text=\"Label\"]', timeout=2)
        # Click on Label Text Field to give address Label
        self.cli.wait_click(
            '//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[@hint_text=\"Label\"]', timeout=2)
        # Enter a Label Randomly
        random_label = ""
        for _ in range(10):
            random_label += choice(ascii_lowercase)
            self.cli.setattr('//RandomBoxlayout//AnchorLayout[1]/MDTextField[0]', "text", random_label)
            self.cli.sleep(0.1)
        # Checking the Button is rendered
        self.assertExists('//RandomBoxlayout//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=3)
        # Click on Proceed Next button to generate random Address
        self.cli.wait_click('//RandomBoxlayout//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=3)
        # Checking "My Address" Screen after creating a address
        self.assertExists("//ScreenManager[@current=\"myaddress\"]", timeout=5)
        # Checking the new address is created
        self.assertExists('//MDList[0]/CustomTwoLineAvatarIconListItem', timeout=10)

    @skip_screen_checks
    @ordered
    def test_set_default_address(self):
        """Select First Address From Drawer-Box"""
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"myaddress\"]", timeout=5)
        # This is for opening side navbar
        self.open_side_navbar()
        # Click to open Address Dropdown
        self.cli.wait_click('//NavigationItem[0]/CustomSpinner[0]', timeout=5)
        # Checking the dropdown option is exist
        self.assertExists('//MySpinnerOption[0]', timeout=5)
        is_open = self.cli.getattr('//NavigationItem[0]/CustomSpinner[@is_open]', 'is_open')
        # Check the state of dropdown.
        self.assertEqual(is_open, True)
        # Selection of an address to set as a default address.
        self.cli.wait_click('//MySpinnerOption[0]', timeout=5)
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=5)
