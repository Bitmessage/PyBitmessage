# pylint: disable=no-member,too-many-arguments,too-few-public-methods
# pylint: disable=no-init,import-error

"""Addressbook widgets are here."""

from kivy.app import App
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

POPUP_HEIGHT_PROPORTION = 0.25


class HelperAddressBook(object):
    """Widget utilities for Addressbook."""

    @staticmethod
    def address_detail_popup(obj, send_message, update_address, close_popup, width):
        """
        Shows address details in a popup with clear actions.

        Args:
            obj: The widget containing the address details to display.
            send_message: The function to call when the "Send message" button is pressed.
            update_address: The function to call when the "Save" button is pressed.
            close_popup: The function to call when the "Cancel" button is pressed or the popup is closed.
            width: The desired width of the popup as a proportion of the screen.
        """

        buttons = [
            MDRaisedButton(text="Send message", on_release=send_message),
            MDRaisedButton(text="Update Address", on_release=update_address),
            MDRaisedButton(text="Cancel", on_release=close_popup),
        ]

        return MDDialog(
            type="custom",
            size_hint=(width, POPUP_HEIGHT_PROPORTION),
            content_cls=obj,
            buttons=buttons,
        )

    @staticmethod
    def compose_message(from_addr=None, to_addr=None):
        """
        Composes a new message (UI-independent).

        Args:
            from_addr (str, optional): The address to set in the "From" field. Defaults to None.
            to_addr (str, optional): The address to set in the "To" field. Defaults to None.
        """

        app = App.get_running_app()

        ids = app.root.ids
        create_screen = ids.id_create.children[1].ids

        # Reset fields
        create_screen.txt_input.text = to_addr if to_addr else from_addr
        create_screen.ti.text = ""
        create_screen.composer_dropdown.text = "Select"
        create_screen.subject.text = ""
        create_screen.body.text = ""

        # Navigate to create screen
        ids.scr_mngr.current = "create"
