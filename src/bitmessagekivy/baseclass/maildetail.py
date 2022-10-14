# pylint: disable=unused-argument, consider-using-f-string, import-error, attribute-defined-outside-init
# pylint: disable=unnecessary-comprehension, no-member, no-name-in-module, too-few-public-methods

"""
Maildetail screen for inbox, sent, draft and trash.
"""

import os
from datetime import datetime

from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.properties import (
    StringProperty,
    NumericProperty
)
from kivy.uix.screenmanager import Screen
from kivy.factory import Factory
from kivy.app import App

from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (
    OneLineListItem,
    IRightBodyTouch
)

from pybitmessage.bitmessagekivy.baseclass.common import (
    toast, avatar_image_first_letter, show_time_history, kivy_state_variables
)
from pybitmessage.bitmessagekivy.baseclass.popup import SenderDetailPopup
from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.helper_sql import sqlQuery
from pybitmessage.helper_sent import delete, retrieve_message_details
from pybitmessage.helper_inbox import trash


class OneLineListTitle(OneLineListItem):
    """OneLineListTitle class for kivy Ui"""
    __events__ = ('on_long_press', )
    long_press_time = NumericProperty(1)

    def on_state(self, instance, value):
        """On state"""
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        """Do long press"""
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        """On long press"""
        self.copymessageTitle(self.text)

    def copymessageTitle(self, title_text):
        """this method is for displaying dialog box"""
        self.title_text = title_text
        width = .8 if platform == 'android' else .55
        self.dialog_box = MDDialog(
            text=title_text,
            size_hint=(width, .25),
            buttons=[
                MDFlatButton(
                    text="Copy", on_release=self.callback_for_copy_title
                ),
                MDFlatButton(
                    text="Cancel", on_release=self.callback_for_copy_title,
                ),
            ],)
        self.dialog_box.open()

    def callback_for_copy_title(self, instance):
        """Callback of alert box"""
        if instance.text == 'Copy':
            Clipboard.copy(self.title_text)
        self.dialog_box.dismiss()
        toast(instance.text)


class IconRightSampleWidget(IRightBodyTouch, MDIconButton):
    """IconRightSampleWidget class for kivy Ui"""


class MailDetail(Screen):  # pylint: disable=too-many-instance-attributes
    """MailDetail Screen class for kivy Ui"""

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
        """Mail Details method"""
        super(MailDetail, self).__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method MailDetail mails"""
        self.page_type = self.kivy_state.detail_page_type if self.kivy_state.detail_page_type else ''
        try:
            if self.kivy_state.detail_page_type in ('sent', 'draft'):
                data = retrieve_message_details(self.kivy_state.mail_id)
                self.assign_mail_details(data)
                App.get_running_app().set_mail_detail_header()
            elif self.kivy_state.detail_page_type == 'inbox':
                data = sqlQuery(
                    "select toaddress, fromaddress, subject, message, received from inbox"
                    " where msgid = ?", self.kivy_state.mail_id)
                self.assign_mail_details(data)
                App.get_running_app().set_mail_detail_header()
        except Exception as e:  # pylint: disable=unused-variable
            print('Something wents wrong!!')

    def assign_mail_details(self, data):
        """Assigning mail details"""
        subject = data[0][2].decode() if isinstance(data[0][2], bytes) else data[0][2]
        body = data[0][3].decode() if isinstance(data[0][2], bytes) else data[0][3]
        self.to_addr = data[0][0] if len(data[0][0]) > 4 else ' '
        self.from_addr = data[0][1]

        self.subject = subject.capitalize(
        ) if subject.capitalize() else self.no_subject
        self.message = body
        if len(data[0]) == 7:
            self.status = data[0][4]
        self.time_tag = show_time_history(data[0][4]) if self.kivy_state.detail_page_type == 'inbox' \
            else show_time_history(data[0][6])
        self.avatarImg = os.path.join(self.kivy_state.imageDir, 'draft-icon.png') \
            if self.kivy_state.detail_page_type == 'draft' \
            else (os.path.join(self.kivy_state.imageDir, 'text_images', '{0}.png'.format(avatar_image_first_letter(
                self.subject.strip()))))
        self.timeinseconds = data[0][4] if self.kivy_state.detail_page_type == 'inbox' else data[0][6]

    def delete_mail(self):
        """Method for mail delete"""
        msg_count_objs = App.get_running_app().root.ids.content_drawer.ids
        self.kivy_state.searching_text = ''
        self.children[0].children[0].active = True
        if self.kivy_state.detail_page_type == 'sent':
            App.get_running_app().root.ids.sc4.ids.sent_search.ids.search_field.text = ''
            delete(self.kivy_state.mail_id)
            msg_count_objs.send_cnt.ids.badge_txt.text = str(int(self.kivy_state.sent_count) - 1)
            self.kivy_state.sent_count = str(int(self.kivy_state.sent_count) - 1)
            self.parent.screens[2].ids.ml.clear_widgets()
            self.parent.screens[2].loadSent(self.kivy_state.association)
        elif self.kivy_state.detail_page_type == 'inbox':
            App.get_running_app().root.ids.id_inbox.ids.inbox_search.ids.search_field.text = ''
            trash(self.kivy_state.mail_id)
            msg_count_objs.inbox_cnt.ids.badge_txt.text = str(
                int(self.kivy_state.inbox_count) - 1)
            self.kivy_state.inbox_count = str(int(self.kivy_state.inbox_count) - 1)
            self.parent.screens[0].ids.ml.clear_widgets()
            self.parent.screens[0].loadMessagelist(self.kivy_state.association)

        elif self.kivy_state.detail_page_type == 'draft':
            delete(self.kivy_state.mail_id)
            msg_count_objs.draft_cnt.ids.badge_txt.text = str(
                int(self.kivy_state.draft_count) - 1)
            self.kivy_state.draft_count = str(int(self.kivy_state.draft_count) - 1)
            self.parent.screens[13].clear_widgets()
            self.parent.screens[13].add_widget(Factory.Draft())

        if self.kivy_state.detail_page_type != 'draft':
            msg_count_objs.trash_cnt.ids.badge_txt.text = str(
                int(self.kivy_state.trash_count) + 1)
            msg_count_objs.allmail_cnt.ids.badge_txt.text = str(
                int(self.kivy_state.all_count) - 1)
            self.kivy_state.trash_count = str(int(self.kivy_state.trash_count) + 1)
            self.kivy_state.all_count = str(int(self.kivy_state.all_count) - 1) if \
                int(self.kivy_state.all_count) else '0'
            self.parent.screens[3].clear_widgets()
            self.parent.screens[3].add_widget(Factory.Trash())
            self.parent.screens[14].clear_widgets()
            self.parent.screens[14].add_widget(Factory.Allmails())
        Clock.schedule_once(self.callback_for_delete, 4)

    def callback_for_delete(self, dt=0):
        """Delete method from allmails"""
        if self.kivy_state.detail_page_type:
            self.children[0].children[0].active = False
            App.get_running_app().set_common_header()
            self.parent.current = 'allmails' \
                if self.kivy_state.is_allmail else self.kivy_state.detail_page_type
            self.kivy_state.detail_page_type = ''
            toast('Deleted')

    def get_message_details_to_reply(self, data):
        """Getting message details and fill into fields when reply"""
        sender_address = ' wrote:--------------\n'
        message_time = '\n\n --------------On '
        composer_obj = self.parent.screens[1].children[1].ids
        composer_obj.ti.text = data[0][0]
        composer_obj.btn.text = data[0][0]
        composer_obj.txt_input.text = data[0][1]
        split_subject = data[0][2].split('Re:', 1)
        composer_obj.subject.text = 'Re: ' + (split_subject[1] if len(split_subject) > 1 else split_subject[0])
        time_obj = datetime.fromtimestamp(int(data[0][4]))
        time_tag = time_obj.strftime("%d %b %Y, %I:%M %p")
        sender_name = data[0][1]
        composer_obj.body.text = (
            message_time + time_tag + ', ' + sender_name + sender_address + data[0][3])
        composer_obj.body.focus = True
        composer_obj.body.cursor = (0, 0)

    def inbox_reply(self):
        """Reply inbox messages"""
        self.kivy_state.in_composer = True
        data = retrieve_message_details(self.kivy_state.mail_id)
        self.get_message_details_to_reply(data)
        App.get_running_app().root.ids.sc3.children[1].ids.rv.data = ''
        self.parent.current = 'create'
        App.get_running_app().set_navbar_for_composer()

    def get_message_details_for_draft_reply(self, data):
        """Getting and setting message details fill into fields when draft reply"""
        composer_ids = (
            self.parent.parent.ids.sc3.children[1].ids)
        composer_ids.ti.text = data[0][1]
        composer_ids.btn.text = data[0][1]
        composer_ids.txt_input.text = data[0][0]
        composer_ids.subject.text = data[0][2] if data[0][2] != self.no_subject else ''
        composer_ids.body.text = data[0][3]

    def write_msg(self, navApp):
        """Write on draft mail"""
        self.kivy_state.send_draft_mail = self.kivy_state.mail_id
        data = retrieve_message_details(self.kivy_state.mail_id)
        self.get_message_details_for_draft_reply(data)
        self.parent.current = 'create'
        navApp.set_navbar_for_composer()

    def detailedPopup(self):
        """Detailed popup"""
        obj = SenderDetailPopup()
        obj.open()
        arg = (self.to_addr, self.from_addr, self.timeinseconds)
        obj.assignDetail(*arg)

    @staticmethod
    def callback_for_menu_items(text_item, *arg):
        """Callback of alert box"""
        toast(text_item)
