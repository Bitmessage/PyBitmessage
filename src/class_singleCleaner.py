import threading
import shared
import time
import sys

'''The singleCleaner class is a timer-driven thread that cleans data structures to free memory, resends messages when a remote node doesn't respond, and sends pong messages to keep connections alive if the network isn't busy.
It cleans these data structures in memory:
    inventory (moves data to the on-disk sql database)

It cleans these tables on the disk:
    inventory (clears data more than 2 days and 12 hours old)
    pubkeys (clears pubkeys older than 4 weeks old which we have not used personally)

It resends messages when there has been no response:
    resends getpubkey messages in 4 days (then 8 days, then 16 days, etc...)
    resends msg messages in 4 days (then 8 days, then 16 days, etc...)

'''


class singleCleaner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        timeWeLastClearedInventoryAndPubkeysTables = 0

        while True:
            shared.sqlLock.acquire()
            shared.UISignalQueue.put((
                'updateStatusBar', 'Doing housekeeping (Flushing inventory in memory to disk...)'))
            for hash, storedValue in shared.inventory.items():
                objectType, streamNumber, payload, receivedTime = storedValue
                if int(time.time()) - 3600 > receivedTime:
                    t = (hash, objectType, streamNumber, payload, receivedTime)
                    shared.sqlSubmitQueue.put(
                        '''INSERT INTO inventory VALUES (?,?,?,?,?)''')
                    shared.sqlSubmitQueue.put(t)
                    shared.sqlReturnQueue.get()
                    del shared.inventory[hash]
            shared.sqlSubmitQueue.put('commit')
            shared.UISignalQueue.put(('updateStatusBar', ''))
            shared.sqlLock.release()
            shared.broadcastToSendDataQueues((
                0, 'pong', 'no data'))  # commands the sendData threads to send out a pong message if they haven't sent anything else in the last five minutes. The socket timeout-time is 10 minutes.
            # If we are running as a daemon then we are going to fill up the UI
            # queue which will never be handled by a UI. We should clear it to
            # save memory.
            if shared.safeConfigGetBoolean('bitmessagesettings', 'daemon'):
                shared.UISignalQueue.queue.clear()
            if timeWeLastClearedInventoryAndPubkeysTables < int(time.time()) - 7380:
                timeWeLastClearedInventoryAndPubkeysTables = int(time.time())
                # inventory (moves data from the inventory data structure to
                # the on-disk sql database)
                shared.sqlLock.acquire()
                # inventory (clears pubkeys after 28 days and everything else
                # after 2 days and 12 hours)
                t = (int(time.time()) - shared.lengthOfTimeToLeaveObjectsInInventory, int(
                    time.time()) - shared.lengthOfTimeToHoldOnToAllPubkeys)
                shared.sqlSubmitQueue.put(
                    '''DELETE FROM inventory WHERE (receivedtime<? AND objecttype<>'pubkey') OR (receivedtime<?  AND objecttype='pubkey') ''')
                shared.sqlSubmitQueue.put(t)
                shared.sqlReturnQueue.get()

                # pubkeys
                t = (int(time.time()) - shared.lengthOfTimeToHoldOnToAllPubkeys,)
                shared.sqlSubmitQueue.put(
                    '''DELETE FROM pubkeys WHERE time<? AND usedpersonally='no' ''')
                shared.sqlSubmitQueue.put(t)
                shared.sqlReturnQueue.get()
                shared.sqlSubmitQueue.put('commit')

                t = ()
                shared.sqlSubmitQueue.put(
                    '''select toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, pubkeyretrynumber, msgretrynumber FROM sent WHERE ((status='awaitingpubkey' OR status='msgsent') AND folder='sent') ''')  # If the message's folder='trash' then we'll ignore it.
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                for row in queryreturn:
                    if len(row) < 5:
                        with shared.printLock:
                            sys.stderr.write(
                                'Something went wrong in the singleCleaner thread: a query did not return the requested fields. ' + repr(row))
                        time.sleep(3)

                        break
                    toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, pubkeyretrynumber, msgretrynumber = row
                    if status == 'awaitingpubkey':
                        if int(time.time()) - lastactiontime > (shared.maximumAgeOfAnObjectThatIAmWillingToAccept * (2 ** (pubkeyretrynumber))):
                            print 'It has been a long time and we haven\'t heard a response to our getpubkey request. Sending again.'
                            try:
                                del shared.neededPubkeys[
                                    toripe]  # We need to take this entry out of the shared.neededPubkeys structure because the shared.workerQueue checks to see whether the entry is already present and will not do the POW and send the message because it assumes that it has already done it recently.
                            except:
                                pass

                            shared.UISignalQueue.put((
                                'updateStatusBar', 'Doing work necessary to again attempt to request a public key...'))
                            t = (int(
                                time.time()), pubkeyretrynumber + 1, toripe)
                            shared.sqlSubmitQueue.put(
                                '''UPDATE sent SET lastactiontime=?, pubkeyretrynumber=?, status='msgqueued' WHERE toripe=?''')
                            shared.sqlSubmitQueue.put(t)
                            shared.sqlReturnQueue.get()
                            shared.sqlSubmitQueue.put('commit')
                            shared.workerQueue.put(('sendmessage', ''))
                    else:  # status == msgsent
                        if int(time.time()) - lastactiontime > (shared.maximumAgeOfAnObjectThatIAmWillingToAccept * (2 ** (msgretrynumber))):
                            print 'It has been a long time and we haven\'t heard an acknowledgement to our msg. Sending again.'
                            t = (int(
                                time.time()), msgretrynumber + 1, 'msgqueued', ackdata)
                            shared.sqlSubmitQueue.put(
                                '''UPDATE sent SET lastactiontime=?, msgretrynumber=?, status=? WHERE ackdata=?''')
                            shared.sqlSubmitQueue.put(t)
                            shared.sqlReturnQueue.get()
                            shared.sqlSubmitQueue.put('commit')
                            shared.workerQueue.put(('sendmessage', ''))
                            shared.UISignalQueue.put((
                                'updateStatusBar', 'Doing work necessary to again attempt to deliver a message...'))
                shared.sqlSubmitQueue.put('commit')
                shared.sqlLock.release()
            time.sleep(300)
