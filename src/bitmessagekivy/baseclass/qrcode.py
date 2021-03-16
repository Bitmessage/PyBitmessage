# pylint: disable=too-few-public-methods


import state
from bitmessagekivy.baseclass.common import toast
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


class ShowQRCode(Screen):
    """ShowQRCode Screen class for kivy Ui"""
    address = StringProperty()

    def qrdisplay(self, instasnce, address):
        """Method used for showing QR Code"""
        self.ids.qr.clear_widgets()
        state.kivyapp.set_toolbar_for_QrCode()
        try:
            from kivy.garden.qrcode import QRCodeWidget
        except Exception:
            from kivy_garden.qrcode import QRCodeWidget
        self.address = address
        self.ids.qr.add_widget(QRCodeWidget(data=address))
        self.ids.qr.children[0].show_border = False
        instasnce.parent.parent.parent.dismiss()
        toast('Show QR code')
