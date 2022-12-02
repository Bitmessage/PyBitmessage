from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks
from .common import ordered


class PaymentScreen(TeleniumTestProcess):
    """SubscriptionPayment Screen Functionality Testing"""

    @ordered
    def test_select_subscription(self):
        """Select Subscription From List of Subscriptions"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open the side navbar
        self.open_side_navbar()
        # Dragging from sent to inbox to get Payment tab
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=10)
        # this is for opening Payment screen
        self.cli.wait_click('//NavigationItem[@text=\"Purchase\"]', timeout=5)
        # Checking the navbar is in closed state
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # Assert for checking Current Screen
        self.assertExists("//ScreenManager[@current=\"payment\"]", timeout=5)
        # Scrolling Down Product list
        self.drag(
            '//ProductCategoryLayout[0]/ProductLayout[0]',
            '//ProductCategoryLayout[0]/ProductLayout[1]')
        # assert for checking scroll function
        self.assertCheckScrollDown('//Payment//ScrollView[0]', timeout=5)
        # Scrolling Up Product list
        self.drag(
            '//ProductCategoryLayout[0]/ProductLayout[1]',
            '//ProductCategoryLayout[0]/ProductLayout[0]')
        # assert for checking scroll function
        self.assertCheckScrollUp('//Payment//ScrollView[0]', timeout=10)

    @skip_screen_checks
    @ordered
    def test_buy_option(self):
        """Check subscription"""
        # Click on BUY Button
        self.cli.wait_click('//MDRaisedButton[@text=\"BUY\"]', timeout=5)
        # CLick on the Payment Method
        self.cli.click_on('//ScrollView[0]//ListItemWithLabel[0]')
        # Check pop up is opened
        self.assertExists('//PaymentMethodLayout[@disabled=false]', timeout=10)
        # Click out side to dismiss the popup
        self.cli.wait_click('//MDRaisedButton[5]', timeout=5)
        # Checking Current screen(Payment screen)
        self.assertExists("//ScreenManager[@current=\"payment\"]", timeout=5)
