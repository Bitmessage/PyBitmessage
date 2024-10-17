# pylint: disable=unused-import, too-many-public-methods, unused-variable, too-many-ancestors
# pylint: disable=no-name-in-module, too-few-public-methods, import-error, unused-argument, too-many-arguments
# pylint: disable=attribute-defined-outside-init, global-variable-not-assigned, too-many-instance-attributes

"""
Kivy UI for inbox screen
"""
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
from kivy.app import App
from kivy.uix.screenmanager import Screen
from pybitmessage.bitmessagekivy.baseclass.common import kivy_state_variables, load_image_path


class Inbox(Screen):
    """Inbox Screen class for Kivy UI"""

    queryreturn = ListProperty()
    has_refreshed = True
    account = StringProperty()
    no_search_res_found = "No search result found"
    label_str = "Yet no message for this account!"

    def __init__(self, *args, **kwargs):
        """Initialize Kivy variables and set up the UI"""
        super().__init__(*args, **kwargs)  # pylint: disable=missing-super-argument
        self.kivy_running_app = App.get_running_app()
        self.kivy_state = kivy_state_variables()
        self.image_dir = load_image_path()
        Clock.schedule_once(self.init_ui, 0)

    def set_default_address(self):
        """Set the default address if none is selected"""
        if not self.kivy_state.selected_address and self.kivy_running_app.identity_list:
            self.kivy_state.selected_address = self.kivy_running_app.identity_list[0]

    def init_ui(self, dt=0):
        """Initialize UI and load message list"""
        self.loadMessagelist()

    def loadMessagelist(self, where="", what=""):
        """Load inbox messages"""
        self.set_default_address()
        self.account = self.kivy_state.selected_address

    def refresh_callback(self, *args):
        """Refresh the inbox messages while showing a loading spinner"""

        def refresh_on_scroll_down(interval):
            """Reset search fields and reload data on scroll"""
            self.kivy_state.searching_text = ""
            self.children[2].children[1].ids.search_field.text = ""
            self.ids.ml.clear_widgets()
            self.loadMessagelist(self.kivy_state.selected_address)
            self.has_refreshed = True
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_on_scroll_down, 1)
