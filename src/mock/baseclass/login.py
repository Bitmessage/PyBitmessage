# pylint: disable=import-error, no-name-in-module, too-few-public-methods


"""
Kivy Login screen
"""

from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from baseclass.common import toast

from kivymd.uix.behaviors.elevation import RectangularElevationBehavior

from pybitmessage.bmconfigparser import BMConfigParser
from pybitmessage import queues
from pybitmessage import state


class Login(Screen):
    """Login Screeen class for kivy Ui"""
    # pylint: disable=too-few-public-methods
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
        # entered_label = str(self.ids.lab.text).strip()
        entered_label = str(self.ids.add_random_bx.children[0].ids.lab.text).strip()
        if not entered_label:
            self.ids.add_random_bx.children[0].ids.lab.focus = True
        streamNumberForAddress = 1
        eighteenByteRipe = False
        nonceTrialsPerByte = 1000
        payloadLengthExtraBytes = 1000
        lables = [BMConfigParser().get(obj, 'label')
                  for obj in BMConfigParser().addresses()]
        if entered_label and entered_label not in lables:
            toast('Address Creating...')
            queues.addressGeneratorQueue.put((
                'createRandomAddress', 4, streamNumberForAddress, entered_label, 1,
                "", eighteenByteRipe, nonceTrialsPerByte,
                payloadLengthExtraBytes))
            self.parent.parent.ids.toolbar.opacity = 1
            self.parent.parent.ids.toolbar.disabled = False
            state.kivyapp.loadMyAddressScreen(True)
            self.manager.current = 'myaddress'
            Clock.schedule_once(self.address_created_callback, 6)

    def address_created_callback(self, dt=0):  # pylint: disable=unused-argument
        """New address created"""
        state.kivyapp.loadMyAddressScreen(False)
        state.kivyapp.root.ids.sc10.ids.ml.clear_widgets()
        state.kivyapp.root.ids.sc10.is_add_created = True
        state.kivyapp.root.ids.sc10.init_ui()
        self.reset_address_spinner()
        toast('New address created')

    def reset_address_spinner(self):
        """reseting spinner address and UI"""
        addresses = [addr for addr in BMConfigParser().addresses()
                     if BMConfigParser().get(str(addr), 'enabled') == 'true']
        self.manager.parent.ids.content_drawer.ids.btn.values = []
        self.manager.parent.ids.sc3.children[1].ids.btn.values = []
        self.manager.parent.ids.content_drawer.ids.btn.values = addresses
        self.manager.parent.ids.sc3.children[1].ids.btn.values = addresses

    @staticmethod
    def add_validation(instance):
        """Checking validation at address creation time"""
        entered_label = str(instance.text.strip())
        lables = [BMConfigParser().get(obj, 'label')
                  for obj in BMConfigParser().addresses()]
        if entered_label in lables:
            instance.error = True
            instance.helper_text = 'it is already exist you'\
                ' can try this Ex. ( {0}_1, {0}_2 )'.format(
                    entered_label)
        elif entered_label:
            instance.error = False
        else:
            instance.error = False
            instance.helper_text = 'This field is required'

    def reset_address_label(self):
        """Resetting address labels"""
        if not self.ids.add_random_bx.children:
            self.ids.add_random_bx.add_widget(RandomBoxlayout())


class InfoLayout(BoxLayout, RectangularElevationBehavior):
    """InfoLayout class for kivy Ui"""
    # pylint: disable=too-few-public-methods


class RandomBoxlayout(BoxLayout):
    """RandomBoxlayout class for BoxLayout behaviour"""
    # pylint: disable=too-few-public-methods
