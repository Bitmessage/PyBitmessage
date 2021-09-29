from time import time
from telenium.client import TeleniumHttpException
from .telenium_process import TeleniumTestProcess
from .common import ordered
from random import choice
from string import ascii_lowercase

class CreateRandomAddress(TeleniumTestProcess):
    """This is for testing randrom address creation"""
    
    @staticmethod
    def populate_test_data():
        pass

    @ordered
    def test_login_screen(self):
        # import pdb; pdb.set_trace()
        """Click on Proceed Button to Proceed to Next Screen."""
        # Checking current Screen(Login screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=20, value='login')
        # Clicking on Proceed Next Button
        # print(self.cli.getattr('//Screen[0]//AnchorLayout[1]//Check[@active]', 'active'), '------------------------')
        # is_checked = self.cli.getattr('//Screen[0]//AnchorLayout[1]//Check[@active]', 'active')
        # self.assertExists("//ScreenManager[@current=\"login\"]", timeout=5)
        start = time()
        deadline = start + 2
        while time() < deadline:
            try:
                # Clicking on Proceed Next Button to redirect to "random" screen
                self.cli.wait_click('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
            except:
                # Checking Current Screen(Random Screen) after Clicking on "Proceed Next" Button 
                self.assertExists("//ScreenManager[@current=\"random\"]", timeout=5)
                
        # if not is_checked:
        #     # self.assertExists('//Screen[0]//AnchorLayout[1]//Check[@active=\"True\"]', timeout=5)
        #     self.cli.wait_click('//Screen[0]//AnchorLayout[1]//Check', timeout=2)
        #     self.assertEqual(self.cli.getattr('//Screen[0]//AnchorLayout[1]//Check[@active]', 'active'), True)
        #     self.cli.wait_click('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
        # else:
        #     self.cli.wait_click('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
        #     self.assertEqual(self.cli.getattr('//Screen[0]//AnchorLayout[1]//Check[@active]', 'active'), True)
        #     # self.assertExists('//Screen[0]//AnchorLayout[1]//Check[@active~=\"True\"]', timeout=5)


        # self.assertTrue(self.cli.getattr('//Screen[0]//AnchorLayout[1]//Check[@active]', 'active'), True)
        # self.assertExists('//Screen[0]//AnchorLayout[1]//Check[@active~=\"True\"]', timeout=5)
        # self.assertEqual(self.cli.getattr('//Screen[0]//AnchorLayout[1]//Check[@active]', 'active'), True)
        # self.assertExists('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
        # self.cli.wait('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
        # self.cli.wait_click('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
        # Checking Current Screen(Random Screen) after Clicking on "Proceed Next" Button 
        self.assertExists("//ScreenManager[@current=\"random\"]", timeout=5)

    @ordered
    def test_random_screen(self):
        """Creating New Adress For New User."""
        # Clicking on Label Text Field to give address name
        # self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]', timeout=2)
        # Generating Label Randomly
        random_label = ""
        for _ in range(10):
            random_label += choice(ascii_lowercase)
            self.cli.setattr('//RandomBoxlayout//AnchorLayout[1]/MDTextField[0]', "text", random_label)
            self.cli.sleep(0.1)
        # Click on Proceed Next button to generate random Address
        self.cli.wait_click('//RandomBoxlayout//MDFillRoundFlatIconButton[0]', timeout=2)
        # Checking My Address Screen
        # self.assertExists("//MyAddress[@name~=\"myaddress\"]", timeout=3)
        self.assertExists("//ScreenManager[@current=\"myaddress\"]", timeout=5)

    @ordered
    def test_create_new_address(self):
        """Clicking on Navigation Drawer To Open New Address"""
        # CLick to Open side Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # Scroll Down to get New Address Tab
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # Checking state of scrolled screen
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=3)
        self.assertExists('//NavigationItem[@text=\"New address\"]', timeout=5)
        # Clicking on New Address Tab
        self.cli.wait_click('//NavigationItem[@text=\"New address\"]', timeout=3)
        start = time()
        deadline = start + 2
        while time() < deadline:
            try:
                # Clicking on Proceed Next Button to redirect to "random" screen
                self.cli.wait_click('//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=5)
            except:
                # Checking Current Screen(Random Screen) after Clicking on "Proceed Next" Button 
                self.assertExists("//ScreenManager[@current=\"random\"]", timeout=5)
        # Checking current Screen(Login screen)
        # self.assertExists("//Login[@name~=\"login\"]", timeout=3)
        # self.assertExists("//ScreenManager[@current=\"login\"]", timeout=5)
        # Click on Proceed Next button to enter 'Random' Screen
        # self.cli.wait_click(
            # '//Screen[0]//MDFillRoundFlatIconButton[@text=\"Proceed Next\"]', timeout=2)
        # Checking Current Screen(Random Screen) after Clicking on Proceed Next Button 
        # self.assertExists("//Random[@name~=\"random\"]", timeout=1)
        # self.assertExists("//ScreenManager[@current=\"random\"]", timeout=5)
        # Executing above function to create new address
        self.test_random_screen()

    @ordered
    def test_select_address(self):
        # import pdb; pdb.set_trace()
        """Select First Address From Drawer-Box"""
        self.assertExists("//ScreenManager[@current=\"myaddress\"]", timeout=5)
        # This is for checking the Side nav Bar is closed
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # This is for checking the menu button is appeared
        self.assertExists('//MDActionTopAppBarButton[@icon~=\"menu\"]', timeout=5)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # Scrolling up to get address dropdown
        self.drag("//NavigationItem[@text=\"Address Book\"]", "//NavigationItem[@text=\"Settings\"]")
        # Checking scroll state
        self.assertCheckScrollUp('//ContentNavigationDrawer//ScrollView[0]', timeout=5)
        # Click to open Address Dropdown
        self.cli.wait_click('//NavigationItem[0]/CustomSpinner[0]', timeout=5)
        self.assertExists('//MySpinnerOption', timeout=5)
        is_open = self.cli.getattr('//NavigationItem[0]/CustomSpinner[@is_open]', 'is_open')
        print(is_open, '----------------------------------<true>')
        # import pdb; pdb.set_trace()
        self.assertEqual(is_open, True)
        self.cli.wait_click('//MySpinnerOption[0]', timeout=5)
        # is_open = self.cli.getattr('//NavigationItem[0]/CustomSpinner[@is_open]', 'is_open')
        # print(is_open, '----------------------------------<false>')
        # self.assertEqual(is_open, False)
        # self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=5)
        # Checking the state of dropdown (Should be open)
        # self.assertNotEqual('//NavigationItem[0]/CustomSpinner[@is_open]', False)
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=5)