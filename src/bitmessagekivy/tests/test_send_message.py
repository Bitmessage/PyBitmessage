import time
from bmconfigparser import BMConfigParser
from telenium.tests import TeleniumTestCase


class SendMessage(TeleniumTestCase):
    """Sent Screen Functionality Testing"""

    def runTest(self):
        print(self,"-------------Welcome To Kivy Testing Application Thirds Page-------------")

    def test_select_sent(self):
        """Sending Message From Inbox Screen
        opens a pop-up(screen)which send message from sender to reciever"""
        print("=====================Test - Sending Message From Inbox Screen=====================")
        time.sleep(2)
        self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        time.sleep(1)
        self.cli.click_on('//NavigationItem[1]')
        time.sleep(1)
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        time.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/MyMDTextField[0]')
        time.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/MyTextInput[0]')
        time.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/MyTextInput[0]', "text", "second add")
        time.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]')
        time.sleep(4)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]')
        time.sleep(4)
        self.cli.click_on('//MDIconButton[2]')
        time.sleep(3)
        self.cli.click_on('//MDFlatButton[0]')
        time.sleep(5)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        time.sleep(2)
        self.cli.click_on('//MyTextInput[0]')
        time.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]')
        time.sleep(2)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'heyyyyyy')
        time.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]')
        time.sleep(4)
        random_label=""
        for char in "how are you this is message body":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]','text',random_label)
            time.sleep(0.2)
        time.sleep(3)
        self.cli.click_on('//MDIconButton[2]')
        time.sleep(3)
        self.cli.click_on('//MDFlatButton[0]')
        time.sleep(6)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]',"text",data[0])
        time.sleep(3)
        self.cli.click_on('//MDIconButton[2]')
        time.sleep(3)
        self.cli.click_on('//MDFlatButton[0]')
        time.sleep(3)       
   
    def test_sent_multiple_message(self):
        """Sending Second Message From Inbox Screen
        for testing the search and delete functionality for two messages on the screen"""
        print("=====================Test - Sending Message From Inbox Screen=====================")
        time.sleep(3)
        self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        time.sleep(5)
        self.cli.click_on('//NavigationItem[1]')
        time.sleep(3)
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        time.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        time.sleep(2)
        self.cli.click_on('//MyTextInput[0]')
        time.sleep(3)
        data = BMConfigParser().addresses()
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]', "text", data[0])
        time.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'Second')
        time.sleep(3)
        random_label=""
        for char in "Hey This Is Second Message Body":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]',"text",random_label)
            time.sleep(0.2)
        time.sleep(2)
        self.cli.click_on('//MDIconButton[2]')
        time.sleep(5)
        self.cli.execute('app.clickNavDrawer()')
        time.sleep(3)
        self.cli.click_on('//NavigationItem[2]')
        time.sleep(3)


if __name__ == '__main__':
    """Start Application"""
    TeleniumTestCase.start_process()
    obj = SendMessage()
    obj.test_select_sent()
    obj.test_sent_multiple_message()
