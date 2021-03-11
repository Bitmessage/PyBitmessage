from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class PaymentScreen(TeleniumTestProcess):
    """SubscriptionPayment Screen Functionality Testing"""

    def test_select_subscripton(self):
        """Select Subscripton From List of Subscriptons"""
        print("=====================Test -Select Subscripton From List of Subscriptons=====================")
        self.cli.sleep(4)
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(3)
        self.cli.drag("//NavigationItem[@text=\"Sent\"]","//NavigationItem[@text=\"Inbox\"]",1)
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[8]')
        self.cli.sleep(3)
        self.cli.drag('//Payment/BoxLayout[0]/ScrollView[0]/BoxLayout[0]/ProductCategoryLayout[0]/ProductLayout[1]',
            '//Payment/BoxLayout[0]/ScrollView[0]/BoxLayout[0]/ProductCategoryLayout[0]/ProductLayout[0]', 1)
        self.cli.sleep(2)
        self.cli.click_on('//MDRaisedButton[3]')
        self.cli.sleep(2)
        self.cli.click_on('//ListItemWithLabel[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MDRaisedButton[3]')
        self.cli.sleep(2)
