# pylint: disable=no-name-in-module, too-few-public-methods, import-error, unused-argument


"""
Bitmessage android(mobile) interface
"""

import ast
import os
import importlib

from kivy.lang import Builder
from kivy.lang import Observable
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty
)
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.core.window import Window


from kivymd.app import MDApp
from kivymd.uix.list import (
    OneLineAvatarIconListItem,
    OneLineListItem
)

from pybitmessage.bitmessagekivy.kivy_state import KivyStateVariables
from pybitmessage.bmconfigparser import config

with open(os.path.join(os.path.dirname(__file__), "screens_data.json")) as read_file:
    all_data = ast.literal_eval(read_file.read())
    data_screens = list(all_data.keys())

for key in all_data:
    if all_data[key]['Import']:
        import_data = all_data.get(key)['Import']
        import_to = import_data.split("import")[1].strip()
        import_from = import_data.split("import")[0].split('from')[1].strip()
        importlib.import_module(import_from, import_to)


class Lang(Observable):
    """UI Language"""

    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Lang, self).__init__()
        self.ugettext = None
        self.lang = defaultlang

    @staticmethod
    def _(text):
        return text


class NavigationItem(OneLineAvatarIconListItem):
    """UI for NavigationItem class on Side Navigation bar"""
    badge_text = StringProperty()
    icon = StringProperty()
    active = BooleanProperty(False)

    def currentlyActive(self):
        """Currenly active"""
        for nav_obj in self.parent.children:
            nav_obj.active = False
        self.active = True


class NavigationDrawerDivider(OneLineListItem):
    """
    A small full-width divider line for Side Navigation bar
    """

    disabled = True
    divider = None
    _txt_top_pad = NumericProperty(dp(8))
    _txt_bot_pad = NumericProperty(dp(8))

    def __init__(self, **kwargs):
        # pylint: disable=bad-super-call
        super(OneLineListItem, self).__init__(**kwargs)
        self.height = dp(16)


class NavigationDrawerSubheader(OneLineListItem):
    """
    A subheader for separating content in :class:`MDNavigationDrawer`
    Works well alongside :class:`NavigationDrawerDivider`
    """

    disabled = True
    divider = None
    theme_text_color = 'Secondary'


class ContentNavigationDrawer(BoxLayout):
    """Helper for Side navigation bar which contains screen names"""

    def __init__(self, *args, **kwargs):
        """Method used for to initialize side navbar"""
        super(ContentNavigationDrawer, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for class contentNavigationDrawer"""
        self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)

    def check_scroll_y(self, instance, somethingelse):
        """show data on scroll down"""
        if self.ids.btn.is_open:
            self.ids.btn.is_open = False


class CustomSpinner(Spinner):
    """
    A Dropdown on side navigation bar which hold the identity and can switch to other identity
    """

    def __init__(self, *args, **kwargs):
        """Method used for setting size of spinner"""
        super(CustomSpinner, self).__init__(*args, **kwargs)
        self.dropdown_cls.max_height = Window.size[1] / 3
        self.values = list(addr for addr in config.addresses()
                           if config.get(str(addr), 'enabled') == 'true')


class NavigateApp(MDApp):
    """Navigation Layout of class"""
    def __init__(self):
        super(NavigateApp, self).__init__()
        self.kivy_state_obj = KivyStateVariables()

    title = "PyBitmessage"
    image_path = KivyStateVariables().image_dir
    tr = Lang("en")  # for changing in franch replace en with fr

    def build(self):  # pylint:disable=no-self-use
        """Method builds the widget"""
        for kv in data_screens:
            Builder.load_file(
                os.path.join(
                    os.path.dirname(__file__),
                    'kv',
                    '{0}.kv'.format(all_data[kv]["kv_string"]),
                )
            )
        return Builder.load_file(os.path.join(os.path.dirname(__file__), 'main.kv'))

    def set_screen(self, screen_name):
        """Set the screen name when navigate to other screens"""
        self.root.ids.scr_mngr.current = screen_name

    def run(self):
        """Running the widgets"""
        self.kivy_state_obj.kivyui_ready.set()
        super(NavigateApp, self).run()

    def loadMyAddressScreen(self, action):
        """loadMyAddressScreen method spin the loader"""
        if len(self.root.ids.id_myaddress.children) <= 2:
            self.root.ids.id_myaddress.children[0].active = action
        else:
            self.root.ids.id_myaddress.children[1].active = action
