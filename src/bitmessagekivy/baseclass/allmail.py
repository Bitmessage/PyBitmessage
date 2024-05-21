# pylint: disable=import-error, no-name-in-module
# pylint: disable=unused-argument, no-member, attribute-defined-outside-init

"""
allmail.py
==============

All mails are managed in allmail screen

"""

from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivy.app import App

from pybitmessage.bitmessagekivy.baseclass.common import (
    show_limited_cnt, empty_screen_label, kivy_state_variables,
)

import logging
logger = logging.getLogger('default')


class Allmails(Screen):
    """Allmails Screen for kivy Ui"""
    data = ListProperty()
    has_refreshed = True
    all_mails = ListProperty()
    account = StringProperty()
    label_str = 'yet no message for this account!!!!!!!!!!!!!'

    def __init__(self, *args, **kwargs):
        """Method Parsing the address"""
        super(Allmails, self).__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()
        if self.kivy_state.selected_address == '':
            if App.get_running_app().identity_list:
                self.kivy_state.selected_address = App.get_running_app().identity_list[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method all mails"""
        self.loadMessagelist()
        logger.debug(dt)

    def loadMessagelist(self):
        """Load Inbox, Sent anf Draft list of messages"""
        self.account = self.kivy_state.selected_address
        self.ids.tag_label.text = ''
        if self.all_mails:
            self.ids.tag_label.text = 'All Mails'
            self.kivy_state.all_count = str(
                int(self.kivy_state.sent_count) + int(self.kivy_state.inbox_count))
            self.set_AllmailCnt(self.kivy_state.all_count)
        else:
            self.set_AllmailCnt('0')
            self.ids.ml.add_widget(empty_screen_label(self.label_str))

    @staticmethod
    def set_AllmailCnt(Count):
        """This method is used to set allmails message count"""
        allmailCnt_obj = App.get_running_app().root.ids.content_drawer.ids.allmail_cnt
        allmailCnt_obj.ids.badge_txt.text = show_limited_cnt(int(Count))
