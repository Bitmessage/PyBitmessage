import os
import tempfile

from .telenium_process import TeleniumTestProcess, cleanup
from .common import ordered, skip_screen_checks
from random import choice
from string import ascii_lowercase


class CreateRandomAddress(TeleniumTestProcess):
    """This is for testing randrom address creation"""

    @classmethod
    def setUpClass(cls):
        # pylint: disable=bad-super-call
        os.environ["BITMESSAGE_HOME"] = tempfile.gettempdir()
        cleanup()
        super(TeleniumTestProcess, cls).setUpClass()

    @skip_screen_checks
    @ordered
    def test_login_screen(self):
        """Clicking on Proceed Button to Proceed to Next Screen."""
        print("=====================Test - Login Screen=====================")
        self.cli.sleep(3)
        self.assertExists("//Login[@name~=\"login\"]", timeout=1)
        self.cli.wait_click(
            '//ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]/MDFillRoundFlatIconButton[0]')
        self.cli.sleep(3)
        self.assertExists("//Random[@name~=\"random\"]", timeout=1)

    @skip_screen_checks
    @ordered
    def test_random_screen(self):
        """Creating New Adress For New User."""
        print("=====================Test - Create New Address=====================")
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        self.cli.sleep(3)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        self.cli.sleep(3)
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        self.cli.sleep(3)
        random_label = ""
        for _ in range(10):
            random_label += choice(ascii_lowercase)
            self.cli.setattr('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]', "text", random_label)
            self.cli.sleep(0.2)
        self.cli.sleep(1)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        self.cli.sleep(5)
        self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=3)

    @skip_screen_checks
    @ordered
    def test_create_new_address(self):
        """Clicking on Navigation Drawer To Open New Address"""
        print("=====================Test - Create New Address=====================")
        self.cli.sleep(5)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(2)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]", 1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[9]')
        self.assertExists("//Login[@name~=\"login\"]", timeout=1)
        self.cli.sleep(4)
        self.cli.wait_click(
            '''//Login/BoxLayout[0]/BoxLayout[0]/ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]'''
            '''/MDFillRoundFlatIconButton[0]''')
        self.assertExists("//Random[@name~=\"random\"]", timeout=1)
        self.test_random_screen()

    @skip_screen_checks
    @ordered
    def test_select_address(self):
        """Select First Address From Drawer-Box"""
        print("=====================Test - Select First Address From Drawer-Box=======================")
        self.cli.sleep(3)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(2)
        self.cli.drag("//NavigationItem[@text=\"Address Book\"]", "//NavigationItem[@text=\"Settings\"]", 1)
        self.cli.sleep(2)
        self.cli.click_on('//NavigationItem[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MySpinnerOption[0]')
        self.cli.sleep(3)
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=1)
