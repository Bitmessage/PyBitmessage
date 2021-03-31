from bitmessagekivy.get_platform import platform
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from functools import partial
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.button import Button
from kivymd.uix.button import MDFlatButton
from kivy.uix.carousel import Carousel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivy.uix.screenmanager import Screen

import state

from bitmessagekivy.baseclass.common import (
    showLimitedCnt, avatarImageFirstLetter,
    AddTimeWidget, ThemeClsColor, AvatarSampleWidget
)

from bitmessagekivy.baseclass.common import (
    toast, showLimitedCnt, ThemeClsColor, chipTag,
    AddTimeWidget, AvatarSampleWidget
)


class Trash(Screen):
    """Trash Screen class for kivy Ui"""

    trash_messages = ListProperty()
    has_refreshed = True
    # delete_index = StringProperty()
    table_name = StringProperty()

    def __init__(self, *args, **kwargs):
        """Trash method, delete sent message and add in Trash"""
        super(Trash, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method trash screen"""
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        self.ids.tag_label.text = ''
        self.trashDataQuery(0, 20)
        if self.trash_messages:
            self.ids.tag_label.text = 'Trash'
            # src_mng_obj = state.kivyapp.root.children[2].children[0].ids
            # src_mng_obj.trash_cnt.badge_text = state.trash_count
            self.set_TrashCnt(state.trash_count)
            self.set_mdList()
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_TrashCnt('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="yet no trashed message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def trashDataQuery(self, start_indx, end_indx):
        """Trash message query"""
        self.trash_messages = sqlQuery(
            "SELECT toaddress, fromaddress, subject, message,"
            " folder ||',' || 'sent' as  folder, ackdata As"
            " id, DATE(senttime) As actionTime, senttime as msgtime FROM sent"
            " WHERE folder = 'trash'  and fromaddress = '{0}' UNION"
            " SELECT toaddress, fromaddress, subject, message,"
            " folder ||',' || 'inbox' as  folder, msgid As id,"
            " DATE(received) As actionTime, received as msgtime FROM inbox"
            " WHERE folder = 'trash' and toaddress = '{0}'"
            " ORDER BY actionTime DESC limit {1}, {2}".format(
                state.association, start_indx, end_indx))

    def set_TrashCnt(self, Count):  # pylint: disable=no-self-use
        """This method is used to set trash message count"""
        trashCnt_obj = state.kivyapp.root.ids.content_drawer.ids.trash_cnt
        trashCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    def set_mdList(self):
        """This method is used to create the mdlist"""
        total_trash_msg = len(self.ids.ml.children)
        for item in self.trash_messages:
            subject = item[2].decode() if isinstance(item[2], bytes) else item[2]
            body = item[3].decode() if isinstance(item[3], bytes) else item[3]
            meny = TwoLineAvatarIconListItem(
                text=item[1],
                secondary_text=(item[2][:50] + '........' if len(
                    subject) >= 50 else (subject + ',' + body)[0:50] + '........').replace('\t', '').replace('  ', ''),
                theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny._txt_right_pad = dp(70)
            img_latter = state.imageDir + '/text_images/{}.png'.format(
                subject[0].upper() if (subject[0].upper() >= 'A' and subject[0].upper() <= 'Z') else '!')
            meny.add_widget(AvatarSampleWidget(source=img_latter))
            meny.add_widget(AddTimeWidget(item[7]))
            meny.add_widget(chipTag('inbox 'if 'inbox' in item[4] else 'sent'))
            carousel = Carousel(direction='right')
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text='Delete')
            del_btn.background_normal = ''
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(
                self.delete_permanently, item[5], item[4]))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            carousel.index = 1
            self.ids.ml.add_widget(carousel)
        self.has_refreshed = True if total_trash_msg != len(
            self.ids.ml.children) else False

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_trash_msg = len(self.ids.ml.children)
            self.update_trash_screen_on_scroll(total_trash_msg)

    def update_trash_screen_on_scroll(self, total_trash_msg):
        """Load more data on scroll down"""
        self.trashDataQuery(total_trash_msg, 5)
        self.set_mdList()

    def delete_permanently(self, data_index, folder, instance, *args):
        """Deleting trash mail permanently"""
        self.table_name = folder.split(',')[1]
        self.delete_index = data_index
        self.delete_confirmation()

    def callback_for_screen_load(self, dt=0):
        """This methos is for loading screen"""
        self.ids.ml.clear_widgets()
        self.init_ui(0)
        self.children[1].active = False
        toast('Message is permanently deleted')

    def delete_confirmation(self):
        """Show confirmation delete popup"""
        width = .8 if platform == 'android' else .55
        dialog_box = MDDialog(
            text='Are you sure you want to delete this'
            ' message permanently from trash?',
            size_hint=(width, .25),
            buttons=[
                MDFlatButton(
                    text="Yes", on_release=lambda x: callback_for_delete_msg("Yes")
                ),
                MDFlatButton(
                    text="No", on_release=lambda x: callback_for_delete_msg("No"),
                ),
            ],)
        dialog_box.open()

        def callback_for_delete_msg(text_item, *arg):
            """Getting the callback of alert box"""
            if text_item == 'Yes':
                self.delete_message_from_trash()
            else:
                toast(text_item)
            dialog_box.dismiss()

    # def callback_for_delete_msg(self, text_item, *arg):
    #     """Getting the callback of alert box"""
    #     if text_item == 'Yes':
    #         self.delete_message_from_trash()
    #     else:
    #         toast(text_item)

    def delete_message_from_trash(self):
        """Deleting message from trash"""
        self.children[1].active = True
        if self.table_name == 'inbox':
            sqlExecute(
                "DELETE FROM inbox WHERE msgid = ?;", self.delete_index)
        elif self.table_name == 'sent':
            sqlExecute(
                "DELETE FROM sent WHERE ackdata = ?;", self.delete_index)
        if int(state.trash_count) > 0:
            # msg_count_objs.trash_cnt.badge_text = str(
            #     int(state.trash_count) - 1)
            self.set_TrashCnt(int(state.trash_count) - 1)
            state.trash_count = str(int(state.trash_count) - 1)
            Clock.schedule_once(self.callback_for_screen_load, 1)
