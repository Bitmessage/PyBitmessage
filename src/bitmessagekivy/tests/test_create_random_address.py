import os
import tempfile
import time
from random import choice
from string import ascii_lowercase
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class CreateRandomAddress(TeleniumTestProcess):
    
    def test_login_screen(self):
        """Clicking on Proceed Button to Proceed to Next Screen."""
        print("=====================Test - Login Screen=====================")
        time.sleep(3)
        self.cli.wait_click('//Login/BoxLayout[0]/BoxLayout[0]/ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]/MDFillRoundFlatIconButton[0]')
        time.sleep(3)

    def test_random_screen(self):
        """Creating New Adress For New User."""
        print("=====================Test - Create New Address=====================")
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        time.sleep(3)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        time.sleep(3)
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        time.sleep(3)
        random_label = ""
        for _ in range(10):
            random_label += choice(ascii_lowercase)
            self.cli.setattr('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]', "text", random_label)
            time.sleep(0.2)
        time.sleep(1)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        time.sleep(5)

    def test_create_new_address(self):
        """Clicking on Navigation Drawer To Open New Address"""
        print("=====================Test - Create New Address=====================")
        time.sleep(5)
        self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        time.sleep(2)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        time.sleep(3)
        self.cli.click_on('//NavigationItem[9]')
        time.sleep(4)
        self.cli.wait_click('//Login/BoxLayout[0]/BoxLayout[0]/ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]/MDFillRoundFlatIconButton[0]')

    def test_select_address(self):
        """Select First Address From Drawer-Box"""
        print("=====================Test - Select First Address From Drawer-Box=======================")
        time.sleep(3)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(2)
        self.cli.drag("//NavigationItem[@text=\"Address Book\"]","//NavigationItem[@text=\"Settings\"]",1)
        time.sleep(2)
        self.cli.click_on('//NavigationItem[0]')
        time.sleep(2)
        self.cli.click_on('//MySpinnerOption[0]')


if __name__ == '__main__':
    """Start Application"""
    obj = CreateRandomAddress()
    obj.setUpClass(True) # this is for showing another process running error
    obj.test_login_screen()
    obj.test_random_screen()
    obj.test_create_new_address()
    obj.test_random_screen()
    obj.test_select_address()
    # obj.remove_temp_data()
