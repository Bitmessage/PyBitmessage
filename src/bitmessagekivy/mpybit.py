# pylint: disable=no-name-in-module, too-few-public-methods


"""
Bitmessage android(mobile) interface
"""

import ast
import os

from kivy.lang import Builder
from kivy.lang import Observable

from kivymd.app import MDApp

from pybitmessage.semaphores import kivyuisignaler
from pybitmessage.bitmessagekivy.kivy_state import KivyStateVariables


with open(os.path.join(os.path.dirname(__file__), "screens_data.json")) as read_file:
    all_data = ast.literal_eval(read_file.read())
    data_screens = list(all_data.keys())

for modules in data_screens:
    exec(all_data[modules]['Import'])


class Lang(Observable):
    """UI Language"""

    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Lang, self).__init__()
        self.ugettext = None
        self.lang = defaultlang

    @staticmethod
    def _(text):
        return text


class NavigateApp(MDApp):
    """Navigation Layout of class"""
    def __init__(self):
        super(NavigateApp, self).__init__()
        self.kivy_state_obj = KivyStateVariables()

    title = "PyBitmessage"
    tr = Lang("en")  # for changing in franch replace en with fr

    def build(self):  # pylint:disable=no-self-use
        """Method builds the widget"""
        for kv in data_screens:
            Builder.load_file(
                os.path.join(
                    os.path.dirname(__file__),
                    'kv',
                    '{0}.kv'.format(all_data[kv]["kv_string"]),
                )
            )
        return Builder.load_file(os.path.join(os.path.dirname(__file__), 'main.kv'))

    def set_screen(self, screen_name):
        """Set the screen name when navigate to other screens"""
        self.root.ids.scr_mngr.current = screen_name

    def run(self):
        """Running the widgets"""
        kivyuisignaler.release()
        super(NavigateApp, self).run()
