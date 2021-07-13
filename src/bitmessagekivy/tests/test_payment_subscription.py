from .telenium_process import TeleniumTestProcess


class PaymentScreen(TeleniumTestProcess):
    """SubscriptionPayment Screen Functionality Testing"""

    def test_select_subscripton(self):
        """Select Subscripton From List of Subscriptons"""
        print("=====================Test -Select Subscripton From List of Subscriptons=====================")
        self.cli.sleep(10)
        # this is for opening Nav drawer
        self.click_on('//MDActionTopAppBarButton[@icon=\"menu\"]')
        # Dragging from sent to inbox to get Payment tab.
        self.drag("//NavigationItem[@text=\"Sent\"]", "//NavigationItem[@text=\"Inbox\"]")
        # this is for opening Payment screen
        self.click_on('//NavigationItem[@text=\"Purchase\"]', seconds=1)
        self.assertExists("//Payment[@name~=\"payment\"]", timeout=2)
        self.cli.drag(
            '//Payment/BoxLayout[0]/ScrollView[0]/BoxLayout[0]/ProductCategoryLayout[0]/ProductLayout[1]',
            '//Payment/BoxLayout[0]/ScrollView[0]/BoxLayout[0]/ProductCategoryLayout[0]/ProductLayout[0]', 1)
        self.cli.sleep(2)
        self.click_on('//MDRaisedButton[3]')
        self.cli.sleep(2)
        self.cli.click_on('//ListItemWithLabel[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MDRaisedButton[3]')
        self.cli.sleep(2)
        self.assertExists("//Payment[@name~=\"payment\"]", timeout=2)

