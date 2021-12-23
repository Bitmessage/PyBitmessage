"""
Ui Singnaler for kivy interface
"""
from threading import Thread

from pybitmessage import queues
from pybitmessage import state
# from semaphores import kivyuisignaler

from threading import Semaphore



class UIkivySignaler(Thread):
    """Kivy ui signaler"""

    def run(self):
        kivyuisignaler = Semaphore(0)
        kivyuisignaler.acquire()
        while state.shutdown == 0:
            try:
                command, data = queues.UISignalQueue.get()
                if command == 'writeNewAddressToTable':
                    address = data[1]
                    state.kivyapp.variable_1.append(address)
                # elif command == 'rerenderAddressBook':
                #     state.kivyapp.obj_1.refreshs()
                # Need to discuss this
                elif command == 'writeNewpaymentAddressToTable':
                    pass
                elif command == 'updateSentItemStatusByAckdata':
                    state.kivyapp.status_dispatching(data)
            except Exception as e:
                print(e)
