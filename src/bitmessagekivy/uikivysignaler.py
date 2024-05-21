"""
    UI Singnaler for kivy interface
"""

import logging

from threading import Thread
from kivy.app import App

from pybitmessage import queues
from pybitmessage import state

from pybitmessage.bitmessagekivy.baseclass.common import kivy_state_variables

logger = logging.getLogger('default')


class UIkivySignaler(Thread):
    """Kivy ui signaler"""

    def __init__(self, *args, **kwargs):
        super(UIkivySignaler, self).__init__(*args, **kwargs)
        self.kivy_state = kivy_state_variables()

    def run(self):
        self.kivy_state.kivyui_ready.wait()
        while state.shutdown == 0:
            try:
                command, data = queues.UISignalQueue.get()
                if command == 'writeNewAddressToTable':
                    address = data[1]
                    App.get_running_app().identity_list.append(address)
                elif command == 'updateSentItemStatusByAckdata':
                    App.get_running_app().status_dispatching(data)
                elif command == 'writeNewpaymentAddressToTable':
                    pass
            except Exception as e:
                logger.debug(e)
