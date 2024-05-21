# pylint: disable=unused-argument, consider-using-f-string, import-error, attribute-defined-outside-init
# pylint: disable=unnecessary-comprehension, no-member, no-name-in-module, too-few-public-methods

"""
    Trash screen
"""

from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen
from kivy.app import App

from pybitmessage.bitmessagekivy.baseclass.common import kivy_state_variables


class Trash(Screen):
    """Trash Screen class for kivy Ui"""

    trash_messages = ListProperty()
    has_refreshed = True
    delete_index = None
    table_name = StringProperty()
    no_msg_found_str = "Yet no trashed message for this account!"

    def __init__(self, *args, **kwargs):
        """Trash method, delete sent message and add in Trash"""
        super(Trash, self).__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()
        if self.kivy_state.selected_address == '':
            if App.get_running_app().identity_list:
                self.kivy_state.selected_address = App.get_running_app().identity_list[0]
