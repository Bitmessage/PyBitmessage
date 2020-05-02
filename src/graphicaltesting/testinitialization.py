"""Trigger Test"""
import unittest

import test_addressgeneration
import test_addsubscription
import test_blackwhitelist
import test_chans
import test_messagesend
import test_networkstatus
import test_popupmenu
import test_quit
import test_settingwindow
from testloader import BitmessageTestCase


def test_initialize(myapp):
    """Inititalizing the test cases"""
    suite = unittest.TestSuite()
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_addressgeneration.BitmessageTest_AddressGeneration, myapp=myapp))
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_messagesend.BitmessageTest_MessageTesting, myapp=myapp))
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_addsubscription.BitmessageTest_AddSubscription, myapp=myapp))
    suite.addTest(BitmessageTestCase.bitmessage_testloader(test_networkstatus.BitmessageTest_NetworkTest, myapp=myapp))
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_blackwhitelist.BitmessageTest_BlackandWhiteList, myapp=myapp))
    suite.addTest(BitmessageTestCase.bitmessage_testloader(test_chans.BitmessageTest_ChansTest, myapp=myapp))
    suite.addTest(BitmessageTestCase.bitmessage_testloader(test_popupmenu.BitmessageTest_Inbox_PopMenu, myapp=myapp))
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_popupmenu.BitmessageTest_AddressBox_PopMenu, myapp=myapp))
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_popupmenu.BitmessageTest_Subscription_PopMenu, myapp=myapp))
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_popupmenu.BitmessageTest_BlackWhiteList_PopMenu, myapp=myapp))
    suite.addTest(
        BitmessageTestCase.bitmessage_testloader(test_settingwindow.BitmessageTest_SettingWindowTest, myapp=myapp))
    suite.addTest(BitmessageTestCase.bitmessage_testloader(test_quit.BitmessageTest_QuitTest, myapp=myapp))
    unittest.TextTestRunner().run(suite)
