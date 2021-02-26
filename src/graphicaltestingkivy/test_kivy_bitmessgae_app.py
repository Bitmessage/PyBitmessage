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
    cmd_entrypoint = [u'/home/cis/py3porting/Chatroom/PyBitmessage/src/main.py']

    def runTest(self):
        """Test Run Method."""
        print(self,"=====================Welcome To Kivy Testing Application=====================")
    
    def test_login_screen(self):
        """Clicking on Proceed Button to Proceed to Next Screen."""
        print("=====================Test - Login Screen=====================")
        time.sleep(3)
        self.cli.wait_click('//Login/BoxLayout[0]/BoxLayout[0]/ScreenManager[0]/Screen[0]/BoxLayout[0]/AnchorLayout[3]/MDFillRoundFlatIconButton[0]')
        time.sleep(3)

    def test_random_screen(self):
        """Creating New Adress For New User."""
        print("=====================Test - Create New Address=====================")
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        time.sleep(3)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        time.sleep(3)
        self.cli.click_on('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]')
        time.sleep(3)
        random_label = ""
        for _ in range(10):
            random_label += choice(ascii_lowercase)
            self.cli.setattr('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[1]/MDTextField[0]', "text", random_label)
            time.sleep(0.2)
        time.sleep(1)
        self.cli.wait_click('//RandomBoxlayout/BoxLayout[0]/AnchorLayout[2]/MDFillRoundFlatIconButton[0]')
        time.sleep(5)
     
if __name__ == '__main__':
    """Start Application"""
    TeleniumTestCase.start_process()
    Bitmessage_Login_Screen().runTest()
    print("==================start from first screen=====================")
    f=open("/home/cis/.config/PyBitmessage/keys.dat")
    get_file=f.read()
    find_address=get_file.find("label")
    print('m...................................', find_address)
    if find_address != -1:
        print('in if....................................')
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
        select_address=test_telenium_cases.Bitmessage_Select_Address()
        select_address.test_calling_all_methods()
        address_book=test_telenium_cases.Bitmessage_AddressBook_Screen_Message()
        address_book.test_all_address_book_method()
        setting=test_telenium_cases.Bitmessage_Setting_Screen()
        setting.test_setting()
        existing_Address=test_telenium_cases.Bitmessage_MyAddress_Screen_Message()
        existing_Address.test_select_myaddress_list()
        existing_Address.test_show_Qrcode()
        existing_Address.test_send_message_from()
        subscription_payment=test_telenium_cases.Bitmessage_SubscriptionPayment_Screen()
        subscription_payment.test_select_subscripton()
        credits=test_telenium_cases.Bitmessage_Credits_Screen()
        credits.test_check_credits()
        network_status=test_telenium_cases.Bitmessage_NetwrokStatus_Screen()
        network_status.test_total_selection()
    else :
        Bitmessage_Login_Screen().test_login_screen()
        Bitmessage_Login_Screen().test_random_screen()
        new_address=test_telenium_cases.Bitmessage_Create_New_Address()
        new_address.test_create_new_address()
        Bitmessage_Login_Screen().test_random_screen()
        select_address=test_telenium_cases.Bitmessage_Select_Address()
        select_address.test_calling_all_methods()
        sent_message=test_telenium_cases.Bitmessage_Sent_Screen_Message()
        sent_message.test_select_sent()
        sent_message.test_sent_multiple_message()
        inbox_message=test_telenium_cases.Bitmessage_Inbox_Screen_Message()
        inbox_message.test_all_inbox_method()
        sent_message.test_all_sent_method()
        draft_message=test_telenium_cases.Bitmessage_Draft_Screen_Message()
        draft_message.test_all_draft_method()
        trash_message=test_telenium_cases.Bitmessage_Trash_Screen_Message()
        trash_message.test_delete_trash_message()
        all_mails=test_telenium_cases.Bitmessage_AllMail_Screen_Message()
        all_mails.test_select_all_mails()
        all_mails.test_delete_message_from_draft()
        address_book=test_telenium_cases.Bitmessage_AddressBook_Screen_Message()
        address_book.test_all_address_book_method()
        setting=test_telenium_cases.Bitmessage_Setting_Screen()
        setting.test_setting()
        existing_Address=test_telenium_cases.Bitmessage_MyAddress_Screen_Message()
        existing_Address.test_select_myaddress_list()
        existing_Address.test_show_Qrcode()
        existing_Address.test_send_message_from()
        subscription_payment=test_telenium_cases.Bitmessage_SubscriptionPayment_Screen()
        subscription_payment.test_select_subscripton()
        network_status=test_telenium_cases.Bitmessage_NetwrokStatus_Screen()
        network_status.test_total_selection()
