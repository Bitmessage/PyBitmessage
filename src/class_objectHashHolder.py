# objectHashHolder is a timer-driven thread. One objectHashHolder thread is used
# by each sendDataThread. It uses it whenever a sendDataThread needs to
# advertise an object to peers. Instead of sending it out immediately, it must
# wait a random number of seconds for each connection so that different peers
# get different objects at different times. Thus an attacker who is
# connecting to many network nodes who receives a message first from Alice
# cannot be sure if Alice is the node who originated the message.

import random
import time
import threading

class objectHashHolder(threading.Thread):
    def __init__(self, sendDataThreadMailbox):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.sendDataThreadMailbox = sendDataThreadMailbox # This queue is used to submit data back to our associated sendDataThread.
        self.collectionOfLists = {}
        for i in range(10):
            self.collectionOfLists[i] = []

    def run(self):
        iterator = 0
        while not self.shutdown:
            if len(self.collectionOfLists[iterator]) > 0:
                self.sendDataThreadMailbox.put((0, 'sendinv', self.collectionOfLists[iterator]))
                self.collectionOfLists[iterator] = []
            iterator += 1
            iterator %= 10
            time.sleep(1)

    def holdHash(self,hash):
        self.collectionOfLists[random.randrange(0, 10)].append(hash)

    def close(self):
        self.shutdown = True