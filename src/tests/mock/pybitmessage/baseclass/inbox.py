# from pybitmessage.get_platform import platform
# from pybitmessage import identiconGeneration

# from pybitmessage import kivy_helper_search
# from pybitmessage.bmconfigparser import BMConfigParser
from pybitmessage.helper_sql import sqlExecute
from functools import partial
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel

from pybitmessage import state

from common import (
    showLimitedCnt, avatarImageFirstLetter,
    ThemeClsColor, toast, SwipeToDeleteItem,
    ShowTimeHistoy
)
from maildetail import MailDetail
from trash import Trash


class Inbox(Screen):
    """Inbox Screen class for kivy Ui"""

    queryreturn = ListProperty()
    has_refreshed = True
    account = StringProperty()

    def __init__(self, *args, **kwargs):
        """Method Parsing the address"""
        super(Inbox, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    @staticmethod
    def set_defaultAddress():
        """This method set's default address"""
        if state.association == "":
            if state.kivyapp.variable_1:
                state.association = state.kivyapp.variable_1[0]

    def init_ui(self, dt=0):
        """Clock schdule for method inbox accounts"""
        self.loadMessagelist()

    def loadMessagelist(self, where="", what=""):
        """Load Inbox list for Inbox messages"""
        self.set_defaultAddress()
        self.account = state.association
        if state.searcing_text:
            # self.children[2].children[0].children[0].scroll_y = 1.0
            self.ids.scroll_y.scroll_y = 1.0
            where = ["subject", "message"]
            what = state.searcing_text
        xAddress = "toaddress"
        data = []
        self.ids.tag_label.text = ""
        self.inboxDataQuery(xAddress, where, what)
        self.ids.tag_label.text = ""
        if self.queryreturn:
            self.ids.tag_label.text = "Inbox"
            state.kivyapp.get_inbox_count()
            self.set_inboxCount(state.inbox_count)
            for mail in self.queryreturn:
                # third_text = mail[3].replace('\n', ' ')
                body = mail[3].decode() if isinstance(mail[3], bytes) else mail[3]
                subject = mail[5].decode() if isinstance(mail[5], bytes) else mail[5]
                data.append(
                    {
                        "text": mail[4].strip(),
                        "secondary_text": (
                            subject[:50] + "........"
                            if len(subject) >= 50
                            else (subject + "," + body)[0:50] + "........"
                        )
                        .replace("\t", "")
                        .replace("  ", ""),
                        "msgid": mail[1],
                        "received": mail[6]
                    }
                )

            self.has_refreshed = True
            self.set_mdList(data)
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_inboxCount("0")
            content = MDLabel(
                font_style="Caption",
                theme_text_color="Primary",
                text="No message found!"
                if state.searcing_text
                else "yet no message for this account!!!!!!!!!!!!!",
                halign="center",
                size_hint_y=None,
                valign="top"
            )
            self.ids.ml.add_widget(content)

    def set_inboxCount(self, msgCnt):  # pylint: disable=no-self-use
        """This method is used to sent inbox message count"""
        src_mng_obj = state.kivyapp.root.ids.content_drawer.ids
        src_mng_obj.inbox_cnt.ids.badge_txt.text = showLimitedCnt(int(msgCnt))
        state.kivyapp.get_sent_count()
        state.all_count = str(
            int(state.sent_count) + int(state.inbox_count))
        src_mng_obj.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(state.all_count))

    def inboxDataQuery(self, xAddress, where, what, start_indx=0, end_indx=20):
        """This method is used for retrieving inbox data"""
        # self.queryreturn = kivy_helper_search.search_sql(
        #     xAddress, self.account, "inbox", where, what, False, start_indx, end_indx
        # )
        pass

    def set_mdList(self, data):
        """This method is used to create the mdList"""
        total_message = len(self.ids.ml.children)
        for item in data:
            message_row = SwipeToDeleteItem(
                text=item["text"],
            )
            listItem = message_row.ids.content
            listItem.secondary_text = item["secondary_text"]
            listItem.theme_text_color = "Custom"
            listItem.text_color = ThemeClsColor
            listItem._txt_right_pad = dp(70)
            image = state.imageDir + "/text_images/{}.png".format(
                avatarImageFirstLetter(item["secondary_text"].strip()))
            message_row.ids.avater_img.source = image
            listItem.bind(on_release=partial(self.inbox_detail, item["msgid"], message_row))
            message_row.ids.time_tag.text = str(ShowTimeHistoy(item["received"]))
            message_row.ids.delete_msg.bind(on_press=partial(self.delete, item["msgid"]))
            self.ids.ml.add_widget(message_row)
        update_message = len(self.ids.ml.children)
        self.has_refreshed = True if total_message != update_message else False

    def check_scroll_y(self, instance, somethingelse):
        """Loads data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_message = len(self.ids.ml.children)
            self.update_inbox_screen_on_scroll(total_message)

    def update_inbox_screen_on_scroll(self, total_message, where="", what=""):
        """This method is used to load more data on scroll down"""
        data = []
        if state.searcing_text:
            where = ["subject", "message"]
            what = state.searcing_text
        self.inboxDataQuery("toaddress", where, what, total_message, 5)
        for mail in self.queryreturn:
            # third_text = mail[3].replace('\n', ' ')
            subject = mail[3].decode() if isinstance(mail[3], bytes) else mail[3]
            body = mail[5].decode() if isinstance(mail[5], bytes) else mail[5]
            data.append(
                {
                    "text": mail[4].strip(),
                    "secondary_text": body[:50] + "........"
                    if len(body) >= 50
                    else (body + "," + subject.replace("\n", ""))[0:50] + "........",
                    "msgid": mail[1],
                    "received": mail[6]
                }
            )
        self.set_mdList(data)

    def inbox_detail(self, msg_id, instance, *args):
        """Load inbox page details"""
        if instance.state == 'closed':
            instance.ids.delete_msg.disabled = True
            if instance.open_progress == 0.0:
                state.detailPageType = "inbox"
                state.mail_id = msg_id
                if self.manager:
                    src_mng_obj = self.manager
                else:
                    src_mng_obj = self.parent.parent
                src_mng_obj.screens[11].clear_widgets()
                src_mng_obj.screens[11].add_widget(MailDetail())
                src_mng_obj.current = "mailDetail"
        else:
            instance.ids.delete_msg.disabled = False

    def delete(self, data_index, instance, *args):
        """Delete inbox mail from inbox listing"""
        sqlExecute("UPDATE inbox SET folder = 'trash' WHERE msgid = ?;", data_index)
        msg_count_objs = self.parent.parent.ids.content_drawer.ids
        if int(state.inbox_count) > 0:
            msg_count_objs.inbox_cnt.ids.badge_txt.text = showLimitedCnt(
                int(state.inbox_count) - 1
            )
            msg_count_objs.trash_cnt.ids.badge_txt.text = showLimitedCnt(
                int(state.trash_count) + 1
            )
            state.inbox_count = str(int(state.inbox_count) - 1)
            state.trash_count = str(int(state.trash_count) + 1)
            if int(state.all_count) > 0:
                msg_count_objs.allmail_cnt.ids.badge_txt.text = showLimitedCnt(
                    int(state.all_count) - 1
                )
                state.all_count = str(int(state.all_count) - 1)

            if int(state.inbox_count) <= 0:
                # self.ids.identi_tag.children[0].text = ''
                self.ids.tag_label.text = ''
        self.ids.ml.remove_widget(
            instance.parent.parent)
        toast('Deleted')
        # self.update_trash()

    def archive(self, data_index, instance, *args):
        """Archive inbox mail from inbox listing"""
        sqlExecute("UPDATE inbox SET folder = 'trash' WHERE msgid = ?;", data_index)
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox"""
        self.manager.parent.ids.sc5.clear_widgets()
        self.manager.parent.ids.sc5.add_widget(Trash())
        # try:
        #     self.parent.screens[4].clear_widgets()
        #     self.parent.screens[4].add_widget(Trash())
        # except Exception:
        #     self.parent.parent.screens[4].clear_widgets()
        #     self.parent.parent.screens[4].add_widget(Trash())

    def refresh_callback(self, *args):
        """Method updates the state of application,
        While the spinner remains on the screen"""

        def refresh_callback(interval):
            """Method used for loading the inbox screen data"""
            state.searcing_text = ""
            self.children[2].children[1].ids.search_field.text = ""
            self.ids.ml.clear_widgets()
            self.loadMessagelist(state.association)
            self.has_refreshed = True
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)
