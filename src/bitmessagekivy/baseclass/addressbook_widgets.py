# pylint: disable=no-member, too-many-arguments, too-few-public-methods
"""
Addressbook widgets are here.
"""

from kivy.app import App
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog


class HelperAddressBook(object):
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
        window_obj = App.get_runnint_app().root.ids
        if to_addr:
            window_obj.sc3.children[1].ids.txt_input.text = to_addr
        if from_addr:
            window_obj.sc3.children[1].ids.txt_input.text = from_addr
        window_obj.sc3.children[1].ids.ti.text = ''
        window_obj.sc3.children[1].ids.btn.text = 'Select'
        window_obj.sc3.children[1].ids.subject.text = ''
        window_obj.sc3.children[1].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
