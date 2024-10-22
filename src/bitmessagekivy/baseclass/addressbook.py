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

from kivy.properties import (
    ListProperty,
    StringProperty
)
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
from dbcompat import dbstr

logger = logging.getLogger('default')


class AddressBook(Screen, HelperAddressBook):
    """AddressBook Screen class for kivy Ui"""

    queryreturn = ListProperty()
    has_refreshed = True
    address_label = StringProperty()
    address = StringProperty()
    label_str = "No contact Address found yet......"
    no_search_res_found = "No search result found"

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details"""
        super(AddressBook, self).__init__(*args, **kwargs)
        self.addbook_popup = None
        self.kivy_state = kivy_state_variables()

    def loadAddresslist(self, account, where="", what=""):
        """Clock Schdule for method AddressBook"""
        if self.kivy_state.searching_text:
            self.ids.scroll_y.scroll_y = 1.0
            where = ['label', 'address']
            what = self.kivy_state.searching_text
        xAddress = ''
        self.ids.tag_label.text = ''
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "addressbook", where, what, False)
        self.queryreturn = [[obj[0].decode("utf-8", "replace"), obj[1].decode("utf-8", "replace")] for obj in reversed(self.queryreturn)]
        if self.queryreturn:
            self.ids.tag_label.text = 'Address Book'
            self.has_refreshed = True
            self.set_mdList(0, 20)
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.ids.ml.add_widget(empty_screen_label(self.label_str, self.no_search_res_found))

    def set_mdList(self, start_index, end_index):
        """Creating the mdList"""
        for item in self.queryreturn[start_index:end_index]:
            message_row = SwipeToDeleteItem(
                text=item[0],
            )
            listItem = message_row.ids.content
            listItem.secondary_text = item[1]
            listItem.theme_text_color = "Custom"
            listItem.text_color = ThemeClsColor
            image = os.path.join(
                self.kivy_state.imageDir, "text_images", "{}.png".format(avatar_image_first_letter(item[0].strip()))
            )
            message_row.ids.avater_img.source = image
            listItem.bind(on_release=partial(
                self.addBook_detail, item[1], item[0], message_row))
            message_row.ids.delete_msg.bind(on_press=partial(self.delete_address, item[1]))
            self.ids.ml.add_widget(message_row)

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            exist_addresses = len(self.ids.ml.children)
            if exist_addresses != len(self.queryreturn):
                self.update_addressBook_on_scroll(exist_addresses)
            self.has_refreshed = (
                True if exist_addresses != len(self.queryreturn) else False
            )

    def update_addressBook_on_scroll(self, exist_addresses):
        """Load more data on scroll down"""
        self.set_mdList(exist_addresses, exist_addresses + 5)

    @staticmethod
    def refreshs(*args):
        """Refresh the Widget"""

    # @staticmethod
    def addBook_detail(self, address, label, instance, *args):
        """Addressbook details"""
        if instance.state == 'closed':
            instance.ids.delete_msg.disabled = True
            if instance.open_progress == 0.0:
                obj = SavedAddressDetailPopup()
                self.address_label = obj.address_label = label
                self.address = obj.address = address
                width = .9 if platform == 'android' else .8
                self.addbook_popup = self.address_detail_popup(
                    obj, self.send_message_to, self.update_addbook_label,
                    self.close_pop, width)
                self.addbook_popup.auto_dismiss = False
                self.addbook_popup.open()
        else:
            instance.ids.delete_msg.disabled = False

    def delete_address(self, address, instance, *args):
        """Delete inbox mail from inbox listing"""
        self.ids.ml.remove_widget(instance.parent.parent)
        # if len(self.ids.ml.children) == 0:
        if self.ids.ml.children is not None:
            self.ids.tag_label.text = ''
        sqlExecute(
            "DELETE FROM  addressbook WHERE address = ?", dbstr(address))
        toast('Address Deleted')

    def close_pop(self, instance):
        """Pop is Canceled"""
        self.addbook_popup.dismiss()
        toast('Canceled')

    def update_addbook_label(self, instance):
        """Updating the label of address book address"""
        address_list = kivy_helper_search.search_sql(folder="addressbook")
        stored_labels = [labels[0].decode("utf-8", "replace") for labels in address_list]
        add_dict = {}
        for row in address_list:
            label, address = row
            label = label.decode("utf-8", "replace")
            address = address.decode("utf-8", "replace")
            add_dict[label] = address
        label = str(self.addbook_popup.content_cls.ids.add_label.text)
        if label in stored_labels and self.address == add_dict[label]:
            stored_labels.remove(label)
        if label and label not in stored_labels:
            sqlExecute("""
                UPDATE addressbook
                SET label = ?
                WHERE address = ?""", dbstr(label), dbstr(self.addbook_popup.content_cls.address))
            App.get_running_app().root.ids.id_addressbook.ids.ml.clear_widgets()
            App.get_running_app().root.ids.id_addressbook.loadAddresslist(None, 'All', '')
            self.addbook_popup.dismiss()
            toast('Saved')

    def send_message_to(self, instance):
        """Method used to fill to_address of composer autofield"""
        App.get_running_app().set_navbar_for_composer()
        self.compose_message(None, self.address)
        self.addbook_popup.dismiss()
