# pylint: disable=import-error, attribute-defined-outside-init
# pylint: disable=no-member, no-name-in-module, unused-argument, too-few-public-methods

"""
All the popup are managed here.

"""
import logging
from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.app import App

from pybitmessage.bitmessagekivy import kivy_helper_search
from pybitmessage.bitmessagekivy.get_platform import platform

from pybitmessage.bitmessagekivy.baseclass.common import toast

from pybitmessage.addresses import decodeAddress

logger = logging.getLogger('default')


class AddressChangingLoader(Popup):
    """Run a Screen Loader when changing the Identity for kivy UI"""

    def __init__(self, **kwargs):
        super(AddressChangingLoader, self).__init__(**kwargs)
        Clock.schedule_once(self.dismiss_popup, 0.5)

    def dismiss_popup(self, dt):
        """Dismiss popups"""
        self.dismiss()


class AddAddressPopup(BoxLayout):
    """Popup for adding new address to addressbook"""

    validation_dict = {
        "missingbm": "The address should start with ''BM-''",
        "checksumfailed": "The address is not typed or copied correctly",
        "versiontoohigh": "The version number of this address is higher than this"
        " software can support. Please upgrade Bitmessage.",
        "invalidcharacters": "The address contains invalid characters.",
        "ripetooshort": "Some data encoded in the address is too short.",
        "ripetoolong": "Some data encoded in the address is too long.",
        "varintmalformed": "Some data encoded in the address is malformed."
    }
    valid = False

    def __init__(self, **kwargs):
        super(AddAddressPopup, self).__init__(**kwargs)

    def checkAddress_valid(self, instance):
        """Checking address is valid or not"""
        my_addresses = (
            App.get_running_app().root.ids.content_drawer.ids.identity_dropdown.values)
        add_book = [addr[1].decode("utf-8", "replace") for addr in kivy_helper_search.search_sql(
            folder="addressbook")]
        entered_text = str(instance.text).strip()
        if entered_text in add_book:
            text = 'Address is already in the addressbook.'
        elif entered_text in my_addresses:
            text = 'You can not save your own address.'
        elif entered_text:
            text = self.addressChanged(entered_text)

        if entered_text in my_addresses or entered_text in add_book:
            self.ids.address.error = True
            self.ids.address.helper_text = text
        elif entered_text and self.valid:
            self.ids.address.error = False
        elif entered_text:
            self.ids.address.error = True
            self.ids.address.helper_text = text
        else:
            self.ids.address.error = True
            self.ids.address.helper_text = 'This field is required'

    def checkLabel_valid(self, instance):
        """Checking address label is unique or not"""
        entered_label = instance.text.strip()
        addr_labels = [labels[0].decode("utf-8", "replace") for labels in kivy_helper_search.search_sql(
            folder="addressbook")]
        if entered_label in addr_labels:
            self.ids.label.error = True
            self.ids.label.helper_text = 'Label name already exists.'
        elif entered_label:
            self.ids.label.error = False
        else:
            self.ids.label.error = True
            self.ids.label.helper_text = 'This field is required'

    def _onSuccess(self, addressVersion, streamNumber, ripe):
        pass

    def addressChanged(self, addr):
        """Address validation callback, performs validation and gives feedback"""
        status, addressVersion, streamNumber, ripe = decodeAddress(
            str(addr))
        self.valid = status == 'success'

        if self.valid:
            text = "Address is valid."
            self._onSuccess(addressVersion, streamNumber, ripe)
            return text
        return self.validation_dict.get(status)


class SavedAddressDetailPopup(BoxLayout):
    """Pop-up for Saved Address details for kivy UI"""

    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):
        """Set screen of address detail page"""
        super(SavedAddressDetailPopup, self).__init__(**kwargs)

    def checkLabel_valid(self, instance):
        """Checking address label is unique of not"""
        entered_label = str(instance.text.strip())
        address_list = kivy_helper_search.search_sql(folder="addressbook")
        addr_labels = [labels[0].decode("utf-8", "replace") for labels in address_list]
        add_dict = {}
        for row in address_list:
            label, address = row
            label = label.decode("utf-8", "replace")
            address = address.decode("utf-8", "replace")
            add_dict[label] = address
        if self.address and entered_label in addr_labels \
                and self.address != add_dict[entered_label]:
            self.ids.add_label.error = True
            self.ids.add_label.helper_text = 'label name already exists.'
        elif entered_label:
            self.ids.add_label.error = False
        else:
            self.ids.add_label.error = True
            self.ids.add_label.helper_text = 'This field is required'


class MyaddDetailPopup(BoxLayout):
    """MyaddDetailPopup class for kivy Ui"""

    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):
        """My Address Details screen setting"""
        super(MyaddDetailPopup, self).__init__(**kwargs)

    def send_message_from(self):
        """Method used to fill from address of composer autofield"""
        App.get_running_app().set_navbar_for_composer()
        window_obj = App.get_running_app().root.ids
        window_obj.id_create.children[1].ids.ti.text = self.address
        window_obj.id_create.children[1].ids.composer_dropdown.text = self.address
        window_obj.id_create.children[1].ids.txt_input.text = ''
        window_obj.id_create.children[1].ids.subject.text = ''
        window_obj.id_create.children[1].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
        self.parent.parent.parent.dismiss()

    def close_pop(self):
        """Pop is Cancelled"""
        self.parent.parent.parent.dismiss()
        toast('Cancelled')


class AppClosingPopup(Popup):
    """AppClosingPopup class for kivy Ui"""

    def __init__(self, **kwargs):
        super(AppClosingPopup, self).__init__(**kwargs)

    def closingAction(self, text):
        """Action on closing window"""
        exit_message = "*******************EXITING FROM APPLICATION*******************"
        if text == 'Yes':
            logger.debug(exit_message)
            import shutdown
            shutdown.doCleanShutdown()
        else:
            self.dismiss()
            toast(text)


class SenderDetailPopup(Popup):
    """SenderDetailPopup class for kivy Ui"""

    to_addr = StringProperty()
    from_addr = StringProperty()
    time_tag = StringProperty()

    def __init__(self, **kwargs):
        """this metthod initialized the send message detial popup"""
        super(SenderDetailPopup, self).__init__(**kwargs)

    def assignDetail(self, to_addr, from_addr, timeinseconds):
        """Detailes assigned"""
        self.to_addr = to_addr
        self.from_addr = from_addr
        time_obj = datetime.fromtimestamp(int(timeinseconds))
        self.time_tag = time_obj.strftime("%d %b %Y, %I:%M %p")
        device_type = 2 if platform == 'android' else 1.5
        pop_height = 1.2 * device_type * (self.ids.sd_label.height + self.ids.dismiss_btn.height)
        if len(to_addr) > 3:
            self.height = pop_height
            self.ids.to_addId.size_hint_y = None
            self.ids.to_addId.height = 50
            self.ids.to_addtitle.add_widget(ToAddressTitle())
            frmaddbox = ToAddrBoxlayout()
            frmaddbox.set_toAddress(to_addr)
            self.ids.to_addId.add_widget(frmaddbox)
        else:
            self.ids.space_1.height = dp(0)
            self.ids.space_2.height = dp(0)
            self.ids.myadd_popup_box.spacing = dp(8 if platform == 'android' else 3)
            self.height = pop_height / 1.2


class ToAddrBoxlayout(BoxLayout):
    """ToAddrBoxlayout class for kivy Ui"""
    to_addr = StringProperty()

    def set_toAddress(self, to_addr):
        """This method is use to set to address"""
        self.to_addr = to_addr


class ToAddressTitle(BoxLayout):
    """ToAddressTitle class for BoxLayout behaviour"""
