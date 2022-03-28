# pylint: disable=no-member, too-many-arguments, too-few-public-methods
"""
Addressbook widgets are here.
"""


from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel

import state

no_address_found = "No contact found yet......"
empty_search_label = "No contact found!"


# pylint: disable=no-init, old-style-class
class DefaultLabelMixin:
    """Common label on blank screen"""

    @staticmethod
    def default_label_when_empty():
        """This function returns default message while no address is there."""
        content = MDLabel(
            font_style='Caption',
            theme_text_color='Primary',
            # FIXME: searching_text supposed to be inside kivy_sate.py, typo and need to create a PR for kivy_state.py
            text=empty_search_label if state.searching_text else no_address_found,
            halign='center', size_hint_y=None, valign='top')
        return content


class HelperAddressBook(DefaultLabelMixin):
    """Widget used in Addressbook are here"""

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

    @staticmethod
    def compose_message(from_addr=None, to_addr=None):
        """This UI independent method for message sending to reciever"""
        window_obj = state.kivyapp.root.ids
        if to_addr:
            window_obj.sc3.children[1].ids.txt_input.text = to_addr
        if from_addr:
            window_obj.sc3.children[1].ids.txt_input.text = from_addr
        window_obj.sc3.children[1].ids.ti.text = ''
        window_obj.sc3.children[1].ids.btn.text = 'Select'
        window_obj.sc3.children[1].ids.subject.text = ''
        window_obj.sc3.children[1].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
