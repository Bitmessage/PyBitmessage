# from ..get_platform import platform
platform = "linux"
# from pybitmessage import kivy_helper_search

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from pybitmessage import state
from pybitmessage.addresses import decodeAddress
from datetime import datetime

from common import toast


class LoadingPopup(Popup):
    """LoadingPopup class for kivy Ui"""

    def __init__(self, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        # call dismiss_popup in 2 seconds
        Clock.schedule_once(self.dismiss_popup, 0.5)

    def dismiss_popup(self, dt):
        """Dismiss popups"""
        self.dismiss()


class GrashofPopup(BoxLayout):
    """GrashofPopup class for kivy Ui"""

    valid = False

    def __init__(self, **kwargs):
        """Grash of pop screen settings"""
        super(GrashofPopup, self).__init__(**kwargs)

    def checkAddress_valid(self, instance):
        """Checking address is valid or not"""
        # my_addresses = (
        #     state.kivyapp.root.ids.content_drawer.ids.btn.values)
        # add_book = [addr[1] for addr in kivy_helper_search.search_sql(
        #     folder="addressbook")]
        # entered_text = str(instance.text).strip()
        # if entered_text in add_book:
        #     text = 'Address is already in the addressbook.'
        # elif entered_text in my_addresses:
        #     text = 'You can not save your own address.'
        # elif entered_text:
        #     text = self.addressChanged(entered_text)

        # if entered_text in my_addresses or entered_text in add_book:
        #     self.ids.address.error = True
        #     self.ids.address.helper_text = text
        # elif entered_text and self.valid:
        #     self.ids.address.error = False
        # elif entered_text:
        #     self.ids.address.error = True
        #     self.ids.address.helper_text = text
        # else:
        #     self.ids.address.error = False
        #     self.ids.address.helper_text = 'This field is required'
        pass

    def checkLabel_valid(self, instance):
        """Checking address label is unique or not"""
        # entered_label = instance.text.strip()
        # addr_labels = [labels[0] for labels in kivy_helper_search.search_sql(
        #     folder="addressbook")]
        # if entered_label in addr_labels:
        #     self.ids.label.error = True
        #     self.ids.label.helper_text = 'label name already exists.'
        # elif entered_label:
        #     self.ids.label.error = False
        # else:
        #     self.ids.label.error = False
        #     self.ids.label.helper_text = 'This field is required'
        pass

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
        elif status == 'missingbm':
            text = "The address should start with ''BM-''"
        elif status == 'checksumfailed':
            text = (
                "The address is not typed or copied correctly"
                # " (the checksum failed)."
            )
        elif status == 'versiontoohigh':
            text = (
                "The version number of this address is higher than this"
                " software can support. Please upgrade Bitmessage.")
        elif status == 'invalidcharacters':
            text = "The address contains invalid characters."
        elif status == 'ripetooshort':
            text = "Some data encoded in the address is too short."
        elif status == 'ripetoolong':
            text = "Some data encoded in the address is too long."
        elif status == 'varintmalformed':
            text = "Some data encoded in the address is malformed."
        return text


class AddbookDetailPopup(BoxLayout):
    """AddbookDetailPopup class for kivy Ui"""

    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):
        """Set screen of address detail page"""
        super(AddbookDetailPopup, self).__init__(**kwargs)

    def checkLabel_valid(self, instance):
        """Checking address label is unique of not"""
        entered_label = str(instance.text.strip())
        address_list = kivy_helper_search.search_sql(folder="addressbook")
        addr_labels = [labels[0] for labels in address_list]
        add_dict = dict(address_list)
        if self.address and entered_label in addr_labels \
                and self.address != add_dict[entered_label]:
            self.ids.add_label.error = True
            self.ids.add_label.helper_text = 'label name already exists.'
        elif entered_label:
            self.ids.add_label.error = False
        else:
            self.ids.add_label.error = False
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
        state.kivyapp.set_navbar_for_composer()
        window_obj = state.kivyapp.root.ids
        window_obj.sc3.children[1].ids.ti.text = self.address
        window_obj.sc3.children[1].ids.btn.text = self.address
        window_obj.sc3.children[1].ids.txt_input.text = ''
        window_obj.sc3.children[1].ids.subject.text = ''
        window_obj.sc3.children[1].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
        self.parent.parent.parent.dismiss()

    # @staticmethod
    def close_pop(self):
        """Pop is Canceled"""
        self.parent.parent.parent.dismiss()
        toast('Canceled')


class AppClosingPopup(Popup):
    """AppClosingPopup class for kivy Ui"""

    def __init__(self, **kwargs):
        super(AppClosingPopup, self).__init__(**kwargs)

    def closingAction(self, text):
        """Action on closing window"""
        if text == 'Yes':
            print("*******************EXITING FROM APPLICATION*******************")
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
