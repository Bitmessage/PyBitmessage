# pylint: disable=unused-argument, consider-using-f-string, import-error, attribute-defined-outside-init
# pylint: disable=unnecessary-comprehension, no-member, no-name-in-module, too-few-public-methods

"""
MailDetail screen for inbox, sent, draft, and trash.
"""

import os
from datetime import datetime
import logging

from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.factory import Factory
from kivy.app import App

from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, IRightBodyTouch

from pybitmessage.bitmessagekivy.baseclass.common import (
    toast, avatar_image_first_letter, show_time_history, kivy_state_variables
)
from pybitmessage.bitmessagekivy.baseclass.popup import SenderDetailPopup
from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.helper_sql import sqlQuery


class OneLineListTitle(OneLineListItem):
    """OneLineListTitle class for Kivy UI."""
    __events__ = ('on_long_press', )
    long_press_time = NumericProperty(1)

    def on_state(self, instance, value):
        """Handle state change for long press."""
        if value == 'down':
            self._clock_event = Clock.schedule_once(self._do_long_press, self.long_press_time)
        else:
            self._clock_event.cancel()

    def _do_long_press(self, dt):
        """Trigger the long press event."""
        self.dispatch('on_long_press')

    def on_long_press(self, *args):
        """Handle long press and display message title."""
        self.copy_message_title(self.text)

    def copy_message_title(self, title_text):
        """Display dialog box with options to copy the message title."""
        self.title_text = title_text
        width = 0.8 if platform == 'android' else 0.55
        self.dialog_box = MDDialog(
            text=title_text,
            size_hint=(width, 0.25),
            buttons=[
                MDFlatButton(text="Copy", on_release=self.copy_title_callback),
                MDFlatButton(text="Cancel", on_release=self.copy_title_callback),
            ],
        )
        self.dialog_box.open()

    def copy_title_callback(self, instance):
        """Handle dialog box button callback."""
        if instance.text == 'Copy':
            Clipboard.copy(self.title_text)
        self.dialog_box.dismiss()
        toast(instance.text)


class IconRightSampleWidget(IRightBodyTouch, MDIconButton):
    """IconRightSampleWidget class for Kivy UI."""

class MailDetail(Screen):  # pylint: disable=too-many-instance-attributes
    """MailDetail Screen class for Kivy UI."""

    to_addr = StringProperty()
    from_addr = StringProperty()
    subject = StringProperty()
    message = StringProperty()
    status = StringProperty()
    page_type = StringProperty()
    time_tag = StringProperty()
    avatarImg = StringProperty()
    no_subject = '(no subject)'

    def __init__(self, *args, **kwargs):
        """Initialize MailDetail screen."""
        super().__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Initialize UI elements based on page type."""
        self.page_type = self.kivy_state.detail_page_type or ''
        try:
            if self.page_type in ('sent', 'draft'):
                App.get_running_app().set_mail_detail_header()
            elif self.page_type == 'inbox':
                data = sqlQuery(
                    "SELECT toaddress, fromaddress, subject, message, received FROM inbox "
                    "WHERE msgid = ?", self.kivy_state.mail_id
                )
                self.assign_mail_details(data)
                App.get_running_app().set_mail_detail_header()
        except Exception:
            print('Something went wrong!')

    def assign_mail_details(self, data):
        """Assign mail details from query result."""
        subject = data[0][2].decode() if isinstance(data[0][2], bytes) else data[0][2]
        body = data[0][3].decode() if isinstance(data[0][3], bytes) else data[0][3]
        self.to_addr = data[0][0] if len(data[0][0]) > 4 else ' '
        self.from_addr = data[0][1]

        self.subject = subject.capitalize() or self.no_subject
        self.message = body
        if len(data[0]) == 7:
            self.status = data[0][4]
        self.time_tag = show_time_history(data[0][4]) if self.page_type == 'inbox' else show_time_history(data[0][6])
        self.avatarImg = (
            os.path.join(self.kivy_state.image_dir, 'draft-icon.png')
            if self.page_type == 'draft'
            else os.path.join(self.kivy_state.image_dir, 'text_images', f'{avatar_image_first_letter(self.subject.strip())}.png')  # noqa: E999
        )
        self.timeinseconds = data[0][4] if self.page_type == 'inbox' else data[0][6]

    def delete_mail(self):
        """Delete the current mail and update UI."""
        msg_count_objs = App.get_running_app().root.ids.content_drawer.ids
        self.kivy_state.searching_text = ''
        self.children[0].children[0].active = True

        if self.page_type == 'sent':
            self._update_sent_mail(msg_count_objs)
        elif self.page_type == 'inbox':
            self._update_inbox_mail(msg_count_objs)
        elif self.page_type == 'draft':
            self._update_draft_mail(msg_count_objs)

        if self.page_type != 'draft':
            self._update_mail_counts(msg_count_objs)

        Clock.schedule_once(self.callback_for_delete, 4)
    
    #created separate function for more readablity and maintanence

    def _update_sent_mail(self, msg_count_objs):
        """Update UI for sent mail."""
        App.get_running_app().root.ids.id_sent.ids.sent_search.ids.search_field.text = ''
        msg_count_objs.send_cnt.ids.badge_txt.text = str(int(self.kivy_state.sent_count) - 1)
        self.kivy_state.sent_count = str(int(self.kivy_state.sent_count) - 1)
        self.parent.screens[2].ids.ml.clear_widgets()
        self.parent.screens[2].loadSent(self.kivy_state.selected_address)

    def _update_inbox_mail(self, msg_count_objs):
        """Update UI for inbox mail."""
        App.get_running_app().root.ids.id_inbox.ids.inbox_search.ids.search_field.text = ''
        msg_count_objs.inbox_cnt.ids.badge_txt.text = str(int(self.kivy_state.inbox_count) - 1)
        self.kivy_state.inbox_count = str(int(self.kivy_state.inbox_count) - 1)
        self.parent.screens[0].ids.ml.clear_widgets()
        self.parent.screens[0].loadMessagelist(self.kivy_state.selected_address)

    def _update_draft_mail(self, msg_count_objs):
        """Update UI for draft mail."""
        msg_count_objs.draft_cnt.ids.badge_txt.text = str(int(self.kivy_state.draft_count) - 1)
        self.kivy_state.draft_count = str(int(self.kivy_state.draft_count) - 1)
        self.parent.screens[13].clear_widgets()
        self.parent.screens[13].add_widget(Factory.Draft())

    def _update_mail_counts(self, msg_count_objs):
        """Update mail counts and refresh relevant screens."""
        msg_count_objs.trash_cnt.ids.badge_txt.text = str(int(self.kivy_state.trash_count) + 1)
        msg_count_objs.allmail_cnt.ids.badge_txt.text = str(int(self.kivy_state.all_count) - 1)
        self.kivy_state.trash_count = str(int(self.kivy_state.trash_count) + 1)
        self.kivy_state.all_count = str(int(self.kivy_state.all_count) - 1) if int(self.kivy_state.all_count) else '0'
        self.parent.screens[3].clear_widgets()
        self.parent.screens[3].add_widget(Factory.Trash())
        self.parent.screens[14].clear_widgets()
        self.parent.screens[14].add_widget(Factory.AllMails())

    def callback_for_delete(self, dt=0):
        """Handle post-deletion operations."""
        if self.page_type:
            self.children[0].children[0].active = False
            App.get_running_app().set_common_header()
            self.parent.current = 'allmails' if self.kivy_state.is_allmail else self.page_type
            self.kivy_state.detail_page_type = ''
            toast('Deleted')

    def get_message_details_to_reply(self, data):
        """Prepare message details for reply."""
        sender_address = ' wrote:--------------\n'
        message_time = '\n\n --------------On '
        composer_obj = self.parent.screens[1].children[1].ids
        composer_obj.ti.text = data[0][0]
        composer_obj.composer_dropdown.text = data[0][0]
        composer_obj.txt_input.text = data[0][1]
        split_subject = data[0][2].split('Re:', 1)
        composer_obj.subject.text = 'Re: ' + (split_subject[1] if len(split_subject) > 1 else split_subject[0])
        time_obj = datetime.fromtimestamp(int(data[0][4]))
        time_tag = time_obj.strftime("%d %b %Y, %I:%M %p")
        sender_name = data[0][1]
        composer_obj.body.text = (
            message_time + time_tag + ', ' + sender_name + sender_address + data[0][3]
        )
        composer_obj.body.focus = True
        composer_obj.body.cursor = (0, 0)

    def inbox_reply(self):
        """Prepare for replying to an inbox message."""
        self.kivy_state.in_composer = True
        App.get_running_app().root.ids.id_create.children[1].ids.rv.data = ''
        App.get_running_app().root.ids.sc3.children[1].ids.rv.data = ''
        self.parent.current = 'create'
        App.get_running_app().set_navbar_for_composer()

    def get_message_details_for_draft_reply(self, data):
        """Prepare message details for a draft reply."""
        composer_ids = self.parent.parent.ids.id_create.children[1].ids
        composer_ids.ti.text = data[0][1]
        composer_ids.btn.text = data[0][1]
        composer_ids.txt_input.text = data[0][0]
        composer_ids.subject.text = data[0][2] if data[0][2] != self.no_subject else ''
        composer_ids.body.text = data[0][3]

    def write_msg(self, navApp):
        """Switch to draft mail composition."""
        self.kivy_state.send_draft_mail = self.kivy_state.mail_id
        self.parent.current = 'create'
        navApp.set_navbar_for_composer()

    def detailedPopup(self):
        """Show detailed sender information popup."""
        obj = SenderDetailPopup()
        obj.open()
        obj.assignDetail(self.to_addr, self.from_addr, self.timeinseconds)

    @staticmethod
    def callback_for_menu_items(text_item, *args):
        """Handle menu item callback."""
        toast(text_item)
