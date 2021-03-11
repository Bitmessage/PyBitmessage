import os
import tempfile

from bitmessagekivy.tests.telenium_process import TeleniumTestProcess, cleanup
from .common import ordered
from random import choice
from string import ascii_lowercase


class CreateRandomAddress(TeleniumTestProcess):
    
    @classmethod
    def setUpClass(cls):
        os.environ["BITMESSAGE_HOME"] = tempfile.gettempdir()
        cleanup()
        super(TeleniumTestProcess, cls).setUpClass()

    @ordered
    def test_login_screen(self):
        """Clicking on Proceed Button to Proceed to Next Screen."""
        print("=====================Test - Login Screen=====================")
        self.cli.sleep(3)
        self.cli.wait_click('//Login/BoxLayout[0]/BoxLayout[0]/ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]/MDFillRoundFlatIconButton[0]')
        self.cli.sleep(3)

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

    @ordered
    def test_create_new_address(self):
        """Clicking on Navigation Drawer To Open New Address"""
        print("=====================Test - Create New Address=====================")
        self.cli.sleep(5)
        self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.sleep(2)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[9]')
        self.cli.sleep(4)
        self.cli.wait_click('//Login/BoxLayout[0]/BoxLayout[0]/ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]/MDFillRoundFlatIconButton[0]')
        self.test_random_screen()

    @ordered
    def test_select_address(self):
        """Select First Address From Drawer-Box"""
        print("=====================Test - Select First Address From Drawer-Box=======================")
        self.cli.sleep(3)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(2)
        self.cli.drag("//NavigationItem[@text=\"Address Book\"]","//NavigationItem[@text=\"Settings\"]",1)
        self.cli.sleep(2)
        self.cli.click_on('//NavigationItem[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MySpinnerOption[0]')
