"""
The objectProcessor thread, of which there is only one, processes the network objects
"""
import hashlib
import logging
import random
import threading
import time
from binascii import hexlify
from subprocess import call  # nosec

import highlevelcrypto
import knownnodes
import shared
from addresses import (
    calculateInventoryHash, decodeAddress, decodeVarint, encodeAddress,
    encodeVarint, varintDecodeError
)
from bmconfigparser import BMConfigParser

import helper_bitcoin
import helper_inbox
import helper_msgcoding
import helper_sent
from helper_sql import SqlBulkExecute, sqlExecute, sqlQuery
from helper_ackPayload import genAckPayload
from network import bmproto
from network.node import Peer

import protocol
import queues
import state
import tr
from fallback import RIPEMD160Hash

import l10n
# pylint: disable=too-many-locals, too-many-return-statements
# pylint: disable=too-many-branches, too-many-statements

logger = logging.getLogger('default')


class objectProcessor(threading.Thread):
    """
    The objectProcessor thread, of which there is only one, receives network
    objects (msg, broadcast, pubkey, getpubkey) from the receiveDataThreads.
    """
    def __init__(self):
        threading.Thread.__init__(self, name="objectProcessor")
        random.seed()
        # It may be the case that the last time Bitmes0sage was running,
        # the user closed it before it finished processing everything in the
        # objectProcessorQueue. Assuming that Bitmessage wasn't closed
        # forcefully, it should have saved the data in the queue into the
        # objectprocessorqueue table. Let's pull it out.
        queryreturn = sqlQuery(
            '''SELECT objecttype, data FROM objectprocessorqueue''')
        for row in queryreturn:
            objectType, data = row
            queues.objectProcessorQueue.put((objectType, data))
        sqlExecute('''DELETE FROM objectprocessorqueue''')
        logger.debug(
            'Loaded %s objects from disk into the objectProcessorQueue.',
            len(queryreturn))
        self._ack_obj = bmproto.BMStringParser()
        self.successfullyDecryptMessageTimings = []

    def run(self):
        """Process the objects from `.queues.objectProcessorQueue`"""
        while True:
            objectType, data = queues.objectProcessorQueue.get()
            self.checkackdata(data)
            try:
                if objectType == protocol.OBJECT_GETPUBKEY:
                    self.processgetpubkey(data)
                elif objectType == protocol.OBJECT_PUBKEY:
                    self.processpubkey(data)
                elif objectType == protocol.OBJECT_MSG:
                    self.processmsg(data)
                elif objectType == protocol.OBJECT_BROADCAST:
                    self.processbroadcast(data)
                elif objectType == protocol.OBJECT_ONIONPEER:
                    self.processonion(data)
                # is more of a command, not an object type. Is used to get
                # this thread past the queue.get() so that it will check
                # the shutdown variable.
                elif objectType == 'checkShutdownVariable':
                    pass
                else:
                    if isinstance(objectType, int):
                        logger.info(
                            'Don\'t know how to handle object type 0x%08X',
                            objectType)
                    else:
                        logger.info(
                            'Don\'t know how to handle object type %s',
                            objectType)
            except helper_msgcoding.DecompressionSizeException as e:
                logger.error(
                    'The object is too big after decompression (stopped'
                    ' decompressing at %ib, your configured limit %ib).'
                    ' Ignoring',
                    e.size, BMConfigParser().safeGetInt("zlib", "maxsize"))
            except varintDecodeError as e:
                logger.debug(
                    'There was a problem with a varint while processing an'
                    ' object. Some details: %s', e)
            except Exception:
                logger.critical(
                    'Critical error within objectProcessorThread: \n',
                    exc_info=True)

            if state.shutdown:
                # Wait just a moment for most of the connections to close
                time.sleep(.5)
                numberOfObjectsThatWereInTheObjectProcessorQueue = 0
                with SqlBulkExecute() as sql:
                    while queues.objectProcessorQueue.curSize > 0:
                        objectType, data = queues.objectProcessorQueue.get()
                        sql.execute(
                            'INSERT INTO objectprocessorqueue VALUES (?,?)',
                            objectType, data)
                        numberOfObjectsThatWereInTheObjectProcessorQueue += 1
                logger.debug(
                    'Saved %s objects from the objectProcessorQueue to'
                    ' disk. objectProcessorThread exiting.',
                    numberOfObjectsThatWereInTheObjectProcessorQueue)
                state.shutdown = 2
                break

    @staticmethod
    def checkackdata(data):
        """Checking Acknowledgement of message received or not?"""
        # pylint: disable=protected-access
        # Let's check whether this is a message acknowledgement bound for us.
        if len(data) < 32:
            return

        # bypass nonce and time, retain object type/version/stream + body
        readPosition = 16

        if bytes(data[readPosition:]) in shared.ackdataForWhichImWatching:
            logger.info('This object is an acknowledgement bound for me.')
            del shared.ackdataForWhichImWatching[bytes(data[readPosition:])]
            sqlExecute(
                'UPDATE sent SET status=?, lastactiontime=?'
                ' WHERE ackdata=?',
                'ackreceived', int(time.time()), data[readPosition:])
            queues.UISignalQueue.put((
                'updateSentItemStatusByAckdata',
                (
                    data[readPosition:],
                    tr._translate(
                        "MainWindow",
                        "Acknowledgement of the message received %1"
                    ).arg(l10n.formatTimestamp())
                )
            ))
        else:
            logger.debug('This object is not an acknowledgement bound for me.')

    @staticmethod
    def processonion(data):
        """Process onionpeer object"""
        readPosition = 20  # bypass the nonce, time, and object type
        length = decodeVarint(data[readPosition:readPosition + 10])[1]
        readPosition += length
        stream, length = decodeVarint(data[readPosition:readPosition + 10])
        readPosition += length
        # it seems that stream is checked in network.bmproto
        port, length = decodeVarint(data[readPosition:readPosition + 10])
        host = protocol.checkIPAddress(data[readPosition + length:])

        if not host:
            return
        peer = Peer(host, port)
        with knownnodes.knownNodesLock:
            knownnodes.addKnownNode(
                stream, peer, is_self=state.ownAddresses.get(peer))

    @staticmethod
    def processgetpubkey(data):
        """Process getpubkey object"""
        if len(data) > 200:
            logger.info(
                'getpubkey is abnormally long. Sanity check failed.'
                ' Ignoring object.')
            return
        readPosition = 20  # bypass the nonce, time, and object type
        requestedAddressVersionNumber, addressVersionLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += addressVersionLength
        streamNumber, streamNumberLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += streamNumberLength

        if requestedAddressVersionNumber == 0:
            logger.debug(
                'The requestedAddressVersionNumber of the pubkey request'
                ' is zero. That doesn\'t make any sense. Ignoring it.')
            return
        elif requestedAddressVersionNumber == 1:
            logger.debug(
                'The requestedAddressVersionNumber of the pubkey request'
                ' is 1 which isn\'t supported anymore. Ignoring it.')
            return
        elif requestedAddressVersionNumber > 4:
            logger.debug(
                'The requestedAddressVersionNumber of the pubkey request'
                ' is too high. Can\'t understand. Ignoring it.')
            return

        myAddress = ''
        if requestedAddressVersionNumber <= 3:
            requestedHash = data[readPosition:readPosition + 20]
            if len(requestedHash) != 20:
                logger.debug(
                    'The length of the requested hash is not 20 bytes.'
                    ' Something is wrong. Ignoring.')
                return
            logger.info(
                'the hash requested in this getpubkey request is: %s',
                hexlify(requestedHash))
            # if this address hash is one of mine
            if bytes(requestedHash) in shared.myAddressesByHash:
                myAddress = shared.myAddressesByHash[requestedHash]
        elif requestedAddressVersionNumber >= 4:
            requestedTag = data[readPosition:readPosition + 32]
            if len(requestedTag) != 32:
                logger.debug(
                    'The length of the requested tag is not 32 bytes.'
                    ' Something is wrong. Ignoring.')
                return
            logger.debug(
                'the tag requested in this getpubkey request is: %s',
                hexlify(requestedTag))
            if bytes(requestedTag) in shared.myAddressesByTag:
                myAddress = shared.myAddressesByTag[bytes(requestedTag)]

        if myAddress == '':
            logger.info('This getpubkey request is not for any of my keys.')
            return

        if decodeAddress(myAddress)[1] != requestedAddressVersionNumber:
            logger.warning(
                '(Within the processgetpubkey function) Someone requested'
                ' one of my pubkeys but the requestedAddressVersionNumber'
                ' doesn\'t match my actual address version number.'
                ' Ignoring.')
            return
        if decodeAddress(myAddress)[2] != streamNumber:
            logger.warning(
                '(Within the processgetpubkey function) Someone requested'
                ' one of my pubkeys but the stream number on which we'
                ' heard this getpubkey object doesn\'t match this'
                ' address\' stream number. Ignoring.')
            return
        if BMConfigParser().safeGetBoolean(myAddress, 'chan'):
            logger.info(
                'Ignoring getpubkey request because it is for one of my'
                ' chan addresses. The other party should already have'
                ' the pubkey.')
            return
        lastPubkeySendTime = BMConfigParser().safeGetInt(
            myAddress, 'lastpubkeysendtime')
        # If the last time we sent our pubkey was more recent than
        # 28 days ago...
        if lastPubkeySendTime > time.time() - 2419200:
            logger.info(
                'Found getpubkey-requested-item in my list of EC hashes'
                ' BUT we already sent it recently. Ignoring request.'
                ' The lastPubkeySendTime is: %s', lastPubkeySendTime)
            return
        logger.info(
            'Found getpubkey-requested-hash in my list of EC hashes.'
            ' Telling Worker thread to do the POW for a pubkey message'
            ' and send it out.')
        if requestedAddressVersionNumber == 2:
            queues.workerQueue.put(('doPOWForMyV2Pubkey', requestedHash))
        elif requestedAddressVersionNumber == 3:
            queues.workerQueue.put(('sendOutOrStoreMyV3Pubkey', requestedHash))
        elif requestedAddressVersionNumber == 4:
            queues.workerQueue.put(('sendOutOrStoreMyV4Pubkey', myAddress))

    def processpubkey(self, data):
        """Process a pubkey object"""
        pubkeyProcessingStartTime = time.time()
        shared.numberOfPubkeysProcessed += 1
        queues.UISignalQueue.put((
            'updateNumberOfPubkeysProcessed', 'no data'))
        readPosition = 20  # bypass the nonce, time, and object type
        addressVersion, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        if addressVersion == 0:
            logger.debug(
                '(Within processpubkey) addressVersion of 0 doesn\'t'
                ' make sense.')
            return
        if addressVersion > 4 or addressVersion == 1:
            logger.info(
                'This version of Bitmessage cannot handle version %s'
                ' addresses.', addressVersion)
            return
        if addressVersion == 2:
            # sanity check. This is the minimum possible length.
            if len(data) < 146:
                logger.debug(
                    '(within processpubkey) payloadLength less than 146.'
                    ' Sanity check failed.')
                return
            readPosition += 4
            publicSigningKey = data[readPosition:readPosition + 64]
            # Is it possible for a public key to be invalid such that trying to
            # encrypt or sign with it will cause an error? If it is, it would
            # be easiest to test them here.
            readPosition += 64
            publicEncryptionKey = data[readPosition:readPosition + 64]
            if len(publicEncryptionKey) < 64:
                logger.debug(
                    'publicEncryptionKey length less than 64. Sanity check'
                    ' failed.')
                return
            readPosition += 64
            # The data we'll store in the pubkeys table.
            dataToStore = data[20:readPosition]
            sha = hashlib.new('sha512')
            sha.update(
                '\x04'.encode() + publicSigningKey + '\x04'.encode() + publicEncryptionKey)
            ripe = RIPEMD160Hash(sha.digest()).digest()

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    'within recpubkey, addressVersion: %s, streamNumber: %s'
                    '\nripe %s\npublicSigningKey in hex: %s'
                    '\npublicEncryptionKey in hex: %s',
                    addressVersion, streamNumber, hexlify(ripe),
                    hexlify(publicSigningKey), hexlify(publicEncryptionKey)
                )

            address = encodeAddress(addressVersion, streamNumber, ripe)

            queryreturn = sqlQuery(
                "SELECT usedpersonally FROM pubkeys WHERE address=?"
                " AND usedpersonally='yes'", address)
            # if this pubkey is already in our database and if we have
            # used it personally:
            if queryreturn != []:
                logger.info(
                    'We HAVE used this pubkey personally. Updating time.')
                t = (address, addressVersion, dataToStore,
                     int(time.time()), 'yes')
            else:
                logger.info(
                    'We have NOT used this pubkey personally. Inserting'
                    ' in database.')
                t = (address, addressVersion, dataToStore,
                     int(time.time()), 'no')
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
            self.possibleNewPubkey(address)
        if addressVersion == 3:
            if len(data) < 170:  # sanity check.
                logger.warning(
                    '(within processpubkey) payloadLength less than 170.'
                    ' Sanity check failed.')
                return
            readPosition += 4
            publicSigningKey = ('\x04').encode() + data[readPosition:readPosition + 64]
            readPosition += 64
            publicEncryptionKey = ('\x04').encode() + data[readPosition:readPosition + 64]
            readPosition += 64
            _, specifiedNonceTrialsPerByteLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += specifiedNonceTrialsPerByteLength
            _, specifiedPayloadLengthExtraBytesLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += specifiedPayloadLengthExtraBytesLength
            endOfSignedDataPosition = readPosition
            # The data we'll store in the pubkeys table.
            dataToStore = data[20:readPosition]
            signatureLength, signatureLengthLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += signatureLengthLength
            signature = bytes(data[readPosition:readPosition + signatureLength])
            if highlevelcrypto.verify(
                    bytes(data[8:endOfSignedDataPosition]),
                    signature, hexlify(publicSigningKey)):
                logger.debug('ECDSA verify passed (within processpubkey)')
            else:
                logger.warning('ECDSA verify failed (within processpubkey)')
                return

            sha = hashlib.new('sha512')
            sha.update(publicSigningKey + publicEncryptionKey)
            ripe = RIPEMD160Hash(sha.digest()).digest()

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    'within recpubkey, addressVersion: %s, streamNumber: %s'
                    '\nripe %s\npublicSigningKey in hex: %s'
                    '\npublicEncryptionKey in hex: %s',
                    addressVersion, streamNumber, hexlify(ripe),
                    hexlify(publicSigningKey), hexlify(publicEncryptionKey)
                )

            address = encodeAddress(addressVersion, streamNumber, ripe)
            queryreturn = sqlQuery(
                "SELECT usedpersonally FROM pubkeys WHERE address=?"
                " AND usedpersonally='yes'", address)
            # if this pubkey is already in our database and if we have
            # used it personally:
            if queryreturn != []:
                logger.info(
                    'We HAVE used this pubkey personally. Updating time.')
                t = (address, addressVersion, dataToStore,
                     int(time.time()), 'yes')
            else:
                logger.info(
                    'We have NOT used this pubkey personally. Inserting'
                    ' in database.')
                t = (address, addressVersion, dataToStore,
                     int(time.time()), 'no')
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
            self.possibleNewPubkey(address)

        if addressVersion == 4:
            if len(data) < 350:  # sanity check.
                logger.debug(
                    '(within processpubkey) payloadLength less than 350.'
                    ' Sanity check failed.')
                return

            tag = data[readPosition:readPosition + 32]
            if bytes(tag) not in state.neededPubkeys:
                logger.info(
                    'We don\'t need this v4 pubkey. We didn\'t ask for it.')
                return

            # Let us try to decrypt the pubkey
            toAddress, _ = state.neededPubkeys[bytes(tag)] #check with py2
            if protocol.decryptAndCheckPubkeyPayload(bytes(data),   toAddress) == \
                    'successful':
                # At this point we know that we have been waiting on this
                # pubkey. This function will command the workerThread
                # to start work on the messages that require it.
                self.possibleNewPubkey(toAddress)

        # Display timing data
        timeRequiredToProcessPubkey = time.time(
        ) - pubkeyProcessingStartTime
        logger.debug(
            'Time required to process this pubkey: %s',
            timeRequiredToProcessPubkey)

    def processmsg(self, data):
        """Process a message object"""
        messageProcessingStartTime = time.time()
        shared.numberOfMessagesProcessed += 1
        queues.UISignalQueue.put((
            'updateNumberOfMessagesProcessed', 'no data'))
        readPosition = 20  # bypass the nonce, time, and object type
        msgVersion, msgVersionLength = decodeVarint(
            data[readPosition:readPosition + 9])
        if msgVersion != 1:
            logger.info(
                'Cannot understand message versions other than one.'
                ' Ignoring message.')
            return
        readPosition += msgVersionLength

        streamNumberAsClaimedByMsg, streamNumberAsClaimedByMsgLength = \
            decodeVarint(data[readPosition:readPosition + 9])
        readPosition += streamNumberAsClaimedByMsgLength
        inventoryHash = calculateInventoryHash(data)
        initialDecryptionSuccessful = False

        # This is not an acknowledgement bound for me. See if it is a message
        # bound for me by trying to decrypt it with my private keys.
        for key, cryptorObject in sorted(
                shared.myECCryptorObjects.items(),
                key=lambda x: random.random()):
            try:
                # continue decryption attempts to avoid timing attacks
                if initialDecryptionSuccessful:
                    cryptorObject.decrypt(bytes(data[readPosition:]))
                else:
                    decryptedData = cryptorObject.decrypt(bytes(data[readPosition:]))
                    # This is the RIPE hash of my pubkeys. We need this
                    # below to compare to the destination_ripe included
                    # in the encrypted data.
                    toRipe = key
                    initialDecryptionSuccessful = True
                    logger.info(
                        'EC decryption successful using key associated'
                        ' with ripe hash: %s.', hexlify(key))
            except Exception:
                pass
        if not initialDecryptionSuccessful:
            # This is not a message bound for me.
            logger.info(
                'Length of time program spent failing to decrypt this'
                ' message: %s seconds.',
                time.time() - messageProcessingStartTime)
            return

        # This is a message bound for me.
        # Look up my address based on the RIPE hash.
        toAddress = shared.myAddressesByHash[toRipe]
        readPosition = 0
        sendersAddressVersionNumber, sendersAddressVersionNumberLength = \
            decodeVarint(decryptedData[readPosition:readPosition + 10])
        readPosition += sendersAddressVersionNumberLength
        if sendersAddressVersionNumber == 0:
            logger.info(
                'Cannot understand sendersAddressVersionNumber = 0.'
                ' Ignoring message.')
            return
        if sendersAddressVersionNumber > 4:
            logger.info(
                'Sender\'s address version number %s not yet supported.'
                ' Ignoring message.', sendersAddressVersionNumber)
            return
        if len(decryptedData) < 170:
            logger.info(
                'Length of the unencrypted data is unreasonably short.'
                ' Sanity check failed. Ignoring message.')
            return
        sendersStreamNumber, sendersStreamNumberLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        if sendersStreamNumber == 0:
            logger.info('sender\'s stream number is 0. Ignoring message.')
            return
        readPosition += sendersStreamNumberLength
        readPosition += 4
        pubSigningKey = '\x04'.encode() + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        pubEncryptionKey = '\x04'.encode() + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        if sendersAddressVersionNumber >= 3:
            requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = \
                decodeVarint(decryptedData[readPosition:readPosition + 10])
            readPosition += varintLength
            logger.info(
                'sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is %s',
                requiredAverageProofOfWorkNonceTrialsPerByte)
            requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += varintLength
            logger.info(
                'sender\'s requiredPayloadLengthExtraBytes is %s',
                requiredPayloadLengthExtraBytes)
        # needed for when we store the pubkey in our database of pubkeys
        # for later use.
        endOfThePublicKeyPosition = readPosition
        if toRipe != decryptedData[readPosition:readPosition + 20]:
            logger.info(
                'The original sender of this message did not send it to'
                ' you. Someone is attempting a Surreptitious Forwarding'
                ' Attack.\nSee: '
                'http://world.std.com/~dtd/sign_encrypt/sign_encrypt7.html'
                '\nyour toRipe: %s\nembedded destination toRipe: %s',
                hexlify(toRipe),
                hexlify(decryptedData[readPosition:readPosition + 20])
            )
            return
        readPosition += 20
        messageEncodingType, messageEncodingTypeLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += messageEncodingTypeLength
        messageLength, messageLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += messageLengthLength
        message = decryptedData[readPosition:readPosition + messageLength]
        # print 'First 150 characters of message:', repr(message[:150])
        readPosition += messageLength
        ackLength, ackLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += ackLengthLength
        ackData = decryptedData[readPosition:readPosition + ackLength]
        readPosition += ackLength
        # needed to mark the end of what is covered by the signature
        positionOfBottomOfAckData = readPosition
        signatureLength, signatureLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += signatureLengthLength
        signature = decryptedData[
            readPosition:readPosition + signatureLength]
        signedData = bytes(data[8:20]) + encodeVarint(1) + encodeVarint(
            streamNumberAsClaimedByMsg
        ) + decryptedData[:positionOfBottomOfAckData]

        if not highlevelcrypto.verify(
                signedData, signature, hexlify(pubSigningKey)):
            logger.debug('ECDSA verify failed')
            return
        logger.debug('ECDSA verify passed')
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                'As a matter of intellectual curiosity, here is the Bitcoin'
                ' address associated with the keys owned by the other person:'
                ' %s  ..and here is the testnet address: %s. The other person'
                ' must take their private signing key from Bitmessage and'
                ' import it into Bitcoin (or a service like Blockchain.info)'
                ' for it to be of any use. Do not use this unless you know'
                ' what you are doing.',
                helper_bitcoin.calculateBitcoinAddressFromPubkey(pubSigningKey),
                helper_bitcoin.calculateTestnetAddressFromPubkey(pubSigningKey)
            )
        # Used to detect and ignore duplicate messages in our inbox
        sigHash = hashlib.sha512(
            hashlib.sha512(signature).digest()).digest()[32:]

        # calculate the fromRipe.
        sha = hashlib.new('sha512')
        sha.update(pubSigningKey + pubEncryptionKey)
        ripe = RIPEMD160Hash(sha.digest()).digest()
        fromAddress = encodeAddress(
            sendersAddressVersionNumber, sendersStreamNumber, ripe)

        # Let's store the public key in case we want to reply to this
        # person.
        sqlExecute(
            '''INSERT INTO pubkeys VALUES (?,?,?,?,?)''',
            fromAddress,
            sendersAddressVersionNumber,
            decryptedData[:endOfThePublicKeyPosition],
            int(time.time()),
            'yes')

        # Check to see whether we happen to be awaiting this
        # pubkey in order to send a message. If we are, it will do the POW
        # and send it.
        self.possibleNewPubkey(fromAddress)
        # If this message is bound for one of my version 3 addresses (or
        # higher), then we must check to make sure it meets our demanded
        # proof of work requirement. If this is bound for one of my chan
        # addresses then we skip this check; the minimum network POW is
        # fine.
        # If the toAddress version number is 3 or higher and not one of
        # my chan addresses:
        if decodeAddress(toAddress)[1] >= 3 \
                and not BMConfigParser().safeGetBoolean(toAddress, 'chan'):
            # If I'm not friendly with this person:
            if not shared.isAddressInMyAddressBookSubscriptionsListOrWhitelist(
                    fromAddress):
                requiredNonceTrialsPerByte = int(BMConfigParser().get(
                    toAddress, 'noncetrialsperbyte'))
                requiredPayloadLengthExtraBytes = int(BMConfigParser().get(
                    toAddress, 'payloadlengthextrabytes'))
                if not protocol.isProofOfWorkSufficient(
                        data, requiredNonceTrialsPerByte,
                        requiredPayloadLengthExtraBytes):
                    logger.info(
                        'Proof of work in msg is insufficient only because'
                        ' it does not meet our higher requirement.')
                    return
        # Gets set to True if the user shouldn't see the message according
        # to black or white lists.
        blockMessage = False
        # If we are using a blacklist
        if BMConfigParser().get(
                'bitmessagesettings', 'blackwhitelist') == 'black':
            queryreturn = sqlQuery(
                "SELECT label FROM blacklist where address=? and enabled='1'",
                fromAddress)
            if queryreturn != []:
                logger.info('Message ignored because address is in blacklist.')

                blockMessage = True
        else:  # We're using a whitelist
            queryreturn = sqlQuery(
                "SELECT label FROM whitelist where address=? and enabled='1'",
                fromAddress)
            if queryreturn == []:
                logger.info(
                    'Message ignored because address not in whitelist.')
                blockMessage = True

        toLabel = BMConfigParser().get(toAddress, 'label')
        if toLabel == '':
            toLabel = toAddress
        try:
            decodedMessage = helper_msgcoding.MsgDecode(
                messageEncodingType, message)
        except helper_msgcoding.MsgDecodeException:
            return
        subject = decodedMessage.subject
        body = decodedMessage.body

        # Let us make sure that we haven't already received this message
        if helper_inbox.isMessageAlreadyInInbox(sigHash):
            logger.info('This msg is already in our inbox. Ignoring it.')
            blockMessage = True
        if not blockMessage:
            if messageEncodingType != 0:
                t = (inventoryHash, toAddress, fromAddress, subject,
                     int(time.time()), body, 'inbox', messageEncodingType,
                     0, sigHash)
                helper_inbox.insert(t)

                queues.UISignalQueue.put(('displayNewInboxMessage', (
                    inventoryHash, toAddress, fromAddress, subject, body)))

            # If we are behaving as an API then we might need to run an
            # outside command to let some program know that a new message
            # has arrived.
            if BMConfigParser().safeGetBoolean(
                    'bitmessagesettings', 'apienabled'):
                try:
                    apiNotifyPath = BMConfigParser().get(
                        'bitmessagesettings', 'apinotifypath')
                except:
                    apiNotifyPath = ''
                if apiNotifyPath != '':
                    call([apiNotifyPath, "newMessage"])

            # Let us now check and see whether our receiving address is
            # behaving as a mailing list
            if BMConfigParser().safeGetBoolean(toAddress, 'mailinglist') \
                    and messageEncodingType != 0:
                try:
                    mailingListName = BMConfigParser().get(
                        toAddress, 'mailinglistname')
                except:
                    mailingListName = ''
                # Let us send out this message as a broadcast
                subject = self.addMailingListNameToSubject(
                    subject, mailingListName)
                # Let us now send this message out as a broadcast
                message = time.strftime(
                    "%a, %Y-%m-%d %H:%M:%S UTC", time.gmtime()
                ) + '   Message ostensibly from ' + fromAddress \
                    + ':\n\n' + body
                # The fromAddress for the broadcast that we are about to
                # send is the toAddress (my address) for the msg message
                # we are currently processing.
                fromAddress = toAddress
                # We don't actually need the ackdata for acknowledgement
                # since this is a broadcast message but we can use it to
                # update the user interface when the POW is done generating.
                streamNumber = decodeAddress(fromAddress)[2]

                ackdata = genAckPayload(streamNumber, 0)
                toAddress = '[Broadcast subscribers]'
                ripe = ''

                # We really should have a discussion about how to
                # set the TTL for mailing list broadcasts. This is obviously
                # hard-coded.
                TTL = 2 * 7 * 24 * 60 * 60  # 2 weeks
                t = ('',
                     toAddress,
                     ripe,
                     fromAddress,
                     subject,
                     message,
                     ackdata,
                     int(time.time()),  # sentTime (this doesn't change)
                     int(time.time()),  # lastActionTime
                     0,
                     'broadcastqueued',
                     0,
                     'sent',
                     messageEncodingType,
                     TTL)
                helper_sent.insert(t)

                queues.UISignalQueue.put((
                    'displayNewSentMessage', (
                        toAddress, '[Broadcast subscribers]', fromAddress,
                        subject, message, ackdata)
                ))
                queues.workerQueue.put(('sendbroadcast', ''))

        # Don't send ACK if invalid, blacklisted senders, invisible
        # messages, disabled or chan
        if (
            self.ackDataHasAValidHeader(ackData) and not blockMessage and
            messageEncodingType != 0 and
            not BMConfigParser().safeGetBoolean(toAddress, 'dontsendack') and
            not BMConfigParser().safeGetBoolean(toAddress, 'chan')
        ):
            self._ack_obj.send_data(ackData[24:])

        # Display timing data
        timeRequiredToAttemptToDecryptMessage = time.time(
        ) - messageProcessingStartTime
        self.successfullyDecryptMessageTimings.append(
            timeRequiredToAttemptToDecryptMessage)
        timing_sum = 0
        for item in self.successfullyDecryptMessageTimings:
            timing_sum += item
        logger.debug(
            'Time to decrypt this message successfully: %s'
            '\nAverage time for all message decryption successes since'
            ' startup: %s.',
            timeRequiredToAttemptToDecryptMessage,
            timing_sum / len(self.successfullyDecryptMessageTimings)
        )

    def processbroadcast(self, data):
        """Process a broadcast object"""
        messageProcessingStartTime = time.time()
        shared.numberOfBroadcastsProcessed += 1
        queues.UISignalQueue.put((
            'updateNumberOfBroadcastsProcessed', 'no data'))
        inventoryHash = calculateInventoryHash(data)
        readPosition = 20  # bypass the nonce, time, and object type
        broadcastVersion, broadcastVersionLength = decodeVarint(
            data[readPosition:readPosition + 9])
        readPosition += broadcastVersionLength
        if broadcastVersion < 4 or broadcastVersion > 5:
            logger.info(
                'Cannot decode incoming broadcast versions less than 4'
                ' or higher than 5. Assuming the sender isn\'t being silly,'
                ' you should upgrade Bitmessage because this message shall'
                ' be ignored.'
            )
            return
        cleartextStreamNumber, cleartextStreamNumberLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += cleartextStreamNumberLength
        if broadcastVersion == 4:
            # v4 broadcasts are encrypted the same way the msgs are
            # encrypted. To see if we are interested in a v4 broadcast,
            # we try to decrypt it. This was replaced with v5 broadcasts
            # which include a tag which we check instead, just like we do
            # with v4 pubkeys.
            signedData = data[8:readPosition]
            initialDecryptionSuccessful = False
            for key, cryptorObject in sorted(
                    shared.MyECSubscriptionCryptorObjects.items(),
                    key=lambda x: random.random()):
                try:
                    # continue decryption attempts to avoid timing attacks
                    if initialDecryptionSuccessful:
                        cryptorObject.decrypt(data[readPosition:])
                    else:
                        decryptedData = cryptorObject.decrypt(
                            data[readPosition:])
                        # This is the RIPE hash of the sender's pubkey.
                        # We need this below to compare to the RIPE hash
                        # of the sender's address to verify that it was
                        # encrypted by with their key rather than some
                        # other key.
                        toRipe = key
                        initialDecryptionSuccessful = True
                        logger.info(
                            'EC decryption successful using key associated'
                            ' with ripe hash: %s', hexlify(key))
                except Exception:
                    logger.debug(
                        'cryptorObject.decrypt Exception:', exc_info=True)
            if not initialDecryptionSuccessful:
                # This is not a broadcast I am interested in.
                logger.debug(
                    'Length of time program spent failing to decrypt this'
                    ' v4 broadcast: %s seconds.',
                    time.time() - messageProcessingStartTime)
                return
        elif broadcastVersion == 5:
            embeddedTag = data[readPosition:readPosition + 32]
            readPosition += 32
            if bytes(embeddedTag) not in shared.MyECSubscriptionCryptorObjects:
                logger.debug('We\'re not interested in this broadcast.')
                return
            # We are interested in this broadcast because of its tag.
            # We're going to add some more data which is signed further down.
            signedData = data[8:readPosition]
            cryptorObject = shared.MyECSubscriptionCryptorObjects[embeddedTag]
            try:
                decryptedData = cryptorObject.decrypt(data[readPosition:])
                logger.debug('EC decryption successful')
            except Exception:
                logger.debug(
                    'Broadcast version %s decryption Unsuccessful.',
                    broadcastVersion)
                return
        # At this point this is a broadcast I have decrypted and am
        # interested in.
        readPosition = 0
        sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
            decryptedData[readPosition:readPosition + 9])
        if broadcastVersion == 4:
            if sendersAddressVersion < 2 or sendersAddressVersion > 3:
                logger.warning(
                    'Cannot decode senderAddressVersion other than 2 or 3.'
                    ' Assuming the sender isn\'t being silly, you should'
                    ' upgrade Bitmessage because this message shall be'
                    ' ignored.'
                )
                return
        elif broadcastVersion == 5:
            if sendersAddressVersion < 4:
                logger.info(
                    'Cannot decode senderAddressVersion less than 4 for'
                    ' broadcast version number 5. Assuming the sender'
                    ' isn\'t being silly, you should upgrade Bitmessage'
                    ' because this message shall be ignored.'
                )
                return
        readPosition += sendersAddressVersionLength
        sendersStream, sendersStreamLength = decodeVarint(
            decryptedData[readPosition:readPosition + 9])
        if sendersStream != cleartextStreamNumber:
            logger.info(
                'The stream number outside of the encryption on which the'
                ' POW was completed doesn\'t match the stream number'
                ' inside the encryption. Ignoring broadcast.'
            )
            return
        readPosition += sendersStreamLength
        readPosition += 4
        sendersPubSigningKey = '\x04' + \
            decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        sendersPubEncryptionKey = '\x04' + \
            decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        if sendersAddressVersion >= 3:
            requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = \
                decodeVarint(decryptedData[readPosition:readPosition + 10])
            readPosition += varintLength
            logger.debug(
                'sender\'s requiredAverageProofOfWorkNonceTrialsPerByte'
                ' is %s', requiredAverageProofOfWorkNonceTrialsPerByte)
            requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += varintLength
            logger.debug(
                'sender\'s requiredPayloadLengthExtraBytes is %s',
                requiredPayloadLengthExtraBytes)
        endOfPubkeyPosition = readPosition

        sha = hashlib.new('sha512')
        sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
        calculatedRipe = RIPEMD160Hash(sha.digest()).digest()

        if broadcastVersion == 4:
            if toRipe != calculatedRipe:
                logger.info(
                    'The encryption key used to encrypt this message'
                    ' doesn\'t match the keys inbedded in the message'
                    ' itself. Ignoring message.'
                )
                return
        elif broadcastVersion == 5:
            calculatedTag = hashlib.sha512(hashlib.sha512(
                encodeVarint(sendersAddressVersion) +
                encodeVarint(sendersStream) + calculatedRipe
            ).digest()).digest()[32:]
            if calculatedTag != embeddedTag:
                logger.debug(
                    'The tag and encryption key used to encrypt this'
                    ' message doesn\'t match the keys inbedded in the'
                    ' message itself. Ignoring message.'
                )
                return
        messageEncodingType, messageEncodingTypeLength = decodeVarint(
            decryptedData[readPosition:readPosition + 9])
        if messageEncodingType == 0:
            return
        readPosition += messageEncodingTypeLength
        messageLength, messageLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 9])
        readPosition += messageLengthLength
        message = decryptedData[readPosition:readPosition + messageLength]
        readPosition += messageLength
        readPositionAtBottomOfMessage = readPosition
        signatureLength, signatureLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 9])
        readPosition += signatureLengthLength
        signature = decryptedData[
            readPosition:readPosition + signatureLength]
        signedData += decryptedData[:readPositionAtBottomOfMessage]
        if not highlevelcrypto.verify(
                signedData, signature, hexlify(sendersPubSigningKey)):
            logger.debug('ECDSA verify failed')
            return
        logger.debug('ECDSA verify passed')
        # Used to detect and ignore duplicate messages in our inbox
        sigHash = hashlib.sha512(
            hashlib.sha512(signature).digest()).digest()[32:]

        fromAddress = encodeAddress(
            sendersAddressVersion, sendersStream, calculatedRipe)
        logger.info('fromAddress: %s', fromAddress)

        # Let's store the public key in case we want to reply to this person.
        sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''',
                   fromAddress,
                   sendersAddressVersion,
                   decryptedData[:endOfPubkeyPosition],
                   int(time.time()),
                   'yes')

        # Check to see whether we happen to be awaiting this
        # pubkey in order to send a message. If we are, it will do the POW
        # and send it.
        self.possibleNewPubkey(fromAddress)

        fromAddress = encodeAddress(
            sendersAddressVersion, sendersStream, calculatedRipe)
        logger.debug('fromAddress: %s', fromAddress)

        try:
            decodedMessage = helper_msgcoding.MsgDecode(
                messageEncodingType, message)
        except helper_msgcoding.MsgDecodeException:
            return
        subject = decodedMessage.subject
        body = decodedMessage.body

        toAddress = '[Broadcast subscribers]'
        if helper_inbox.isMessageAlreadyInInbox(sigHash):
            logger.info('This broadcast is already in our inbox. Ignoring it.')
            return
        t = (inventoryHash, toAddress, fromAddress, subject, int(
            time.time()), body, 'inbox', messageEncodingType, 0, sigHash)
        helper_inbox.insert(t)

        queues.UISignalQueue.put(('displayNewInboxMessage', (
            inventoryHash, toAddress, fromAddress, subject, body)))

        # If we are behaving as an API then we might need to run an
        # outside command to let some program know that a new message
        # has arrived.
        if BMConfigParser().safeGetBoolean('bitmessagesettings', 'apienabled'):
            try:
                apiNotifyPath = BMConfigParser().get(
                    'bitmessagesettings', 'apinotifypath')
            except:
                apiNotifyPath = ''
            if apiNotifyPath != '':
                call([apiNotifyPath, "newBroadcast"])

        # Display timing data
        logger.info(
            'Time spent processing this interesting broadcast: %s',
            time.time() - messageProcessingStartTime)

    def possibleNewPubkey(self, address):
        """
        We have inserted a pubkey into our pubkey table which we received
        from a pubkey, msg, or broadcast message. It might be one that we
        have been waiting for. Let's check.
        """

        # For address versions <= 3, we wait on a key with the correct
        # address version, stream number and RIPE hash.
        _, addressVersion, streamNumber, ripe = decodeAddress(address)
        if addressVersion <= 3:
            if address in state.neededPubkeys:
                del state.neededPubkeys[address]
                self.sendMessages(address)
            else:
                logger.debug(
                    'We don\'t need this pub key. We didn\'t ask for it.'
                    ' For address: %s', address)
        # For address versions >= 4, we wait on a pubkey with the correct tag.
        # Let us create the tag from the address and see if we were waiting
        # for it.
        elif addressVersion >= 4:
            tag = hashlib.sha512(hashlib.sha512(
                encodeVarint(addressVersion) + encodeVarint(streamNumber)
                + ripe
            ).digest()).digest()[32:]
            if tag in state.neededPubkeys:
                del state.neededPubkeys[tag]
                self.sendMessages(address)

    @staticmethod
    def sendMessages(address):
        """
        This method is called by the `possibleNewPubkey` when it sees
        that we now have the necessary pubkey to send one or more messages.
        """
        logger.info('We have been awaiting the arrival of this pubkey.')
        sqlExecute(
            "UPDATE sent SET status='doingmsgpow', retrynumber=0"
            " WHERE toaddress=?"
            " AND (status='awaitingpubkey' OR status='doingpubkeypow')"
            " AND folder='sent'", address)
        queues.workerQueue.put(('sendmessage', ''))

    @staticmethod
    def ackDataHasAValidHeader(ackData):
        """Checking ackData with valid Header, not sending ackData when false"""
        if len(ackData) < protocol.Header.size:
            logger.info(
                'The length of ackData is unreasonably short. Not sending'
                ' ackData.')
            return False

        magic, command, payloadLength, checksum = protocol.Header.unpack(
            ackData[:protocol.Header.size])
        if magic != 0xE9BEB4D9:
            logger.info('Ackdata magic bytes were wrong. Not sending ackData.')
            return False
        payload = ackData[protocol.Header.size:]
        if len(payload) != payloadLength:
            logger.info(
                'ackData payload length doesn\'t match the payload length'
                ' specified in the header. Not sending ackdata.')
            return False
        # ~1.6 MB which is the maximum possible size of an inv message.
        if payloadLength > 1600100:
            # The largest message should be either an inv or a getdata
            # message at 1.6 MB in size.
            # That doesn't mean that the object may be that big. The
            # shared.checkAndShareObjectWithPeers function will verify
            # that it is no larger than 2^18 bytes.
            return False
        # test the checksum in the message.
        if checksum != hashlib.sha512(payload).digest()[0:4]:
            logger.info('ackdata checksum wrong. Not sending ackdata.')
            return False
        command = command.rstrip('\x00'.encode())
        if command != 'object'.encode():
            return False
        return True

    @staticmethod
    def addMailingListNameToSubject(subject, mailingListName):
        """Adding mailingListName to subject"""
        subject = subject.strip()
        if subject[:3] == 'Re:' or subject[:3] == 'RE:':
            subject = subject[3:].strip()
        if '[' + mailingListName + ']' in subject:
            return subject
        return '[' + mailingListName + '] ' + subject
