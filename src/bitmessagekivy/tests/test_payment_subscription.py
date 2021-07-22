from time import time

from kivy.core.window import Animation
from .telenium_process import TeleniumTestProcess


class PaymentScreen(TeleniumTestProcess):
    """SubscriptionPayment Screen Functionality Testing"""

    def test_select_subscripton(self):
        """Select Subscripton From List of Subscriptons"""
        print("=====================Test -Select Subscripton From List of Subscriptons=====================")
        self.cli.sleep(10)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=3)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # Dragging from sent to inbox to get Payment tab.
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # assert for checking scroll function
        self.assertCheckScrollDown('//ContentNavigationDrawer//ScrollView[0]', timeout=3)
        # this is for opening Payment screen
        self.cli.wait_click('//NavigationItem[@text=\"Purchase\"]', timeout=2)
        # Assert for checking Current Screen
        self.assertExists("//Payment[@name~=\"payment\"]", timeout=3)
        # Scrolling Down Product list 
        self.cli.sleep(0.5)
        self.drag(
            '//ProductCategoryLayout[0]/ProductLayout[1]',
            '//ProductCategoryLayout[0]/ProductLayout[0]')
        # assert for checking scroll function
        self.assertCheckScrollDown('//Payment//ScrollView[0]', timeout=3)
        self.cli.sleep(2)
        print(self.cli.getattr('//Payment//MDCustomBottomSheet//MDBottomSheet[0]', 'animation'), 'pop is open or not  ----------------------------------------------````````````````````````````````````````````````````````````~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        self.cli.sleep(2)
        # Click on BUY Button
        self.cli.wait_click('//MDRaisedButton[@text=\"BUY\"]', timeout=2)
        # CLick on the Payment Method
        self.cli.click_on('//ScrollView[0]/ListItemWithLabel[0]')
        # Check pop up is opened
        self.assertEqual(self.cli.getattr('//PaymentMethodLayout/BoxLayout[0]/MDLabel[0]', 'text'), 'Select Payment Method')
        # Click out side to dismiss the popup
        self.cli.wait_click('//MDRaisedButton[3]', timeout=2)
        # Checking Current screen(Payment screen)
        self.assertExists("//Payment[@name~=\"payment\"]", timeout=2)
        