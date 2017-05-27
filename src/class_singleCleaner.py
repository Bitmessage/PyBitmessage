import threading
import shared
import time
import sys
import os

import tr#anslate
from bmconfigparser import BMConfigParser
from helper_sql import *
from helper_threading import *
from inventory import Inventory
from debug import logger
import knownnodes
import queues
import protocol
import state

"""
The singleCleaner class is a timer-driven thread that cleans data structures 
to free memory, resends messages when a remote node doesn't respond, and 
sends pong messages to keep connections alive if the network isn't busy.
It cleans these data structures in memory:
inventory (moves data to the on-disk sql database)
inventorySets (clears then reloads data out of sql database)

It cleans these tables on the disk:
inventory (clears expired objects)
pubkeys (clears pubkeys older than 4 weeks old which we have not used personally)
knownNodes (clears addresses which have not been online for over 3 days)

It resends messages when there has been no response:
resends getpubkey messages in 5 days (then 10 days, then 20 days, etc...)
resends msg messages in 5 days (then 10 days, then 20 days, etc...)

"""


class singleCleaner(threading.Thread, StoppableThread):

    def __init__(self):
        threading.Thread.__init__(self, name="singleCleaner")
        self.initStop()

    def run(self):
        timeWeLastClearedInventoryAndPubkeysTables = 0
        try:
            shared.maximumLengthOfTimeToBotherResendingMessages = (float(BMConfigParser().get('bitmessagesettings', 'stopresendingafterxdays')) * 24 * 60 * 60) + (float(BMConfigParser().get('bitmessagesettings', 'stopresendingafterxmonths')) * (60 * 60 * 24 *365)/12)
        except:
            # Either the user hasn't set stopresendingafterxdays and stopresendingafterxmonths yet or the options are missing from the config file.
            shared.maximumLengthOfTimeToBotherResendingMessages = float('inf')

        # initial wait
        if state.shutdown == 0:
            self.stop.wait(300)

        while state.shutdown == 0:
            queues.UISignalQueue.put((
                'updateStatusBar', 'Doing housekeeping (Flushing inventory in memory to disk...)'))
            Inventory().flush()
            queues.UISignalQueue.put(('updateStatusBar', ''))
            
            protocol.broadcastToSendDataQueues((
                0, 'pong', 'no data')) # commands the sendData threads to send out a pong message if they haven't sent anything else in the last five minutes. The socket timeout-time is 10 minutes.
            # If we are running as a daemon then we are going to fill up the UI
            # queue which will never be handled by a UI. We should clear it to
            # save memory.
            if BMConfigParser().safeGetBoolean('bitmessagesettings', 'daemon'):
                queues.UISignalQueue.queue.clear()
            if timeWeLastClearedInventoryAndPubkeysTables < int(time.time()) - 7380:
                timeWeLastClearedInventoryAndPubkeysTables = int(time.time())
                Inventory().clean()
                # pubkeys
                sqlExecute(
                    '''DELETE FROM pubkeys WHERE time<? AND usedpersonally='no' ''',
                    int(time.time()) - shared.lengthOfTimeToHoldOnToAllPubkeys)

                # Let us resend getpubkey objects if we have not yet heard a pubkey, and also msg objects if we have not yet heard an acknowledgement
                queryreturn = sqlQuery(
                    '''select toaddress, ackdata, status FROM sent WHERE ((status='awaitingpubkey' OR status='msgsent') AND folder='sent' AND sleeptill<? AND senttime>?) ''',
                    int(time.time()),
                    int(time.time()) - shared.maximumLengthOfTimeToBotherResendingMessages)
                for row in queryreturn:
                    if len(row) < 2:
                        logger.error('Something went wrong in the singleCleaner thread: a query did not return the requested fields. ' + repr(row))
                        self.stop.wait(3)
                        break
                    toAddress, ackData, status = row
                    if status == 'awaitingpubkey':
                        resendPubkeyRequest(toAddress)
                    elif status == 'msgsent':
                        resendMsg(ackData)

            # cleanup old nodes
            now = int(time.time())
            toDelete = []
            with knownnodes.knownNodesLock:
                for stream in knownnodes.knownNodes:
                    for node in knownnodes.knownNodes[stream].keys():
                        if now - knownnodes.knownNodes[stream][node] > 2419200: # 28 days
                            shared.needToWriteKownNodesToDisk = True
                            del knownnodes.knownNodes[stream][node]

            # Let us write out the knowNodes to disk if there is anything new to write out.
            if shared.needToWriteKnownNodesToDisk:
                try:
                    knownnodes.saveKnownNodes()
                except Exception as err:
                    if "Errno 28" in str(err):
                        logger.fatal('(while receiveDataThread knownnodes.needToWriteKnownNodesToDisk) Alert: Your disk or data storage volume is full. ')
                        queues.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                        if shared.daemon:
                            os._exit(0)
                shared.needToWriteKnownNodesToDisk = False

            # clear download queues
            for thread in threading.enumerate():
                if thread.isAlive() and hasattr(thread, 'downloadQueue'):
                    thread.downloadQueue.clear()

            # TODO: cleanup pending upload / download

            if state.shutdown == 0:
                self.stop.wait(300)


def resendPubkeyRequest(address):
    logger.debug('It has been a long time and we haven\'t heard a response to our getpubkey request. Sending again.')
    try:
        del state.neededPubkeys[
            address] # We need to take this entry out of the neededPubkeys structure because the queues.workerQueue checks to see whether the entry is already present and will not do the POW and send the message because it assumes that it has already done it recently.
    except:
        pass

    queues.UISignalQueue.put((
         'updateStatusBar', 'Doing work necessary to again attempt to request a public key...'))
    sqlExecute(
        '''UPDATE sent SET status='msgqueued' WHERE toaddress=?''',
        address)
    queues.workerQueue.put(('sendmessage', ''))

def resendMsg(ackdata):
    logger.debug('It has been a long time and we haven\'t heard an acknowledgement to our msg. Sending again.')
    sqlExecute(
        '''UPDATE sent SET status='msgqueued' WHERE ackdata=?''',
        ackdata)
    queues.workerQueue.put(('sendmessage', ''))
    queues.UISignalQueue.put((
    'updateStatusBar', 'Doing work necessary to again attempt to deliver a message...'))
