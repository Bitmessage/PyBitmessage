# from bitmessagekivy import identiconGeneration
from bitmessagekivy import kivy_helper_search
from bmconfigparser import BMConfigParser
from functools import partial
from helper_sql import sqlExecute
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import StringProperty, ListProperty

from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel

import state

from bitmessagekivy.baseclass.common import (
    showLimitedCnt, ThemeClsColor, avatarImageFirstLetter,
    toast, SwipeToDeleteItem, ShowTimeHistoy
)
from bitmessagekivy.baseclass.maildetail import MailDetail


class Sent(Screen):
    """Sent Screen class for kivy Ui"""
    # pylint: disable=unused-argument

    queryreturn = ListProperty()
    has_refreshed = True
    account = StringProperty()

    def __init__(self, *args, **kwargs):
        """Association with the screen"""
        super(Sent, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method sent accounts"""
        self.loadSent()
        print(dt)

    def loadSent(self, where="", what=""):
        """Load Sent list for Sent messages"""
        self.account = state.association
        if state.searcing_text:
            self.ids.scroll_y.scroll_y = 1.0
            where = ['subject', 'message']
            what = state.searcing_text
        xAddress = 'fromaddress'
        data = []
        self.ids.tag_label.text = ''
        self.sentDataQuery(xAddress, where, what)
        if self.queryreturn:
            self.ids.tag_label.text = 'Sent'
            self.set_sentCount(state.sent_count)
            for mail in self.queryreturn:
                data.append({
                    'text': mail[1].strip(),
                    'secondary_text': (mail[2][:50] + '........' if len(
                        mail[2]) >= 50 else (mail[2] + ',' + mail[3])[0:50] + '........').replace(
                            '\t', '').replace('  ', ''),
                    'ackdata': mail[5], 'senttime': mail[6]},)
            self.set_mdlist(data, 0)
            self.has_refreshed = True
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_sentCount('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="No message found!" if state.searcing_text
                else "yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def sentDataQuery(self, xAddress, where, what, start_indx=0, end_indx=20):  # pylint: disable=too-many-arguments
        """This method is used to retrieving data from sent table"""
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress,
            self.account,
            'sent',
            where,
            what,
            False,
            start_indx,
            end_indx)

    def set_mdlist(self, data, set_index=0):
        """This method is used to create the mdList"""
        total_sent_msg = len(self.ids.ml.children)
        for item in data:
            message_row = SwipeToDeleteItem(
                text=item["text"],
            )
            listItem = message_row.ids.content
            listItem.secondary_text = item["secondary_text"]
            listItem.theme_text_color = "Custom"
            listItem.text_color = ThemeClsColor
            image = state.imageDir + '/text_images/{}.png'.format(
                avatarImageFirstLetter(item['secondary_text'].strip()))
            message_row.ids.avater_img.source = image
            listItem.bind(on_release=partial(self.sent_detail, item['ackdata'], message_row))
            message_row.ids.time_tag.text = str(ShowTimeHistoy(item['senttime']))
            message_row.ids.delete_msg.bind(on_press=partial(self.delete, item["ackdata"]))
            self.ids.ml.add_widget(message_row, index=set_index)

        updated_msgs = len(self.ids.ml.children)
        self.has_refreshed = True if total_sent_msg != updated_msgs else False

    def update_sent_messagelist(self):
        """This method is used to update screen when new mail is sent"""
        self.account = state.association
        if len(self.ids.ml.children) < 3:
            self.ids.ml.clear_widgets()
            self.loadSent()
            if state.association == state.check_sent_acc:
                total_sent = int(state.sent_count) + 1
                state.sent_count = str(int(state.sent_count) + 1)
                self.set_sentCount(total_sent)
            else:
                total_sent = int(state.sent_count)
        else:
            data = []
            self.sentDataQuery('fromaddress', '', '', 0, 1)
            if state.association == state.check_sent_acc:
                total_sent = int(state.sent_count) + 1
                state.sent_count = str(int(state.sent_count) + 1)
                self.set_sentCount(total_sent)
            else:
                total_sent = int(state.sent_count)
            for mail in self.queryreturn:
                data.append({
                    'text': mail[1].strip(),
                    'secondary_text': (mail[2][:50] + '........' if len(
                        mail[2]) >= 50 else (mail[2] + ',' + mail[3])[0:50] + '........').replace(
                            '\t', '').replace('  ', ''),
                    'ackdata': mail[5], 'senttime': mail[6]})
            self.set_mdlist(data, total_sent - 1)
        if state.msg_counter_objs and state.association == (
                state.check_sent_acc):
            state.all_count = str(int(state.all_count) + 1)
            state.msg_counter_objs.allmail_cnt.badge_text = state.all_count
            state.check_sent_acc = None

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll down"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_sent_msg = len(self.ids.ml.children)
            self.update_sent_screen_on_scroll(total_sent_msg)

    def update_sent_screen_on_scroll(self, total_sent_msg, where="", what=""):
        """This method is used to load more data on scroll down"""
        if state.searcing_text:
            where = ['subject', 'message']
            what = state.searcing_text
        self.sentDataQuery('fromaddress', where, what, total_sent_msg, 5)
        data = []
        for mail in self.queryreturn:
            data.append({
                'text': mail[1].strip(),
                'secondary_text': mail[2][:50] + '........' if len(
                    mail[2]) >= 50 else (mail[2] + ',' + mail[3].replace(
                        '\n', ''))[0:50] + '........',
                'ackdata': mail[5], 'senttime': mail[6]})
        self.set_mdlist(data, 0)

    @staticmethod
    def set_sentCount(total_sent):
        """Set the total no. of sent message count"""
        src_mng_obj = state.kivyapp.root.ids.content_drawer.ids.send_cnt
        if state.association:
            src_mng_obj.ids.badge_txt.text = showLimitedCnt(int(total_sent))
        else:
            src_mng_obj.ids.badge_txt.text = '0'

    def sent_detail(self, ackdata, instance, *args):
        """Load sent mail details"""
        if instance.state == 'closed':
            instance.ids.delete_msg.disabled = True
            if instance.open_progress == 0.0:
                state.detailPageType = 'sent'
                state.mail_id = ackdata
                if self.manager:
                    src_mng_obj = self.manager
                else:
                    src_mng_obj = self.parent.parent
                src_mng_obj.screens[11].clear_widgets()
                src_mng_obj.screens[11].add_widget(MailDetail())
                src_mng_obj.current = 'mailDetail'
        else:
            instance.ids.delete_msg.disabled = False

    def delete(self, data_index, instance, *args):
        """Delete sent mail from sent mail listing"""
        msg_count_objs = self.parent.parent.ids.content_drawer.ids
        if int(state.sent_count) > 0:
            msg_count_objs.send_cnt.ids.badge_txt.text = showLimitedCnt(int(state.sent_count) - 1)
            msg_count_objs.trash_cnt.ids.badge_txt.text = showLimitedCnt(int(state.trash_count) + 1)
            msg_count_objs.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(state.all_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            state.trash_count = str(int(state.trash_count) + 1)
            state.all_count = str(int(state.all_count) - 1)
            if int(state.sent_count) <= 0:
                self.ids.tag_label.text = ''
        sqlExecute(
            "UPDATE sent SET folder = 'trash'"
            " WHERE ackdata = ?;", data_index)
        self.ids.ml.remove_widget(instance.parent.parent)
        toast('Deleted')

    def archive(self, data_index, instance, *args):
        """Archive sent mail from sent mail listing"""
        sqlExecute(
            "UPDATE sent SET folder = 'trash'"
            " WHERE ackdata = ?;", data_index)
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox"""
        try:
            self.parent.screens[3].clear_widgets()
            self.parent.screens[3].add_widget(Factory.Trash())
            # self.parent.screens[14].clear_widgets()
            # self.parent.screens[14].add_widget(Factory.Allmails())
        except Exception:
            self.parent.parent.screens[3].clear_widgets()
            self.parent.parent.screens[3].add_widget(Factory.Trash())
            # self.parent.parent.screens[14].clear_widgets()
            # self.parent.parent.screens[14].add_widget(Factory.Allmails())
