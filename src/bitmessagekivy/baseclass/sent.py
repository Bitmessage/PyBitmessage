# pylint: disable=import-error, attribute-defined-outside-init, too-many-arguments
# pylint: disable=no-member, no-name-in-module, unused-argument, too-few-public-methods

"""
   Sent screen; All sent message managed here.
"""

from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App

from pybitmessage.bitmessagekivy.baseclass.common import kivy_state_variables


class Sent(Screen):
    """Sent Screen class for kivy UI"""

    queryreturn = ListProperty()
    account = StringProperty()
    has_refreshed = True
    no_search_res_found = "No search result found"
    label_str = "Yet no message for this account!"

    def __init__(self, *args, **kwargs):
        """Association with the screen"""
        super(Sent, self).__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()
        if self.kivy_state.selected_address == '':
            if App.get_running_app().identity_list:
                self.kivy_state.selected_address = App.get_running_app().identity_list[0]
