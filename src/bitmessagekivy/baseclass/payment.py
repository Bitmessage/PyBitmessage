# pylint: disable=import-error, no-name-in-module, too-few-public-methods, too-many-ancestors

'''
    Payment/subscription frontend
'''

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.app import App

from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    IRightBodyTouch,
    OneLineAvatarIconListItem
)

from bitmessagekivy.baseclass.common import toast, kivy_state_variables


class Payment(Screen):
    """Payment Screen class for kivy Ui"""

    def __init__(self, *args, **kwargs):
        """Instantiate kivy state variable"""
        super(Payment, self).__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()

    # TODO: get_free_credits() is not used anywhere, will be used later for Payment/subscription.
    def get_free_credits(self, instance):  # pylint: disable=unused-argument
        """Get the available credits"""
        # pylint: disable=no-self-use
        self.kivy_state.available_credit = 0
        existing_credits = 0
        if existing_credits > 0:
            toast(
                'We already have added free credit'
                ' for the subscription to your account!')
        else:
            toast('Credit added to your account!')
            # TODO: There is no sc18 screen id is available,
            # need to create sc18 for Credits screen inside main.kv
            App.get_running_app().root.ids.sc18.ids.cred.text = '{0}'.format(
                self.kivy_state.available_credit)


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
