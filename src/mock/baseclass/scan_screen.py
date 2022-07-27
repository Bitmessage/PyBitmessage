# pylint: disable=import-error, no-name-in-module, import-outside-toplevel
# pylint: disable=no-member, attribute-defined-outside-init, arguments-differ

"""
Kivy QR Scan screen
"""

import os

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen

from pybitmessage.get_platform import platform


class ScanScreen(Screen):
    """ScanScreen is for scaning Qr code"""
    # pylint: disable=unused-argument
    # pylint: disable=W0212
    camera_avaialbe = BooleanProperty(False)
    previous_open_screen = StringProperty()
    pop_up_instance = ObjectProperty()

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details"""
        super(ScanScreen, self).__init__(*args, **kwargs)
        self.check_camera()

    def check_camera(self):
        """This method is used for checking camera avaibility"""
        if platform != "android":
            import cv2
            cap = cv2.VideoCapture(0)
            while cap.isOpened():
                print('Camera is available!')
                self.camera_avaialbe = True
                break
            else:
                print("Camera is not available!")
                self.camera_avaialbe = False
        else:
            self.camera_avaialbe = True

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
                    os.path.dirname(os.path.dirname(__file__)), "kv/{}.kv").format("scanner")
            )
            self.add_widget(tmp)
        if platform == "android":
            Clock.schedule_once(self.start_camera, 0)

    def on_enter(self):
        """
       on_enter works better on linux
       It creates a black screen on android until camera gets loaded
       """
        # print(self.children)
        if platform != "android":
            # pass
            Clock.schedule_once(self.start_camera, 0)

    def on_leave(self):
        """this methos will call on leave"""
        # pass
        Clock.schedule_once(self.stop_camera, 0)

    def start_camera(self, *args):
        """Its used for starting camera for scanning qrcode"""
        self.xcam = self.children[0].ids.zbarcam.ids.xcamera
        if platform == "android":
            self.xcam.play = True

        else:
            Clock.schedule_once(self.open_cam, 0)

    def stop_camera(self, *args):
        """Its used for stop the camera"""
        self.xcam.play = False
        if platform != "android":
            self.xcam._camera._device.release()

    def open_cam(self, *args):
        """It will open up the camera"""
        if not self.xcam._camera._device.isOpened():
            self.xcam._camera._device.open(self.xcam._camera._index)
        self.xcam.play = True
