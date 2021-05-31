from bitmessagekivy.get_platform import platform
from bitmessagekivy import kivy_helper_search
from helper_sql import sqlExecute
from functools import partial
from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import Screen

import state

from bitmessagekivy.baseclass.common import (
    avatarImageFirstLetter, toast,
    ThemeClsColor, SwipeToDeleteItem
)
from bitmessagekivy.baseclass.popup import AddbookDetailPopup


class AddressBook(Screen):
    """AddressBook Screen class for kivy Ui"""

    queryreturn = ListProperty()
    has_refreshed = True
    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details"""
        super(AddressBook, self).__init__(*args, **kwargs)
        self.addbook_popup = None
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method AddressBook"""
        self.loadAddresslist(None, 'All', '')
        print(dt)

    def loadAddresslist(self, account, where="", what=""):
        """Clock Schdule for method AddressBook"""
        if state.searcing_text:
            self.ids.scroll_y.scroll_y = 1.0
            where = ['label', 'address']
            what = state.searcing_text
        xAddress = ''
        self.ids.tag_label.text = ''
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "addressbook", where, what, False)
        self.queryreturn = [obj for obj in reversed(self.queryreturn)]
        if self.queryreturn:
            self.ids.tag_label.text = 'Address Book'
            self.has_refreshed = True
            self.set_mdList(0, 20)
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="No contact found!" if state.searcing_text
                else "No contact found yet...... ",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

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
            # listItem.add_widget(AvatarSampleWidget(
            #     source=state.imageDir + '/text_images/{}.png'.format(
            #         avatarImageFirstLetter(item[0].strip()))))
            image = state.imageDir + "/text_images/{}.png".format(
                avatarImageFirstLetter(item[0].strip()))
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
        # state.navinstance.ids.sc11.ids.ml.clear_widgets()
        # state.navinstance.ids.sc11.loadAddresslist(None, 'All', '')

    # @staticmethod
    def addBook_detail(self, address, label, instance, *args):
        """Addressbook details"""
        if instance.state == 'closed':
            instance.ids.delete_msg.disabled = True
            if instance.open_progress == 0.0:
                obj = AddbookDetailPopup()
                self.address_label = obj.address_label = label
                self.address = obj.address = address
                width = .9 if platform == 'android' else .8
                self.addbook_popup = MDDialog(
                    type="custom",
                    size_hint=(width, .25),
                    content_cls=obj,
                    buttons=[
                        MDRaisedButton(
                            text="Send message to",
                            on_release=self.send_message_to,
                        ),
                        MDRaisedButton(
                            text="Save",
                            on_release=self.update_addbook_label,
                        ),
                        MDRaisedButton(
                            text="Cancel",
                            on_release=self.close_pop,
                        ),
                    ],
                )
                # self.addbook_popup.set_normal_height()
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
            "DELETE FROM  addressbook WHERE address = '{}';".format(address))
        toast('Address Deleted')

    def close_pop(self, instance):
        """Pop is Canceled"""
        self.addbook_popup.dismiss()
        toast('Canceled')

    def update_addbook_label(self, instance):
        """Updating the label of address book address"""
        address_list = kivy_helper_search.search_sql(folder="addressbook")
        stored_labels = [labels[0] for labels in address_list]
        add_dict = dict(address_list)
        label = str(self.addbook_popup.content_cls.ids.add_label.text)
        if label in stored_labels and self.address == add_dict[label]:
            stored_labels.remove(label)
        if label and label not in stored_labels:
            sqlExecute(
                "UPDATE addressbook SET label = '{}' WHERE"
                " address = '{}';".format(
                    label, self.addbook_popup.content_cls.address))
            state.kivyapp.root.ids.sc11.ids.ml.clear_widgets()
            state.kivyapp.root.ids.sc11.loadAddresslist(None, 'All', '')
            self.addbook_popup.dismiss()
            toast('Saved')

    def send_message_to(self, instance):
        """Method used to fill to_address of composer autofield"""
        state.kivyapp.set_navbar_for_composer()
        window_obj = state.kivyapp.root.ids
        window_obj.sc3.children[1].ids.txt_input.text = self.address
        window_obj.sc3.children[1].ids.ti.text = ''
        window_obj.sc3.children[1].ids.btn.text = 'Select'
        window_obj.sc3.children[1].ids.subject.text = ''
        window_obj.sc3.children[1].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
        self.addbook_popup.dismiss()
