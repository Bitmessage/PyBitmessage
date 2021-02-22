import time
from telenium.tests import TeleniumTestCase
import random
import string
import  os
import test_telenium_cases
from random import choice
from string import ascii_lowercase


class Bitmessage_Login_Screen(TeleniumTestCase):
    """Login Functionality Testing"""
    # cmd_entrypoint = [u'/home/cis/peterwork_new/PyBitmessage/src/main.py']
    cmd_entrypoint = [u'/home/cis/py3porting/Chatroom/PyBitmessage/src/main.py']

    def runTest(self):
        """Test Run Method."""
        print(self,"=====================Welcome To Kivy Testing Application=====================")
    
    def test_login_screen(self):
        """Clicking on Proceed Button to Proceed to Next Screen."""
        print("=====================Test - Login Screen=====================")
        # time.sleep(3)   
        # self.cli.drag("/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Login[0]/ScrollView[0]/BoxLayout[0]/MDCheckbox[0]","/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Login[0]/ScrollView[0]/BoxLayout[0]/BoxLayout[0]",2)
        time.sleep(3)
        self.cli.wait_click('//Login/BoxLayout[0]/BoxLayout[0]/ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]/MDFillRoundFlatIconButton[0]')
        # self.cli.wait_click(u'/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Login[0]/ScrollView[0]/BoxLayout[0]/BoxLayout[2]/AnchorLayout[0]/MDRaisedButton[0]/MDLabel[0]')
        time.sleep(3)

    def test_random_screen(self):
        """Creating New Adress For New User."""
        print("=====================Test - Create New Address=====================")
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        # self.cli.click_on('/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Random[0]/ScrollView[0]/BoxLayout[0]/MDTextField[0]')
        time.sleep(3)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        # self.cli.wait_click(u'/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Random[0]/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/AnchorLayout[0]/MDRaisedButton[0]/MDLabel[0]')    
        time.sleep(3)
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        # self.cli.click_on('/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Random[0]/ScrollView[0]/BoxLayout[0]/MDTextField[0]')
        time.sleep(3)
        random_label = ""
        for _ in range(10):
            random_label += choice(ascii_lowercase)
            self.cli.setattr('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]', "text", random_label)
            # self.cli.setattr(u'/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Random[0]/ScrollView[0]/BoxLayout[0]/MDTextField[0]', "text", random_label)
            time.sleep(0.2)
        time.sleep(1)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        # self.cli.wait_click(u'/NavigationLayout/BoxLayout[1]/FloatLayout[0]/BoxLayout[0]/ScreenManager[0]/Random[0]/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/AnchorLayout[0]/MDRaisedButton[0]/MDLabel[0]')    
        time.sleep(5)
     
if __name__ == '__main__':
    """Start Application"""
    # import pdb;pdb.set_trace()
    TeleniumTestCase.start_process()
    Bitmessage_Login_Screen().runTest()
    print("==================start from first screen=====================")
    f=open("/home/cis/.config/PyBitmessage/keys.dat")
    get_file=f.read()
    find_address=get_file.find("label")
    print('m...................................', find_address)
    if find_address != -1 and False:
        # select_address=test_telenium_cases.Bitmessage_Select_Address()
        # select_address.test_check_already_created_address()
        # select_address.test_calling_all_methods()
        # sent_message=test_telenium_cases.Bitmessage_Sent_Screen_Message()
        # sent_message.test_select_sent()
        # sent_message.test_sent_multiple_message()
        # inbox_message=test_telenium_cases.Bitmessage_Inbox_Screen_Message()
        # inbox_message.test_all_inbox_method()
        # sent_message.test_all_sent_method()
        # # sent_message.test_archive_sent_message_from_list()
        # draft_message=test_telenium_cases.Bitmessage_Draft_Screen_Message()
        # draft_message.test_all_draft_method()
        # trash_message=test_telenium_cases.Bitmessage_Trash_Screen_Message()
        # trash_message.test_delete_trash_message()
        # all_mails=test_telenium_cases.Bitmessage_AllMail_Screen_Message()
        # all_mails.test_select_all_mails()
        # all_mails.test_delete_message_from_draft()
        address_book=test_telenium_cases.Bitmessage_AddressBook_Screen_Message()
        address_book.test_all_address_book_method()
        setting=test_telenium_cases.Bitmessage_Setting_Screen()
        setting.test_setting()
        existing_Address=test_telenium_cases.Bitmessage_MyAddress_Screen_Message()
        existing_Address.test_select_myaddress_list()
        existing_Address.test_send_message_from()
        subscription_payment=test_telenium_cases.Bitmessage_SubscriptionPayment_Screen()
        subscription_payment.test_select_subscripton()
        credits=test_telenium_cases.Bitmessage_Credits_Screen()
        credits.test_check_credits()
        network_status=test_telenium_cases.Bitmessage_NetwrokStatus_Screen()
        network_status.test_total_selection()
    else :
        # Bitmessage_Login_Screen().test_login_screen()
        # Bitmessage_Login_Screen().test_random_screen()
        # new_address=test_telenium_cases.Bitmessage_Create_New_Address()
        # new_address.test_create_new_address()
        # print('line.......................................97')
        # Bitmessage_Login_Screen().test_random_screen()
        # print('line.......................................99')
        # select_address=test_telenium_cases.Bitmessage_Select_Address()
        # print('line.......................................107')
        # select_address.test_calling_all_methods()
        # print('line.......................................105')
        # sent_message=test_telenium_cases.Bitmessage_Sent_Screen_Message()
        # sent_message.test_select_sent()
        # print('line.......................................108')
        # sent_message.test_sent_multiple_message()
        # print('line.......................................110')
        # inbox_message=test_telenium_cases.Bitmessage_Inbox_Screen_Message()
        # inbox_message.test_all_inbox_method()
        # print('line.......................................113')
        # sent_message.test_all_sent_method()
        # print('line.......................................115')
        # draft_message=test_telenium_cases.Bitmessage_Draft_Screen_Message()
        # print('line.......................................117')
        # draft_message.test_all_draft_method()
        # print('line.......................................119')
        # trash_message=test_telenium_cases.Bitmessage_Trash_Screen_Message()
        # print('line.......................................121')
        # trash_message.test_delete_trash_message()
        # print('line.......................................123')
        # all_mails=test_telenium_cases.Bitmessage_AllMail_Screen_Message()
        # print('line.......................................125')
        # all_mails.test_select_all_mails()
        # print('line.......................................127')
        # all_mails.test_delete_message_from_draft()
        print('line.......................................129')
        address_book=test_telenium_cases.Bitmessage_AddressBook_Screen_Message()
        address_book.test_all_address_book_method()
        setting=test_telenium_cases.Bitmessage_Setting_Screen()
        setting.test_setting()
        existing_Address=test_telenium_cases.Bitmessage_MyAddress_Screen_Message()
        existing_Address.test_select_myaddress_list()
        existing_Address.test_send_message_from()
        subscription_payment=test_telenium_cases.Bitmessage_SubscriptionPayment_Screen()
        subscription_payment.test_select_subscripton()
        credits=test_telenium_cases.Bitmessage_Credits_Screen()
        credits.test_check_credits()
        network_status=test_telenium_cases.Bitmessage_NetwrokStatus_Screen()
        network_status.test_total_selection()

        