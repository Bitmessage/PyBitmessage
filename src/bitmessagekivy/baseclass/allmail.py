# pylint: disable=import-error, no-name-in-module
# pylint: disable=unused-argument, no-member, attribute-defined-outside-init

"""
allmail.py
==============

All mails are managed in allmail screen
"""

import logging

from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App

from pybitmessage.bitmessagekivy.baseclass.common import (
    show_limited_cnt, empty_screen_label, kivy_state_variables,
)

logger = logging.getLogger('default')


class AllMails(Screen):
    """AllMails Screen for Kivy UI"""
    data = ListProperty()
    has_refreshed = True
    all_mails = ListProperty()
    account = StringProperty()
    label_str = 'No messages for this account.'

    def __init__(self, *args, **kwargs):
        """Initialize the AllMails screen."""
        super().__init__(*args, **kwargs)  # pylint: disable=missing-super-argument
        self.kivy_state = kivy_state_variables()
        self._initialize_selected_address()
        Clock.schedule_once(self.init_ui, 0)

    def _initialize_selected_address(self):
        """Initialize the selected address from the identity list."""
        if not self.kivy_state.selected_address and App.get_running_app().identity_list:
            self.kivy_state.selected_address = App.get_running_app().identity_list[0]

    def init_ui(self, dt=0):
        """Initialize the UI by loading the message list."""
        self.load_message_list()
        logger.debug("UI initialized after %s seconds.", dt)

    def load_message_list(self):
        """Load the Inbox, Sent, and Draft message lists."""
        self.account = self.kivy_state.selected_address
        self.ids.tag_label.text = 'All Mails' if self.all_mails else ''
        self._update_mail_count()

    def _update_mail_count(self):
        """Update the mail count and handle empty states."""
        if self.all_mails:
            total_count = int(self.kivy_state.sent_count) + int(self.kivy_state.inbox_count)
            self.kivy_state.all_count = str(total_count)
            self.set_all_mail_count(self.kivy_state.all_count)
        else:
            self.set_all_mail_count('0')
            self.ids.ml.add_widget(empty_screen_label(self.label_str))

    @staticmethod
    def set_all_mail_count(count):
        """Set the message count for all mails."""
        allmail_count_widget = App.get_running_app().root.ids.content_drawer.ids.allmail_cnt
        allmail_count_widget.ids.badge_txt.text = show_limited_cnt(int(count))
