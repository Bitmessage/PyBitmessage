# pylint: disable=unused-argument, no-name-in-module, too-few-public-methods
"""
    Base class for Navigation Drawer
"""

from kivy.lang import Observable

from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty
)
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner

from kivy.clock import Clock
from kivy.core.window import Window

from kivymd.uix.list import (
    OneLineAvatarIconListItem,
    OneLineListItem
)

from pybitmessage.bmconfigparser import config


class BaseLanguage(Observable):
    """UI Language"""
    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(BaseLanguage, self).__init__()
        self.ugettext = None
        self.lang = defaultlang

    @staticmethod
    def _(text):
        return text


class BaseNavigationItem(OneLineAvatarIconListItem):
    """NavigationItem class for kivy Ui"""
    badge_text = StringProperty()
    icon = StringProperty()
    active = BooleanProperty(False)

    def currentlyActive(self):
        """Currenly active"""
        for nav_obj in self.parent.children:
            nav_obj.active = False
        self.active = True


class BaseNavigationDrawerDivider(OneLineListItem):
    """
    A small full-width divider that can be placed
    in the :class:`MDNavigationDrawer`
    """

    disabled = True
    divider = None
    _txt_top_pad = NumericProperty(dp(8))
    _txt_bot_pad = NumericProperty(dp(8))

    def __init__(self, **kwargs):
        super(BaseNavigationDrawerDivider, self).__init__(**kwargs)
        self.height = dp(16)


class BaseNavigationDrawerSubheader(OneLineListItem):
    """
    A subheader for separating content in :class:`MDNavigationDrawer`

    Works well alongside :class:`NavigationDrawerDivider`
    """

    disabled = True
    divider = None
    theme_text_color = 'Secondary'


class BaseContentNavigationDrawer(BoxLayout):
    """ContentNavigationDrawer class for kivy Uir"""

    def __init__(self, *args, **kwargs):
        """Method used for contentNavigationDrawer"""
        super(BaseContentNavigationDrawer, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for class contentNavigationDrawer"""
        self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)

    def check_scroll_y(self, instance, somethingelse):
        """show data on scroll down"""
        if self.ids.identity_dropdown.is_open:
            self.ids.identity_dropdown.is_open = False


class BaseIdentitySpinner(Spinner):
    """Base Class for Identity Spinner(Dropdown)"""

    def __init__(self, *args, **kwargs):
        """Method used for setting size of spinner"""
        super(BaseIdentitySpinner, self).__init__(*args, **kwargs)
        self.dropdown_cls.max_height = Window.size[1] / 3
        self.values = list(addr for addr in config.addresses()
                           if config.getboolean(str(addr), 'enabled'))
