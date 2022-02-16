# pylint: disable=import-error, no-name-in-module, import-outside-toplevel
# pylint: disable=too-few-public-methods, attribute-defined-outside-init


"""
Kivy All common pop managed here
"""

from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from baseclass.common import toast

from pybitmessage import state


platform = "linux"


class LoadingPopup(Popup):
    """LoadingPopup class for kivy Ui"""

    def __init__(self, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        # call dismiss_popup in 2 seconds
        Clock.schedule_once(self.dismiss_popup, 0.5)

    def dismiss_popup(self):
        """Dismiss popups"""
        self.dismiss()


class GrashofPopup(BoxLayout):
    """GrashofPopup class for kivy Ui"""

    valid = False

    def checkAddress_valid(self, instance):
        """Checking address is valid or not"""

    def checkLabel_valid(self, instance):
        """Checking address label is unique or not"""

    def _onSuccess(self, addressVersion, streamNumber, ripe):
        """Called when the popup is open"""


class AddbookDetailPopup(BoxLayout):
    """AddbookDetailPopup class for kivy Ui"""

    address_label = StringProperty()
    address = StringProperty()

    def checkLabel_valid(self, instance):
        """Checking address label is unique of not"""
        entered_label = str(instance.text.strip())
        address_list = []
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

    def closingAction(self, text):
        """Action on closing window"""
        if text == 'Yes':
            print("*******************EXITING FROM APPLICATION*******************")
            from pybitmessage import shutdown
            shutdown.doCleanShutdown()
        else:
            self.dismiss()
            toast(text)


class SenderDetailPopup(Popup):
    """SenderDetailPopup class for kivy Ui"""

    to_addr = StringProperty()
    from_addr = StringProperty()
    time_tag = StringProperty()

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
