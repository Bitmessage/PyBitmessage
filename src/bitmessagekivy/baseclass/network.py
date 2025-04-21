# pylint: disable=unused-argument, consider-using-f-string
# pylint: disable=no-name-in-module, too-few-public-methods

"""
Network status
"""

import os

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from pybitmessage import state

if os.environ.get('INSTALL_TESTS', False) and not state.backend_py3_compatible:
    from pybitmessage.mockbm import kivy_main
    stats = kivy_main.network.stats
    object_tracker = kivy_main.network.objectracker
else:
    from pybitmessage.network import stats, objectracker as object_tracker


class NetworkStat(Screen):
    """NetworkStat class for Kivy UI"""

    text_variable_1 = StringProperty(f'Total Connections::0')  # noqa: E999
    text_variable_2 = StringProperty(f'Processed 0 peer-to-peer messages')
    text_variable_3 = StringProperty(f'Processed 0 broadcast messages')
    text_variable_4 = StringProperty(f'Processed 0 public keys')
    text_variable_5 = StringProperty(f'Processed 0 objects to be synced')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # pylint: disable=missing-super-argument
        Clock.schedule_interval(self.update_stats, 1)

    def update_stats(self, dt):
        """Update network statistics"""
        self.text_variable_1 = f'Total Connections::{len(stats.connectedHostsList())}'
        self.text_variable_2 = f'Processed {state.numberOfMessagesProcessed} peer-to-peer messages'
        self.text_variable_3 = f'Processed {state.numberOfBroadcastsProcessed} broadcast messages'
        self.text_variable_4 = f'Processed {state.numberOfPubkeysProcessed} public keys'
        self.text_variable_5 = f'Processed {object_tracker.missingObjects} objects'
