# pylint: disable=no-name-in-module, too-few-public-methods, import-error, unused-argument
# pylint: disable=attribute-defined-outside-init, global-variable-not-assigned, unused-variable

"""
Bitmessage android(mobile) interface
"""

import os
import json
import importlib
import logging

from kivy.lang import Builder
from kivy.lang import Observable
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
    ListProperty
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
from kivymd.uix.bottomsheet import MDCustomBottomSheet

from pybitmessage.bitmessagekivy.kivy_state import KivyStateVariables
from pybitmessage.bmconfigparser import config

logger = logging.getLogger('default')

data_screen_dict = {}


def load_screen_json(data_file="screens_data.json"):
    """Load screens data from json"""

    with open(os.path.join(os.path.dirname(__file__), data_file)) as read_file:
        all_data = json.load(read_file)
        data_screens = list(all_data.keys())

    for key in all_data:
        if all_data[key]['Import']:
            import_data = all_data.get(key)['Import']
            import_to = import_data.split("import")[1].strip()
            import_from = import_data.split("import")[0].split('from')[1].strip()
            data_screen_dict[import_to] = importlib.import_module(import_from, import_to)
    return data_screens, all_data, 'success'


def get_identity_list():
    """Get list of identities and access 'identity_list' variable in .kv file"""
    identity_list = ListProperty(
        addr for addr in config.addresses() if config.getboolean(str(addr), 'enabled')
    )
    return identity_list


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
        if self.ids.identity_dropdown.is_open:
            self.ids.identity_dropdown.is_open = False


class CustomSpinner(Spinner):
    """
    A Dropdown on side navigation bar which hold the identity and can switch to other identity
    """

    def __init__(self, *args, **kwargs):
        """Method used for setting size of spinner"""
        super(CustomSpinner, self).__init__(*args, **kwargs)
        self.dropdown_cls.max_height = Window.size[1] / 3
        self.values = list(addr for addr in config.addresses()
                           if config.getboolean(str(addr), 'enabled'))


class NavigateApp(MDApp):
    """Navigation Layout of class"""

    def __init__(self):
        super(NavigateApp, self).__init__()
        self.data_screens, self.all_data, response = load_screen_json()
        self.kivy_state_obj = KivyStateVariables()

    title = "PyBitmessage"
    identity_list = get_identity_list()
    image_path = KivyStateVariables().image_dir
    tr = Lang("en")  # for changing in franch replace en with fr

    def build(self):  # pylint:disable=no-self-use
        """Method builds the widget"""
        for kv in self.data_screens:
            Builder.load_file(
                os.path.join(
                    os.path.dirname(__file__),
                    'kv',
                    '{0}.kv'.format(self.all_data[kv]["kv_string"]),
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

    def reset_login_screen(self):
        """This method is used for clearing the widgets of random screen"""
        if self.root.ids.id_newidentity.ids.add_random_bx.children:
            self.root.ids.id_newidentity.ids.add_random_bx.clear_widgets()

    def open_payment_layout(self, sku):
        """It basically open up a payment layout for kivy UI"""
        pml = PaymentMethodLayout()
        self.product_id = sku
        self.custom_sheet = MDCustomBottomSheet(screen=pml)
        self.custom_sheet.open()

    def initiate_purchase(self, method_name):
        """initiate_purchase module"""
        logger.debug("Purchasing %s through %s", self.product_id, method_name)


class PaymentMethodLayout(BoxLayout):
    """PaymentMethodLayout class for kivy Ui"""


if __name__ == '__main__':
    NavigateApp().run()
