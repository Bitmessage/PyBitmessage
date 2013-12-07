import time
import threading
import shared
import hashlib
import random
from struct import unpack, pack
import sys
import string
from subprocess import call  # used when the API must execute an outside program
from pyelliptic.openssl import OpenSSL

import highlevelcrypto
from addresses import *
import helper_generic
import helper_bitcoin
import helper_inbox
import helper_sent
from helper_sql import *
import tr
from debug import logger


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

            if objectType == 'getpubkey':
                self.processgetpubkey(data)
            elif objectType == 'pubkey':
                self.processpubkey(data)
            elif objectType == 'msg':
                self.processmsg(data)
            elif objectType == 'broadcast':
                self.processbroadcast(data)
            elif objectType == 'checkShutdownVariable': # is more of a command, not an object type. Is used to get this thread past the queue.get() so that it will check the shutdown variable.
                pass
            else:
                logger.critical('Error! Bug! The class_objectProcessor was passed an object type it doesn\'t recognize: %s' % str(objectType))

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
        readPosition = 8  # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        requestedAddressVersionNumber, addressVersionLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += addressVersionLength
        streamNumber, streamNumberLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += streamNumberLength

        if requestedAddressVersionNumber == 0:
            print 'The requestedAddressVersionNumber of the pubkey request is zero. That doesn\'t make any sense. Ignoring it.'
            return
        elif requestedAddressVersionNumber == 1:
            print 'The requestedAddressVersionNumber of the pubkey request is 1 which isn\'t supported anymore. Ignoring it.'
            return
        elif requestedAddressVersionNumber > 4:
            print 'The requestedAddressVersionNumber of the pubkey request is too high. Can\'t understand. Ignoring it.'
            return

        myAddress = ''
        if requestedAddressVersionNumber <= 3 :
            requestedHash = data[readPosition:readPosition + 20]
            if len(requestedHash) != 20:
                print 'The length of the requested hash is not 20 bytes. Something is wrong. Ignoring.'
                return
            with shared.printLock:
                print 'the hash requested in this getpubkey request is:', requestedHash.encode('hex')
            if requestedHash in shared.myAddressesByHash:  # if this address hash is one of mine
                myAddress = shared.myAddressesByHash[requestedHash]
        elif requestedAddressVersionNumber >= 4:
            requestedTag = data[readPosition:readPosition + 32]
            if len(requestedTag) != 32:
                print 'The length of the requested tag is not 32 bytes. Something is wrong. Ignoring.'
                return
            with shared.printLock:
                print 'the tag requested in this getpubkey request is:', requestedTag.encode('hex')
            if requestedTag in shared.myAddressesByTag:
                myAddress = shared.myAddressesByTag[requestedTag]

        if myAddress == '':
            with shared.printLock:
                print 'This getpubkey request is not for any of my keys.'
            return

        if decodeAddress(myAddress)[1] != requestedAddressVersionNumber:
            with shared.printLock:
                sys.stderr.write(
                 '(Within the recgetpubkey function) Someone requested one of my pubkeys but the requestedAddressVersionNumber doesn\'t match my actual address version number. Ignoring.\n')
            return
        if decodeAddress(myAddress)[2] != streamNumber:
            with shared.printLock:
                sys.stderr.write(
                 '(Within the recgetpubkey function) Someone requested one of my pubkeys but the stream number on which we heard this getpubkey object doesn\'t match this address\' stream number. Ignoring.\n')
            return
        if shared.safeConfigGetBoolean(myAddress, 'chan'):
            with shared.printLock:
                print 'Ignoring getpubkey request because it is for one of my chan addresses. The other party should already have the pubkey.'
            return
        try:
            lastPubkeySendTime = int(shared.config.get(
                myAddress, 'lastpubkeysendtime'))
        except:
            lastPubkeySendTime = 0
        if lastPubkeySendTime > time.time() - shared.lengthOfTimeToHoldOnToAllPubkeys:  # If the last time we sent our pubkey was more recent than 28 days ago...
            with shared.printLock:
                print 'Found getpubkey-requested-item in my list of EC hashes BUT we already sent it recently. Ignoring request. The lastPubkeySendTime is:', lastPubkeySendTime
            return

        with shared.printLock:
            print 'Found getpubkey-requested-hash in my list of EC hashes. Telling Worker thread to do the POW for a pubkey message and send it out.'
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
        readPosition = 8  # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        addressVersion, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        if addressVersion == 0:
            print '(Within processpubkey) addressVersion of 0 doesn\'t make sense.'
            return
        if addressVersion > 4 or addressVersion == 1:
            with shared.printLock:
                print 'This version of Bitmessage cannot handle version', addressVersion, 'addresses.'
            return
        if addressVersion == 2:
            if len(data) < 146:  # sanity check. This is the minimum possible length.
                print '(within processpubkey) payloadLength less than 146. Sanity check failed.'
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
                print 'publicEncryptionKey length less than 64. Sanity check failed.'
                return
            sha = hashlib.new('sha512')
            sha.update(
                '\x04' + publicSigningKey + '\x04' + publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()

            with shared.printLock:
                print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
                print 'ripe', ripe.encode('hex')
                print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
                print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')


            queryreturn = sqlQuery(
                '''SELECT usedpersonally FROM pubkeys WHERE hash=? AND addressversion=? AND usedpersonally='yes' ''', ripe, addressVersion)
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                print 'We HAVE used this pubkey personally. Updating time.'
                t = (ripe, addressVersion, data, embeddedTime, 'yes')
            else:
                print 'We have NOT used this pubkey personally. Inserting in database.'
                t = (ripe, addressVersion, data, embeddedTime, 'no')
                     # This will also update the embeddedTime.
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
            # shared.workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))
            self.possibleNewPubkey(ripe = ripe)
        if addressVersion == 3:
            if len(data) < 170:  # sanity check.
                print '(within processpubkey) payloadLength less than 170. Sanity check failed.'
                return
            bitfieldBehaviors = data[readPosition:readPosition + 4]
            readPosition += 4
            publicSigningKey = '\x04' + data[readPosition:readPosition + 64]
            # Is it possible for a public key to be invalid such that trying to
            # encrypt or sign with it will cause an error? If it is, we should
            # probably test these keys here.
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
            try:
                if not highlevelcrypto.verify(data[8:endOfSignedDataPosition], signature, publicSigningKey.encode('hex')):
                    print 'ECDSA verify failed (within processpubkey)'
                    return
                print 'ECDSA verify passed (within processpubkey)'
            except Exception as err:
                print 'ECDSA verify failed (within processpubkey)', err
                return

            sha = hashlib.new('sha512')
            sha.update(publicSigningKey + publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()

            with shared.printLock:
                print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
                print 'ripe', ripe.encode('hex')
                print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
                print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')


            queryreturn = sqlQuery('''SELECT usedpersonally FROM pubkeys WHERE hash=? AND addressversion=? AND usedpersonally='yes' ''', ripe, addressVersion)
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                print 'We HAVE used this pubkey personally. Updating time.'
                t = (ripe, addressVersion, data, embeddedTime, 'yes')
            else:
                print 'We have NOT used this pubkey personally. Inserting in database.'
                t = (ripe, addressVersion, data, embeddedTime, 'no')
                     # This will also update the embeddedTime.
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
            self.possibleNewPubkey(ripe = ripe)

        if addressVersion == 4:
            """
            There exist a function: shared.decryptAndCheckPubkeyPayload which does something almost
            the same as this section of code. There are differences, however; one being that 
            decryptAndCheckPubkeyPayload requires that a cryptor object be created each time it is
            run which is an expensive operation. This, on the other hand, keeps them saved in 
            the shared.neededPubkeys dictionary so that if an attacker sends us many 
            incorrectly-tagged pubkeys, which would force us to try to decrypt them, this code 
            would run and handle that event quite quickly. 
            """ 
            if len(data) < 350:  # sanity check.
                print '(within processpubkey) payloadLength less than 350. Sanity check failed.'
                return
            signedData = data[8:readPosition] # Some of the signed data is not encrypted so let's keep it for now.
            tag = data[readPosition:readPosition + 32]
            readPosition += 32
            encryptedData = data[readPosition:]
            if tag not in shared.neededPubkeys:
                with shared.printLock:
                    print 'We don\'t need this v4 pubkey. We didn\'t ask for it.'
                return

            # Let us try to decrypt the pubkey
            cryptorObject = shared.neededPubkeys[tag]
            try:
                decryptedData = cryptorObject.decrypt(encryptedData)
            except:
                # Someone must have encrypted some data with a different key
                # but tagged it with a tag for which we are watching.
                with shared.printLock:
                    print 'Pubkey decryption was unsuccessful.'
                return

            readPosition = 0
            bitfieldBehaviors = decryptedData[readPosition:readPosition + 4]
            readPosition += 4
            publicSigningKey = '\x04' + decryptedData[readPosition:readPosition + 64]
            # Is it possible for a public key to be invalid such that trying to
            # encrypt or check a sig with it will cause an error? If it is, we
            # should probably test these keys here.
            readPosition += 64
            publicEncryptionKey = '\x04' + decryptedData[readPosition:readPosition + 64]
            readPosition += 64
            specifiedNonceTrialsPerByte, specifiedNonceTrialsPerByteLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += specifiedNonceTrialsPerByteLength
            specifiedPayloadLengthExtraBytes, specifiedPayloadLengthExtraBytesLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += specifiedPayloadLengthExtraBytesLength
            signedData += decryptedData[:readPosition]
            signatureLength, signatureLengthLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += signatureLengthLength
            signature = decryptedData[readPosition:readPosition + signatureLength]
            try:
                if not highlevelcrypto.verify(signedData, signature, publicSigningKey.encode('hex')):
                    print 'ECDSA verify failed (within processpubkey)'
                    return
                print 'ECDSA verify passed (within processpubkey)'
            except Exception as err:
                print 'ECDSA verify failed (within processpubkey)', err
                return

            sha = hashlib.new('sha512')
            sha.update(publicSigningKey + publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()

            # We need to make sure that the tag on the outside of the encryption
            # is the one generated from hashing these particular keys.
            if tag != hashlib.sha512(hashlib.sha512(encodeVarint(addressVersion) + encodeVarint(streamNumber) + ripe).digest()).digest()[32:]:
                with shared.printLock:
                    print 'Someone was trying to act malicious: tag doesn\'t match the keys in this pubkey message. Ignoring it.'
                return
            else:
                print 'Tag successfully matches keys in pubkey message' # testing. Will remove soon.

            with shared.printLock:
                print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
                print 'ripe', ripe.encode('hex')
                print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
                print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')

            t = (ripe, addressVersion, signedData, embeddedTime, 'yes')
            sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)

            fromAddress = encodeAddress(addressVersion, streamNumber, ripe)
            # That this point we know that we have been waiting on this pubkey.
            # This function will command the workerThread to start work on
            # the messages that require it.
            self.possibleNewPubkey(address = fromAddress)

        # Display timing data
        timeRequiredToProcessPubkey = time.time(
        ) - pubkeyProcessingStartTime
        with shared.printLock:
            print 'Time required to process this pubkey:', timeRequiredToProcessPubkey


    def processmsg(self, data):
        messageProcessingStartTime = time.time()
        shared.numberOfMessagesProcessed += 1
        shared.UISignalQueue.put((
            'updateNumberOfMessagesProcessed', 'no data'))
        readPosition = 8 # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4
        streamNumberAsClaimedByMsg, streamNumberAsClaimedByMsgLength = decodeVarint(
            data[readPosition:readPosition + 9])
        readPosition += streamNumberAsClaimedByMsgLength
        inventoryHash = calculateInventoryHash(data)
        initialDecryptionSuccessful = False
        # Let's check whether this is a message acknowledgement bound for us.
        if data[readPosition:] in shared.ackdataForWhichImWatching:
            with shared.printLock:
                print 'This msg IS an acknowledgement bound for me.'

            del shared.ackdataForWhichImWatching[data[readPosition:]]
            sqlExecute('UPDATE sent SET status=? WHERE ackdata=?',
                       'ackreceived', data[readPosition:])
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (data[readPosition:], tr.translateText("MainWindow",'Acknowledgement of the message received. %1').arg(unicode(
                time.strftime(shared.config.get('bitmessagesettings', 'timeformat'), time.localtime(int(time.time()))), 'utf-8')))))
            return
        else:
            with shared.printLock:
                print 'This was NOT an acknowledgement bound for me.'
            # print 'shared.ackdataForWhichImWatching', shared.ackdataForWhichImWatching


        # This is not an acknowledgement bound for me. See if it is a message
        # bound for me by trying to decrypt it with my private keys.
        for key, cryptorObject in shared.myECCryptorObjects.items():
            try:
                decryptedData = cryptorObject.decrypt(
                    data[readPosition:])
                toRipe = key  # This is the RIPE hash of my pubkeys. We need this below to compare to the destination_ripe included in the encrypted data.
                initialDecryptionSuccessful = True
                with shared.printLock:
                    print 'EC decryption successful using key associated with ripe hash:', key.encode('hex')
                break
            except Exception as err:
                pass
                # print 'cryptorObject.decrypt Exception:', err
        if not initialDecryptionSuccessful:
            # This is not a message bound for me.
            with shared.printLock:
                print 'Length of time program spent failing to decrypt this message:', time.time() - messageProcessingStartTime, 'seconds.'
            return

        # This is a message bound for me.
        toAddress = shared.myAddressesByHash[
            toRipe]  # Look up my address based on the RIPE hash.
        readPosition = 0
        messageVersion, messageVersionLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += messageVersionLength
        if messageVersion != 1:
            print 'Cannot understand message versions other than one. Ignoring message.'
            return
        sendersAddressVersionNumber, sendersAddressVersionNumberLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += sendersAddressVersionNumberLength
        if sendersAddressVersionNumber == 0:
            print 'Cannot understand sendersAddressVersionNumber = 0. Ignoring message.'
            return
        if sendersAddressVersionNumber > 4:
            print 'Sender\'s address version number', sendersAddressVersionNumber, 'not yet supported. Ignoring message.'
            return
        if len(decryptedData) < 170:
            print 'Length of the unencrypted data is unreasonably short. Sanity check failed. Ignoring message.'
            return
        sendersStreamNumber, sendersStreamNumberLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        if sendersStreamNumber == 0:
            print 'sender\'s stream number is 0. Ignoring message.'
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
            print 'sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is', requiredAverageProofOfWorkNonceTrialsPerByte
            requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += varintLength
            print 'sender\'s requiredPayloadLengthExtraBytes is', requiredPayloadLengthExtraBytes
        endOfThePublicKeyPosition = readPosition  # needed for when we store the pubkey in our database of pubkeys for later use.
        if toRipe != decryptedData[readPosition:readPosition + 20]:
            with shared.printLock:
                print 'The original sender of this message did not send it to you. Someone is attempting a Surreptitious Forwarding Attack.'
                print 'See: http://world.std.com/~dtd/sign_encrypt/sign_encrypt7.html'
                print 'your toRipe:', toRipe.encode('hex')
                print 'embedded destination toRipe:', decryptedData[readPosition:readPosition + 20].encode('hex')
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
        try:
            if not highlevelcrypto.verify(decryptedData[:positionOfBottomOfAckData], signature, pubSigningKey.encode('hex')):
                print 'ECDSA verify failed'
                return
            print 'ECDSA verify passed'
        except Exception as err:
            print 'ECDSA verify failed', err
            return
        with shared.printLock:
            print 'As a matter of intellectual curiosity, here is the Bitcoin address associated with the keys owned by the other person:', helper_bitcoin.calculateBitcoinAddressFromPubkey(pubSigningKey), '  ..and here is the testnet address:', helper_bitcoin.calculateTestnetAddressFromPubkey(pubSigningKey), '. The other person must take their private signing key from Bitmessage and import it into Bitcoin (or a service like Blockchain.info) for it to be of any use. Do not use this unless you know what you are doing.'

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
                '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + decryptedData[messageVersionLength:endOfThePublicKeyPosition],
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
                '\x00\x00\x00\x00\x00\x00\x00\x01' + decryptedData[messageVersionLength:endOfThePublicKeyPosition],
                int(time.time()),
                'yes')
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(address = fromAddress)
        # If this message is bound for one of my version 3 addresses (or
        # higher), then we must check to make sure it meets our demanded
        # proof of work requirement.
        if decodeAddress(toAddress)[1] >= 3:  # If the toAddress version number is 3 or higher:
            if not shared.isAddressInMyAddressBookSubscriptionsListOrWhitelist(fromAddress):  # If I'm not friendly with this person:
                requiredNonceTrialsPerByte = shared.config.getint(
                    toAddress, 'noncetrialsperbyte')
                requiredPayloadLengthExtraBytes = shared.config.getint(
                    toAddress, 'payloadlengthextrabytes')
                if not shared.isProofOfWorkSufficient(data, requiredNonceTrialsPerByte, requiredPayloadLengthExtraBytes):
                    print 'Proof of work in msg message insufficient only because it does not meet our higher requirement.'
                    return
        blockMessage = False  # Gets set to True if the user shouldn't see the message according to black or white lists.
        if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':  # If we are using a blacklist
            queryreturn = sqlQuery(
                '''SELECT label FROM blacklist where address=? and enabled='1' ''',
                fromAddress)
            if queryreturn != []:
                with shared.printLock:
                    print 'Message ignored because address is in blacklist.'

                blockMessage = True
        else:  # We're using a whitelist
            queryreturn = sqlQuery(
                '''SELECT label FROM whitelist where address=? and enabled='1' ''',
                fromAddress)
            if queryreturn == []:
                print 'Message ignored because address not in whitelist.'
                blockMessage = True
        if not blockMessage:
            toLabel = shared.config.get(toAddress, 'label')
            if toLabel == '':
                toLabel = toAddress

            if messageEncodingType == 2:
                subject, body = self.decodeType2Message(message)
            elif messageEncodingType == 1:
                body = message
                subject = ''
            elif messageEncodingType == 0:
                print 'messageEncodingType == 0. Doing nothing with the message. They probably just sent it so that we would store their public key or send their ack data for them.'
            else:
                body = 'Unknown encoding type.\n\n' + repr(message)
                subject = ''
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
            if ackData[4:16] == 'getpubkey\x00\x00\x00':
                shared.checkAndSharegetpubkeyWithPeers(ackData[24:])
            elif ackData[4:16] == 'pubkey\x00\x00\x00\x00\x00\x00':
                shared.checkAndSharePubkeyWithPeers(ackData[24:])
            elif ackData[4:16] == 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                shared.checkAndShareMsgWithPeers(ackData[24:])
            elif ackData[4:16] == 'broadcast\x00\x00\x00':
                shared.checkAndShareBroadcastWithPeers(ackData[24:])

        # Display timing data
        timeRequiredToAttemptToDecryptMessage = time.time(
        ) - messageProcessingStartTime
        shared.successfullyDecryptMessageTimings.append(
            timeRequiredToAttemptToDecryptMessage)
        sum = 0
        for item in shared.successfullyDecryptMessageTimings:
            sum += item
        with shared.printLock:
            print 'Time to decrypt this message successfully:', timeRequiredToAttemptToDecryptMessage
            print 'Average time for all message decryption successes since startup:', sum / len(shared.successfullyDecryptMessageTimings)


    def processbroadcast(self, data):
        messageProcessingStartTime = time.time()
        shared.numberOfBroadcastsProcessed += 1
        shared.UISignalQueue.put((
            'updateNumberOfBroadcastsProcessed', 'no data'))
        inventoryHash = calculateInventoryHash(data)
        readPosition = 8  # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        broadcastVersion, broadcastVersionLength = decodeVarint(
            data[readPosition:readPosition + 9])
        readPosition += broadcastVersionLength
        if broadcastVersion < 1 or broadcastVersion > 3:
            print 'Cannot decode incoming broadcast versions higher than 3. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.'
            return
        if broadcastVersion == 1:
            beginningOfPubkeyPosition = readPosition  # used when we add the pubkey to our pubkey table
            sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
                data[readPosition:readPosition + 9])
            if sendersAddressVersion <= 1 or sendersAddressVersion >= 3:
                # Cannot decode senderAddressVersion higher than 2. Assuming
                # the sender isn\'t being silly, you should upgrade Bitmessage
                # because this message shall be ignored.
                return
            readPosition += sendersAddressVersionLength
            if sendersAddressVersion == 2:
                sendersStream, sendersStreamLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                readPosition += sendersStreamLength
                behaviorBitfield = data[readPosition:readPosition + 4]
                readPosition += 4
                sendersPubSigningKey = '\x04' + \
                    data[readPosition:readPosition + 64]
                readPosition += 64
                sendersPubEncryptionKey = '\x04' + \
                    data[readPosition:readPosition + 64]
                readPosition += 64
                endOfPubkeyPosition = readPosition
                sendersHash = data[readPosition:readPosition + 20]
                if sendersHash not in shared.broadcastSendersForWhichImWatching:
                    # Display timing data
                    with shared.printLock:
                        print 'Time spent deciding that we are not interested in this v1 broadcast:', time.time() - messageProcessingStartTime

                    return
                # At this point, this message claims to be from sendersHash and
                # we are interested in it. We still have to hash the public key
                # to make sure it is truly the key that matches the hash, and
                # also check the signiture.
                readPosition += 20

                sha = hashlib.new('sha512')
                sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
                ripe = hashlib.new('ripemd160')
                ripe.update(sha.digest())
                if ripe.digest() != sendersHash:
                    # The sender of this message lied.
                    return
                messageEncodingType, messageEncodingTypeLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                if messageEncodingType == 0:
                    return
                readPosition += messageEncodingTypeLength
                messageLength, messageLengthLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                readPosition += messageLengthLength
                message = data[readPosition:readPosition + messageLength]
                readPosition += messageLength
                readPositionAtBottomOfMessage = readPosition
                signatureLength, signatureLengthLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                readPosition += signatureLengthLength
                signature = data[readPosition:readPosition + signatureLength]
                try:
                    if not highlevelcrypto.verify(data[12:readPositionAtBottomOfMessage], signature, sendersPubSigningKey.encode('hex')):
                        print 'ECDSA verify failed'
                        return
                    print 'ECDSA verify passed'
                except Exception as err:
                    print 'ECDSA verify failed', err
                    return
                # verify passed
                fromAddress = encodeAddress(
                    sendersAddressVersion, sendersStream, ripe.digest())
                with shared.printLock:
                    print 'fromAddress:', fromAddress

                # Let's store the public key in case we want to reply to this person.
                # We don't have the correct nonce or time (which would let us
                # send out a pubkey message) so we'll just fill it with 1's. We
                # won't be able to send this pubkey to others (without doing
                # the proof of work ourselves, which this program is programmed
                # to not do.)
                sqlExecute(
                    '''INSERT INTO pubkeys VALUES (?,?,?,?,?)''',
                    ripe.digest(),
                    sendersAddressVersion,
                    '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + data[beginningOfPubkeyPosition:endOfPubkeyPosition],
                    int(time.time()),
                    'yes')
                # This will check to see whether we happen to be awaiting this
                # pubkey in order to send a message. If we are, it will do the
                # POW and send it.
                self.possibleNewPubkey(ripe=ripe.digest())


                if messageEncodingType == 2:
                    subject, body = decodeType2Message(message)
                elif messageEncodingType == 1:
                    body = message
                    subject = ''
                elif messageEncodingType == 0:
                    print 'messageEncodingType == 0. Doing nothing with the message.'
                else:
                    body = 'Unknown encoding type.\n\n' + repr(message)
                    subject = ''

                toAddress = '[Broadcast subscribers]'
                if messageEncodingType != 0:

                    t = (inventoryHash, toAddress, fromAddress, subject, int(
                        time.time()), body, 'inbox', messageEncodingType, 0)
                    helper_inbox.insert(t)

                    shared.UISignalQueue.put(('displayNewInboxMessage', (
                        inventoryHash, toAddress, fromAddress, subject, body)))

                    # If we are behaving as an API then we might need to run an
                    # outside command to let some program know that a new
                    # message has arrived.
                    if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
                        try:
                            apiNotifyPath = shared.config.get(
                                'bitmessagesettings', 'apinotifypath')
                        except:
                            apiNotifyPath = ''
                        if apiNotifyPath != '':
                            call([apiNotifyPath, "newBroadcast"])

                # Display timing data
                with shared.printLock:
                    print 'Time spent processing this interesting broadcast:', time.time() - messageProcessingStartTime

        if broadcastVersion == 2:
            cleartextStreamNumber, cleartextStreamNumberLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += cleartextStreamNumberLength
            initialDecryptionSuccessful = False
            for key, cryptorObject in shared.MyECSubscriptionCryptorObjects.items():
                try:
                    decryptedData = cryptorObject.decrypt(data[readPosition:])
                    toRipe = key  # This is the RIPE hash of the sender's pubkey. We need this below to compare to the RIPE hash of the sender's address to verify that it was encrypted by with their key rather than some other key.
                    initialDecryptionSuccessful = True
                    print 'EC decryption successful using key associated with ripe hash:', key.encode('hex')
                    break
                except Exception as err:
                    pass
                    # print 'cryptorObject.decrypt Exception:', err
            if not initialDecryptionSuccessful:
                # This is not a broadcast I am interested in.
                with shared.printLock:
                    print 'Length of time program spent failing to decrypt this v2 broadcast:', time.time() - messageProcessingStartTime, 'seconds.'

                return
            # At this point this is a broadcast I have decrypted and thus am
            # interested in.
            signedBroadcastVersion, readPosition = decodeVarint(
                decryptedData[:10])
            beginningOfPubkeyPosition = readPosition  # used when we add the pubkey to our pubkey table
            sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersAddressVersion < 2 or sendersAddressVersion > 3:
                print 'Cannot decode senderAddressVersion other than 2 or 3. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.'
                return
            readPosition += sendersAddressVersionLength
            sendersStream, sendersStreamLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersStream != cleartextStreamNumber:
                print 'The stream number outside of the encryption on which the POW was completed doesn\'t match the stream number inside the encryption. Ignoring broadcast.'
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
                print 'sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is', requiredAverageProofOfWorkNonceTrialsPerByte
                requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                print 'sender\'s requiredPayloadLengthExtraBytes is', requiredPayloadLengthExtraBytes
            endOfPubkeyPosition = readPosition

            sha = hashlib.new('sha512')
            sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
            ripe = hashlib.new('ripemd160')
            ripe.update(sha.digest())

            if toRipe != ripe.digest():
                print 'The encryption key used to encrypt this message doesn\'t match the keys inbedded in the message itself. Ignoring message.'
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
            try:
                if not highlevelcrypto.verify(decryptedData[:readPositionAtBottomOfMessage], signature, sendersPubSigningKey.encode('hex')):
                    print 'ECDSA verify failed'
                    return
                print 'ECDSA verify passed'
            except Exception as err:
                print 'ECDSA verify failed', err
                return
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
            elif messageEncodingType == 1:
                body = message
                subject = ''
            elif messageEncodingType == 0:
                print 'messageEncodingType == 0. Doing nothing with the message.'
            else:
                body = 'Unknown encoding type.\n\n' + repr(message)
                subject = ''

            toAddress = '[Broadcast subscribers]'
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
                        call([apiNotifyPath, "newBroadcast"])

            # Display timing data
            with shared.printLock:
                print 'Time spent processing this interesting broadcast:', time.time() - messageProcessingStartTime

        if broadcastVersion == 3:
            cleartextStreamNumber, cleartextStreamNumberLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += cleartextStreamNumberLength
            embeddedTag = data[readPosition:readPosition+32]
            readPosition += 32
            if embeddedTag not in shared.MyECSubscriptionCryptorObjects:
                with shared.printLock:
                    print 'We\'re not interested in this broadcast.'
                return
            # We are interested in this broadcast because of its tag.
            cryptorObject = shared.MyECSubscriptionCryptorObjects[embeddedTag]
            try:
                decryptedData = cryptorObject.decrypt(data[readPosition:])
                print 'EC decryption successful'
            except Exception as err:
                with shared.printLock:
                    print 'Broadcast version 3 decryption Unsuccessful.'
                return

            signedBroadcastVersion, readPosition = decodeVarint(
                decryptedData[:10])
            beginningOfPubkeyPosition = readPosition  # used when we add the pubkey to our pubkey table
            sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersAddressVersion < 4:
                print 'Cannot decode senderAddressVersion less than 4 for broadcast version number 3. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.'
                return
            readPosition += sendersAddressVersionLength
            sendersStream, sendersStreamLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersStream != cleartextStreamNumber:
                print 'The stream number outside of the encryption on which the POW was completed doesn\'t match the stream number inside the encryption. Ignoring broadcast.'
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
                print 'sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is', requiredAverageProofOfWorkNonceTrialsPerByte
                requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                print 'sender\'s requiredPayloadLengthExtraBytes is', requiredPayloadLengthExtraBytes
            endOfPubkeyPosition = readPosition

            sha = hashlib.new('sha512')
            sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            calculatedRipe = ripeHasher.digest()

            calculatedTag = hashlib.sha512(hashlib.sha512(encodeVarint(
                sendersAddressVersion) + encodeVarint(sendersStream) + calculatedRipe).digest()).digest()[32:]
            if calculatedTag != embeddedTag:
                print 'The tag and encryption key used to encrypt this message doesn\'t match the keys inbedded in the message itself. Ignoring message.'
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
            try:
                if not highlevelcrypto.verify(decryptedData[:readPositionAtBottomOfMessage], signature, sendersPubSigningKey.encode('hex')):
                    print 'ECDSA verify failed'
                    return
                print 'ECDSA verify passed'
            except Exception as err:
                print 'ECDSA verify failed', err
                return
            # verify passed

            fromAddress = encodeAddress(
                sendersAddressVersion, sendersStream, calculatedRipe)
            with shared.printLock:
                print 'fromAddress:', fromAddress

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
            elif messageEncodingType == 1:
                body = message
                subject = ''
            elif messageEncodingType == 0:
                print 'messageEncodingType == 0. Doing nothing with the message.'
            else:
                body = 'Unknown encoding type.\n\n' + repr(message)
                subject = ''

            toAddress = '[Broadcast subscribers]'
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
                        call([apiNotifyPath, "newBroadcast"])

            # Display timing data
            with shared.printLock:
                print 'Time spent processing this interesting broadcast:', time.time() - messageProcessingStartTime


    # We have inserted a pubkey into our pubkey table which we received from a
    # pubkey, msg, or broadcast message. It might be one that we have been
    # waiting for. Let's check.
    def possibleNewPubkey(self, ripe=None, address=None):
        # For address versions <= 3, we wait on a key with the correct ripe hash
        if ripe != None:
            if ripe in shared.neededPubkeys:
                print 'We have been awaiting the arrival of this pubkey.'
                del shared.neededPubkeys[ripe]
                sqlExecute(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND (status='awaitingpubkey' or status='doingpubkeypow') and folder='sent' ''',
                    ripe)
                shared.workerQueue.put(('sendmessage', ''))
            else:
                with shared.printLock:
                    print 'We don\'t need this pub key. We didn\'t ask for it. Pubkey hash:', ripe.encode('hex')
        # For address versions >= 4, we wait on a pubkey with the correct tag.
        # Let us create the tag from the address and see if we were waiting
        # for it.
        elif address != None:
            status, addressVersion, streamNumber, ripe = decodeAddress(address)
            tag = hashlib.sha512(hashlib.sha512(encodeVarint(
                addressVersion) + encodeVarint(streamNumber) + ripe).digest()).digest()[32:]
            if tag in shared.neededPubkeys:
                print 'We have been awaiting the arrival of this pubkey.'
                del shared.neededPubkeys[tag]
                sqlExecute(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND (status='awaitingpubkey' or status='doingpubkeypow') and folder='sent' ''',
                    ripe)
                shared.workerQueue.put(('sendmessage', ''))

    def ackDataHasAVaildHeader(self, ackData):
        if len(ackData) < 24:
            print 'The length of ackData is unreasonably short. Not sending ackData.'
            return False
        if ackData[0:4] != '\xe9\xbe\xb4\xd9':
            print 'Ackdata magic bytes were wrong. Not sending ackData.'
            return False
        ackDataPayloadLength, = unpack('>L', ackData[16:20])
        if len(ackData) - 24 != ackDataPayloadLength:
            print 'ackData payload length doesn\'t match the payload length specified in the header. Not sending ackdata.'
            return False
        if ackData[20:24] != hashlib.sha512(ackData[24:]).digest()[0:4]:  # test the checksum in the message.
            print 'ackdata checksum wrong. Not sending ackdata.'
            return False
        if ackDataPayloadLength > 180000000: # If the size of the message is greater than 180MB, ignore it.
            return False
        if (ackData[4:16] != 'getpubkey\x00\x00\x00' and
            ackData[4:16] != 'pubkey\x00\x00\x00\x00\x00\x00' and
            ackData[4:16] != 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00' and
            ackData[4:16] != 'broadcast\x00\x00\x00'):
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