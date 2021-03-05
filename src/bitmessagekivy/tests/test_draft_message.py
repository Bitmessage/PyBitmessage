import time
from bitmessagekivy.tests.telenium_process import TeleniumTestProcess


class DraftMessage(TeleniumTestProcess):
    """Draft Screen Functionality Testing"""

    def test_select_draft_message(self):
        """Select A Draft Screen From Navigaion-Drawer-Box Then
           Send a drafted message """
        print("=====================Test - Select A Draft Screen From Navigaion-Drawer-Box=====================")
        # OPEN NAVIGATION-DRAWER
        time.sleep(4)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(2)
        # OPEN INBOX SCREEN
        self.cli.click_on('//NavigationItem[1]')
        time.sleep(2)
        # CLICK ON PLUS ICON BUTTON
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        time.sleep(3)
        # SELECT - TO ADDRESS
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        time.sleep(2)
        self.cli.click_on('//MyTextInput[0]')
        time.sleep(3)
        # ADD FROM MESSAGE
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]', "text",'BM-2cSsuH1bUWBski8bvdqnK2DivMqQCeQA1J')
        time.sleep(3)
        # CLICK BACK-BUTTON
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDIconButton[0]')
        time.sleep(5)
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        time.sleep(3)
        # SELECT - TO ADDRESS
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        time.sleep(1)
        self.cli.click_on('//MyTextInput[0]')
        time.sleep(3)
        # ADD FROM MESSAGE
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]', "text",'BM-2cSsuH1bUWBski8bvdqnK2DivMqQCeQA1J')
        time.sleep(4)
        random_label=""
        for char in "Another Draft message":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', random_label)
            time.sleep(0.2)
        # CLICK BACK-BUTTON
        self.cli.click_on('//MDToolbar/BoxLayout[0]/MDIconButton[0]')
        time.sleep(4)
   
    def test_edit_draft_messgae(self):
        """Select A Message From List of Messages Then
            make changes and send it."""
        print("=====================Test - Edit A Message From Draft Screen=====================")
        # OPEN NAVIGATION-DRAWER
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(4)
        # OPEN DRAFT SCREEN
        self.cli.click_on('//NavigationItem[3]')
        time.sleep(4)
        # SHOW DRAFT MESSAGE AND SELECT FIRST MESSAGE
        self.cli.click_on('//Carousel[0]//TwoLineAvatarIconListItem[0]')
        time.sleep(3)
        # CLICK EDIT BUTTON
        self.cli.click_on('//MDToolbar/BoxLayout[2]/MDIconButton[0]')
        time.sleep(5)
        random_label=""
        for char in "Hey,This is draft Message Body":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]', 'text', random_label)
            time.sleep(0.2)
        time.sleep(3)
        self.cli.click_on('//MDIconButton[2]')
        time.sleep(5)
        
    def test_delete_draft_message(self):
        """Delete A Message From List of Messages"""
        print("=====================Test - Delete A Message From List of Messages=====================")
        time.sleep(5)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(4)
        self.cli.click_on('//NavigationItem[3]')
        time.sleep(5)
        self.cli.click_on('//Carousel[0]//TwoLineAvatarIconListItem[0]')
        time.sleep(5)
        self.cli.click_on('//MDToolbar/BoxLayout[2]/MDIconButton[1]')
        time.sleep(2)
    
    def test_all_draft_method(self):
        """Calling All The Methods Draft Class"""
        self.test_select_draft_message()
        self.test_edit_draft_messgae()
        self.test_delete_draft_message()


if __name__ == '__main__':
    """Start Application"""
    obj = DraftMessage()
    obj.setUpClass()
    obj.test_all_draft_method()
