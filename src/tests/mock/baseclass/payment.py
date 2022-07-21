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


class Payment(Screen):
    """Payment Screen class for kivy Ui"""

    @staticmethod
    def create_hidden_payment_address():
        """This is basically used for creating hidden address used in payment for purchasing credits"""
        pass


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
