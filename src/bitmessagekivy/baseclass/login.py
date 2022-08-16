# pylint: disable=no-member, too-many-arguments, too-few-public-methods
# pylint: disable=no-name-in-module, unused-argument, arguments-differ

"""
Login screen appears when the App is first time starts and when new Address is generated.
"""


from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.app import App

from backend.address_generator import AddressGenerator  # pylint: disable=import-error
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from bitmessagekivy.baseclass.common import toast
from bmconfigparser import config


class Login(Screen):
    """Login Screeen class for kivy Ui"""
    log_text1 = (
        'You may generate addresses by using either random numbers'
        ' or by using a passphrase If you use a passphrase, the address'
        ' is called a deterministic; address The Random Number option is'
        ' selected by default but deterministic addresses have several pros'
        ' and cons:')
    log_text2 = ('If talk about pros You can recreate your addresses on any computer'
                 ' from memory, You need-not worry about backing up your keys.dat file'
                 ' as long as you can remember your passphrase and aside talk about cons'
                 ' You must remember (or write down) your  You must remember the address'
                 ' version number and the stream number along with your passphrase If you'
                 ' choose a weak passphrase and someone on the Internet can brute-force it,'
                 ' they can read your messages and send messages as you')


class Random(Screen):
    """Random Screen class for Ui"""

    is_active = BooleanProperty(False)
    checked = StringProperty("")

    def generateaddress(self):
        """Method for Address Generator"""
        entered_label = str(self.ids.add_random_bx.children[0].ids.lab.text).strip()
        if not entered_label:
            self.ids.add_random_bx.children[0].ids.lab.focus = True
        is_address = AddressGenerator.random_address_generation(
            entered_label, streamNumberForAddress=1, eighteenByteRipe=False,
            nonceTrialsPerByte=1000, payloadLengthExtraBytes=1000
        )
        if is_address:
            toast('Creating New Address ...')
            self.parent.parent.ids.toolbar.opacity = 1
            self.parent.parent.ids.toolbar.disabled = False
            App.get_running_app().loadMyAddressScreen(True)
            self.manager.current = 'myaddress'
            Clock.schedule_once(self.address_created_callback, 6)

    def address_created_callback(self, dt=0):
        """New address created"""
        App.get_running_app().loadMyAddressScreen(False)
        App.get_running_app().root.ids.id_myaddress.ids.ml.clear_widgets()
        App.get_running_app().root.ids.id_myaddress.is_add_created = True
        App.get_running_app().root.ids.id_myaddress.init_ui()
        self.reset_address_spinner()
        toast('New address created')

    def reset_address_spinner(self):
        """reseting spinner address and UI"""
        addresses = [addr for addr in config.addresses()
                     if config.get(str(addr), 'enabled') == 'true']
        self.manager.parent.ids.content_drawer.ids.identity_dropdown.values = []
        self.manager.parent.ids.sc3.children[1].ids.identity_dropdown.values = []
        self.manager.parent.ids.content_drawer.ids.identity_dropdown.values = addresses
        self.manager.parent.ids.sc3.children[1].ids.identity_dropdown.values = addresses

    @staticmethod
    def add_validation(instance):
        """Retrieve created labels and validate"""
        entered_label = str(instance.text.strip())
        AddressGenerator.address_validation(instance, entered_label)

    def reset_address_label(self):
        """Resetting address labels"""
        if not self.ids.add_random_bx.children:
            self.ids.add_random_bx.add_widget(RandomBoxlayout())


class InfoLayout(BoxLayout, RectangularElevationBehavior):
    """InfoLayout class for kivy Ui"""


class RandomBoxlayout(BoxLayout):
    """RandomBoxlayout class for BoxLayout behaviour"""
