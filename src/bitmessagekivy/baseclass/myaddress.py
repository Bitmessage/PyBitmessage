# pylint: disable=unused-argument, import-error, no-member, attribute-defined-outside-init
# pylint: disable=no-name-in-module, too-few-public-methods, too-many-instance-attributes

"""
myaddress.py
==============
This module manages all generated addresses in MyAddress.
"""

import os
from functools import partial

from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManagerException
from kivy.app import App
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarIconListItem
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
    """UI Toggle button"""


class CustomTwoLineAvatarIconListItem(TwoLineAvatarIconListItem):
    """Customized list item with Avatar and Icon."""


class MyAddress(Screen, HelperMyAddress):
    """Screen class to manage user addresses in the Kivy app."""

    address_label = StringProperty()
    text_address = StringProperty()
    addresses_list = ListProperty()
    has_refreshed = True
    is_add_created = False
    label_str = "No addresses have been created by the user."
    no_search_res_found = "No search results found."
    min_scroll_y_limit = 0.0
    scroll_y_step = 0.06
    number_of_addresses = 20
    addresses_at_a_time = 15
    canvas_color_black = [0, 0, 0, 0]
    canvas_color_gray = [0.5, 0.5, 0.5, 0.5]
    is_android_width = 0.9
    other_platform_width = 0.6
    disabled_addr_width = 0.8
    other_platform_disabled_addr_width = 0.55
    max_scroll_limit = 1.0

    def __init__(self, *args, **kwargs):
        """Initialize MyAddress screen and schedule UI setup."""
        super().__init__(*args, **kwargs)  # pylint: disable=missing-super-argument
        self.image_dir = load_image_path()
        self.kivy_running_app = App.get_running_app()
        self.kivy_state = self.kivy_running_app.kivy_state_obj
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, _dt=0):
        """Initialize the address UI and load the list of addresses."""
        self.addresses_list = config.addresses()
        if self.kivy_state.searching_text:
            self.ids.refresh_layout.scroll_y = self.max_scroll_limit
            self.addresses_list = [
                address for address in config.addresses() if self.filter_address(address)
            ]
        self.addresses_list.reverse()
        self.ids.tag_label.text = ''
        if self.addresses_list:
            self.ids.tag_label.text = 'My Addresses'
            self.has_refreshed = True
            self.populate_address_list(0, self.addresses_at_a_time)
            self.ids.refresh_layout.bind(scroll_y=self.check_scroll_y)
        else:
            self.ids.ml.add_widget(empty_screen_label(self.label_str, self.no_search_res_found))
            if not self.kivy_state.searching_text and not self.is_add_created:
                try:
                    self.manager.current = 'login'
                except ScreenManagerException:
                    pass

    def populate_address_list(self, first_index, last_index):
        """Populate the address list within the specified range."""
        data = self.get_address_list(first_index, last_index)
        for item in data:
            self.create_address_widget(item)

    def get_address_list(self, first_index, last_index):
        """Fetch address details and return them as a list of dictionaries."""
        return [
            {'text': config.get(address, 'label'), 'secondary_text': address}
            for address in self.addresses_list[first_index:last_index]
        ]

    def create_address_widget(self, item):
        """Create and configure a UI widget for each address."""
        is_enabled = config.getboolean(item['secondary_text'], 'enabled')
        address_widget = CustomTwoLineAvatarIconListItem(
            text=item['text'], secondary_text=item['secondary_text'],
            theme_text_color='Custom' if is_enabled else 'Primary',
            text_color=ThemeClsColor
        )
        address_widget.canvas.children[3].rgba = self.canvas_color_black if is_enabled else self.canvas_color_gray
        avatar_image_path = os.path.join(
            self.image_dir, "text_images", f"{avatar_image_first_letter(item['text'].strip())}.png"
        )
        address_widget.add_widget(AvatarSampleWidget(source=avatar_image_path))
        address_widget.bind(on_press=partial(self.show_address_details, item['secondary_text'], item['text']))
        self.configure_address_status(item, address_widget, is_enabled)

    def configure_address_status(self, item, widget, is_enabled):
        """Configure the address status and add appropriate toggle or badge."""
        if self.kivy_state.selected_address == item['secondary_text'] and is_enabled:
            widget.add_widget(self.is_active_badge())
        else:
            widget.add_widget(ToggleBtn(active=is_enabled))
        self.ids.ml.add_widget(widget)

    def check_scroll_y(self, _instance, _scroll_value):
        """Load more addresses when the user scrolls down."""
        if self.ids.refresh_layout.scroll_y <= self.min_scroll_y_limit and self.has_refreshed:
            self.ids.refresh_layout.scroll_y = self.scroll_y_step
            current_address_count = len(self.ids.ml.children)
            if current_address_count != len(self.addresses_list):
                self.load_more_addresses(current_address_count)
            self.has_refreshed = (current_address_count != len(self.addresses_list))

    def load_more_addresses(self, current_address_count):
        """Load additional addresses when scrolling."""
        self.populate_address_list(current_address_count, current_address_count + self.number_of_addresses)

    def show_address_details(self, address, label, *args):
        """Display address details in a popup."""
        if config.getboolean(address, 'enabled'):
            detail_popup = MyaddDetailPopup()
            self.address_label = detail_popup.address_label = label
            self.text_address = detail_popup.address = address
            popup_width = self.is_android_width if platform == 'android' else self.other_platform_width
            self.myadddetail_popup = self.create_address_detail_popup(detail_popup, popup_width)
            self.myadddetail_popup.auto_dismiss = False
            self.myadddetail_popup.open()
        else:
            popup_width = self.disabled_addr_width if platform == 'android' else self.other_platform_disabled_addr_width
            self.dialog_box = self.create_inactive_address_popup(popup_width, self.inactive_address_callback)
            self.dialog_box.open()

    def inactive_address_callback(self, selected_item, *args):
        """Handle user action from the inactive address alert."""
        self.dialog_box.dismiss()
        toast(selected_item)

    def refresh_callback(self, *args):
        """Refresh the screen by resetting the UI."""
        def update_ui(_interval):
            """Clear search input and refresh the address list."""
            self.kivy_state.searching_text = ''
            self.ids.search_bar.ids.search_field.text = ''
            self.has_refreshed = True
            self.ids.ml.clear_widgets()
            self.init_ui()
            self.ids.refresh_layout.refresh_done()
            Clock.schedule_once(self.update_enabled_addresses, 0)

        Clock.schedule_once(update_ui, 1)

    @staticmethod
    def filter_address(address):
        """Check if the current address matches the search term."""
        search_text = App.get_running_app().kivy_state_obj.searching_text.lower()
        return config.search_addresses(address, search_text)

    def disable_address_ui(self, address, instance):
        """Disable the selected address in the UI."""
        config.disable_address(address)
        instance.parent.parent.theme_text_color = 'Primary'
        instance.parent.parent.canvas.children[3].rgba = MyAddress.canvas_color_gray
        toast('Address disabled')
        Clock.schedule_once(self.update_enabled_addresses, 0)

    def enable_address_ui(self, address, instance):
        """Enable the selected address in the UI."""
        config.enable_address(address)
        instance.parent.parent.theme_text_color = 'Custom'
        instance.parent.parent.canvas.children[3].rgba = MyAddress.canvas_color_black
        toast('Address enabled')
        Clock.schedule_once(self.update_enabled_addresses, 0)

    def update_enabled_addresses(self, _dt=0):
        """Update the list of enabled addresses after a change."""
        enabled_addresses = [addr for addr in config.addresses() if config.getboolean(addr, 'enabled')]
        parent_ui = self.parent.parent.ids
        parent_ui.content_drawer.ids.identity_dropdown.values = enabled_addresses
        parent_ui.id_create.children[1].ids.composer_dropdown.values = enabled_addresses
        self.kivy_running_app.identity_list = enabled_addresses

    def toggleAction(self, instance):
        """Toggle the enable/disable state of an address."""
        address = instance.parent.parent.secondary_text
        if instance.active:
            self.enable_address_ui(address, instance)
        else:
            self.disable_address_ui(address, instance)
