from bitmessagekivy.tests.telenium_process import TeleniumTestProcess
from .common import ordered

data = [
    'BM-2cWmjntZ47WKEUtocrdvs19y5CivpKoi1h',
    'BM-2cVpswZo8rWLXDVtZEUNcDQvnvHJ6TLRYr'
]


class SendMessage(TeleniumTestProcess):
    """Sent Screen Functionality Testing"""

    @ordered
    def test_send_message_and_validation(self):
        """
            Sending Message From Inbox Screen
            opens a pop-up(screen)which send message from sender to reciever
        """
        print("=====================Test - Sending Message From Inbox Screen with validation Checks=====================")
        self.cli.sleep(3)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(2)
        self.cli.click_on('//NavigationItem[1]')
        self.cli.sleep(2)
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        self.cli.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/MyMDTextField[0]')
        self.cli.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/MyTextInput[0]')
        self.cli.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/MyTextInput[0]', "text", "second add")
        self.cli.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]')
        self.cli.sleep(4)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]')
        self.cli.sleep(4)
        self.cli.click_on('//MDActionTopAppBarButton[2]')
        self.cli.sleep(3)
        self.cli.click_on('//MDFlatButton[0]')
        self.cli.sleep(5)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MyTextInput[0]')
        self.cli.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]')
        self.cli.sleep(2)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'heyyyyyy')
        self.cli.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]')
        self.cli.sleep(4)
        random_label=""
        for char in "how are you this is message body":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]','text',random_label)
            self.cli.sleep(0.2)
        self.cli.sleep(3)
        self.cli.click_on('//MDActionTopAppBarButton[2]')
        self.cli.sleep(3)
        self.cli.click_on('//MDFlatButton[0]')
        self.cli.sleep(6)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]',"text", data[0])
        self.cli.sleep(3)
        self.cli.click_on('//MDActionTopAppBarButton[2]')
        self.cli.sleep(3)

    @ordered   
    def test_sent_multiple_messages(self):
        """
            Sending Second Message From Inbox Screen
            for testing the search and delete functionality for two messages on the screen
        """
        print("=====================Test - Sending Message From Inbox Screen=====================")
        self.cli.sleep(3)
        # self.cli.execute('app.root.ids.nav_drawer.set_state("toggle")')
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(5)
        self.cli.click_on('//NavigationItem[1]')
        self.cli.sleep(3)
        self.cli.click_on('//Inbox/ComposerButton[0]/MDFloatingActionButton[0]')
        self.cli.sleep(3)
        self.cli.click_on('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[0]/BoxLayout[0]/CustomSpinner[0]/ArrowImg[0]')
        self.cli.sleep(2)
        self.cli.click_on('//MyTextInput[0]')
        self.cli.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/BoxLayout[1]/BoxLayout[0]/MyTextInput[0]', "text", data[0])
        self.cli.sleep(3)
        self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/MyMDTextField[0]', 'text', 'Second')
        self.cli.sleep(3)
        random_label=""
        for char in "Hey This Is Second Message Body":
            random_label += char
            self.cli.setattr('//DropDownWidget/ScrollView[0]/BoxLayout[0]/ScrollView[0]/TextInput[0]',"text",random_label)
            self.cli.sleep(0.2)
        self.cli.sleep(2)
        self.cli.click_on('//MDActionTopAppBarButton[2]')
        self.cli.sleep(5)
        self.cli.execute('app.clickNavDrawer()')
        self.cli.sleep(3)
        self.cli.click_on('//NavigationItem[2]')
        self.cli.sleep(3)
