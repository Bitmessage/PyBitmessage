"""
The singleCleaner class is a timer-driven thread that cleans data structures
to free memory, resends messages when a remote node doesn't respond, and
sends pong messages to keep connections alive if the network isn't busy.
It cleans these data structures in memory:
inventory (moves data to the on-disk sql database)
inventorySets (clears then reloads data out of sql database)

It cleans these tables on the disk:
inventory (clears expired objects)
pubkeys (clears pubkeys older than 4 weeks old which we have not used
 personally)
knownNodes (clears addresses which have not been online for over 3 days)

It resends messages when there has been no response:
resends getpubkey messages in 5 days (then 10 days, then 20 days, etc...)
resends msg messages in 5 days (then 10 days, then 20 days, etc...)

"""

import gc
import os
import shared
import threading
import time

import tr
from bmconfigparser import BMConfigParser
from helper_sql import sqlQuery, sqlExecute
from helper_threading import StoppableThread
from inventory import Inventory
from network.connectionpool import BMConnectionPool
from debug import logger
import knownnodes
import queues
import state

def resendStaleMessages():
    staleMessages = sqlQuery("""
        SELECT "toaddress", "ackdata", "status" FROM "sent"
        WHERE "status" IN ('awaitingpubkey', 'msgsent') AND "sleeptill" < ? AND "senttime" > ? AND "folder" == 'sent';
    """, int(time.time()), int(time.time()) - shared.maximumLengthOfTimeToBotherResendingMessages)

    resendMessages = False

    for destination, ackData, status in staleMessages:
        if status == "awaitingpubkey":
            logger.info("Retrying getpubkey request for %s", destination)

            sqlExecute("""
                UPDATE "sent" SET "status" = 'msgqueued'
                WHERE "status" == 'awaitingpubkey' AND "ackdata" == ?;
            """, ackData)
        elif status == "msgsent":
            state.watchedAckData -= {ackData}

            sqlExecute("""
                UPDATE "sent" SET "status" = 'msgqueued'
                WHERE "status" == 'msgsent' AND "ackdata" == ?;
            """, ackData)

        queues.UISignalQueue.put(("updateSentItemStatusByAckdata", (
            ackData,
            tr._translate(
                "MainWindow",
                "Queued."
            )
        )))

        resendMessages = True

    if resendMessages:
        logger.info("Resending old messages with undelivered acks or unknown pubkeys")

        queues.workerQueue.put(("sendmessage", ))

class singleCleaner(threading.Thread, StoppableThread):
    cycleLength = 300
    expireDiscoveredPeers = 300

    def __init__(self):
        threading.Thread.__init__(self, name="singleCleaner")
        self.initStop()

    def run(self):
        gc.disable()
        timeWeLastClearedInventoryAndPubkeysTables = 0
        try:
            shared.maximumLengthOfTimeToBotherResendingMessages = (
                float(BMConfigParser().get(
                    'bitmessagesettings', 'stopresendingafterxdays')) *
                24 * 60 * 60
            ) + (
                float(BMConfigParser().get(
                    'bitmessagesettings', 'stopresendingafterxmonths')) *
                (60 * 60 * 24 * 365)/12)
        except:
            # Either the user hasn't set stopresendingafterxdays and
            # stopresendingafterxmonths yet or the options are missing
            # from the config file.
            shared.maximumLengthOfTimeToBotherResendingMessages = float('inf')

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
            if shared.thisapp.daemon or not state.enableGUI:
                queues.UISignalQueue.queue.clear()
            if timeWeLastClearedInventoryAndPubkeysTables < \
                    int(time.time()) - 7380:
                timeWeLastClearedInventoryAndPubkeysTables = int(time.time())
                Inventory().clean()
                # pubkeys
                sqlExecute(
                    "DELETE FROM pubkeys WHERE time<? AND usedpersonally='no'",
                    int(time.time()) - shared.lengthOfTimeToHoldOnToAllPubkeys)

                # Let us resend getpubkey objects if we have not yet heard
                # a pubkey, and also msg objects if we have not yet heard
                # an acknowledgement

                resendStaleMessages()

            # cleanup old nodes
            now = int(time.time())

            with knownnodes.knownNodesLock:
                for stream in knownnodes.knownNodes:
                    keys = knownnodes.knownNodes[stream].keys()
                    for node in keys:
                        try:
                            # scrap old nodes
                            if now - knownnodes.knownNodes[stream][node]["lastseen"] > 2419200: # 28 days
                                shared.needToWriteKnownNodesToDisk = True
                                del knownnodes.knownNodes[stream][node]
                                continue
                            # scrap old nodes with low rating
                            if now - knownnodes.knownNodes[stream][node]["lastseen"] > 10800 and knownnodes.knownNodes[stream][node]["rating"] <= knownnodes.knownNodesForgetRating:
                                shared.needToWriteKnownNodesToDisk = True
                                del knownnodes.knownNodes[stream][node]
                                continue
                        except TypeError:
                            print "Error in %s" % node
                    keys = []

            # Let us write out the knowNodes to disk
            # if there is anything new to write out.
            if shared.needToWriteKnownNodesToDisk:
                try:
                    knownnodes.saveKnownNodes()
                except Exception as err:
                    if "Errno 28" in str(err):
                        logger.fatal(
                            '(while receiveDataThread'
                            ' knownnodes.needToWriteKnownNodesToDisk)'
                            ' Alert: Your disk or data storage volume'
                            ' is full. '
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
                        if shared.daemon or not state.enableGUI:
                            os._exit(0)
                shared.needToWriteKnownNodesToDisk = False

#            # clear download queues
#            for thread in threading.enumerate():
#                if thread.isAlive() and hasattr(thread, 'downloadQueue'):
#                    thread.downloadQueue.clear()

            # inv/object tracking
            for connection in \
                    BMConnectionPool().inboundConnections.values() + \
                    BMConnectionPool().outboundConnections.values():
                connection.clean()

            # discovery tracking
            exp = time.time() - singleCleaner.expireDiscoveredPeers
            reaper = (k for k, v in state.discoveredPeers.items() if v < exp)
            for k in reaper:
                try:
                    del state.discoveredPeers[k]
                except KeyError:
                    pass
            # TODO: cleanup pending upload / download

            gc.collect()

            if state.shutdown == 0:
                self.stop.wait(singleCleaner.cycleLength)
