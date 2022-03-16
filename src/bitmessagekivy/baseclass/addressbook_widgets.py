# pylint: disable=no-member, too-many-arguments
"""
Addressbook widgets are here.
"""


from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel

import state


class HelperAddressBook(object):
    """Widget used in Addressbook are here"""
    def __init__(self):
        pass

    @staticmethod
    def default_label_when_empty():
        """This function returns default message while no address is there."""
        content = MDLabel(
            font_style='Caption',
            theme_text_color='Primary',
            # FIXME: searching_text supposed to be inside kivy_sate.py and need to create a PR for kivy_state.py
            text="No contact found!" if state.searching_text
            else "No contact found yet...... ", halign='center', size_hint_y=None, valign='top')
        return content

    @staticmethod
    def address_detail_popup(obj, send_message, update_address, close_popup, width):
        """This function shows the address's details and opens the popup."""
        show_dialogue = MDDialog(
            type="custom",
            size_hint=(width, .25),
            content_cls=obj,
            buttons=[
                MDRaisedButton(
                    text="Send message to",
                    on_release=send_message,
                ),
                MDRaisedButton(
                    text="Save",
                    on_release=update_address,
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=close_popup,
                ),
            ],
        )
        return show_dialogue
