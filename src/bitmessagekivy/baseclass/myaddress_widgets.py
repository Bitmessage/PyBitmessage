# pylint: disable=too-many-arguments, no-name-in-module, import-error
# pylint: disable=too-few-public-methods, no-member, too-many-ancestors

"""
MyAddress widgets are here.
"""

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IRightBodyTouch

from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.bitmessagekivy.baseclass.common import ThemeClsColor


class BadgeText(IRightBodyTouch, MDLabel):
    """BadgeText class for kivy UI"""


class HelperMyAddress(object):
    """Widget used in MyAddress are here"""
    dialog_height = .25

    @staticmethod
    def is_active_badge():
        """This function show the 'active' label of active Address."""
        active_status = 'Active'
        is_android_width = 90
        width = 50
        height = 60
        badge_obj = BadgeText(
            size_hint=(None, None),
            size=[is_android_width if platform == 'android' else width, height],
            text=active_status, halign='center',
            font_style='Body1', theme_text_color='Custom',
            text_color=ThemeClsColor, font_size='13sp'
        )
        return badge_obj

    @staticmethod
    def myaddress_detail_popup(obj, width):
        """This method show the details of address as popup opens."""
        show_myaddress_dialogue = MDDialog(
            type="custom",
            size_hint=(width, HelperMyAddress.dialog_height),
            content_cls=obj,
        )
        return show_myaddress_dialogue

    @staticmethod
    def inactive_address_popup(width, callback_for_menu_items):
        """This method shows the warning popup if the address is inactive"""
        dialog_text = 'Address is not currently active. Please click on Toggle button to active it.'
        dialog_box = MDDialog(
            text=dialog_text,
            size_hint=(width, HelperMyAddress.dialog_height),
            buttons=[
                MDFlatButton(
                    text="Ok", on_release=lambda x: callback_for_menu_items("Ok")
                ),
            ],
        )
        return dialog_box
