from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel

from pybitmessage import state

from pybitmessage.baseclass.common import showLimitedCnt


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
            self.ids.scroll_y.scroll_y = 1.0
            where = ["subject", "message"]
            what = state.searcing_text
        xAddress = "toaddress"
        data = []
        self.ids.tag_label.text = ""
        if self.queryreturn:
            pass
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

    def check_scroll_y(self, instance, somethingelse):
        """Loads data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_message = len(self.ids.ml.children)
