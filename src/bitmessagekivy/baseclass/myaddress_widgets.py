# pylint: disable=too-many-arguments, no-name-in-module, import-error, no-init
# pylint: disable=too-few-public-methods, no-member, too-many-ancestors, useless-object-inheritance

"""
Widgets for the MyAddress module.
"""

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IRightBodyTouch

from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.bitmessagekivy.baseclass.common import ThemeClsColor


class BadgeText(IRightBodyTouch, MDLabel):
    """Class representing a badge text in the UI."""


class HelperMyAddress(object):
    """Helper class to manage MyAddress widgets and dialogs."""

    dialog_height = 0.25  # Consistent decimal notation

    @staticmethod
    def is_active_badge():
        """Return a label showing 'Active' status for the address."""
        active_status = 'Active'
        badge_width = 90 if platform == 'android' else 50
        badge_height = 60

        return BadgeText(
            size_hint=(None, None),
            size=[badge_width, badge_height],
            text=active_status,
            halign='center',
            font_style='Body1',
            theme_text_color='Custom',
            text_color=ThemeClsColor,
            font_size='13sp'
        )

    @staticmethod
    def myaddress_detail_popup(obj, width):
        """Show address details in a popup dialog."""
        return MDDialog(
            type="custom",
            size_hint=(width, HelperMyAddress.dialog_height),
            content_cls=obj,
        )

    @staticmethod
    def inactive_address_popup(width, callback_for_menu_items):
        """Show a warning dialog when the address is inactive."""
        dialog_text = (
            'Address is not currently active. Please click the Toggle button to activate it.'
        )

        return MDDialog(
            text=dialog_text,
            size_hint=(width, HelperMyAddress.dialog_height),
            buttons=[
                MDFlatButton(
                    text="Ok", on_release=lambda x: callback_for_menu_items("Ok")
                ),
            ],
        )
