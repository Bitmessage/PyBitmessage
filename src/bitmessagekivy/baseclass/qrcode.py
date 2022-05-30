# pylint: disable=import-error, no-name-in-module, too-few-public-methods

"""
Generate QRcode of saved addresses in addressbook.
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy_garden.qrcode import QRCodeWidget
from debug import logger


class ShowQRCode(Screen):
    """ShowQRCode Screen class for kivy Ui"""
    address = StringProperty()

    def __init__(self, *args, **kwargs):
        """Instantiate kivy state variable"""
        super(ShowQRCode, self).__init__(*args, **kwargs)
        self.kivy_running_app = App.get_running_app()

    def qrdisplay(self, instance, address):
        """Method used for showing QR Code"""
        self.ids.qr.clear_widgets()
        self.kivy_running_app.set_toolbar_for_QrCode()
        self.address = address  # used for label
        self.ids.qr.add_widget(QRCodeWidget(data=self.address))
        self.ids.qr.children[0].show_border = False
        instance.parent.parent.parent.dismiss()
        logger.debug('Show QR code')
