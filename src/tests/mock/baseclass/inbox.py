# pylint: disable=too-many-lines, import-error, no-name-in-module, unused-argument, no-init
# pylint: disable=too-many-ancestors, too-many-locals, useless-super-delegation, no-self-use
# pylint: disable=protected-access, super-with-arguments, pointless-statement, undefined-variable
# pylint: disable=import-outside-toplevel, ungrouped-imports, wrong-import-order, unused-import
# pylint: disable=invalid-name, unnecessary-comprehension, broad-except, simplifiable-if-expression
# pylint: disable=too-many-return-statements, unnecessary-pass, bad-option-value, old-style-class
# pylint: disable=no-else-return, unused-variable, attribute-defined-outside-init, no-method-argument
# pylint: disable=too-many-function-args, no-member, consider-using-in, abstract-method, exec-used
# pylint: disable=arguments-differ, too-few-public-methods, consider-using-f-string, useless-return
# pylint: disable=inconsistent-return-statements, missing-function-docstring, unspecified-encoding
# pylint: disable=too-many-arguments

"""
Kivy Inbox screen
"""

from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel

from pybitmessage import state
from pybitmessage import kivy_state

from baseclass.common import showLimitedCnt


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
        if kivy_state.association == "":
            if state.kivyapp.variable_1:
                kivy_state.association = state.kivyapp.variable_1[0]

    def init_ui(self, dt=0):
        """Clock schdule for method inbox accounts"""
        self.loadMessagelist()

    def loadMessagelist(self, where="", what=""):
        """Load Inbox list for Inbox messages"""
        self.set_defaultAddress()
        self.account = kivy_state.association
        if kivy_state.searcing_text:
            self.ids.scroll_y.scroll_y = 1.0
            where = ["subject", "message"]
            what = kivy_state.searcing_text
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
                if kivy_state.searcing_text
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
        kivy_state.all_count = str(
            int(kivy_state.sent_count) + int(kivy_state.inbox_count))
        src_mng_obj.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(kivy_state.all_count))

    def check_scroll_y(self, instance, somethingelse):
        """Loads data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_message = len(self.ids.ml.children)
