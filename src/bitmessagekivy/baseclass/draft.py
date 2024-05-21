# pylint: disable=unused-argument, import-error, too-many-arguments
# pylint: disable=unnecessary-comprehension, no-member, no-name-in-module

"""
draft.py
==============

Draft screen

"""
from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivy.app import App
from pybitmessage.bitmessagekivy.baseclass.common import (
    show_limited_cnt, empty_screen_label,
    kivy_state_variables
)
import logging
logger = logging.getLogger('default')


class Draft(Screen):
    """Draft screen class for kivy Ui"""

    data = ListProperty()
    account = StringProperty()
    queryreturn = ListProperty()
    has_refreshed = True
    label_str = "yet no message for this account!!!!!!!!!!!!!"

    def __init__(self, *args, **kwargs):
        """Method used for storing draft messages"""
        super(Draft, self).__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()
        if self.kivy_state.selected_address == '':
            if App.get_running_app().identity_list:
                self.kivy_state.selected_address = App.get_running_app().identity_list[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schedule for method draft accounts"""
        self.load_draft()
        logger.debug(dt)

    def load_draft(self, where="", what=""):
        """Load draft list for Draft messages"""
        self.set_draft_count('0')
        self.ids.ml.add_widget(empty_screen_label(self.label_str))

    @staticmethod
    def set_draft_count(Count):
        """Set the count of draft mails"""
        draftCnt_obj = App.get_running_app().root.ids.content_drawer.ids.draft_cnt
        draftCnt_obj.ids.badge_txt.text = show_limited_cnt(int(Count))
