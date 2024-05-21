from .telenium_process import TeleniumTestProcess
from .common import ordered


class FileManagerOpening(TeleniumTestProcess):
    """File-manager Opening Functionality Testing"""
    @ordered
    def test_open_file_manager(self):
        """Opening and Closing File-manager"""
        # Checking current Screen(Inbox screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open side navbar
        self.open_side_navbar()
        # Click to open Address Dropdown
        self.assertExists('//NavigationItem[0][@text=\"dropdown_nav_item\"]', timeout=5)
        self.assertExists(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"]', timeout=1
        )
        # Check the state of dropdown
        self.assertExists(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@is_open=false]', timeout=1
        )
        self.cli.wait(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@state=\"normal\"]', timeout=5
        )
        self.cli.wait_click(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"]', timeout=1
        )
        # Check the state of dropdown.
        self.assertExists(
            '//NavigationItem[0][@text=\"dropdown_nav_item\"]'
            '/IdentitySpinner[@name=\"identity_dropdown\"][@is_open=true]', timeout=1
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
        # this is for scrolling Nav drawer
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # Checking File-manager icon
        self.assertExists(
            '//ContentNavigationDrawer//MDIconButton[1][@icon=\"file-image\"]',
            timeout=5
        )
        # Clicking on file manager icon
        self.cli.wait_click(
            '//ContentNavigationDrawer//MDIconButton[1][@icon=\"file-image\"]',
            timeout=5)
        # Checking the state of file manager is it open or not
        self.assertTrue(self.cli.execute('app.file_manager_open'))
        # Closing the filemanager
        self.cli.execute('app.exit_manager()')
        # Checking the state of file manager is it closed or not
        self.assertTrue(self.cli.execute('app.exit_manager()'))
