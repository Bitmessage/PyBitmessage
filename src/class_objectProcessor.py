import time
import threading
import shared
import hashlib
import random
from struct import unpack, pack
import sys
import string
from subprocess import call  # used when the API must execute an outside program
import traceback

from pyelliptic.openssl import OpenSSL
import highlevelcrypto
from addresses import *
import helper_generic
from helper_generic import addDataPadding
import helper_bitcoin
import helper_inbox
import helper_sent
from helper_sql import *
import tr
from debug import logger
import l10n


class objectProcessor(threading.Thread):
    """
    The objectProcessor thread, of which there is only one, receives network
    objecs (msg, broadcast, pubkey, getpubkey) from the receiveDataThreads.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        """
        It may be the case that the last time Bitmessage was running, the user
        closed it before it finished processing everything in the
        objectProcessorQueue. Assuming that Bitmessage wasn't closed forcefully,
        it should have saved the data in the queue into the objectprocessorqueue 
        table. Let's pull it out.
        """
        queryreturn = sqlQuery(
            '''SELECT objecttype, data FROM objectprocessorqueue''')
        with shared.objectProcessorQueueSizeLock:
            for row in queryreturn:
                objectType, data = row
                shared.objectProcessorQueueSize += len(data)
                shared.objectProcessorQueue.put((objectType,data))
        sqlExecute('''DELETE FROM objectprocessorqueue''')
        logger.debug('Loaded %s objects from disk into the objectProcessorQueue.' % str(len(queryreturn)))


    def run(self):
        while True:
            objectType, data = shared.objectProcessorQueue.get()

            try:
                if objectType == 0: # getpubkey
                    self.processgetpubkey(data)
                elif objectType == 1: #pubkey
                    self.processpubkey(data)
                elif objectType == 2: #msg
                    self.processmsg(data)
                elif objectType == 3: #broadcast
                    self.processbroadcast(data)
                elif objectType == 'checkShutdownVariable': # is more of a command, not an object type. Is used to get this thread past the queue.get() so that it will check the shutdown variable.
                    pass
                else:
                    logger.critical('Error! Bug! The class_objectProcessor was passed an object type it doesn\'t recognize: %s' % str(objectType))
            except varintDecodeError as e:
                logger.debug("There was a problem with a varint while processing an object. Some details: %s" % e)
            except Exception as e:
                logger.critical("Critical error within objectProcessorThread: \n%s" % traceback.format_exc())

            with shared.objectProcessorQueueSizeLock:
                shared.objectProcessorQueueSize -= len(data) # We maintain objectProcessorQueueSize so that we will slow down requesting objects if too much data accumulates in the queue.

            if shared.shutdown:
                time.sleep(.5) # Wait just a moment for most of the connections to close
                numberOfObjectsThatWereInTheObjectProcessorQueue = 0
                with SqlBulkExecute() as sql:
                    while shared.objectProcessorQueueSize > 1:
                        objectType, data = shared.objectProcessorQueue.get()
                        sql.execute('''INSERT INTO objectprocessorqueue VALUES (?,?)''',
                                   objectType,data)
                        with shared.objectProcessorQueueSizeLock:
                            shared.objectProcessorQueueSize -= len(data) # We maintain objectProcessorQueueSize so that we will slow down requesting objects if too much data accumulates in the queue.
                        numberOfObjectsThatWereInTheObjectProcessorQueue += 1
                logger.debug('Saved %s objects from the objectProcessorQueue to disk. objectProcessorThread exiting.' % str(numberOfObjectsThatWereInTheObjectProcessorQueue))
                shared.shutdown = 2
                break
    
    def processgetpubkey(self, data):
        readPosition = 20  # bypass the nonce, time, and object type
        requestedAddressVersionNumber, addressVersionLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += addressVersionLength
        streamNumber, streamNumberLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += streamNumberLength

        if requestedAddressVersionNumber == 0:
            logger.debug('The requestedAddressVersionNumber of the pubkey request is zero. That doesn\'t make any sense. Ignoring it.')
            return
        elif requestedAddressVersionNumber == 1:
            logger.debug('The requestedAddressVersionNumber of the pubkey request is 1 which isn\'t supported anymore. Ignoring it.')
            return
        elif requestedAddressVersionNumber > 4:
            logger.debug('The requestedAddressVersionNumber of the pubkey request is too high. Can\'t understand. Ignoring it.')
            return

        myAddress = ''
        if requestedAddressVersionNumber <= 3 :
            requestedHash = data[readPosition:readPosition + 20]
            if len(requestedHash) != 20:
                logger.debug('The length of the requested hash is not 20 bytes. Something is wrong. Ignoring.')
                return
            logger.info('the hash requested in this getpubkey request is: %s' % requestedHash.encode('hex'))
            if requestedHash in shared.myAddressesByHash:  # if this address hash is one of mine
                myAddress = shared.myAddressesByHash[requestedHash]
        elif requestedAddressVersionNumber >= 4:
            requestedTag = data[readPosition:readPosition + 32]
            if len(requestedTag) != 32:
                logger.debug('The length of the requested tag is not 32 bytes. Something is wrong. Ignoring.')
                return
            logger.debug('the tag requested in this getpubkey request is: %s' % requestedTag.encode('hex'))
            if requestedTag in shared.myAddressesByTag:
                myAddress = shared.myAddressesByTag[requestedTag]

        if myAddress == '':
            logger.info('This getpubkey request is not for any of my keys.')
            return

        if decodeAddress(myAddress)[1] != requestedAddressVersionNumber:
            logger.warning('(Within the processgetpubkey function) Someone requested one of my pubkeys but the requestedAddressVersionNumber doesn\'t match my actual address version number. Ignoring.')
            return
        if decodeAddress(myAddress)[2] != streamNumber:
            logger.warning('(Within the processgetpubkey function) Someone requested one of my pubkeys but the stream number on which we heard this getpubkey object doesn\'t match this address\' stream number. Ignoring.')
            return
        if shared.safeConfigGetBoolean(myAddress, 'chan'):
            logger.info('Ignoring getpubkey request because it is for one of my chan addresses. The other party should already have the pubkey.')
            return
        try:
            lastPubkeySendTime = int(shared.config.get(
                myAddress, 'lastpubkeysendtime'))
        except:
            lastPubkeySendTime = 0
        if lastPubkeySendTime > time.time() - 2419200:  # If the last time we sent our pubkey was more recent than 28 days ago...
            logger.info('Found getpubkey-requested-item in my list of EC hashes BUT we already sent it recently. Ignoring request. The lastPubkeySendTime is: %s' % lastPubkeySendTime) 
            return
        logger.info('Found getpubkey-requested-hash in my list of EC hashes. Telling Worker thread to do the POW for a pubkey message and send it out.') 
        if requestedAddressVersionNumber == 2:
            shared.workerQueue.put((
                'doPOWForMyV2Pubkey', requestedHash))
        elif requestedAddressVersionNumber == 3:
            shared.workerQueue.put((
                'sendOutOrStoreMyV3Pubkey', requestedHash))
        elif requestedAddressVersionNumber == 4:
            shared.workerQueue.put((
                'sendOutOrStoreMyV4Pubkey', myAddress))

    def processpubkey(self, data):
        pubkeyProcessingStartTime = time.time()
        shared.numberOfPubkeysProcessed += 1
        shared.UISignalQueue.put((
            'updateNumberOfPubkeysProcessed', 'no data'))
        embeddedTime, = unpack('>Q', data[8:16])
        readPosition = 20  # bypass the nonce, time, and object type
        addressVersion, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        if addressVersion == 0:
            logger.debug('(Within processpubkey) addressVersion of 0 doesn\'t make sense.')
            return
        if addressVersion > 4 or addressVersion == 1:
            logger.info('This version of Bitmessage cannot handle version %s addresses.' % addressVersion)
            return
        if addressVersion == 2:
            if len(data) < 146:  # sanity check. This is the minimum possible length.
                logger.debug('(within processpubkey) payloadLength less than 146. Sanity check failed.')
                return
            bitfieldBehaviors = data[readPosition:readPosition + 4]
            readPosition += 4
            publicSigningKey = data[readPosition:readPosition + 64]
            # Is it possible for a public key to be invalid such that trying to
            # encrypt or sign with it will cause an error? If it is, we should
            # probably test these keys here.
            readPosition += 64
            publicEncryptionKey = data[readPosition:readPosition + 64]
            if len(publicEncryptionKey) < 64:
                logger.debug('publicEncryptionKey length less than 64. Sanity check failed.')
                return
            sha = hashlib.new('sha512')
            sha.update(
                '\x04' + publicSigningKey + '\x04' + publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()


            logger.info('within recpubkey, addressVersion: %s, streamNumber: %s \n\
                        ripe %s\n\
                        publicSigningKey in hex: %s\n\
                        publicEncryptionKey in hex: %s' % (addressVersion, 
                                                           streamNumber, 
                                                           ripe.encode('hex'), 
                                                           publicSigningKey.encode('hex'), 
                                                           publicEncryptionKey.encode('hex')
                                                           )
                        )

            queryreturn = sqlQuery(
                '''SELECT usedpersonally FROM pubkeys WHERE hash=? AND addressversion=? AND usedpersonally='yes' ''', ripe, addressVersion)
            
            """
            With the changes in protocol v3, we have to be careful to store pubkey data 
            in the database the same way we did before to maintain backwards compatibility
            with what is in people's databases already. This means that for v2 keys, we 
            must store the nonce, the time, and then everything else starting with the 
            address version.
            """
            dataToStore = '\x00' * 8 # fake nonce
            dataToStore += data[8:16] # the time
            dataToStore += data[20:] # everything else
            
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                logger.info('We HAVE used this pubkey personally. Updating time.')
                t = (ripe, addressVersion, dataToStore, int(time.time()), 'yes')
            else:
                logger.info('We have NOT used this pubkey personally. Inserting in database.')
                t = (ripe, addressVersion, dataToStore, int(time.time()), 'no')
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
            self.possibleNewPubkey(ripe = ripe)
        if addressVersion == 3:
            if len(data) < 170:  # sanity check.
                logger.warning('(within processpubkey) payloadLength less than 170. Sanity check failed.')
                return
            bitfieldBehaviors = data[readPosition:readPosition + 4]
            readPosition += 4
            publicSigningKey = '\x04' + data[readPosition:readPosition + 64]
            readPosition += 64
            publicEncryptionKey = '\x04' + data[readPosition:readPosition + 64]
            readPosition += 64
            specifiedNonceTrialsPerByte, specifiedNonceTrialsPerByteLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += specifiedNonceTrialsPerByteLength
            specifiedPayloadLengthExtraBytes, specifiedPayloadLengthExtraBytesLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += specifiedPayloadLengthExtraBytesLength
            endOfSignedDataPosition = readPosition
            signatureLength, signatureLengthLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += signatureLengthLength
            signature = data[readPosition:readPosition + signatureLength]
            """
            With the changes in protocol v3, to maintain backwards compatibility, signatures will be sent
            the 'old' way during an upgrade period and then a 'new' simpler way after that. We will therefore
            check the sig both ways. 
            Old way:
            signedData = timePubkeyWasSigned(4 bytes) + addressVersion through extra_bytes
            New way:
            signedData = all of the payload data, from the time down through the extra_bytes
            
            The timePubkeyWasSigned will be calculated by subtracting 28 days form the embedded expiresTime.
            """
            expiresTime, = unpack('>Q', data[8:16])
            TTL = 28 * 24 * 60 * 60
            signedData = pack('>I', (expiresTime - TTL)) # the time that the pubkey was signed. 4 bytes. 
            signedData += data[20:endOfSignedDataPosition] # the address version down through the payloadLengthExtraBytes
            
            if highlevelcrypto.verify(signedData, signature, publicSigningKey.encode('hex')):
                logger.info('ECDSA verify passed (within processpubkey, old method)')
            else:
                logger.warning('ECDSA verify failed (within processpubkey, old method)')
                # let us try the newer signature method
                if highlevelcrypto.verify(data[8:endOfSignedDataPosition], signature, publicSigningKey.encode('hex')):
                    logger.info('ECDSA verify passed (within processpubkey, new method)')
                else:
                    logger.warning('ECDSA verify failed (within processpubkey, new method)')
                    return

            sha = hashlib.new('sha512')
            sha.update(publicSigningKey + publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()
            

            logger.info('within recpubkey, addressVersion: %s, streamNumber: %s \n\
                        ripe %s\n\
                        publicSigningKey in hex: %s\n\
                        publicEncryptionKey in hex: %s' % (addressVersion, 
                                                           streamNumber, 
                                                           ripe.encode('hex'), 
                                                           publicSigningKey.encode('hex'), 
                                                           publicEncryptionKey.encode('hex')
                                                           )
                        )


            """
            With the changes in protocol v3, we have to be careful to store pubkey data 
            in the database the same way we did before to maintain backwards compatibility
            with what is in people's databases already. This means that for v3 keys, we 
            must store the nonce, the time, and then everything else starting with the 
            address version.
            """
            dataToStore = '\x00' * 8 # fake nonce
            dataToStore += data[8:16] # the time
            dataToStore += data[20:] # everything else

            queryreturn = sqlQuery('''SELECT usedpersonally FROM pubkeys WHERE hash=? AND addressversion=? AND usedpersonally='yes' ''', ripe, addressVersion)
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                logger.info('We HAVE used this pubkey personally. Updating time.')
                t = (ripe, addressVersion, dataToStore, int(time.time()), 'yes')
            else:
                logger.info('We have NOT used this pubkey personally. Inserting in database.')
                t = (ripe, addressVersion, dataToStore, int(time.time()), 'no')
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
            self.possibleNewPubkey(ripe = ripe)

        if addressVersion == 4:
            if len(data) < 350:  # sanity check.
                logger.debug('(within processpubkey) payloadLength less than 350. Sanity check failed.')
                return

            tag = data[readPosition:readPosition + 32]
            if tag not in shared.neededPubkeys:
                logger.info('We don\'t need this v4 pubkey. We didn\'t ask for it.')
                return
            
            # Let us try to decrypt the pubkey
            toAddress, cryptorObject = shared.neededPubkeys[tag]
            if shared.decryptAndCheckPubkeyPayload(data, toAddress) == 'successful':
                # At this point we know that we have been waiting on this pubkey.
                # This function will command the workerThread to start work on
                # the messages that require it.
                self.possibleNewPubkey(address=toAddress)

        # Display timing data
        timeRequiredToProcessPubkey = time.time(
        ) - pubkeyProcessingStartTime
        logger.debug('Time required to process this pubkey: %s' % timeRequiredToProcessPubkey)


    def processmsg(self, data):
        messageProcessingStartTime = time.time()
        shared.numberOfMessagesProcessed += 1
        shared.UISignalQueue.put((
            'updateNumberOfMessagesProcessed', 'no data'))
        readPosition = 20 # bypass the nonce, time, and object type
        
        """
        In protocol v2, the next byte(s) was the streamNumber. But starting after
        the protocol v3 upgrade period, the next byte(s) will be a msg version
        number followed by the streamNumber. 
        """
        #msgVersionOutsideEncryption, msgVersionOutsideEncryptionLength = decodeVarint(data[readPosition:readPosition + 9])
        #readPosition += msgVersionOutsideEncryptionLength
        
        streamNumberAsClaimedByMsg, streamNumberAsClaimedByMsgLength = decodeVarint(
            data[readPosition:readPosition + 9])
        readPosition += streamNumberAsClaimedByMsgLength
        inventoryHash = calculateInventoryHash(data)
        initialDecryptionSuccessful = False
        # Let's check whether this is a message acknowledgement bound for us.
        if data[-32:] in shared.ackdataForWhichImWatching:
            logger.info('This msg IS an acknowledgement bound for me.')
            del shared.ackdataForWhichImWatching[data[-32:]]
            sqlExecute('UPDATE sent SET status=? WHERE ackdata=?',
                       'ackreceived', data[-32:])
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (data[-32:], tr.translateText("MainWindow",'Acknowledgement of the message received. %1').arg(l10n.formatTimestamp()))))
            return
        else:
            logger.info('This was NOT an acknowledgement bound for me.')


        # This is not an acknowledgement bound for me. See if it is a message
        # bound for me by trying to decrypt it with my private keys.
        
        # This can be simplified quite a bit after 1416175200: # Sun, 16 Nov 2014 22:00:00 GMT
        for key, cryptorObject in shared.myECCryptorObjects.items():
            try:
                decryptedData = cryptorObject.decrypt(data[readPosition:])
                toRipe = key  # This is the RIPE hash of my pubkeys. We need this below to compare to the destination_ripe included in the encrypted data.
                initialDecryptionSuccessful = True
                logger.info('EC decryption successful using key associated with ripe hash: %s. msg did NOT specify version.' % key.encode('hex'))
                
                # We didn't bypass a msg version above as it is commented out. 
                # But the decryption was successful. Which means that there 
                # wasn't a msg version byte include in this msg.
                msgObjectContainedVersion = False
                break
            except Exception as err:
                # What if a client sent us a msg with 
                # a msg version included? We didn't bypass it above. So 
                # let's try to decrypt the msg assuming that it is present.
                try:
                    decryptedData = cryptorObject.decrypt(data[readPosition+1:]) # notice that we offset by 1 byte compared to the attempt above.
                    toRipe = key  # This is the RIPE hash of my pubkeys. We need this below to compare to the destination_ripe included in the encrypted data.
                    initialDecryptionSuccessful = True
                    logger.info('EC decryption successful using key associated with ripe hash: %s. msg DID specifiy version.' % key.encode('hex'))
                    
                    # There IS a msg version byte include in this msg.
                    msgObjectContainedVersion = True
                    break
                except Exception as err:
                    pass
        if not initialDecryptionSuccessful:
            # This is not a message bound for me.
            logger.info('Length of time program spent failing to decrypt this message: %s seconds.' % (time.time() - messageProcessingStartTime,)) 
            return

        # This is a message bound for me.
        toAddress = shared.myAddressesByHash[
            toRipe]  # Look up my address based on the RIPE hash.
        readPosition = 0
        if not msgObjectContainedVersion: # by which I mean "if the msg object didn't have the msg version outside of the encryption". This confusingness will be removed after the protocol v3 upgrade period.            
            messageVersionWithinEncryption, messageVersionWithinEncryptionLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += messageVersionWithinEncryptionLength
            if messageVersionWithinEncryption != 1:
                logger.info('Cannot understand message versions other than one. Ignoring message.') 
                return
        else:
            messageVersionWithinEncryptionLength = 0 # This variable can disappear after the protocol v3 upgrade period is complete.
        sendersAddressVersionNumber, sendersAddressVersionNumberLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += sendersAddressVersionNumberLength
        if sendersAddressVersionNumber == 0:
            logger.info('Cannot understand sendersAddressVersionNumber = 0. Ignoring message.') 
            return
        if sendersAddressVersionNumber > 4:
            logger.info('Sender\'s address version number %s not yet supported. Ignoring message.' % sendersAddressVersionNumber)  
            return
        if len(decryptedData) < 170:
            logger.info('Length of the unencrypted data is unreasonably short. Sanity check failed. Ignoring message.')
            return
        sendersStreamNumber, sendersStreamNumberLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        if sendersStreamNumber == 0:
            logger.info('sender\'s stream number is 0. Ignoring message.')
            return
        readPosition += sendersStreamNumberLength
        behaviorBitfield = decryptedData[readPosition:readPosition + 4]
        readPosition += 4
        pubSigningKey = '\x04' + decryptedData[
            readPosition:readPosition + 64]
        readPosition += 64
        pubEncryptionKey = '\x04' + decryptedData[
            readPosition:readPosition + 64]
        readPosition += 64
        if sendersAddressVersionNumber >= 3:
            requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += varintLength
            logger.info('sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is %s' % requiredAverageProofOfWorkNonceTrialsPerByte)
            requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += varintLength
            logger.info('sender\'s requiredPayloadLengthExtraBytes is %s' % requiredPayloadLengthExtraBytes)
        endOfThePublicKeyPosition = readPosition  # needed for when we store the pubkey in our database of pubkeys for later use.
        if toRipe != decryptedData[readPosition:readPosition + 20]:
            logger.info('The original sender of this message did not send it to you. Someone is attempting a Surreptitious Forwarding Attack.\n\
                See: http://world.std.com/~dtd/sign_encrypt/sign_encrypt7.html \n\
                your toRipe: %s\n\
                embedded destination toRipe: %s' % (toRipe.encode('hex'), decryptedData[readPosition:readPosition + 20].encode('hex'))
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
        positionOfBottomOfAckData = readPosition  # needed to mark the end of what is covered by the signature
        signatureLength, signatureLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += signatureLengthLength
        signature = decryptedData[
            readPosition:readPosition + signatureLength]
        if not msgObjectContainedVersion:
            # protocol v2. This can be removed after the end of the protocol v3 upgrade period.
            signedData = decryptedData[:positionOfBottomOfAckData]
        else:
            # protocol v3
            signedData = data[8:20] + encodeVarint(1) + encodeVarint(streamNumberAsClaimedByMsg) + decryptedData[:positionOfBottomOfAckData]
        
        if not highlevelcrypto.verify(signedData, signature, pubSigningKey.encode('hex')):
            logger.debug('ECDSA verify failed')
            return
        logger.debug('ECDSA verify passed')
        logger.debug('As a matter of intellectual curiosity, here is the Bitcoin address associated with the keys owned by the other person: %s  ..and here is the testnet address: %s. The other person must take their private signing key from Bitmessage and import it into Bitcoin (or a service like Blockchain.info) for it to be of any use. Do not use this unless you know what you are doing.' %
                     (helper_bitcoin.calculateBitcoinAddressFromPubkey(pubSigningKey), helper_bitcoin.calculateTestnetAddressFromPubkey(pubSigningKey))
                     )

        # calculate the fromRipe.
        sha = hashlib.new('sha512')
        sha.update(pubSigningKey + pubEncryptionKey)
        ripe = hashlib.new('ripemd160')
        ripe.update(sha.digest())
        fromAddress = encodeAddress(
            sendersAddressVersionNumber, sendersStreamNumber, ripe.digest())
        # Let's store the public key in case we want to reply to this
        # person.
        if sendersAddressVersionNumber <= 3:
            sqlExecute(
                '''INSERT INTO pubkeys VALUES (?,?,?,?,?)''',
                ripe.digest(),
                sendersAddressVersionNumber,
                '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + decryptedData[messageVersionWithinEncryptionLength:endOfThePublicKeyPosition],
                int(time.time()),
                'yes')
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(ripe=ripe.digest())
        elif sendersAddressVersionNumber >= 4:
            sqlExecute(
                '''INSERT INTO pubkeys VALUES (?,?,?,?,?)''',
                ripe.digest(),
                sendersAddressVersionNumber,
                '\x00\x00\x00\x00\x00\x00\x00\x01' + decryptedData[messageVersionWithinEncryptionLength:endOfThePublicKeyPosition],
                int(time.time()),
                'yes')
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(address = fromAddress)
        # If this message is bound for one of my version 3 addresses (or
        # higher), then we must check to make sure it meets our demanded
        # proof of work requirement. If this is bound for one of my chan
        # addresses then we skip this check; the minimum network POW is
        # fine.
        if decodeAddress(toAddress)[1] >= 3 and not shared.safeConfigGetBoolean(toAddress, 'chan'):  # If the toAddress version number is 3 or higher and not one of my chan addresses:
            if not shared.isAddressInMyAddressBookSubscriptionsListOrWhitelist(fromAddress):  # If I'm not friendly with this person:
                requiredNonceTrialsPerByte = shared.config.getint(
                    toAddress, 'noncetrialsperbyte')
                requiredPayloadLengthExtraBytes = shared.config.getint(
                    toAddress, 'payloadlengthextrabytes')
                if not shared.isProofOfWorkSufficient(data, requiredNonceTrialsPerByte, requiredPayloadLengthExtraBytes):
                    logger.info('Proof of work in msg is insufficient only because it does not meet our higher requirement.')
                    return
        blockMessage = False  # Gets set to True if the user shouldn't see the message according to black or white lists.
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':  # If we are using a blacklist
            queryreturn = sqlQuery(
                '''SELECT label FROM blacklist where address=? and enabled='1' ''',
                fromAddress)
            if queryreturn != []:
                logger.info('Message ignored because address is in blacklist.')

                blockMessage = True
        else:  # We're using a whitelist
            queryreturn = sqlQuery(
                '''SELECT label FROM whitelist where address=? and enabled='1' ''',
                fromAddress)
            if queryreturn == []:
                logger.info('Message ignored because address not in whitelist.')
                blockMessage = True
        
        toLabel = shared.config.get(toAddress, 'label')
        if toLabel == '':
            toLabel = toAddress

        if messageEncodingType == 2:
            subject, body = self.decodeType2Message(message)
            logger.info('Message subject (first 100 characters): %s' % repr(subject)[:100])
        elif messageEncodingType == 1:
            body = message
            subject = ''
        elif messageEncodingType == 0:
            logger.info('messageEncodingType == 0. Doing nothing with the message. They probably just sent it so that we would store their public key or send their ack data for them.')
            subject = ''
            body = '' 
        else:
            body = 'Unknown encoding type.\n\n' + repr(message)
            subject = ''
        # Let us make sure that we haven't already received this message
        if helper_inbox.isMessageAlreadyInInbox(toAddress, fromAddress, subject, body, messageEncodingType):
            logger.info('This msg is already in our inbox. Ignoring it.')
            blockMessage = True
        if not blockMessage:
            if messageEncodingType != 0:
                t = (inventoryHash, toAddress, fromAddress, subject, int(
                    time.time()), body, 'inbox', messageEncodingType, 0)
                helper_inbox.insert(t)

                shared.UISignalQueue.put(('displayNewInboxMessage', (
                    inventoryHash, toAddress, fromAddress, subject, body)))

            # If we are behaving as an API then we might need to run an
            # outside command to let some program know that a new message
            # has arrived.
            if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
                try:
                    apiNotifyPath = shared.config.get(
                        'bitmessagesettings', 'apinotifypath')
                except:
                    apiNotifyPath = ''
                if apiNotifyPath != '':
                    call([apiNotifyPath, "newMessage"])

            # Let us now check and see whether our receiving address is
            # behaving as a mailing list
            if shared.safeConfigGetBoolean(toAddress, 'mailinglist'):
                try:
                    mailingListName = shared.config.get(
                        toAddress, 'mailinglistname')
                except:
                    mailingListName = ''
                # Let us send out this message as a broadcast
                subject = self.addMailingListNameToSubject(
                    subject, mailingListName)
                # Let us now send this message out as a broadcast
                message = time.strftime("%a, %Y-%m-%d %H:%M:%S UTC", time.gmtime(
                )) + '   Message ostensibly from ' + fromAddress + ':\n\n' + body
                fromAddress = toAddress  # The fromAddress for the broadcast that we are about to send is the toAddress (my address) for the msg message we are currently processing.
                ackdataForBroadcast = OpenSSL.rand(
                    32)  # We don't actually need the ackdataForBroadcast for acknowledgement since this is a broadcast message but we can use it to update the user interface when the POW is done generating.
                toAddress = '[Broadcast subscribers]'
                ripe = ''

                t = ('', toAddress, ripe, fromAddress, subject, message, ackdataForBroadcast, int(
                    time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
                helper_sent.insert(t)

                shared.UISignalQueue.put(('displayNewSentMessage', (
                    toAddress, '[Broadcast subscribers]', fromAddress, subject, message, ackdataForBroadcast)))
                shared.workerQueue.put(('sendbroadcast', ''))

        if self.ackDataHasAVaildHeader(ackData):
            shared.checkAndShareObjectWithPeers(ackData[24:])

        # Display timing data
        timeRequiredToAttemptToDecryptMessage = time.time(
        ) - messageProcessingStartTime
        shared.successfullyDecryptMessageTimings.append(
            timeRequiredToAttemptToDecryptMessage)
        sum = 0
        for item in shared.successfullyDecryptMessageTimings:
            sum += item
        logger.debug('Time to decrypt this message successfully: %s\n\
                     Average time for all message decryption successes since startup: %s.' %
                     (timeRequiredToAttemptToDecryptMessage, sum / len(shared.successfullyDecryptMessageTimings)) 
                     )


    def processbroadcast(self, data):
        messageProcessingStartTime = time.time()
        shared.numberOfBroadcastsProcessed += 1
        shared.UISignalQueue.put((
            'updateNumberOfBroadcastsProcessed', 'no data'))
        inventoryHash = calculateInventoryHash(data)
        readPosition = 20  # bypass the nonce, time, and object type
        broadcastVersion, broadcastVersionLength = decodeVarint(
            data[readPosition:readPosition + 9])
        readPosition += broadcastVersionLength
        if broadcastVersion < 1 or broadcastVersion > 5:
            logger.info('Cannot decode incoming broadcast versions higher than 5. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.') 
            return
        if broadcastVersion == 1:
            logger.info('Version 1 broadcasts are no longer supported. Not processing it at all.')
        if broadcastVersion in [2,4]:
            """
            v2 (and later v4) broadcasts are encrypted the same way the msgs were encrypted. To see if we are interested in a
            v2 broadcast, we try to decrypt it. This was replaced with v3 (and later v5) broadcasts which include a tag which 
            we check instead, just like we do with v4 pubkeys. 
            v2 and v3 broadcasts should be completely obsolete after the protocol v3 upgrade period and some code can be simplified.
            """
            cleartextStreamNumber, cleartextStreamNumberLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += cleartextStreamNumberLength
            signedData = data[8:readPosition] # This doesn't end up being used if the broadcastVersion is 2
            initialDecryptionSuccessful = False
            for key, cryptorObject in shared.MyECSubscriptionCryptorObjects.items():
                try:
                    decryptedData = cryptorObject.decrypt(data[readPosition:])
                    toRipe = key  # This is the RIPE hash of the sender's pubkey. We need this below to compare to the RIPE hash of the sender's address to verify that it was encrypted by with their key rather than some other key.
                    initialDecryptionSuccessful = True
                    logger.info('EC decryption successful using key associated with ripe hash: %s' % key.encode('hex'))
                    break
                except Exception as err:
                    pass
                    # print 'cryptorObject.decrypt Exception:', err
            if not initialDecryptionSuccessful:
                # This is not a broadcast I am interested in.
                logger.debug('Length of time program spent failing to decrypt this v2 broadcast: %s seconds.' % (time.time() - messageProcessingStartTime,))
                return
            # At this point this is a broadcast I have decrypted and thus am
            # interested in.
            readPosition = 0
            if broadcastVersion == 2:
                signedBroadcastVersion, signedBroadcastVersionLength = decodeVarint(
                    decryptedData[:10])
                readPosition += signedBroadcastVersionLength
                
            beginningOfPubkeyPosition = readPosition  # used when we add the pubkey to our pubkey table. This variable can be disposed of after the protocol v3 upgrade period because it will necessarily be at the beginning of the decryptedData; ie it will definitely equal 0
            sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersAddressVersion < 2 or sendersAddressVersion > 3:
                logger.info('Cannot decode senderAddressVersion other than 2 or 3. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.')
                return
            readPosition += sendersAddressVersionLength
            sendersStream, sendersStreamLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersStream != cleartextStreamNumber:
                logger.info('The stream number outside of the encryption on which the POW was completed doesn\'t match the stream number inside the encryption. Ignoring broadcast.') 
                return
            readPosition += sendersStreamLength
            behaviorBitfield = decryptedData[readPosition:readPosition + 4]
            readPosition += 4
            sendersPubSigningKey = '\x04' + \
                decryptedData[readPosition:readPosition + 64]
            readPosition += 64
            sendersPubEncryptionKey = '\x04' + \
                decryptedData[readPosition:readPosition + 64]
            readPosition += 64
            if sendersAddressVersion >= 3:
                requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                logger.debug('sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is %s' % requiredAverageProofOfWorkNonceTrialsPerByte)
                requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                logger.debug('sender\'s requiredPayloadLengthExtraBytes is %s' % requiredPayloadLengthExtraBytes)
            endOfPubkeyPosition = readPosition

            sha = hashlib.new('sha512')
            sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
            ripe = hashlib.new('ripemd160')
            ripe.update(sha.digest())

            if toRipe != ripe.digest():
                logger.info('The encryption key used to encrypt this message doesn\'t match the keys inbedded in the message itself. Ignoring message.') 
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
            if broadcastVersion == 2: # this can be removed after the protocol v3 upgrade period
                signedData = decryptedData[:readPositionAtBottomOfMessage]
            else:
                signedData += decryptedData[:readPositionAtBottomOfMessage]
            if not highlevelcrypto.verify(signedData, signature, sendersPubSigningKey.encode('hex')):
                logger.debug('ECDSA verify failed')
                return
            logger.debug('ECDSA verify passed')
            # verify passed

            # Let's store the public key in case we want to reply to this
            # person.
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''',
                       ripe.digest(),
                       sendersAddressVersion,
                       '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + decryptedData[beginningOfPubkeyPosition:endOfPubkeyPosition],
                       int(time.time()),
                       'yes')
            # shared.workerQueue.put(('newpubkey',(sendersAddressVersion,sendersStream,ripe.digest())))
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(ripe=ripe.digest())

            fromAddress = encodeAddress(
                sendersAddressVersion, sendersStream, ripe.digest())
            with shared.printLock:
                print 'fromAddress:', fromAddress

            if messageEncodingType == 2:
                subject, body = self.decodeType2Message(message)
                logger.info('Broadcast subject (first 100 characters): %s' % repr(subject)[:100])
            elif messageEncodingType == 1:
                body = message
                subject = ''
            elif messageEncodingType == 0:
                logger.info('messageEncodingType == 0. Doing nothing with the message.')
            else:
                body = 'Unknown encoding type.\n\n' + repr(message)
                subject = ''

            toAddress = '[Broadcast subscribers]'
            if messageEncodingType != 0:
                if helper_inbox.isMessageAlreadyInInbox(toAddress, fromAddress, subject, body, messageEncodingType):
                    logger.info('This broadcast is already in our inbox. Ignoring it.')
                else:
                    t = (inventoryHash, toAddress, fromAddress, subject, int(
                        time.time()), body, 'inbox', messageEncodingType, 0)
                    helper_inbox.insert(t)
    
                    shared.UISignalQueue.put(('displayNewInboxMessage', (
                        inventoryHash, toAddress, fromAddress, subject, body)))
    
                    # If we are behaving as an API then we might need to run an
                    # outside command to let some program know that a new message
                    # has arrived.
                    if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
                        try:
                            apiNotifyPath = shared.config.get(
                                'bitmessagesettings', 'apinotifypath')
                        except:
                            apiNotifyPath = ''
                        if apiNotifyPath != '':
                            call([apiNotifyPath, "newBroadcast"])

            # Display timing data
            logger.info('Time spent processing this interesting broadcast: %s' % (time.time() - messageProcessingStartTime,))

        if broadcastVersion in [3,5]:
            # broadcast version 3 should be completely obsolete after the end of the protocol v3 upgrade period
            cleartextStreamNumber, cleartextStreamNumberLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += cleartextStreamNumberLength
            embeddedTag = data[readPosition:readPosition+32]
            readPosition += 32
            if embeddedTag not in shared.MyECSubscriptionCryptorObjects:
                logger.debug('We\'re not interested in this broadcast.') 
                return
            # We are interested in this broadcast because of its tag.
            signedData = data[8:readPosition] # We're going to add some more data which is signed further down.
            cryptorObject = shared.MyECSubscriptionCryptorObjects[embeddedTag]
            try:
                decryptedData = cryptorObject.decrypt(data[readPosition:])
                logger.debug('EC decryption successful')
            except Exception as err:
                logger.debug('Broadcast version %s decryption Unsuccessful.' % broadcastVersion) 
                return

            # broadcast version 3 includes the broadcast version at the beginning
            # of the decryptedData. Broadcast version 5 doesn't.
            readPosition = 0
            if broadcastVersion == 3: # This section can be removed after the protocol v3 upgrade period
                signedBroadcastVersion, signedBroadcastVersionLength = decodeVarint(
                    decryptedData[:10])
                readPosition += signedBroadcastVersionLength
            
            beginningOfPubkeyPosition = readPosition  # used when we add the pubkey to our pubkey table
            sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersAddressVersion < 4:
                logger.info('Cannot decode senderAddressVersion less than 4 for broadcast version number 3 or 4. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.') 
                return
            readPosition += sendersAddressVersionLength
            sendersStream, sendersStreamLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersStream != cleartextStreamNumber:
                logger.info('The stream number outside of the encryption on which the POW was completed doesn\'t match the stream number inside the encryption. Ignoring broadcast.') 
                return
            readPosition += sendersStreamLength
            behaviorBitfield = decryptedData[readPosition:readPosition + 4]
            readPosition += 4
            sendersPubSigningKey = '\x04' + \
                decryptedData[readPosition:readPosition + 64]
            readPosition += 64
            sendersPubEncryptionKey = '\x04' + \
                decryptedData[readPosition:readPosition + 64]
            readPosition += 64
            if sendersAddressVersion >= 3:
                requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                logger.debug('sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is %s' % requiredAverageProofOfWorkNonceTrialsPerByte)
                requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                logger.debug('sender\'s requiredPayloadLengthExtraBytes is %s' % requiredPayloadLengthExtraBytes)
            endOfPubkeyPosition = readPosition

            sha = hashlib.new('sha512')
            sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            calculatedRipe = ripeHasher.digest()

            calculatedTag = hashlib.sha512(hashlib.sha512(encodeVarint(
                sendersAddressVersion) + encodeVarint(sendersStream) + calculatedRipe).digest()).digest()[32:]
            if calculatedTag != embeddedTag:
                logger.debug('The tag and encryption key used to encrypt this message doesn\'t match the keys inbedded in the message itself. Ignoring message.') 
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
            if broadcastVersion == 3: # broadcastVersion 3 should be completely unused after the end of the protocol v3 upgrade period 
                signedData = decryptedData[:readPositionAtBottomOfMessage]
            elif broadcastVersion == 5:
                signedData += decryptedData[:readPositionAtBottomOfMessage]
            if not highlevelcrypto.verify(signedData, signature, sendersPubSigningKey.encode('hex')):
                logger.debug('ECDSA verify failed')
                return
            logger.debug('ECDSA verify passed')
            # verify passed

            fromAddress = encodeAddress(
                sendersAddressVersion, sendersStream, calculatedRipe)
            logger.info('fromAddress: %s' % fromAddress)

            # Let's store the public key in case we want to reply to this person.
            sqlExecute(
                '''INSERT INTO pubkeys VALUES (?,?,?,?,?)''',
                calculatedRipe,
                sendersAddressVersion,
                '\x00\x00\x00\x00\x00\x00\x00\x01' + decryptedData[beginningOfPubkeyPosition:endOfPubkeyPosition],
                int(time.time()),
                'yes')
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the
            # POW and send it.
            self.possibleNewPubkey(address = fromAddress)

            if messageEncodingType == 2:
                subject, body = self.decodeType2Message(message)
                logger.info('Broadcast subject (first 100 characters): %s' % repr(subject)[:100])
            elif messageEncodingType == 1:
                body = message
                subject = ''
            elif messageEncodingType == 0:
                logger.info('messageEncodingType == 0. Doing nothing with the message.')
            else:
                body = 'Unknown encoding type.\n\n' + repr(message)
                subject = ''

            toAddress = '[Broadcast subscribers]'
            if messageEncodingType != 0:
                if helper_inbox.isMessageAlreadyInInbox(toAddress, fromAddress, subject, body, messageEncodingType):
                    logger.info('This broadcast is already in our inbox. Ignoring it.')
                else:
                    t = (inventoryHash, toAddress, fromAddress, subject, int(
                        time.time()), body, 'inbox', messageEncodingType, 0)
                    helper_inbox.insert(t)
    
                    shared.UISignalQueue.put(('displayNewInboxMessage', (
                        inventoryHash, toAddress, fromAddress, subject, body)))
    
                    # If we are behaving as an API then we might need to run an
                    # outside command to let some program know that a new message
                    # has arrived.
                    if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
                        try:
                            apiNotifyPath = shared.config.get(
                                'bitmessagesettings', 'apinotifypath')
                        except:
                            apiNotifyPath = ''
                        if apiNotifyPath != '':
                            call([apiNotifyPath, "newBroadcast"])

            # Display timing data
            logger.debug('Time spent processing this interesting broadcast: %s' % (time.time() - messageProcessingStartTime,))

    # We have inserted a pubkey into our pubkey table which we received from a
    # pubkey, msg, or broadcast message. It might be one that we have been
    # waiting for. Let's check.
    def possibleNewPubkey(self, ripe=None, address=None):
        # For address versions <= 3, we wait on a key with the correct ripe hash
        if ripe != None:
            if ripe in shared.neededPubkeys:
                logger.info('We have been awaiting the arrival of this pubkey.')
                del shared.neededPubkeys[ripe]
                sqlExecute(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND (status='awaitingpubkey' or status='doingpubkeypow') and folder='sent' ''',
                    ripe)
                shared.workerQueue.put(('sendmessage', ''))
            else:
                logger.debug('We don\'t need this pub key. We didn\'t ask for it. Pubkey hash: %s' % ripe.encode('hex'))
        # For address versions >= 4, we wait on a pubkey with the correct tag.
        # Let us create the tag from the address and see if we were waiting
        # for it.
        elif address != None:
            status, addressVersion, streamNumber, ripe = decodeAddress(address)
            tag = hashlib.sha512(hashlib.sha512(encodeVarint(
                addressVersion) + encodeVarint(streamNumber) + ripe).digest()).digest()[32:]
            if tag in shared.neededPubkeys:
                logger.info('We have been awaiting the arrival of this pubkey.')
                del shared.neededPubkeys[tag]
                sqlExecute(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND (status='awaitingpubkey' or status='doingpubkeypow') and folder='sent' ''',
                    ripe)
                shared.workerQueue.put(('sendmessage', ''))

    def ackDataHasAVaildHeader(self, ackData):
        if len(ackData) < shared.Header.size:
            logger.info('The length of ackData is unreasonably short. Not sending ackData.')
            return False
        
        magic,command,payloadLength,checksum = shared.Header.unpack(ackData[:shared.Header.size])
        if magic != 0xE9BEB4D9:
            logger.info('Ackdata magic bytes were wrong. Not sending ackData.')
            return False
        payload = ackData[shared.Header.size:]
        if len(payload) != payloadLength:
            logger.info('ackData payload length doesn\'t match the payload length specified in the header. Not sending ackdata.')
            return False
        if payloadLength > 1600100: # ~1.6 MB which is the maximum possible size of an inv message.
            """
            The largest message should be either an inv or a getdata message at 1.6 MB in size. 
            That doesn't mean that the object may be that big. The 
            shared.checkAndShareObjectWithPeers function will verify that it is no larger than 
            2^18 bytes.
            """
            return False
        if checksum != hashlib.sha512(payload).digest()[0:4]:  # test the checksum in the message.
            logger.info('ackdata checksum wrong. Not sending ackdata.')
            return False
        command = command.rstrip('\x00')
        if command != 'object':
            return False
        return True

    def decodeType2Message(self, message):
        bodyPositionIndex = string.find(message, '\nBody:')
        if bodyPositionIndex > 1:
            subject = message[8:bodyPositionIndex]
            # Only save and show the first 500 characters of the subject.
            # Any more is probably an attack.
            subject = subject[:500]
            body = message[bodyPositionIndex + 6:]
        else:
            subject = ''
            body = message
        # Throw away any extra lines (headers) after the subject.
        if subject:
            subject = subject.splitlines()[0]
        return subject, body

    def addMailingListNameToSubject(self, subject, mailingListName):
        subject = subject.strip()
        if subject[:3] == 'Re:' or subject[:3] == 'RE:':
            subject = subject[3:].strip()
        if '[' + mailingListName + ']' in subject:
            return subject
        else:
            return '[' + mailingListName + '] ' + subject

    def decodeType2Message(self, message):
        bodyPositionIndex = string.find(message, '\nBody:')
        if bodyPositionIndex > 1:
            subject = message[8:bodyPositionIndex]
            # Only save and show the first 500 characters of the subject.
            # Any more is probably an attack.
            subject = subject[:500]
            body = message[bodyPositionIndex + 6:]
        else:
            subject = ''
            body = message
        # Throw away any extra lines (headers) after the subject.
        if subject:
            subject = subject.splitlines()[0]
        return subject, body
