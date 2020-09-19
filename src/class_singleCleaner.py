"""
The `singleCleaner` class is a timer-driven thread that cleans data structures
to free memory, resends messages when a remote node doesn't respond, and
sends pong messages to keep connections alive if the network isn't busy.

It cleans these data structures in memory:
  - inventory (moves data to the on-disk sql database)
  - inventorySets (clears then reloads data out of sql database)

It cleans these tables on the disk:
  - inventory (clears expired objects)
  - pubkeys (clears pubkeys older than 4 weeks old which we have not used
    personally)
  - knownNodes (clears addresses which have not been online for over 3 days)

It resends messages when there has been no response:
  - resends getpubkey messages in 5 days (then 10 days, then 20 days, etc...)
  - resends msg messages in 5 days (then 10 days, then 20 days, etc...)

"""

import gc
import os
import time

import queues
import state
import tr
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from inventory import Inventory
from network import BMConnectionPool, knownnodes, StoppableThread


#: Equals 4 weeks. You could make this longer if you want
#: but making it shorter would not be advisable because
#: there is a very small possibility that it could keep you
#: from obtaining a needed pubkey for a period of time.
lengthOfTimeToHoldOnToAllPubkeys = 2419200


class singleCleaner(StoppableThread):
    """The singleCleaner thread class"""
    name = "singleCleaner"
    cycleLength = 300
    expireDiscoveredPeers = 300

    def run(self):  # pylint: disable=too-many-branches
        gc.disable()
        timeWeLastClearedInventoryAndPubkeysTables = 0
        try:
            state.maximumLengthOfTimeToBotherResendingMessages = (
                float(BMConfigParser().get(
                    'bitmessagesettings', 'stopresendingafterxdays'))
                * 24 * 60 * 60
            ) + (
                float(BMConfigParser().get(
                    'bitmessagesettings', 'stopresendingafterxmonths'))
                * (60 * 60 * 24 * 365) / 12)
        except:
            # Either the user hasn't set stopresendingafterxdays and
            # stopresendingafterxmonths yet or the options are missing
            # from the config file.
            state.maximumLengthOfTimeToBotherResendingMessages = float('inf')

        # initial wait
        if state.shutdown == 0:
            self.stop.wait(singleCleaner.cycleLength)

        while state.shutdown == 0:
            queues.UISignalQueue.put((
                'updateStatusBar',
                'Doing housekeeping (Flushing inventory in memory to disk...)'
            ))
            Inventory().flush()
            queues.UISignalQueue.put(('updateStatusBar', ''))

            # If we are running as a daemon then we are going to fill up the UI
            # queue which will never be handled by a UI. We should clear it to
            # save memory.
            # FIXME redundant?
            if state.thisapp.daemon or not state.enableGUI:
                queues.UISignalQueue.queue.clear()
            if timeWeLastClearedInventoryAndPubkeysTables < \
                    int(time.time()) - 7380:
                timeWeLastClearedInventoryAndPubkeysTables = int(time.time())
                Inventory().clean()
                queues.workerQueue.put(('sendOnionPeerObj', ''))
                # pubkeys
                sqlExecute(
                    "DELETE FROM pubkeys WHERE time<? AND usedpersonally='no'",
                    int(time.time()) - lengthOfTimeToHoldOnToAllPubkeys)

                # Let us resend getpubkey objects if we have not yet heard
                # a pubkey, and also msg objects if we have not yet heard
                # an acknowledgement
                queryreturn = sqlQuery(
                    "SELECT toaddress, ackdata, status FROM sent"
                    " WHERE ((status='awaitingpubkey' OR status='msgsent')"
                    " AND folder='sent' AND sleeptill<? AND senttime>?)",
                    int(time.time()), int(time.time())
                    - state.maximumLengthOfTimeToBotherResendingMessages
                )
                for row in queryreturn:
                    if len(row) < 2:
                        self.logger.error(
                            'Something went wrong in the singleCleaner thread:'
                            ' a query did not return the requested fields. %r',
                            row
                        )
                        self.stop.wait(3)
                        break
                    toAddress, ackData, status = row
                    if status == 'awaitingpubkey':
                        self.resendPubkeyRequest(toAddress)
                    elif status == 'msgsent':
                        self.resendMsg(ackData)

            try:
                # Cleanup knownnodes and handle possible severe exception
                # while writing it to disk
                knownnodes.cleanupKnownNodes()
            except Exception as err:
                # pylint: disable=protected-access
                if "Errno 28" in str(err):
                    self.logger.fatal(
                        '(while writing knownnodes to disk)'
                        ' Alert: Your disk or data storage volume is full.'
                    )
                    queues.UISignalQueue.put((
                        'alert',
                        (tr._translate("MainWindow", "Disk full"),
                         tr._translate(
                             "MainWindow",
                             'Alert: Your disk or data storage volume'
                             ' is full. Bitmessage will now exit.'),
                         True)
                    ))
                    # FIXME redundant?
                    if state.thisapp.daemon or not state.enableGUI:
                        os._exit(1)

            # inv/object tracking
            for connection in BMConnectionPool().connections():
                connection.clean()

            # discovery tracking
            exp = time.time() - singleCleaner.expireDiscoveredPeers
            reaper = (k for k, v in state.discoveredPeers.items() if v < exp)
            for k in reaper:
                try:
                    del state.discoveredPeers[k]
                except KeyError:
                    pass
            # ..todo:: cleanup pending upload / download

            gc.collect()

            if state.shutdown == 0:
                self.stop.wait(singleCleaner.cycleLength)

    def resendPubkeyRequest(self, address):
        """Resend pubkey request for address"""
        self.logger.debug(
            'It has been a long time and we haven\'t heard a response to our'
            ' getpubkey request. Sending again.'
        )
        try:
            # We need to take this entry out of the neededPubkeys structure
            # because the queues.workerQueue checks to see whether the entry
            # is already present and will not do the POW and send the message
            # because it assumes that it has already done it recently.
            del state.neededPubkeys[address]
        except:
            pass

        queues.UISignalQueue.put((
            'updateStatusBar',
            'Doing work necessary to again attempt to request a public key...'
        ))
        sqlExecute(
            '''UPDATE sent SET status='msgqueued' WHERE toaddress=? AND folder='sent' ''',
            address)
        queues.workerQueue.put(('sendmessage', ''))

    def resendMsg(self, ackdata):
        """Resend message by ackdata"""
        self.logger.debug(
            'It has been a long time and we haven\'t heard an acknowledgement'
            ' to our msg. Sending again.'
        )
        sqlExecute(
            '''UPDATE sent SET status='msgqueued' WHERE ackdata=? AND folder='sent' ''',
            ackdata)
        queues.workerQueue.put(('sendmessage', ''))
        queues.UISignalQueue.put((
            'updateStatusBar',
            'Doing work necessary to again attempt to deliver a message...'
        ))
