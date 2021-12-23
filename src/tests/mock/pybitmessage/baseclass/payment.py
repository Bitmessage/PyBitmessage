'''
    This is for pamyent related part
'''
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivy.uix.screenmanager import Screen

from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    IRightBodyTouch,
    OneLineAvatarIconListItem
)

# from bmconfigparser import BMConfigParser
from pybitmessage.baseclass.common import toast

# import queues
from pybitmessage import state


class Payment(Screen):
    """Payment Screen class for kivy Ui"""

    def get_free_credits(self, instance):
        """Get the available credits"""
        # pylint: disable=no-self-use
        state.availabe_credit = instance.parent.children[1].text
        existing_credits = state.kivyapp.root.ids.sc18.ids.cred.text
        if float(existing_credits.split()[1]) > 0:
            toast(
                'We already have added free coins'
                ' for the subscription to your account!')
        else:
            toast('Coins added to your account!')
            state.kivyapp.root.ids.sc18.ids.cred.text = '{0}'.format(
                state.availabe_credit)

    @staticmethod
    def create_hidden_payment_address():
        """This is basically used for creating hidden address used in payment for purchasing credits"""
        # if BMConfigParser().paymentaddress():
        #     toast('hidden payment address already exist for buying subscription...')
        # else:
        #     streamNumberForAddress = 1
        #     eighteenByteRipe = False
        #     nonceTrialsPerByte = 1000
        #     payloadLengthExtraBytes = 1000
        #     queues.addressGeneratorQueue.put((
        #         'createPaymentAddress', 4, streamNumberForAddress, '', 1,
        #         "", eighteenByteRipe, nonceTrialsPerByte,
        #         payloadLengthExtraBytes))
        #     toast('hidden payment address Creating for buying subscription....')


class Category(BoxLayout, RectangularElevationBehavior):
    """Category class for kivy Ui"""
    elevation_normal = .01


class ProductLayout(BoxLayout, RectangularElevationBehavior):
    """ProductLayout class for kivy Ui"""
    elevation_normal = .01


class PaymentMethodLayout(BoxLayout):
    """PaymentMethodLayout class for kivy Ui"""


class ListItemWithLabel(OneLineAvatarIconListItem):
    """ListItemWithLabel class for kivy Ui"""


class RightLabel(IRightBodyTouch, MDLabel):
    """RightLabel class for kivy Ui"""
