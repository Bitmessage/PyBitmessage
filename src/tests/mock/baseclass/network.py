# pylint: disable=consider-using-f-string, no-name-in-module, too-few-public-methods

"""
Kivy Network screen
"""

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class NetworkStat(Screen):
    """NetworkStat class for kivy Ui"""

    text_variable_1 = StringProperty(
        '{0}::{1}'.format('Total Connections', '0'))
    text_variable_2 = StringProperty(
        'Processed {0} per-to-per messages'.format('0'))
    text_variable_3 = StringProperty(
        'Processed {0} brodcast messages'.format('0'))
    text_variable_4 = StringProperty(
        'Processed {0} public keys'.format('0'))
    text_variable_5 = StringProperty(
        'Processed {0} object to be synced'.format('0'))

    def __init__(self, *args, **kwargs):
        """Init method for network stat"""
        super(NetworkStat, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.init_ui, 1)

    def init_ui(self, dt=0):
        """Clock Schdule for method networkstat screen"""
