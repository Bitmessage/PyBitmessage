# pylint: disable=no-name-in-module, too-few-public-methods, import-error, unused-argument, unused-import
# pylint: disable=attribute-defined-outside-init, global-variable-not-assigned, unused-variable, too-many-ancestors

"""
Bitmessage android(mobile) interface
"""

import os
import json
import importlib
import logging

from kivy.lang import Builder
from kivy.properties import (
    ListProperty
)
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (
    IRightBodyTouch
)
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.bottomsheet import MDCustomBottomSheet

from pybitmessage.bitmessagekivy.kivy_state import KivyStateVariables
from pybitmessage.bitmessagekivy.base_navigation import (
    BaseLanguage, BaseNavigationItem, BaseNavigationDrawerDivider,
    BaseNavigationDrawerSubheader, BaseContentNavigationDrawer,
    BaseIdentitySpinner
)

from pybitmessage.bmconfigparser import config
from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.bitmessagekivy.baseclass.common import toast
from pybitmessage.bitmessagekivy.baseclass.popup import AddAddressPopup

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


class Lang(BaseLanguage):
    """UI Language"""


class NavigationItem(BaseNavigationItem):
    """NavigationItem class for kivy Ui"""


class NavigationDrawerDivider(BaseNavigationDrawerDivider):
    """
    A small full-width divider that can be placed
    in the :class:`MDNavigationDrawer`
    """


class NavigationDrawerSubheader(BaseNavigationDrawerSubheader):
    """
    A subheader for separating content in :class:`MDNavigationDrawer`

    Works well alongside :class:`NavigationDrawerDivider`
    """


class ContentNavigationDrawer(BaseContentNavigationDrawer):
    """ContentNavigationDrawer class for kivy Uir"""


class BadgeText(IRightBodyTouch, MDLabel):
    """BadgeText class for kivy Ui"""


class IdentitySpinner(BaseIdentitySpinner):
    """Identity Dropdown in Side Navigation bar"""


class NavigateApp(MDApp):
    """Navigation Layout of class"""

    title = "PyBitmessage"
    identity_list = get_identity_list()
    image_path = KivyStateVariables().image_dir
    tr = Lang("en")  # for changing in franch replace en with fr

    def __init__(self):
        super(NavigateApp, self).__init__()
        self.data_screens, self.all_data, response = load_screen_json()
        self.kivy_state_obj = KivyStateVariables()

    def build(self):
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

    def addingtoaddressbook(self):
        """Dialog for saving address"""
        width = .85 if platform == 'android' else .8
        self.add_popup = MDDialog(
            title='Add contact',
            type="custom",
            size_hint=(width, .23),
            content_cls=AddAddressPopup(),
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=self.savecontact,
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_pop,
                ),
                MDRaisedButton(
                    text="Scan QR code",
                    on_release=self.scan_qr_code,
                ),
            ],
        )
        self.add_popup.auto_dismiss = False
        self.add_popup.open()

    def scan_qr_code(self, instance):
        """this method is used for showing QR code scanner"""
        if self.is_camara_attached():
            self.add_popup.dismiss()
            self.root.ids.id_scanscreen.get_screen(self.root.ids.scr_mngr.current, self.add_popup)
            self.root.ids.scr_mngr.current = 'scanscreen'
        else:
            alert_text = (
                'Currently this feature is not avaialbe!' if platform == 'android' else 'Camera is not available!')
            self.add_popup.dismiss()
            toast(alert_text)

    def is_camara_attached(self):
        """This method is for checking the camera is available or not"""
        self.root.ids.id_scanscreen.check_camera()
        is_available = self.root.ids.id_scanscreen.camera_available
        return is_available

    def savecontact(self, instance):
        """Method is used for saving contacts"""
        pupup_obj = self.add_popup.content_cls
        label = pupup_obj.ids.label.text.strip()
        address = pupup_obj.ids.address.text.strip()
        if label == '' and address == '':
            pupup_obj.ids.label.focus = True
            pupup_obj.ids.address.focus = True
        elif address == '':
            pupup_obj.ids.address.focus = True
        elif label == '':
            pupup_obj.ids.label.focus = True
        else:
            pupup_obj.ids.address.focus = True

    def close_pop(self, instance):
        """Close the popup"""
        self.add_popup.dismiss()
        toast('Canceled')

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
