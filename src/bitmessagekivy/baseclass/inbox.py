# pylint: disable=unused-import, too-many-public-methods, unused-variable, too-many-ancestors
# pylint: disable=no-name-in-module, too-few-public-methods, import-error, unused-argument, too-many-arguments
# pylint: disable=attribute-defined-outside-init, global-variable-not-assigned, too-many-instance-attributes

"""
Kivy UI for inbox screen
"""
from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.app import App
from kivy.uix.screenmanager import Screen

from pybitmessage.bitmessagekivy.baseclass.common import kivy_state_variables, load_image_path


class Inbox(Screen):
    """Inbox Screen class for kivy Ui"""

    queryreturn = ListProperty()
    has_refreshed = True
    account = StringProperty()
    no_search_res_found = "No search result found"
    label_str = "Yet no message for this account!"

    def __init__(self, *args, **kwargs):
        """Initialize kivy variables"""
        super(Inbox, self).__init__(*args, **kwargs)
        self.kivy_running_app = App.get_running_app()
        self.kivy_state = kivy_state_variables()
        self.image_dir = load_image_path()
        Clock.schedule_once(self.init_ui, 0)

    def set_defaultAddress(self):
        """Set default address"""
        if self.kivy_state.association == "":
            if self.kivy_running_app.identity_list:
                self.kivy_state.association = self.kivy_running_app.identity_list[0]

    def init_ui(self, dt=0):
        """loadMessagelist() call at specific interval"""

    def refresh_callback(self, *args):
        """Load inbox messages while wating-loader spins & called in inbox.kv"""

        def refresh_on_scroll_down(interval):
            """Reset fields and load data on scrolling upside down"""
            self.kivy_state.searching_text = ""
            self.children[2].children[1].ids.search_field.text = ""
            self.ids.ml.clear_widgets()
            self.loadMessagelist(self.kivy_state.association)
            self.has_refreshed = True
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_on_scroll_down, 1)
