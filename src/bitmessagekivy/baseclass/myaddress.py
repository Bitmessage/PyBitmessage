# pylint: disable=unused-argument, import-error, no-member, attribute-defined-outside-init
# pylint: disable=no-name-in-module, too-few-public-methods, too-many-instance-attributes

"""
myaddress.py
==============
All generated addresses are managed in MyAddress
"""

import os
from functools import partial

from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen, ScreenManagerException
from kivy.app import App

from kivymd.uix.list import (
    IRightBodyTouch,
    TwoLineAvatarIconListItem,
)
from kivymd.uix.selectioncontrol import MDSwitch

from pybitmessage.bmconfigparser import config

from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.bitmessagekivy.baseclass.common import (
    avatar_image_first_letter, AvatarSampleWidget, ThemeClsColor,
    toast, empty_screen_label, load_image_path
)

from pybitmessage.bitmessagekivy.baseclass.popup import MyaddDetailPopup
from pybitmessage.bitmessagekivy.baseclass.myaddress_widgets import HelperMyAddress


class ToggleBtn(IRightBodyTouch, MDSwitch):
    """ToggleBtn class for kivy UI"""


class CustomTwoLineAvatarIconListItem(TwoLineAvatarIconListItem):
    """CustomTwoLineAvatarIconListItem class for kivy Ui"""


class MyAddress(Screen, HelperMyAddress):
    """MyAddress screen class for kivy Ui"""

    address_label = StringProperty()
    text_address = StringProperty()
    addresses_list = ListProperty()
    has_refreshed = True
    is_add_created = False
    label_str = "Yet no address is created by user!!!!!!!!!!!!!"
    no_search_res_found = "No search result found"
    min_scroll_y_limit = -0.0
    scroll_y_step = 0.06
    number_of_addresses = 20
    addresses_at_a_time = 15
    canvas_color_black = [0, 0, 0, 0]
    canvas_color_gray = [0.5, 0.5, 0.5, 0.5]
    is_android_width = .9
    other_platform_width = .6
    disabled_addr_width = .8
    other_platform_disabled_addr_width = .55
    max_scroll_limit = 1.0

    def __init__(self, *args, **kwargs):
        """Clock schdule for method Myaddress accounts"""
        super(MyAddress, self).__init__(*args, **kwargs)
        self.image_dir = load_image_path()
        self.kivy_running_app = App.get_running_app()
        self.kivy_state = self.kivy_running_app.kivy_state_obj

        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock schdule for method Myaddress accounts"""
        self.addresses_list = config.addresses()
        if self.kivy_state.searching_text:
            self.ids.refresh_layout.scroll_y = self.max_scroll_limit
            filtered_list = [
                x for x in config.addresses()
                if self.filter_address(x)
            ]
            self.addresses_list = filtered_list
        self.addresses_list = [obj for obj in reversed(self.addresses_list)]
        self.ids.tag_label.text = ''
        if self.addresses_list:
            self.ids.tag_label.text = 'My Addresses'
            self.has_refreshed = True
            self.set_mdList(0, self.addresses_at_a_time)
            self.ids.refresh_layout.bind(scroll_y=self.check_scroll_y)
        else:
            self.ids.ml.add_widget(empty_screen_label(self.label_str, self.no_search_res_found))
            if not self.kivy_state.searching_text and not self.is_add_created:
                try:
                    self.manager.current = 'login'
                except ScreenManagerException:
                    pass

    def get_address_list(self, first_index, last_index, data):
        """Getting address and append to the list"""
        for address in self.addresses_list[first_index:last_index]:
            data.append({
                'text': config.get(address, 'label'),
                'secondary_text': address}
            )
        return data

    def set_address_to_widget(self, item):
        """Setting address to the widget"""
        is_enable = config.getboolean(item['secondary_text'], 'enabled')
        meny = CustomTwoLineAvatarIconListItem(
            text=item['text'], secondary_text=item['secondary_text'],
            theme_text_color='Custom' if is_enable else 'Primary',
            text_color=ThemeClsColor,)
        try:
            meny.canvas.children[3].rgba = self.canvas_color_black if is_enable else self.canvas_color
        except Exception:
            pass
        meny.add_widget(AvatarSampleWidget(
            source=os.path.join(
                self.image_dir, "text_images", "{}.png".format(avatar_image_first_letter(
                    item["text"].strip())))
        ))
        meny.bind(on_press=partial(
            self.myadd_detail, item['secondary_text'], item['text']))
        self.set_address_status(item, meny, is_enable)

    def set_address_status(self, item, meny, is_enable):
        """Setting the identity status enable/disable on UI"""
        if self.kivy_state.selected_address == item['secondary_text'] and is_enable:
            meny.add_widget(self.is_active_badge())
        else:
            meny.add_widget(ToggleBtn(active=True if is_enable else False))
        self.ids.ml.add_widget(meny)

    def set_mdList(self, first_index, last_index):
        """Creating the mdlist"""
        data = []
        self.get_address_list(first_index, last_index, data)
        for item in data:
            self.set_address_to_widget(item)

    def check_scroll_y(self, instance, somethingelse):
        """Load data on Scroll down"""
        if self.ids.refresh_layout.scroll_y <= self.min_scroll_y_limit and self.has_refreshed:
            self.ids.refresh_layout.scroll_y = self.scroll_y_step
            my_addresses = len(self.ids.ml.children)
            if my_addresses != len(self.addresses_list):
                self.update_addressBook_on_scroll(my_addresses)
            self.has_refreshed = (
                True if my_addresses != len(self.addresses_list) else False
            )

    def update_addressBook_on_scroll(self, my_addresses):
        """Loads more data on scroll down"""
        self.set_mdList(my_addresses, my_addresses + self.number_of_addresses)

    def myadd_detail(self, fromaddress, label, *args):
        """Load myaddresses details"""
        if config.get(fromaddress, 'enabled'):
            obj = MyaddDetailPopup()
            self.address_label = obj.address_label = label
            self.text_address = obj.address = fromaddress
            width = self.is_android_width if platform == 'android' else self.other_platform_width
            self.myadddetail_popup = self.myaddress_detail_popup(obj, width)
            self.myadddetail_popup.auto_dismiss = False
            self.myadddetail_popup.open()
        else:
            width = self.disabled_addr_width if platform == 'android' else self.other_platform_disabled_addr_width
            self.dialog_box = self.inactive_address_popup(width, self.callback_for_menu_items)
            self.dialog_box.open()

    def callback_for_menu_items(self, text_item, *arg):
        """Callback of inactive address alert box"""
        self.dialog_box.dismiss()
        toast(text_item)

    def refresh_callback(self, *args):
        """Method updates the state of application,
        While the spinner remains on the screen"""
        def refresh_callback(interval):
            """Method used for loading the myaddress screen data"""
            self.kivy_state.searching_text = ''
            self.ids.search_bar.ids.search_field.text = ''
            self.has_refreshed = True
            self.ids.ml.clear_widgets()
            self.init_ui()
            self.ids.refresh_layout.refresh_done()
            Clock.schedule_once(self.address_permision_callback, 0)
        Clock.schedule_once(refresh_callback, 1)

    @staticmethod
    def filter_address(address):
        """It will return True if search is matched"""
        searched_text = App.get_running_app().kivy_state_obj.searching_text.lower()
        return bool(config.search_addresses(address, searched_text))

    def disable_address_ui(self, address, instance):
        """This method is used to disable addresses from UI"""
        config.disable_address(address)
        instance.parent.parent.theme_text_color = 'Primary'
        instance.parent.parent.canvas.children[3].rgba = MyAddress.canvas_color_gray
        toast('Address disabled')
        Clock.schedule_once(self.address_permision_callback, 0)

    def enable_address_ui(self, address, instance):
        """This method is used to enable addresses from UI"""
        config.enable_address(address)
        instance.parent.parent.theme_text_color = 'Custom'
        instance.parent.parent.canvas.children[3].rgba = MyAddress.canvas_color_black
        toast('Address Enabled')
        Clock.schedule_once(self.address_permision_callback, 0)

    def address_permision_callback(self, dt=0):
        """callback for enable or disable addresses"""
        addresses = [addr for addr in config.addresses()
                     if config.getboolean(str(addr), 'enabled')]
        self.parent.parent.ids.content_drawer.ids.identity_dropdown.values = addresses
        self.parent.parent.ids.id_create.children[1].ids.btn.values = addresses
        self.kivy_running_app.identity_list = addresses

    def toggleAction(self, instance):
        """This method is used for enable or disable address"""
        addr = instance.parent.parent.secondary_text
        if instance.active:
            self.enable_address_ui(addr, instance)
        else:
            self.disable_address_ui(addr, instance)
