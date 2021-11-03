from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks


class PaymentScreen(TeleniumTestProcess):
    """SubscriptionPayment Screen Functionality Testing"""

    @skip_screen_checks
    def test_select_subscription(self):
        """Select Subscription From List of Subscriptions"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open the side navbar
        self.open_side_navbar()
        # Dragging from sent to inbox to get Payment tab
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=3)
        # this is for opening Payment screen
        self.cli.wait_click('//NavigationItem[@text=\"Purchase\"]', timeout=5)
        # Assert for checking Current Screen
        self.assertExists("//ScreenManager[@current=\"payment\"]", timeout=5)
        # Scrolling Down Product list
        self.drag(
            '//ProductCategoryLayout[0]/ProductLayout[0]',
            '//ProductCategoryLayout[0]/ProductLayout[1]')
        # assert for checking scroll function
        self.assertCheckScrollDown('//Payment//ScrollView[0]', timeout=3)
        # Scrolling Up Product list
        self.drag(
            '//ProductCategoryLayout[0]/ProductLayout[1]',
            '//ProductCategoryLayout[0]/ProductLayout[0]')
        # assert for checking scroll function
        self.assertCheckScrollDown('//Payment//ScrollView[0]', timeout=3)
        # Click on BUY Button
        self.cli.wait_click('//MDRaisedButton[@text=\"BUY\"]', timeout=2)
        # self.assertEqual('//PaymentMethodLayout[@disabled]', 'True') #Returns None when condition True
        # CLick on the Payment Method
        self.cli.click_on('//ScrollView[0]/ListItemWithLabel[0]')
        # Check pop up is opened
        self.assertTrue('//PaymentMethodLayout[@disabled]', 'False')
        # Click out side to dismiss the popup
        self.cli.wait_click('//MDRaisedButton[3]', timeout=2)
        # Checking Current screen(Payment screen)
        self.assertExists("//ScreenManager[@current=\"payment\"]", timeout=3)
