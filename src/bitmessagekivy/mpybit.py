"""
    Dummy implementation for kivy Desktop and android(mobile) interface
"""
# pylint: disable=too-few-public-methods

from kivy.app import App
from kivy.uix.label import Label

from pybitmessage.bitmessagekivy.kivy_state import KivyStateVariables


class NavigateApp(App):
    """Navigation Layout of class"""

    def __init__(self):
        super(NavigateApp, self).__init__()
        self.kivy_state_obj = KivyStateVariables()

    def build(self):
        """Method builds the widget"""
        # pylint: disable=no-self-use
        return Label(text="Hello World !")

    def clickNavDrawer(self):
        """method for clicking navigation drawer"""
        pass

    def addingtoaddressbook(self):
        """method for clicking address book popup"""
        pass


if __name__ == '__main__':
    NavigateApp().run()
