from .telenium_process import TeleniumTestProcess
from .common import ordered


class PaymentScreen(TeleniumTestProcess):
    """Payment Plan Screen Functionality Testing"""

    @ordered
    def test_select_payment_plan(self):
        """Select Payment plan From List of payments"""
        # This is for checking Current screen
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Method to open the side navbar
        self.open_side_navbar()
        # Dragging from sent to inbox to get Payment tab
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=10)
        # this is for opening Payment screen
        self.cli.wait_click('//NavigationItem[@text=\"Payment plan\"]', timeout=5)
        # Checking the navbar is in closed state
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # Assert for checking Current Screen
        self.assertExists("//ScreenManager[@current=\"payment\"]", timeout=5)
        # Checking state of Current tab Payment plan
        self.assertExists(
            '//Payment/MDTabs[0]//MDTabsLabel[@text=\"Payment\"][@state=\"down\"]', timeout=5
        )
        # Scrolling Down Payment plan Cards
        self.drag(
            '//Payment//MDTabs[0]//MDCard[2]//MDLabel[@text=\"Standard\"]',
            '//Payment//MDTabs[0]//MDCard[1]//MDLabel[@text=\"You can get zero encrypted message per month\"]'
        )
        # Checking the subscription offer cards
        self.assertExists(
            '//Payment/MDTabs[0]//MDCard[3]//MDLabel[@text=\"Premium\"]',
            timeout=10
        )
        # Checking the get it now button
        self.assertExists(
            '//Payment/MDTabs[0]//MDCard[3]//MDRaisedButton[@text=\"Get it now\"]',
            timeout=10
        )
        # Clicking on the get it now button
        self.cli.wait_click(
            '//Payment/MDTabs[0]//MDCard[3]//MDRaisedButton[@text=\"Get it now\"]',
            timeout=10
        )
        # Checking the Payment method popup
        self.assertExists('//PaymentMethodLayout//ScrollView[0]//ListItemWithLabel[0]', timeout=10)
        # CLick on the Payment Method
        self.cli.wait_click(
            '//PaymentMethodLayout//ScrollView[0]//ListItemWithLabel[0]',
            timeout=10
        )
        # Check pop up is opened
        self.assertExists('//PaymentMethodLayout[@disabled=false]', timeout=10)
        # Click out side to dismiss the popup
        self.cli.wait_click('//MDRaisedButton[1]', timeout=10)
        # Checking state of next tab Payment
        self.assertExists(
            '//Payment/MDTabs[0]//MDTabsLabel[@text=\"Extra-Messages\"][@state=\"normal\"]', timeout=5
        )
        # Clicking on Payment tab
        self.cli.wait_click('//Payment/MDTabs[0]//MDTabsLabel[@text=\"Extra-Messages\"]', timeout=5)
        # Checking state of payment tab after click
        self.assertExists(
            '//Payment/MDTabs[0]//MDTabsLabel[@text=\"Extra-Messages\"][@state=\"down\"]', timeout=5
        )
        self.cli.sleep(1)
