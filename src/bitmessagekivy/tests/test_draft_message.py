from .telenium_process import TeleniumTestProcess
from .common import ordered


class DraftMessage(TeleniumTestProcess):
    """Draft Screen Functionality Testing"""

    @ordered
    def test_save_draft_message(self):
        """Select A Draft Screen From Navigaion-Drawer-Box Then
           Send a drafted message """
        print("=====================Test - Select A Draft Screen From Navigaion-Drawer-Box=====================")
        # OPEN NAVIGATION-DRAWER
        self.cli.sleep(4)
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(2)
        # OPEN INBOX SCREEN
        self.cli.click_on('//NavigationItem[1]')
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=2)
        self.cli.sleep(2)
        # CLICK ON PLUS ICON BUTTON
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        self.assertExists("//Create[@name~=\"create\"]", timeout=2)
        self.cli.sleep(3)
        # SELECT - TO ADDRESS
        self.cli.click_on(
            '//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MyTextInput[0]')
        self.cli.sleep(3)
        # ADD FROM MESSAGE
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]',
                         "text", 'BM-2cSsuH1bUWBski8bvdqnK2DivMqQCeQA1J')
        self.cli.sleep(3)
        # CLICK BACK-BUTTON
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=2)
        self.cli.sleep(5)
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        self.assertExists("//Create[@name~=\"create\"]", timeout=2)
        self.cli.sleep(3)
        # SELECT - TO ADDRESS
        self.cli.click_on(
            '//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        self.cli.sleep(1)
        self.cli.click_on('//MyTextInput[0]')
        self.cli.sleep(3)
        # ADD FROM MESSAGE
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/RelativeLayout[0]/BoxLayout[0]/MyTextInput',
                         "text", 'BM-2cSsuH1bUWBski8bvdqnK2DivMqQCeQA1J')
        self.cli.sleep(4)
        # Add SUBJECT
        random_label = ""
        for char in "Another Draft message":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', random_label)
            self.cli.sleep(0.2)
        # CLICK BACK-BUTTON
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(4)
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=1)

    @ordered
    def test_edit_and_resend_draft_messgae(self):
        """Select A Message From List of Messages Then
            make changes and send it."""
        print("=====================Test - Edit A Message From Draft Screen=====================")
        # OPEN NAVIGATION-DRAWER
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(4)
        # OPEN DRAFT SCREEN
        self.cli.click_on('//NavigationItem[3]')
        self.assertExists("//Draft[@name~=\"draft\"]", timeout=2)
        self.cli.sleep(4)
        # SHOW DRAFT MESSAGE AND SELECT FIRST MESSAGE
        # self.cli.click_on('//Carousel[0]//TwoLineAvatarIconListItem[0]')
        self.cli.click_on('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]')
        self.assertExists("//MailDetail[@name~=\"mailDetail\"]", timeout=2)
        self.cli.sleep(3)
        # CLICK EDIT BUTTON
        self.cli.click_on('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[0]')
        self.assertExists("//Create[@name~=\"create\"]", timeout=2)
        self.cli.sleep(5)
        random_label = ""
        for char in "Hey,This is draft Message Body":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/MDTextField[0]',
                             'text', random_label)
            self.cli.sleep(0.2)
        self.cli.sleep(3)
        self.cli.click_on('//MDActionTopAppBarButton[2]')
        # self.cli.sleep(5)
        self.assertExists("//Inbox[@name~=\"inbox\"]", timeout=5)

    @ordered
    def test_delete_draft_message(self):
        """Delete A Message From List of Messages"""
        print("=====================Test - Delete A Message From List of Messages=====================")
        self.cli.sleep(5)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDActionTopAppBarButton[0]')
        self.cli.sleep(4)
        self.cli.click_on('//NavigationItem[3]')
        self.assertExists("//Draft[@name~=\"draft\"]", timeout=1)
        self.cli.sleep(5)
        self.cli.click_on('//SwipeToDeleteItem[0]//TwoLineAvatarIconListItem[0]')
        self.assertExists("//MailDetail[@name~=\"mailDetail\"]", timeout=2)
        # self.cli.click_on('//Carousel[0]//TwoLineAvatarIconListItem[0]')
        self.cli.sleep(5)
        self.cli.click_on('//MDToolbar/BoxLayout[2]/MDActionTopAppBarButton[1]')
        self.cli.sleep(5)
        self.assertExists("//Draft[@name~=\"draft\"]", timeout=1)
