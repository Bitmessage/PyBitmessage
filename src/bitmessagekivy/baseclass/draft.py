# pylint: disable=unused-argument, import-error, too-many-arguments
# pylint: disable=unnecessary-comprehension, no-member, no-name-in-module

"""
draft.py
==============

Draft screen for managing draft messages in Kivy UI.
"""
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App
from pybitmessage.bitmessagekivy.baseclass.common import (
    show_limited_cnt, empty_screen_label, kivy_state_variables
)
import logging

logger = logging.getLogger('default')


class Draft(Screen):
    """Draft screen class for Kivy UI"""

    data = ListProperty()
    account = StringProperty()
    queryreturn = ListProperty()
    has_refreshed = True
    label_str = "Yet no message for this account!"

    def __init__(self, *args, **kwargs):
        """Initialize the Draft screen and set the default account"""
        super().__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()
        if not self.kivy_state.selected_address:
            if App.get_running_app().identity_list:
                self.kivy_state.selected_address = App.get_running_app().identity_list[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Initialize the UI and load draft messages"""
        self.load_draft()
        logger.debug(f"UI initialized with dt: {dt}")  # noqa: E999

    def load_draft(self, where="", what=""):
        """Load the list of draft messages"""
        self.set_draft_count('0')
        self.ids.ml.add_widget(empty_screen_label(self.label_str))

    @staticmethod
    def set_draft_count(count):
        """Set the count of draft messages in the UI"""
        draft_count_obj = App.get_running_app().root.ids.content_drawer.ids.draft_cnt
        draft_count_obj.ids.badge_txt.text = show_limited_cnt(int(count))
