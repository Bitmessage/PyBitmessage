# pylint: disable=unused-argument, consider-using-f-string, import-error
# pylint: disable=unnecessary-comprehension, no-member, no-name-in-module

"""
addressbook.py
==============

All saved addresses are managed in Addressbook

"""

import os
import logging
from functools import partial

from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.app import App

from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.bitmessagekivy import kivy_helper_search
from pybitmessage.bitmessagekivy.baseclass.common import (
    avatar_image_first_letter, toast, empty_screen_label,
    ThemeClsColor, SwipeToDeleteItem, kivy_state_variables
)
from pybitmessage.bitmessagekivy.baseclass.popup import SavedAddressDetailPopup
from pybitmessage.bitmessagekivy.baseclass.addressbook_widgets import HelperAddressBook
from pybitmessage.helper_sql import sqlExecute

logger = logging.getLogger('default')

INITIAL_SCROLL_POSITION = 1.0
SCROLL_THRESHOLD = -0.0
SCROLL_RESET_POSITION = 0.06
INITIAL_LOAD_COUNT = 20
ADDRESS_INCREMENT = 5
POPUP_WIDTH_ANDROID = 0.9
POPUP_WIDTH_OTHER = 0.8


class AddressBook(Screen, HelperAddressBook):
    """AddressBook Screen class for kivy UI"""

    queryreturn = ListProperty()
    has_refreshed = True
    address_label = StringProperty()
    address = StringProperty()
    label_str = "No contact Address found yet......"
    no_search_res_found = "No search result found"

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details"""
        super().__init__(*args, **kwargs)  # pylint: disable=missing-super-argument
        self.addbook_popup = None
        self.kivy_state = kivy_state_variables()

    def loadAddresslist(self, account, where="", what=""):
        """Load address list with optional search filters"""
        if self.kivy_state.searching_text:
            self.ids.scroll_y.scroll_y = INITIAL_SCROLL_POSITION
            where = ['label', 'address']
            what = self.kivy_state.searching_text

        xAddress = ''
        self.ids.tag_label.text = ''
        self.queryreturn = list(reversed(
            kivy_helper_search.search_sql(xAddress, account, "addressbook", where, what, False)
        ))

        if self.queryreturn:
            self.ids.tag_label.text = 'Address Book'
            self.has_refreshed = True
            self.set_mdList(0, INITIAL_LOAD_COUNT)
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.ids.ml.add_widget(empty_screen_label(self.label_str, self.no_search_res_found))

    def set_mdList(self, start_index, end_index):
        """Create the mdList"""
        for item in self.queryreturn[start_index:end_index]:
            message_row = SwipeToDeleteItem(text=item[0])
            listItem = message_row.ids.content
            listItem.secondary_text = item[1]
            listItem.theme_text_color = "Custom"
            listItem.text_color = ThemeClsColor
            # pylint: disable=syntax-error
            image = os.path.join(
                self.kivy_state.image_dir, "text_images",
                f"{avatar_image_first_letter(item[0].strip())}.png"  # noqa: E999
            )
            message_row.ids.avater_img.source = image
            listItem.bind(on_release=partial(self.addBook_detail, item[1], item[0], message_row))
            message_row.ids.delete_msg.bind(on_press=partial(self.delete_address, item[1]))
            self.ids.ml.add_widget(message_row)

    def check_scroll_y(self, instance, _):
        """Load more data on scroll down"""
        if self.ids.scroll_y.scroll_y <= SCROLL_THRESHOLD and self.has_refreshed:
            self.ids.scroll_y.scroll_y = SCROLL_RESET_POSITION
            exist_addresses = len(self.ids.ml.children)
            if exist_addresses != len(self.queryreturn):
                self.update_addressBook_on_scroll(exist_addresses)
            self.has_refreshed = exist_addresses != len(self.queryreturn)

    def update_addressBook_on_scroll(self, exist_addresses):
        """Load more data on scroll"""
        self.set_mdList(exist_addresses, exist_addresses + ADDRESS_INCREMENT)

    @staticmethod
    def refreshs(*args):
        """Refresh the Widget"""

    def addBook_detail(self, address, label, instance, *args):
        """Display Addressbook details"""
        if instance.state == 'closed':
            instance.ids.delete_msg.disabled = True
            if instance.open_progress == 0.0:
                obj = SavedAddressDetailPopup()
                self.address_label = obj.address_label = label
                self.address = obj.address = address
                width = POPUP_WIDTH_ANDROID if platform == 'android' else POPUP_WIDTH_OTHER
                self.addbook_popup = self.address_detail_popup(
                    obj, self.send_message_to, self.update_addbook_label,
                    self.close_pop, width)
                self.addbook_popup.auto_dismiss = False
                self.addbook_popup.open()
        else:
            instance.ids.delete_msg.disabled = False

    def delete_address(self, address, instance, *args):
        """Delete address from the address book"""
        self.ids.ml.remove_widget(instance.parent.parent)
        if self.ids.ml.children:
            self.ids.tag_label.text = ''
        sqlExecute("DELETE FROM addressbook WHERE address = ?", address)
        toast('Address Deleted')

    def close_pop(self, instance):
        """Cancel and close the popup"""
        self.addbook_popup.dismiss()
        toast('Canceled')

    def update_addbook_label(self, instance):
        """Update the label of the address book"""
        address_list = kivy_helper_search.search_sql(folder="addressbook")
        stored_labels = [labels[0] for labels in address_list]
        add_dict = dict(address_list)
        label = str(self.addbook_popup.content_cls.ids.add_label.text)

        if label in stored_labels and self.address == add_dict[label]:
            stored_labels.remove(label)

        if label and label not in stored_labels:
            sqlExecute("""
                UPDATE addressbook
                SET label = ?
                WHERE address = ?""", label, self.addbook_popup.content_cls.address)

            app = App.get_running_app()
            app.root.ids.id_addressbook.ids.ml.clear_widgets()
            app.root.ids.id_addressbook.loadAddresslist(None, 'All', '')
            self.addbook_popup.dismiss()
            toast('Saved')

    def send_message_to(self, instance):
        """Fill the to_address of the composer autofield"""
        App.get_running_app().set_navbar_for_composer()
        self.compose_message(None, self.address)
        self.addbook_popup.dismiss()
