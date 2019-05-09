
from threading import Thread
import state
import queues
from semaphores import kivyuisignaler
from helper_sql import SqlBulkExecute, sqlExecute, sqlQuery, sqlStoredProcedure

class UIkivySignaler(Thread):

    def run(self):
        kivyuisignaler.acquire()
        while state.shutdown == 0:
            try:
                command, data = queues.UISignalQueue.get()
                print("ssssssseeeeeeeeeeeeeeeeeeeeeeeeeewuhatsacomment.................", command)
                if command == 'writeNewAddressToTable':
                    label, address, streamNumber = data
                    state.kivyapp.variable_1.append(address)
                elif command == 'rerenderAddressBook':
                    state.kivyapp.obj_1.refreshs()

            except Exception as e:
                print(e)