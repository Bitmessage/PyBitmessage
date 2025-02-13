# pylint: disable=no-member, too-many-arguments, too-few-public-methods
# pylint: disable=no-name-in-module, unused-argument, arguments-differ

"""
QR code Scan Screen used in message composer to get recipient address

"""

import os
import logging
import cv2

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen

from pybitmessage.bitmessagekivy.get_platform import platform

logger = logging.getLogger('default')


class ScanScreen(Screen):
    """ScanScreen is for scaning Qr code"""
    # pylint: disable=W0212
    camera_available = BooleanProperty(False)
    previous_open_screen = StringProperty()
    pop_up_instance = ObjectProperty()

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details"""
        super(ScanScreen, self).__init__(*args, **kwargs)
        self.check_camera()
        self.zbarcam = None

    def check_camera(self):
        """This method is used for checking camera avaibility"""
        if platform != "android":
            cap = cv2.VideoCapture(0)
            is_cam_open = cap.isOpened()
            while is_cam_open:
                logger.debug('Camera is available!')
                self.camera_available = True
                break
            else:
                logger.debug("Camera is not available!")
                self.camera_available = False
        else:
            self.camera_available = True

    def get_screen(self, screen_name, instance=None):
        """This method is used for getting previous screen name"""
        self.previous_open_screen = screen_name
        if screen_name != 'composer':
            self.pop_up_instance = instance

    def on_pre_enter(self):
        """
       on_pre_enter works little better on android
       It affects screen transition on linux
       """
        if not self.children:
            tmp = Builder.load_file(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), "kv", "{}.kv").format("scanner")
            )
            self.add_widget(tmp)
            self.zbarcam = self.children[0].ids.zbarcam
        if platform == "android":
            Clock.schedule_once(self.start_camera, 0)

    def on_enter(self):
        """
       on_enter works better on linux
       It creates a black screen on android until camera gets loaded
       """
        if platform != "android":
            Clock.schedule_once(self.start_camera, 0)

    def on_leave(self):
        """This method will call on leave"""
        Clock.schedule_once(self.stop_camera, 0)

    def start_camera(self, *args):
        """Its used for starting camera for scanning qrcode"""
        # pylint: disable=attribute-defined-outside-init
        self.zbarcam.start()
        Clock.schedule_interval(self.check_symbol, 0.5)

    def check_symbol(self, *args):
        """Check if the symbol is detected"""
        if self.zbarcam.symbols:
            for symbol in self.zbarcam.symbols:
                # ZBarSymbol.QRCODE is an integer, QRCODE corresponds to 64
                if symbol.type == 'QRCODE':
                    self.stop_camera()
                    self.pop_up_instance.content_cls.address.text = symbol.data.decode("utf-8")
                    self.manager.current = self.previous_open_screen
                    # changing screen closes popup, so need to open again with filled address
                    self.pop_up_instance.open()
                    return False
        return True

    def stop_camera(self, *args):
        """Its used to stop the camera"""
        self.zbarcam.stop()

    def open_cam(self, *args):
        """It will open up the camera"""
        if not self.xcam._camera._device.isOpened():
            self.xcam._camera._device.open(self.xcam._camera._index)
        self.xcam.play = True
