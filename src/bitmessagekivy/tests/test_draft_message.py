from time import time
from .telenium_process import TeleniumTestProcess
from telenium.client import TeleniumHttpException
from .common import ordered

test_address = {'auto_responder': 'BM-2cVWtdUzPwF7UNGDrZftWuHWiJ6xxBpiSP'}


class DraftMessage(TeleniumTestProcess):
    """Draft Screen Functionality Testing"""
    test_subject = 'Test Subject text'
    test_body = 'Hey This is draft Message Body'

    @ordered
    def test_save_message_to_draft(self):
        """
            Saving a message to draft box when click back button
        """
        # Checking current Screen(Login screen)
        self.assert_wait_no_except('//ScreenManager[@current]', timeout=15, value='inbox')
        # Checking the composer button is rendered
        # self.assertExists('//ComposerButton[0]/MDFloatingActionButton[@icon=\"plus\"]', timeout=10)
        # Click on Composer Icon(Plus icon)
        self.cli.wait_click('//ComposerButton[0]/MDFloatingActionButton[@icon=\"plus\"]', timeout=5)
        # Checking Message Composer Screen(Create)
        self.assertExists("//ScreenManager[@current=\"create\"]", timeout=5)

        # ADD SUBJECT
        self.cli.setattr('//DropDownWidget/ScrollView[0]//MyMDTextField[0]', 'text', self.test_subject)
        # Checking Subject Field is Entered
        # self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyMDTextField[@text]', '')
        self.assertExists('//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"{}\"]'.format(self.test_subject), timeout=5)

        # ADD MESSAGE BODY
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text]',
                             'text', self.test_body)
        # Checking Message body is Entered
        # self.assertNotEqual('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text]', '')
        # self.assertExists('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text=\"{}\"]'.format(self.test_body), timeout=5)
        self.assertExists('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[@text=\"{}\"]'.format(self.test_body), timeout=5)

        # Click on Send Icon
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=2)
        # Checking validation Pop up is Opened
        self.assertExists('//MDDialog', timeout=5)
        # Click "OK" button to dismiss the Popup
        self.cli.wait_click('//MDFlatButton[@text=\"Ok\"]', timeout=5)
        # Checking validation Pop up is Closed
        self.assertNotExists('//MDDialog', timeout=5)

        # RECEIVER FIELD
        # Checking Receiver Address Field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=2)
        # Entering Receiver Address
        self.cli.setattr(
            '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", test_address['auto_responder'])
        # Checking Receiver Address filled or not
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"{}\"]'.format(test_address['auto_responder']), timeout=2)
        # self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyTextInput[@text]', '')
        # Checking the sender's Field is empty
        self.assertExists('//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text=\"\"]', timeout=3)
        # Assert to check Sender's address dropdown open or not
        self.assertEqual(self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open'), False)
        # Open Sender's Address DropDown
        self.cli.wait_click('//Create//CustomSpinner[0]/ArrowImg[0]', timeout=5)
        self.assertEqual(self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open'), False)
 
        # start = time()
        # deadline = start + 2
        # while time() < deadline:
        #     if not self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open'):
        #         self.cli.wait_click('//Create//CustomSpinner[0]/ArrowImg[0]', timeout=5)
        #         break
        #     else:
        #         self.cli.sleep(0.3)
        #         continue                
 
        self.assertExists('//ComposerSpinnerOption[0]', timeout=5)
        # Select Sender's Address from Dropdown
        self.cli.wait_click('//ComposerSpinnerOption[0]', timeout=5)
        # Assert to check Sender's address dropdown closed
        self.assertEqual(self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open'), False)
        # Checking sender address is entered
        sender_address = self.cli.getattr('//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text]', 'text')
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text=\"{}\"]'.format(sender_address), timeout=3)

        # CLICK BACK-BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=5)
        # Checking current screen(Login) after BACK Press
        self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=5)

        # # Click on Composer Icon(Plus icon)
        # self.cli.wait_click('//ComposerButton[0]/MDFloatingActionButton[@icon=\"plus\"]', timeout=2)
        # # Checking Message Composer Screen(Create)
        # self.assertExists("//ScreenManager[@current=\"create\"]", timeout=4)
        # # ADD SENDER'S ADDRESS
        # # Checking State of Sender's Address Input Field (Empty)
        # self.assertExists('//DropDownWidget/ScrollView[0]//MDTextField[@text=\"\"]', timeout=2)

        # # Assert to check Sender's address dropdown is closed
        # is_open = self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open')
        # self.assertEqual(is_open, False)
        # # Open Sender's Address DropDown
        # self.cli.wait_click('//Create//CustomSpinner[0]/ArrowImg[0]', timeout=5)
        # # Checking the Address Dropdown is in open State
        # is_open = self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open')
        # # Select Sender's Address from Dropdown
        # self.cli.wait_click('//ComposerSpinnerOption[0]', timeout=3)
        # # Assert to check Sender's address dropdown is closed
        # is_open = self.cli.getattr('//Create//CustomSpinner[@is_open]', 'is_open')
        # self.assertEqual(is_open, False)


    #     # Assert to check Sender's address dropdown open or not
    #     self.assertNotEqual('//DropDownWidget/ScrollView[0]//MDTextField[@text]', '')

    #     # RECEIVER FIELD
    #     # Checking Receiver Address Field
    #     self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"\"]', timeout=2)
    #     # Entering Receiver Address
    #     self.cli.setattr(
    #         '//DropDownWidget/ScrollView[0]//MyTextInput[0]', "text", 'BM-2cSsuH1bUWBski8bvdqnK2DivMqQCeQA1J')
    #     # Checking Receiver Address filled or not
    #     self.assertNotEqual('//DropDownWidget/ScrollView[0]//MyTextInput[@text]', '')
    
    #     # ADD SUBJECT
    #     self.cli.setattr('//DropDownWidget/ScrollView[0]//MyMDTextField[0]', 'text', 'Another Draft message')
    #     # Checking Subject Field is Entered
    #     self.assertExists('//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"Another Draft message\"]', timeout=2)
    
    #     # CLICK BACK-BUTTON
    #     self.cli.wait_click('//MDToolbar//MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=2)
    #     # Checking current screen(Login) after BACK Press
    #     self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=2)

    @ordered
    def test_edit_and_resend_draft_messge(self):
        """Click on a Drafted message to send message."""
        # OPEN NAVIGATION-DRAWER
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # Click to open Draft Screen
        self.cli.wait_click('//NavigationItem[@text=\"Draft\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"close\"]", timeout=5)
        # Checking Draft Screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=5)
        # Checking messages in draft box
        self.assertEqual(len(self.cli.select('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem')), 1)
        self.cli.wait('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        # Click on a Message to view its details (Message Detail screen)
        self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # start = time()
        # deadline = start + 3
        # while time() < deadline:
        #     try:
        #         self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=2)
        #     except TeleniumHttpException:
        #         # Click on a drafted msg to show details
        #         self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        #         self.cli.sleep(0.1)
        #     self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        #     break
            # Assert check that the message is rendered
        # Checking current screen Mail Detail
        # self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=3)
        
        # self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=2)
        # self.cli.wait('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        # self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=3)
        # self.cli.wait('//ScreenManager[@current=\"mailDetail\"]', timeout=5)
        self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=3)

        # CLICK EDIT BUTTON
        self.cli.wait_click('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[@icon=\"pencil\"]', timeout=5)
        # Checking Current Screen 'Create'; composer screen.
        self.assertExists("//ScreenManager[@current=\"create\"]", timeout=10)
        
        # Checking the recipient is in the receiver field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyTextInput[@text=\"{}\"]'.format(test_address['auto_responder']), timeout=2)
        # Checking the sender address is in the sender field
        sender_address = self.cli.getattr('//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text]', 'text')
        self.assertExists(
            '//DropDownWidget/ScrollView[0]//BoxLayout[1]/MDTextField[@text=\"{}\"]'.format(sender_address), timeout=3)
        # Checking the subject text is in the subject field
        self.assertExists('//DropDownWidget/ScrollView[0]//MyMDTextField[@text=\"{}\"]'.format(self.test_subject), timeout=5)
        # Checking the Body text is in the Body field
        self.assertExists('//DropDownWidget/ScrollView[0]//ScrollView[0]/MDTextField[@text=\"{}\"]'.format(self.test_body), timeout=5)
        # CLICK BACK-BUTTON to autosave msg in draft screen
        self.cli.wait_click('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[@icon=\"arrow-left\"]', timeout=5)
        # Checking current screen(Login) after BACK Press
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=5)


        # # Click on Send Icon to send msg
        # self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"send\"]', timeout=5)
        # # Redirected to the inbox screen
        # self.assertExists("//ScreenManager[@current=\"inbox\"]", timeout=10)

        # import pdb;pdb.set_trace()
        # start = time()
        # deadline = start + 5
        # while time() < deadline:
        #     try:
        #         # Checking messages in draft box
        #         # self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem', timeout=5)
        #         # SELECT FIRST MESSAGE
        #         self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        #         print('>>>>>>>>>>>>>>>>>>>try')
        #     except TeleniumHttpException:
        #         print('>>>>>>>>>>>>>>>>>>>except1')
        #         # Checking Current Screen
        #         self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=5)
        #         break
        #         print('>>>>>>>>>>>>>>>>>>>except asserrtex')
        # self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=5)
        # print('>>>>>>>>>>>>>>>>>>><<<<<<<<< asserrtex')

        
        # # SELECT FIRST MESSAGE
        # self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem', timeout=5)
        # # Checking current screen Mail Detail
        # self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=5)


    @ordered
    def test_delete_draft_message(self):
        """Deleting a Drafted Message"""
        # # Saving a msg to draft to perform delete operation
        # self.test_save_message_to_draft()
        #  # OPEN NAVIGATION-DRAWER
        # # this is for opening Nav drawer
        # self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # # checking state of Nav drawer
        # self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
        # # Click to open Draft Screen
        # self.cli.wait_click('//NavigationItem[@text=\"Draft\"]', timeout=5)
        # # Checking Draft Screen
        # self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=5)
        # Assert check that the message is rendered

        # start = time()
        # deadline = start + 2
        # while time() < deadline:
        #     try:
        #         # Click on a drafted msg to show details
        #         self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=1)
        #         # Checking Current screen is Mail Detail
        #         self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=1)
        #         break
        #     except TeleniumHttpException:
        #         # Assert check that the message is rendered
        #         self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=1)
        #         self.cli.sleep(0.1)

        # self.assertEqual(len(self.cli.select('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem')), 1)
        # self.cli.wait('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # self.assertExists('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        # self.cli.wait('//ScreenManager[@current=\"mailDetail\"]', timeout=5)
        # self.assertExists("//ScreenManager[@current=\"mailDetail\"]", timeout=5)

        # # Click on trash-can icon to delete
        # self.cli.wait_click('//MDToolbar//MDActionTopAppBarButton[@icon=\"delete-forever\"]', timeout=5)
        # # After Deleting, Screen is redirected to Draft screen
        # self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=10)
        # checking state of Nav drawer(closed)
        # self.assertExists("//MDNavigationDrawer[@state~=\"close\"]", timeout=2)
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=8)
        # Checking the swipe layer is closed
        # self.assertExists('//MDList[0]//SwipeToDeleteItem[@state=\"closed\"]', timeout=5)
        # Checking the Trash icon is Disabled(Default)
        # self.assertEqual(self.cli.getattr('//MDList[0]//SwipeToDeleteItem[0]//MDIconButton[@disabled]', 'disabled'), True)
        # Swiping the Saveed address from left to right to enable the "trash-can" icon.
        # Click on Saved Address to come back the upper layer in nomal state.
        # self.cli.wait_click('//MDList[0]//SwipeToDeleteItem[0]', timeout=5)
        # self.cli.wait_click('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]', timeout=5)
        self.assertExists('//MDList[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # Click on trash icon
        self.cli.wait_click('//MDList[0]//MDIconButton[@icon=\"trash-can\"]', timeout=5)
        # message_count = len(self.cli.select('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]'))
        # Checking the message is deleted
        self.assertEqual(len(self.cli.select('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]')), 0)
        # Checking current screen
        self.assertExists("//ScreenManager[@current=\"draft\"]", timeout=8)
