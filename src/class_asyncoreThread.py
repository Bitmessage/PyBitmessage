import asyncore
import shared
import threading
import time

class asyncoreThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        with shared.printLock:
            print "Asyncore thread started"

        while True:
            asyncore.loop(timeout=1) # Despite the horrible parameter name, this function will not timeout until all channels are closed.
            time.sleep(1)

