from .telenium_process import TeleniumTestProcess
from .common import skip_screen_checks


class PaymentScreen(TeleniumTestProcess):
    """SubscriptionPayment Screen Functionality Testing"""

    @skip_screen_checks
    def test_select_subscription(self):
        """Select Subscription From List of Subscriptions"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # This is for checking the Side nav Bar id closed
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # This is for checking the menu button is appeared
        self.assertExists('//MDActionTopAppBarButton[@icon~=\"menu\"]', timeout=5)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # Dragging from sent to inbox to get Payment tab
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=3)
        # this is for opening Payment screen
        self.cli.wait_click('//NavigationItem[@text=\"Purchase\"]', timeout=2)
        # Assert for checking Current Screen
        # self.assertExists("//ScreenManager[@current=\"payment\"]", timeout=3)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=2, value='Payment')
        # Scrolling Down Product list
        self.cli.wait_click('//ProductCategoryLayout[0]/ProductLayout[1]', timeout=3)
        # self.click_on('//ProductCategoryLayout[0]/ProductLayout[1]', seconds=1)
        self.drag(
            '//ProductCategoryLayout[0]/ProductLayout[1]',
            '//ProductCategoryLayout[0]/ProductLayout[0]')
        # assert for checking scroll function
        self.assertCheckScrollDown('//Payment//ScrollView[0]', timeout=3)
        # Click on BUY Button
        self.cli.wait_click('//MDRaisedButton[@text=\"BUY\"]', timeout=2)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=2, value='payment')
        # CLick on the Payment Method
        self.cli.click_on('//ScrollView[0]/ListItemWithLabel[0]')
        # Check pop up is opened
        self.assertEqual(self.cli.getattr('//PaymentMethodLayout/BoxLayout[0]/MDLabel[0]', 'text'),
                         'Select Payment Method')
        # Click out side to dismiss the popup
        self.cli.wait_click('//MDRaisedButton[3]', timeout=2)
        # Checking Current screen(Payment screen)
        self.assertExists("//ScreenManager[@current=\"payment\"]", timeout=3)
