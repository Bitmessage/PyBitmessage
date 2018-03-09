"""
0.6.3+ SPECIALOPMODES - STDIO handling threads for netcat and airgap modes

stdInput thread: receives hex-encoded bitmessage objects on STDIN
Supported input formats, format is auto-detected:
  - each line a hex-encoded object
  - each line formatted: hex_timestamp - tab - hex-encoded_object
    (the output format of netcat mode)

objectStdOut thread: replaces the objectProcessor thread in netcat mode,
  outputs to STDOUT in format: hex_timestamp - tab - hex-encoded_object
"""

import threading
import time
from struct import unpack
from binascii import hexlify, unhexlify
from addresses import decodeVarint, calculateInventoryHash
from debug import logger
# 0.6.2+ imports
import protocol
import queues
import state
import shutdown
import shared # statusIconColor
from inventory import Inventory
from helper_sql import sqlQuery, sqlExecute, SqlBulkExecute

stdInputMode = 'netcat' # process STDIN in netcat mode by default

class stdInput(threading.Thread):
    """ Standard Input thread """

    def __init__(self, inputSrc):
        threading.Thread.__init__(self, name="stdInput")
        self.inputSrc = inputSrc
        logger.info('stdInput thread started.')

    def run(self):
        while True:

            # read a line in hex encoding
            line = self.inputSrc.readline()
            if len(line) == 0:
                logger.info("STDIN: End of input")
                shutdown.doCleanShutdown()
                break

            hexObject = line.rstrip()
            hexTStamp = ''

            # detect timestamp-tab-object format (as output by netcat mode)
            if "\t" in hexObject:
                hexTStamp = hexObject.split("\t")[0]
                hexObject = hexObject.split("\t")[-1]

            # unhex the input with error rejection
            try:
                binObject = unhexlify(hexObject)
            except Exception:
                logger.info("STDIN: Invalid input format")
                continue

            # sanity check on object size
            if len(binObject) < 22:
                logger.info("STDIN: Invalid object size")
                continue

            if not state.enableNetwork and state.enableGUI:
                # in airgap mode, trick the status icon that we are in fact
                #   NOT waiting for a connection
                # (may be removed after impact analysis)
                shared.statusIconColor = 'yellow'

            if stdInputMode == 'airgap':
                # airgap mode uses the timestamp
                # unhex the timestamp with error rejection
                if len(hexTStamp) == 16:
                    try:
                        # stdioStamp, = unpack('>Q', unhexlify(hexTStamp))
                        _, = unpack('>Q', unhexlify(hexTStamp))
                    except Exception:
                        logger.info("STDIN: Invalid timestamp format: " + hexTStamp)
                        continue

            # check that proof of work is sufficient.
            if not protocol.isProofOfWorkSufficient(binObject):
                logger.info('STDIN: Insufficient Proof of Work')
                continue

            # extract expiry time, object type
            eTime, = unpack('>Q', binObject[8:16])
            objectType, = unpack('>I', binObject[16:20])

            # extract version number and stream number
            readPosition = 20  # bypass the nonce, time, and object type
            # versionNumber, versionLength
            _, versionLength = decodeVarint(binObject[readPosition:readPosition + 10])
            readPosition += versionLength
            streamNumber, streamNumberLength = decodeVarint(binObject[readPosition:readPosition + 10])
            readPosition += streamNumberLength

            # calculate inventory hash
            inventoryHash = calculateInventoryHash(binObject)

            # duplicate check on inventory hash (both netcat and airgap)
            if inventoryHash in Inventory():
                logger.info("STDIN: Already got object " + hexlify(inventoryHash))
                continue

            # in netcat mode, push object to TX inventory (for broadcasting)
            if stdInputMode == 'netcat':
                # publish object to inventory and advertise
                Inventory()[inventoryHash] = (objectType, streamNumber, binObject, eTime, '')
                logger.info("STDIN: Accepted object (type=%u) " % objectType + hexlify(inventoryHash))
                queues.invQueue.put((streamNumber, inventoryHash))

            # honour global shutdown flag
            if state.shutdown != 0:
                logger.info('stdInput thread shutdown.')
                break

class objectStdOut(threading.Thread):
    """
    The objectStdOut thread receives network objects from the receiveDataThreads.
    """
    def __init__(self):
        threading.Thread.__init__(self, name="objectStdOut")

        # REFACTOR THIS with objectProcessor into objectProcessorQueue
        queryreturn = sqlQuery(
            '''SELECT objecttype, data FROM objectprocessorqueue''')
        for row in queryreturn:
            objectType, data = row
            queues.objectProcessorQueue.put((objectType, data))
        sqlExecute('''DELETE FROM objectprocessorqueue''')
        logger.debug('Loaded %s objects from disk into the objectProcessorQueue.' % str(len(queryreturn)))
        # /REFACTOR THIS

    def run(self):
        while True:
            objectType, data = queues.objectProcessorQueue.get()

            # Output in documented format
            print "%016x" % int(time.time()) + '\t' + hexlify(data)

            if state.shutdown:
                time.sleep(.5) # Wait just a moment for most of the connections to close

                # REFACTOR THIS with objectProcessor into objectProcessorQueue
                numberOfObjectsInObjProcQueue = 0
                with SqlBulkExecute() as sql:
                    while queues.objectProcessorQueue.curSize > 0:
                        objectType, data = queues.objectProcessorQueue.get()
                        sql.execute('''INSERT INTO objectprocessorqueue VALUES (?,?)''',
                                   objectType, data)
                        numberOfObjectsInObjProcQueue += 1
                logger.debug('Saved %s objects from the objectProcessorQueue to disk. objectProcessorThread exiting.' % str(numberOfObjectsInObjProcQueue))
                # /REFACTOR THIS

                state.shutdown = 2
                break

