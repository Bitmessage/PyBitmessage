# objectHashHolder is a timer-driven thread. One objectHashHolder thread is used
# by each sendDataThread. The sendDataThread uses it whenever it needs to
# advertise an object to peers in an inv message, or advertise a peer to other
# peers in an addr message. Instead of sending them out immediately, it must
# wait a random number of seconds for each connection so that different peers
# get different objects at different times. Thus an attacker who is
# connecting to many network nodes who receives a message first from Alice
# cannot be sure if Alice is the node who originated the message.

import random
import time
import threading

class objectHashHolder(threading.Thread):
    size = 10
    def __init__(self, sendDataThreadMailbox):
        threading.Thread.__init__(self, name="objectHashHolder")
        self.shutdown = False
        self.sendDataThreadMailbox = sendDataThreadMailbox # This queue is used to submit data back to our associated sendDataThread.
        self.collectionOfHashLists = []
        self.collectionOfPeerLists = []
        for i in range(objectHashHolder.size):
            self.collectionOfHashLists.append([])
            self.collectionOfPeerLists.append([])

    def run(self):
        iterator = 0
        while not self.shutdown:
            if len(self.collectionOfHashLists[iterator]) > 0:
                self.sendDataThreadMailbox.put((0, 'sendinv', self.collectionOfHashLists[iterator]))
                self.collectionOfHashLists[iterator] = []
            if len(self.collectionOfPeerLists[iterator]) > 0:
                self.sendDataThreadMailbox.put((0, 'sendaddr', self.collectionOfPeerLists[iterator]))
                self.collectionOfPeerLists[iterator] = []
            iterator += 1
            iterator %= objectHashHolder.size
            time.sleep(1)

    def holdHash(self,hash):
        self.collectionOfHashLists[random.randrange(0, objectHashHolder.size)].append(hash)

    def hasHash(self, hash):
        if hash in (hashlist for hashlist in self.collectionOfHashLists):
            return True
        return False

    def holdPeer(self,peerDetails):
        self.collectionOfPeerLists[random.randrange(0, objectHashHolder.size)].append(peerDetails)
        
    def hashCount(self):
        return sum([len(x) for x in self.collectionOfHashLists if type(x) is list])

    def close(self):
        self.shutdown = True
