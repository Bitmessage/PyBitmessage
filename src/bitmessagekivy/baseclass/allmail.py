# pylint: disable=import-error, no-name-in-module
# pylint: disable=unused-argument, no-member, attribute-defined-outside-init

"""
allmail.py
==============

All mails are managed in allmail screen

"""

import os
from functools import partial

from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivy.app import App

import helper_inbox
import helper_sent

from bitmessagekivy.baseclass.common import (
    showLimitedCnt, toast, ThemeClsColor, mail_detail_screen,
    avatarImageFirstLetter, CustomSwipeToDeleteItem,
    ShowTimeHistoy, empty_screen_label, kivy_state_variables
)

from debug import logger
from helper_sql import sqlQuery


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
        if self.kivy_state.association == '':
            if App.get_running_app().variable_1:
                self.kivy_state.association = App.get_running_app().variable_1[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method all mails"""
        self.loadMessagelist()
        logger.debug(dt)

    def loadMessagelist(self):
        """Load Inbox, Sent anf Draft list of messages"""
        self.account = self.kivy_state.association
        self.ids.tag_label.text = ''
        self.allMessageQuery(0, 20)
        if self.all_mails:
            self.ids.tag_label.text = 'All Mails'
            App.get_running_app().get_inbox_count()
            App.get_running_app().get_sent_count()
            self.kivy_state.all_count = str(
                int(self.kivy_state.sent_count) + int(self.kivy_state.inbox_count))
            self.set_AllmailCnt(self.kivy_state.all_count)
            self.set_mdlist()
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_AllmailCnt('0')
            self.ids.ml.add_widget(empty_screen_label(self.label_str))

    def allMessageQuery(self, start_indx, end_indx):
        """Retrieving data from inbox or sent both tables"""
        self.all_mails = sqlQuery(
            "SELECT toaddress, fromaddress, subject, message, folder, ackdata"
            " As id, DATE(senttime) As actionTime, senttime as msgtime FROM sent WHERE"
            " folder = 'sent' and fromaddress = ?"
            " UNION SELECT toaddress, fromaddress, subject, message, folder,"
            " msgid As id, DATE(received) As actionTime, received as msgtime FROM inbox"
            " WHERE folder = 'inbox' and toaddress = ?"
            " ORDER BY actionTime DESC limit ?, ?", self.account, self.account, start_indx, end_indx)

    @staticmethod
    def set_AllmailCnt(Count):
        """This method is used to set allmails message count"""
        allmailCnt_obj = App.get_running_app().root.ids.content_drawer.ids.allmail_cnt
        allmailCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    @staticmethod
    def msg_content_length(body, subject, max_length=50):
        """This function concatinate body and subject if len(subject) > 50 characters"""
        continue_str = '........'
        if len(subject) >= max_length:
            subject = subject[:max_length] + continue_str
        else:
            subject = ((subject + ',' + body)[0:max_length] + continue_str).replace('\t', '').replace('  ', '')
        return subject

    def set_mdlist(self):
        """This method is used to create mdList for allmaills"""
        data_exist = len(self.ids.ml.children)
        for item in self.all_mails:
            body = item[3].decode() if isinstance(item[3], bytes) else item[3]
            subject = item[2].decode() if isinstance(item[2], bytes) else item[2]
            message_row = CustomSwipeToDeleteItem(
                text=item[1],
            )
            listItem = message_row.ids.content
            secondary_text = self.msg_content_length(body, subject)
            listItem.secondary_text = secondary_text
            listItem.theme_text_color = "Custom"
            listItem.text_color = ThemeClsColor
            img_latter = os.path.join(self.kivy_state.imageDir, "text_images", "{}.png".format(
                avatarImageFirstLetter(body.strip())))
            message_row.ids.avater_img.source = img_latter
            listItem.bind(on_release=partial(
                self.mail_detail, item[5], item[4], message_row))
            message_row.ids.time_tag.text = str(ShowTimeHistoy(item[7]))
            message_row.ids.chip_tag.text = item[4]
            message_row.ids.delete_msg.bind(on_press=partial(
                self.swipe_delete, item[5], item[4]))
            self.ids.ml.add_widget(message_row)
        updated_data = len(self.ids.ml.children)
        self.has_refreshed = True if data_exist != updated_data else False

    def check_scroll_y(self, instance, somethingelse):
        """Scroll fixed length"""
        if self.ids.scroll_y.scroll_y <= -0.00 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = .06
            load_more = len(self.ids.ml.children)
            self.updating_allmail(load_more)

    def updating_allmail(self, load_more):
        """This method is used to update the all mail
        listing value on the scroll of screen"""
        self.allMessageQuery(load_more, 5)
        self.set_mdlist()

    def mail_detail(self, unique_id, folder, instance, *args):
        """Load sent and inbox mail details"""
        if instance.state == 'closed':
            instance.ids.delete_msg.disabled = True
            self.kivy_state.is_allmail = True
            mail_detail_screen(self, unique_id, instance, folder, *args)
        else:
            instance.ids.delete_msg.disabled = False

    def swipe_delete(self, unique_id, folder, instance, *args):
        """Delete inbox mail from all mail listing"""
        if folder == 'inbox':
            helper_inbox.trash(unique_id)  # msgid
        else:
            helper_sent.delete(unique_id)  # ackdata
        self.ids.ml.remove_widget(instance.parent.parent)
        try:
            msg_count_objs = self.parent.parent.ids.content_drawer.ids
            nav_lay_obj = self.parent.parent.ids
        except Exception:
            msg_count_objs = self.parent.parent.parent.ids.content_drawer.ids
            nav_lay_obj = self.parent.parent.parent.ids
        if folder == 'inbox':
            msg_count_objs.inbox_cnt.ids.badge_txt.text = showLimitedCnt(int(self.kivy_state.inbox_count) - 1)
            self.kivy_state.inbox_count = str(int(self.kivy_state.inbox_count) - 1)
            nav_lay_obj.sc1.ids.ml.clear_widgets()
            nav_lay_obj.sc1.loadMessagelist(self.kivy_state.association)
        else:
            msg_count_objs.send_cnt.ids.badge_txt.text = showLimitedCnt(int(self.kivy_state.sent_count) - 1)
            self.kivy_state.sent_count = str(int(self.kivy_state.sent_count) - 1)
            nav_lay_obj.sc4.ids.ml.clear_widgets()
            nav_lay_obj.sc4.loadSent(self.kivy_state.association)
        if folder != 'inbox':
            msg_count_objs.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(self.kivy_state.all_count) - 1)
            self.kivy_state.all_count = str(int(self.kivy_state.all_count) - 1)
        msg_count_objs.trash_cnt.ids.badge_txt.text = showLimitedCnt(int(self.kivy_state.trash_count) + 1)
        self.kivy_state.trash_count = str(int(self.kivy_state.trash_count) + 1)
        if int(self.kivy_state.all_count) <= 0:
            self.ids.tag_label.text = ''
        nav_lay_obj.sc17.remove_widget(instance.parent.parent)
        toast('Deleted')

    def refresh_callback(self, *args):
        """Method updates the state of application,
        While the spinner remains on the screen"""
        def refresh_callback(interval):
            """Load the allmails screen data"""
            self.ids.ml.clear_widgets()
            self.remove_widget(self.children[1])
            try:
                screens_obj = self.parent.screens[16]
            except Exception:
                screens_obj = self.parent.parent.screens[16]
            screens_obj.add_widget(Allmails())
            self.ids.refresh_layout.refresh_done()
            self.tick = 0
        Clock.schedule_once(refresh_callback, 1)
