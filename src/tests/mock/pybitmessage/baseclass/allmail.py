from functools import partial
from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel

from pybitmessage import state

from pybitmessage.baseclass.common import (
    showLimitedCnt, toast, ThemeClsColor,
    avatarImageFirstLetter, CutsomSwipeToDeleteItem,
    ShowTimeHistoy
)


class Allmails(Screen):
    """Allmails Screen for kivy Ui"""

    data = ListProperty()
    has_refreshed = True
    all_mails = ListProperty()
    account = StringProperty()

    def __init__(self, *args, **kwargs):
        """Method Parsing the address"""
        super(Allmails, self).__init__(*args, **kwargs)
        if state.association == '':
            if state.kivyapp.variable_1:
                state.association = state.kivyapp.variable_1[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method all mails"""
        self.loadMessagelist()
        print(dt)

    def loadMessagelist(self):
        """Load Inbox, Sent anf Draft list of messages"""
        self.account = state.association
        self.ids.tag_label.text = ''
        if self.all_mails:
            pass
        else:
            self.set_AllmailCnt('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def set_AllmailCnt(self, Count):  # pylint: disable=no-self-use
        """This method is used to set allmails message count"""
        allmailCnt_obj = state.kivyapp.root.ids.content_drawer.ids.allmail_cnt
        allmailCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    def set_mdlist(self):
        """This method is used to create mdList for allmaills"""
        data_exist = len(self.ids.ml.children)
        for item in self.all_mails:
            body = item[3].decode() if isinstance(item[3], bytes) else item[3]
            subject = item[2].decode() if isinstance(item[2], bytes) else item[2]
            message_row = CutsomSwipeToDeleteItem(
                text=item[1],
            )

            listItem = message_row.ids.content
            secondary_text = (subject[:50] + '........' if len(
                subject) >= 50 else (
                    subject + ',' + body)[0:50] + '........').replace('\t', '').replace('  ', '')
            listItem.secondary_text = secondary_text
            listItem.theme_text_color = "Custom"
            listItem.text_color = ThemeClsColor
            img_latter = state.imageDir + '/text_images/{}.png'.format(
                avatarImageFirstLetter(body.strip()))
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

    def mail_detail(self, unique_id, folder, instance, *args):
        """Load sent and inbox mail details"""
        if instance.state == 'closed':
            instance.ids.delete_msg.disabled = True
            if instance.open_progress == 0.0:
                state.detailPageType = folder
                state.is_allmail = True
                state.mail_id = unique_id
                if self.manager:
                    src_mng_obj = self.manager
                else:
                    src_mng_obj = self.parent.parent
                src_mng_obj.screens[11].clear_widgets()
                src_mng_obj.current = 'mailDetail'
        else:
            instance.ids.delete_msg.disabled = False

    def swipe_delete(self, unique_id, folder, instance, *args):
        """Delete inbox mail from all mail listing"""
        self.ids.ml.remove_widget(instance.parent.parent)
        try:
            msg_count_objs = self.parent.parent.ids.content_drawer.ids
            nav_lay_obj = self.parent.parent.ids
        except Exception:
            msg_count_objs = self.parent.parent.parent.ids.content_drawer.ids
            nav_lay_obj = self.parent.parent.parent.ids
        if folder == 'inbox':
            msg_count_objs.inbox_cnt.ids.badge_txt.text = showLimitedCnt(int(state.inbox_count) - 1)
            state.inbox_count = str(int(state.inbox_count) - 1)
            nav_lay_obj.sc1.ids.ml.clear_widgets()
            nav_lay_obj.sc1.loadMessagelist(state.association)
        else:
            msg_count_objs.send_cnt.ids.badge_txt.text = showLimitedCnt(int(state.sent_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            nav_lay_obj.sc4.ids.ml.clear_widgets()
            nav_lay_obj.sc4.loadSent(state.association)
        if folder != 'inbox':
            msg_count_objs.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(state.all_count) - 1)
            state.all_count = str(int(state.all_count) - 1)
        msg_count_objs.trash_cnt.ids.badge_txt.text = showLimitedCnt(int(state.trash_count) + 1)
        state.trash_count = str(int(state.trash_count) + 1)
        if int(state.all_count) <= 0:
            self.ids.tag_label.text = ''
        nav_lay_obj.sc17.remove_widget(instance.parent.parent)
        toast('Deleted')
