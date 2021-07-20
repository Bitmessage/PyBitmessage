from datetime import datetime
from os import wait
from socket import timeout
from time import sleep

from telenium.mods.telenium_client import selectFirst, kivythread, TeleniumMotionEvent, nextid, telenium_input, run_telenium

from .telenium_process import TeleniumTestProcess


class TrashMessage(TeleniumTestProcess):
    
    def smart_click(self, click_on, sleep):
        click_on = self.cli.click_on(click_on)
        sleep = self.cli.sleep(sleep)
        
    """Trash Screen Functionality Testing"""

    def test_delete_trash_message(self):
        """Delete Trash message permanently from trash message listing"""
        print("=====================Test -Delete Message From Trash Message Listing=====================")
        self.cli.sleep(8)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=2)
        # this is for opening Trash screen
        self.cli.wait_click('//NavigationItem[@text=\"Trash\"]', timeout=2)
        # self.cli.click_on('//NavigationItem[4]')
        # Checking Trash Screen
        self.assertExists("//Trash[@name~=\"trash\"]", timeout=5)
        # Transition Effect taking time, so halt is required 
        self.cli.sleep(2)
        # Checking Popup is closed
        self.assertEqual(self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]', '_opens_process'), False)
        # This is for swiping message to activate delete icon.
        self.drag(
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[1]',
            '//Trash[0]//TwoLineAvatarIconListItem[0]/BoxLayout[2]')
        # Checking Popup is Opened
        self.assertEqual(self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]', '_opens_process'), True)
        self.click_on('//MDList[0]/CutsomSwipeToDeleteItem[0]', seconds=1)
        # Checking the Trash Icon after swipe.
        self.assertExists("//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[@icon~=\"trash-can\"]", timeout=2)
        # clicking on Trash Box icon to delete message.
        self.cli.wait_click('//MDList[0]/CutsomSwipeToDeleteItem[0]//MDIconButton[0]', timeout=2)
        # Checking the popup box screen.
        self.assertExists("//MDDialog//MDFlatButton[@text=\"Yes\"]", timeout=2)
        # Clicking on 'Yes' Button on Popup to confirm delete.
        self.click_on('//MDFlatButton[@text=\"Yes\"]', seconds=1.1)
        # Checking Pop is closed
        self.assertEqual(self.cli.getattr('//MDList[0]/CutsomSwipeToDeleteItem[0]', '_opens_process'), False)
        # Checking Trash Screen
        self.assertExists("//Trash[@name~=\"trash\"]", timeout=2)
        total_trash_msgs = len(self.cli.select("//CutsomSwipeToDeleteItem"))
        # Checking the number of messages after delete.
        self.assertEqual(total_trash_msgs, 1)