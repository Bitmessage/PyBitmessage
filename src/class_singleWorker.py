from __future__ import division

import threading
import shared
import time
from time import strftime, localtime, gmtime
import random
from subprocess import call  # used when the API must execute an outside program
from addresses import *
import highlevelcrypto
import proofofwork
import sys
import tr
from debug import logger
from helper_sql import *
import helper_inbox
from helper_generic import addDataPadding
import l10n

# This thread, of which there is only one, does the heavy lifting:
# calculating POWs.


class singleWorker(threading.Thread):

    def __init__(self):
        # QThread.__init__(self, parent)
        threading.Thread.__init__(self)

    def run(self):
        
        # Initialize the neededPubkeys dictionary.
        queryreturn = sqlQuery(
            '''SELECT DISTINCT toaddress FROM sent WHERE (status='awaitingpubkey' AND folder='sent')''')
        for row in queryreturn:
            toAddress, = row
            toStatus, toAddressVersionNumber, toStreamNumber, toRipe = decodeAddress(toAddress)
            if toAddressVersionNumber <= 3 :
                shared.neededPubkeys[toAddress] = 0
            elif toAddressVersionNumber >= 4:
                doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                    toAddressVersionNumber) + encodeVarint(toStreamNumber) + toRipe).digest()).digest()
                privEncryptionKey = doubleHashOfAddressData[:32] # Note that this is the first half of the sha512 hash.
                tag = doubleHashOfAddressData[32:]
                shared.neededPubkeys[tag] = (toAddress, highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex'))) # We'll need this for when we receive a pubkey reply: it will be encrypted and we'll need to decrypt it.

        # Initialize the shared.ackdataForWhichImWatching data structure
        queryreturn = sqlQuery(
            '''SELECT ackdata FROM sent where (status='msgsent' OR status='doingmsgpow')''')
        for row in queryreturn:
            ackdata, = row
            print 'Watching for ackdata', ackdata.encode('hex')
            shared.ackdataForWhichImWatching[ackdata] = 0

        time.sleep(
            10)  # give some time for the GUI to start before we start on existing POW tasks.

        queryreturn = sqlQuery(
            '''SELECT DISTINCT toaddress FROM sent WHERE (status='doingpubkeypow' AND folder='sent')''')
        for row in queryreturn:
            toaddress, = row
            self.requestPubKey(toaddress)

        self.sendMsg()
                     # just in case there are any pending tasks for msg
                     # messages that have yet to be sent.
        self.sendBroadcast()
                           # just in case there are any tasks for Broadcasts
                           # that have yet to be sent.

        while True:
            command, data = shared.workerQueue.get()
            if command == 'sendmessage':
                self.sendMsg()
            elif command == 'sendbroadcast':
                self.sendBroadcast()
            elif command == 'doPOWForMyV2Pubkey':
                self.doPOWForMyV2Pubkey(data)
            elif command == 'sendOutOrStoreMyV3Pubkey':
                self.sendOutOrStoreMyV3Pubkey(data)
            elif command == 'sendOutOrStoreMyV4Pubkey':
                self.sendOutOrStoreMyV4Pubkey(data)
            else:
                with shared.printLock:
                    sys.stderr.write(
                        'Probable programming error: The command sent to the workerThread is weird. It is: %s\n' % command)

            shared.workerQueue.task_done()

    def doPOWForMyV2Pubkey(self, hash):  # This function also broadcasts out the pubkey message once it is done with the POW
        # Look up my stream number based on my address hash
        """configSections = shared.config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile <> 'bitmessagesettings':
                status,addressVersionNumber,streamNumber,hashFromThisParticularAddress = decodeAddress(addressInKeysFile)
                if hash == hashFromThisParticularAddress:
                    myAddress = addressInKeysFile
                    break"""
        myAddress = shared.myAddressesByHash[hash]
        status, addressVersionNumber, streamNumber, hash = decodeAddress(
            myAddress)
        
        TTL = int(28 * 24 * 60 * 60 + random.randrange(-300, 300))# 28 days from now plus or minus five minutes
        embeddedTime = int(time.time() + TTL)
        payload = pack('>Q', (embeddedTime))
        payload += '\x00\x00\x00\x01' # object type: pubkey
        payload += encodeVarint(addressVersionNumber)  # Address version number
        payload += encodeVarint(streamNumber)
        payload += '\x00\x00\x00\x01'  # bitfield of features supported by me (see the wiki).

        try:
            privSigningKeyBase58 = shared.config.get(
                myAddress, 'privsigningkey')
            privEncryptionKeyBase58 = shared.config.get(
                myAddress, 'privencryptionkey')
        except Exception as err:
            with shared.printLock:
                sys.stderr.write(
                    'Error within doPOWForMyV2Pubkey. Could not read the keys from the keys.dat file for a requested address. %s\n' % err)
            return

        privSigningKeyHex = shared.decodeWalletImportFormat(
            privSigningKeyBase58).encode('hex')
        privEncryptionKeyHex = shared.decodeWalletImportFormat(
            privEncryptionKeyBase58).encode('hex')
        pubSigningKey = highlevelcrypto.privToPub(
            privSigningKeyHex).decode('hex')
        pubEncryptionKey = highlevelcrypto.privToPub(
            privEncryptionKeyHex).decode('hex')

        payload += pubSigningKey[1:]
        payload += pubEncryptionKey[1:]

        # Do the POW for this pubkey message
        target = 2 ** 64 / (shared.networkDefaultProofOfWorkNonceTrialsPerByte*(len(payload) + 8 + shared.networkDefaultPayloadLengthExtraBytes + ((TTL*(len(payload)+8+shared.networkDefaultPayloadLengthExtraBytes))/(2 ** 16))))
        print '(For pubkey message) Doing proof of work...'
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        print '(For pubkey message) Found proof of work', trialValue, 'Nonce:', nonce
        payload = pack('>Q', nonce) + payload

        inventoryHash = calculateInventoryHash(payload)
        objectType = 1
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime,'')
        shared.inventorySets[streamNumber].add(inventoryHash)

        with shared.printLock:
            print 'broadcasting inv with hash:', inventoryHash.encode('hex')

        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))
        shared.UISignalQueue.put(('updateStatusBar', ''))
        try:
            shared.config.set(
                myAddress, 'lastpubkeysendtime', str(int(time.time())))
            shared.writeKeysFile()
        except:
            # The user deleted the address out of the keys.dat file before this
            # finished.
            pass

    # If this isn't a chan address, this function assembles the pubkey data,
    # does the necessary POW and sends it out. If it *is* a chan then it
    # assembles the pubkey and stores is in the pubkey table so that we can
    # send messages to "ourselves".
    def sendOutOrStoreMyV3Pubkey(self, hash): 
        try:
            myAddress = shared.myAddressesByHash[hash]
        except:
            #The address has been deleted.
            return
        if shared.safeConfigGetBoolean(myAddress, 'chan'):
            with shared.printLock:
                print 'This is a chan address. Not sending pubkey.'
            return
        status, addressVersionNumber, streamNumber, hash = decodeAddress(
            myAddress)
        
        TTL = int(28 * 24 * 60 * 60 + random.randrange(-300, 300))# 28 days from now plus or minus five minutes
        embeddedTime = int(time.time() + TTL)
        signedTimeForProtocolV2 = embeddedTime - TTL
        """
        According to the protocol specification, the expiresTime along with the pubkey information is
        signed. But to be backwards compatible during the upgrade period, we shall sign not the 
        expiresTime but rather the current time. There must be precisely a 28 day difference
        between the two. After the upgrade period we'll switch to signing the whole payload with the
        expiresTime time.
        """
        payload = pack('>Q', (embeddedTime))
        payload += '\x00\x00\x00\x01' # object type: pubkey
        payload += encodeVarint(addressVersionNumber)  # Address version number
        payload += encodeVarint(streamNumber)
        payload += '\x00\x00\x00\x01'  # bitfield of features supported by me (see the wiki).

        try:
            privSigningKeyBase58 = shared.config.get(
                myAddress, 'privsigningkey')
            privEncryptionKeyBase58 = shared.config.get(
                myAddress, 'privencryptionkey')
        except Exception as err:
            with shared.printLock:
                sys.stderr.write(
                    'Error within sendOutOrStoreMyV3Pubkey. Could not read the keys from the keys.dat file for a requested address. %s\n' % err)

            return

        privSigningKeyHex = shared.decodeWalletImportFormat(
            privSigningKeyBase58).encode('hex')
        privEncryptionKeyHex = shared.decodeWalletImportFormat(
            privEncryptionKeyBase58).encode('hex')
        pubSigningKey = highlevelcrypto.privToPub(
            privSigningKeyHex).decode('hex')
        pubEncryptionKey = highlevelcrypto.privToPub(
            privEncryptionKeyHex).decode('hex')

        payload += pubSigningKey[1:]
        payload += pubEncryptionKey[1:]

        payload += encodeVarint(shared.config.getint(
            myAddress, 'noncetrialsperbyte'))
        payload += encodeVarint(shared.config.getint(
            myAddress, 'payloadlengthextrabytes'))
        
        signature = highlevelcrypto.sign(payload, privSigningKeyHex)
        payload += encodeVarint(len(signature))
        payload += signature

        # Do the POW for this pubkey message
        target = 2 ** 64 / (shared.networkDefaultProofOfWorkNonceTrialsPerByte*(len(payload) + 8 + shared.networkDefaultPayloadLengthExtraBytes + ((TTL*(len(payload)+8+shared.networkDefaultPayloadLengthExtraBytes))/(2 ** 16))))
        with shared.printLock:
            print '(For pubkey message) Doing proof of work...'
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        with shared.printLock:
            print '(For pubkey message) Found proof of work. Nonce:', nonce

        payload = pack('>Q', nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 1
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime,'')
        shared.inventorySets[streamNumber].add(inventoryHash)

        with shared.printLock:
            print 'broadcasting inv with hash:', inventoryHash.encode('hex')

        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))
        shared.UISignalQueue.put(('updateStatusBar', ''))
        try:
            shared.config.set(
                myAddress, 'lastpubkeysendtime', str(int(time.time())))
            shared.writeKeysFile()
        except:
            # The user deleted the address out of the keys.dat file before this
            # finished.
            pass

    # If this isn't a chan address, this function assembles the pubkey data,
    # does the necessary POW and sends it out. 
    def sendOutOrStoreMyV4Pubkey(self, myAddress):
        if not shared.config.has_section(myAddress):
            #The address has been deleted.
            return
        if shared.safeConfigGetBoolean(myAddress, 'chan'):
            with shared.printLock:
                print 'This is a chan address. Not sending pubkey.'
            return
        status, addressVersionNumber, streamNumber, hash = decodeAddress(
            myAddress)
        
        TTL = int(28 * 24 * 60 * 60 + random.randrange(-300, 300))# 28 days from now plus or minus five minutes
        embeddedTime = int(time.time() + TTL)
        payload = pack('>Q', (embeddedTime))
        payload += '\x00\x00\x00\x01' # object type: pubkey
        payload += encodeVarint(addressVersionNumber)  # Address version number
        payload += encodeVarint(streamNumber)

        dataToEncrypt = '\x00\x00\x00\x01'  # bitfield of features supported by me (see the wiki).

        try:
            privSigningKeyBase58 = shared.config.get(
                myAddress, 'privsigningkey')
            privEncryptionKeyBase58 = shared.config.get(
                myAddress, 'privencryptionkey')
        except Exception as err:
            with shared.printLock:
                sys.stderr.write(
                    'Error within sendOutOrStoreMyV4Pubkey. Could not read the keys from the keys.dat file for a requested address. %s\n' % err)
            return

        privSigningKeyHex = shared.decodeWalletImportFormat(
            privSigningKeyBase58).encode('hex')
        privEncryptionKeyHex = shared.decodeWalletImportFormat(
            privEncryptionKeyBase58).encode('hex')
        pubSigningKey = highlevelcrypto.privToPub(
            privSigningKeyHex).decode('hex')
        pubEncryptionKey = highlevelcrypto.privToPub(
            privEncryptionKeyHex).decode('hex')
        dataToEncrypt += pubSigningKey[1:]
        dataToEncrypt += pubEncryptionKey[1:]

        dataToEncrypt += encodeVarint(shared.config.getint(
            myAddress, 'noncetrialsperbyte'))
        dataToEncrypt += encodeVarint(shared.config.getint(
            myAddress, 'payloadlengthextrabytes'))
        
        # When we encrypt, we'll use a hash of the data
        # contained in an address as a decryption key. This way in order to
        # read the public keys in a pubkey message, a node must know the address
        # first. We'll also tag, unencrypted, the pubkey with part of the hash
        # so that nodes know which pubkey object to try to decrypt when they
        # want to send a message.
        doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
            addressVersionNumber) + encodeVarint(streamNumber) + hash).digest()).digest()
        payload += doubleHashOfAddressData[32:] # the tag
        signature = highlevelcrypto.sign(payload + dataToEncrypt, privSigningKeyHex)
        dataToEncrypt += encodeVarint(len(signature))
        dataToEncrypt += signature
        
        privEncryptionKey = doubleHashOfAddressData[:32]
        pubEncryptionKey = highlevelcrypto.pointMult(privEncryptionKey)
        payload += highlevelcrypto.encrypt(
            dataToEncrypt, pubEncryptionKey.encode('hex'))

        # Do the POW for this pubkey message
        target = 2 ** 64 / (shared.networkDefaultProofOfWorkNonceTrialsPerByte*(len(payload) + 8 + shared.networkDefaultPayloadLengthExtraBytes + ((TTL*(len(payload)+8+shared.networkDefaultPayloadLengthExtraBytes))/(2 ** 16))))
        print '(For pubkey message) Doing proof of work...'
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        print '(For pubkey message) Found proof of work', trialValue, 'Nonce:', nonce

        payload = pack('>Q', nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 1
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime, doubleHashOfAddressData[32:])
        shared.inventorySets[streamNumber].add(inventoryHash)

        with shared.printLock:
            print 'broadcasting inv with hash:', inventoryHash.encode('hex')

        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))
        shared.UISignalQueue.put(('updateStatusBar', ''))
        try:
            shared.config.set(
                myAddress, 'lastpubkeysendtime', str(int(time.time())))
            shared.writeKeysFile()
        except Exception as err:
            logger.error('Error: Couldn\'t add the lastpubkeysendtime to the keys.dat file. Error message: %s' % err)

    def sendBroadcast(self):
        queryreturn = sqlQuery(
            '''SELECT fromaddress, subject, message, ackdata, ttl FROM sent WHERE status=? and folder='sent' ''', 'broadcastqueued')
        for row in queryreturn:
            fromaddress, subject, body, ackdata, TTL = row
            status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                fromaddress)
            if addressVersionNumber <= 1:
                with shared.printLock:
                    sys.stderr.write(
                        'Error: In the singleWorker thread, the sendBroadcast function doesn\'t understand the address version.\n')
                return
            # We need to convert our private keys to public keys in order
            # to include them.
            try:
                privSigningKeyBase58 = shared.config.get(
                    fromaddress, 'privsigningkey')
                privEncryptionKeyBase58 = shared.config.get(
                    fromaddress, 'privencryptionkey')
            except:
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                    ackdata, tr.translateText("MainWindow", "Error! Could not find sender address (your address) in the keys.dat file."))))
                continue

            privSigningKeyHex = shared.decodeWalletImportFormat(
                privSigningKeyBase58).encode('hex')
            privEncryptionKeyHex = shared.decodeWalletImportFormat(
                privEncryptionKeyBase58).encode('hex')

            pubSigningKey = highlevelcrypto.privToPub(privSigningKeyHex).decode(
                'hex')  # At this time these pubkeys are 65 bytes long because they include the encoding byte which we won't be sending in the broadcast message.
            pubEncryptionKey = highlevelcrypto.privToPub(
                privEncryptionKeyHex).decode('hex')

            if TTL > 28 * 24 * 60 * 60:
                TTL = 28 * 24 * 60 * 60
            if TTL < 60*60:
                TTL = 60*60
            TTL = int(TTL + random.randrange(-300, 300))# add some randomness to the TTL
            embeddedTime = int(time.time() + TTL)
            payload = pack('>Q', embeddedTime)
            payload += '\x00\x00\x00\x03' # object type: broadcast

            if addressVersionNumber <= 3:
                payload += encodeVarint(4)  # broadcast version
            else:
                payload += encodeVarint(5)  # broadcast version
            
            payload += encodeVarint(streamNumber)
            if addressVersionNumber >= 4:
                doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                    addressVersionNumber) + encodeVarint(streamNumber) + ripe).digest()).digest()
                tag = doubleHashOfAddressData[32:]
                payload += tag
            else:
                tag = ''

            dataToEncrypt = encodeVarint(addressVersionNumber)
            dataToEncrypt += encodeVarint(streamNumber)
            dataToEncrypt += '\x00\x00\x00\x01'  # behavior bitfield
            dataToEncrypt += pubSigningKey[1:]
            dataToEncrypt += pubEncryptionKey[1:]
            if addressVersionNumber >= 3:
                dataToEncrypt += encodeVarint(shared.config.getint(fromaddress,'noncetrialsperbyte'))
                dataToEncrypt += encodeVarint(shared.config.getint(fromaddress,'payloadlengthextrabytes'))
            dataToEncrypt += '\x02' # message encoding type
            dataToEncrypt += encodeVarint(len('Subject:' + subject + '\n' + 'Body:' + body))  #Type 2 is simple UTF-8 message encoding per the documentation on the wiki.
            dataToEncrypt += 'Subject:' + subject + '\n' + 'Body:' + body
            dataToSign = payload + dataToEncrypt
            
            signature = highlevelcrypto.sign(
                dataToSign, privSigningKeyHex)
            dataToEncrypt += encodeVarint(len(signature))
            dataToEncrypt += signature

            # Encrypt the broadcast with the information contained in the broadcaster's address. 
            # Anyone who knows the address can generate the private encryption key to decrypt 
            # the broadcast. This provides virtually no privacy; its purpose is to keep 
            # questionable and illegal content from flowing through the Internet connections 
            # and being stored on the disk of 3rd parties. 
            if addressVersionNumber <= 3:
                privEncryptionKey = hashlib.sha512(encodeVarint(
                    addressVersionNumber) + encodeVarint(streamNumber) + ripe).digest()[:32]
            else:
                privEncryptionKey = doubleHashOfAddressData[:32]

            pubEncryptionKey = highlevelcrypto.pointMult(privEncryptionKey)
            payload += highlevelcrypto.encrypt(
                dataToEncrypt, pubEncryptionKey.encode('hex'))

            target = 2 ** 64 / (shared.networkDefaultProofOfWorkNonceTrialsPerByte*(len(payload) + 8 + shared.networkDefaultPayloadLengthExtraBytes + ((TTL*(len(payload)+8+shared.networkDefaultPayloadLengthExtraBytes))/(2 ** 16))))
            print '(For broadcast message) Doing proof of work...'
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                ackdata, tr.translateText("MainWindow", "Doing work necessary to send broadcast..."))))
            initialHash = hashlib.sha512(payload).digest()
            trialValue, nonce = proofofwork.run(target, initialHash)
            print '(For broadcast message) Found proof of work', trialValue, 'Nonce:', nonce

            payload = pack('>Q', nonce) + payload
            
            # Sanity check. The payload size should never be larger than 256 KiB. There should
            # be checks elsewhere in the code to not let the user try to send a message this large
            # until we implement message continuation. 
            if len(payload) > 2 ** 18: # 256 KiB
                logger.critical('This broadcast object is too large to send. This should never happen. Object size: %s' % len(payload))
                continue

            inventoryHash = calculateInventoryHash(payload)
            objectType = 3
            shared.inventory[inventoryHash] = (
                objectType, streamNumber, payload, embeddedTime, tag)
            shared.inventorySets[streamNumber].add(inventoryHash)
            with shared.printLock:
                print 'sending inv (within sendBroadcast function) for object:', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                streamNumber, 'advertiseobject', inventoryHash))

            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Broadcast sent on %1").arg(l10n.formatTimestamp()))))

            # Update the status of the message in the 'sent' table to have
            # a 'broadcastsent' status
            sqlExecute(
                'UPDATE sent SET msgid=?, status=?, lastactiontime=? WHERE ackdata=?',
                inventoryHash,
                'broadcastsent',
                int(time.time()),
                ackdata)
        

    def sendMsg(self):
        while True: # while we have a msg that needs some work
            
            # Select just one msg that needs work.
            queryreturn = sqlQuery(
                '''SELECT toaddress, fromaddress, subject, message, ackdata, status, ttl, retrynumber FROM sent WHERE (status='msgqueued' or status='doingmsgpow' or status='forcepow') and folder='sent' LIMIT 1''')
            if len(queryreturn) == 0: # if there is no work to do then 
                break                 # break out of this sendMsg loop and 
                                      # wait for something to get put in the shared.workerQueue.
            row = queryreturn[0]
            toaddress, fromaddress, subject, message, ackdata, status, TTL, retryNumber = row
            toStatus, toAddressVersionNumber, toStreamNumber, toRipe = decodeAddress(
                toaddress)
            fromStatus, fromAddressVersionNumber, fromStreamNumber, fromRipe = decodeAddress(
                fromaddress)
            
            # We may or may not already have the pubkey for this toAddress. Let's check.
            if status == 'forcepow':
                # if the status of this msg is 'forcepow' then clearly we have the pubkey already
                # because the user could not have overridden the message about the POW being
                # too difficult without knowing the required difficulty.
                pass
            elif status == 'doingmsgpow':
                # We wouldn't have set the status to doingmsgpow if we didn't already have the pubkey
                # so let's assume that we have it.
                pass
            # If we are sending a message to ourselves or a chan then we won't need an entry in the pubkeys table; we can calculate the needed pubkey using the private keys in our keys.dat file.
            elif shared.config.has_section(toaddress):
                sqlExecute(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toaddress=? AND status='msgqueued' ''',
                    toaddress)
                status='doingmsgpow'
            elif status == 'msgqueued':
                # Let's see if we already have the pubkey in our pubkeys table
                queryreturn = sqlQuery(
                    '''SELECT address FROM pubkeys WHERE address=?''', toaddress)
                if queryreturn != []:  # If we have the needed pubkey in the pubkey table already, 
                    # set the status of this msg to doingmsgpow
                    sqlExecute(
                        '''UPDATE sent SET status='doingmsgpow' WHERE toaddress=? AND status='msgqueued' ''',
                        toaddress)
                    status = 'doingmsgpow'
                    # mark the pubkey as 'usedpersonally' so that we don't delete it later. If the pubkey version
                    # is >= 4 then usedpersonally will already be set to yes because we'll only ever have 
                    # usedpersonally v4 pubkeys in the pubkeys table.
                    sqlExecute(
                        '''UPDATE pubkeys SET usedpersonally='yes' WHERE address=?''',
                        toaddress)
                else:  # We don't have the needed pubkey in the pubkeys table already.
                    if toAddressVersionNumber <= 3:
                        toTag = ''
                    else:
                        toTag = hashlib.sha512(hashlib.sha512(encodeVarint(toAddressVersionNumber)+encodeVarint(toStreamNumber)+toRipe).digest()).digest()[32:]
                    if toaddress in shared.neededPubkeys or toTag in shared.neededPubkeys:
                        # We already sent a request for the pubkey
                        sqlExecute(
                            '''UPDATE sent SET status='awaitingpubkey', sleeptill=? WHERE toaddress=? AND status='msgqueued' ''', 
                            int(time.time()) + 2.5*24*60*60,
                            toaddress)
                        shared.UISignalQueue.put(('updateSentItemStatusByToAddress', (
                            toaddress, tr.translateText("MainWindow",'Encryption key was requested earlier.'))))
                        continue #on with the next msg on which we can do some work
                    else:
                        # We have not yet sent a request for the pubkey
                        needToRequestPubkey = True
                        if toAddressVersionNumber >= 4: # If we are trying to send to address version >= 4 then 
                                                        # the needed pubkey might be encrypted in the inventory.
                                                        # If we have it we'll need to decrypt it and put it in 
                                                        # the pubkeys table.
                            
                            # The decryptAndCheckPubkeyPayload function expects that the shared.neededPubkeys
                            # dictionary already contains the toAddress and cryptor object associated with
                            # the tag for this toAddress.
                            doubleHashOfToAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                                toAddressVersionNumber) + encodeVarint(toStreamNumber) + toRipe).digest()).digest()
                            privEncryptionKey = doubleHashOfToAddressData[:32] # The first half of the sha512 hash.
                            tag = doubleHashOfToAddressData[32:] # The second half of the sha512 hash.
                            shared.neededPubkeys[tag] = (toaddress, highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex')))
                            
                            queryreturn = sqlQuery(
                                '''SELECT payload FROM inventory WHERE objecttype=1 and tag=? ''', toTag)
                            if queryreturn != []: # if there are any pubkeys in our inventory with the correct tag..
                                for row in queryreturn:
                                    payload, = row
                                    if shared.decryptAndCheckPubkeyPayload(payload, toaddress) == 'successful':
                                        needToRequestPubkey = False
                                        sqlExecute(
                                            '''UPDATE sent SET status='doingmsgpow', retrynumber=0 WHERE toaddress=? AND (status='msgqueued' or status='awaitingpubkey' or status='doingpubkeypow')''',
                                            toaddress)
                                        del shared.neededPubkeys[tag]
                                        break
                                    #else:  # There was something wrong with this pubkey object even
                                            # though it had the correct tag- almost certainly because
                                            # of malicious behavior or a badly programmed client. If
                                            # there are any other pubkeys in our inventory with the correct
                                            # tag then we'll try to decrypt those.

                            if needToRequestPubkey: # Obviously we had no success looking in the sql inventory. Let's look through the memory inventory.
                                with shared.inventoryLock:
                                    for hash, storedValue in shared.inventory.items():
                                        objectType, streamNumber, payload, expiresTime, tag = storedValue
                                        if objectType == 1 and tag == toTag:
                                            if shared.decryptAndCheckPubkeyPayload(payload, toaddress) == 'successful': #if valid, this function also puts it in the pubkeys table.
                                                needToRequestPubkey = False
                                                sqlExecute(
                                                    '''UPDATE sent SET status='doingmsgpow', retrynumber=0 WHERE toaddress=? AND (status='msgqueued' or status='awaitingpubkey' or status='doingpubkeypow')''',
                                                    toaddress)
                                                del shared.neededPubkeys[tag]
                                                break
                        if needToRequestPubkey:
                            sqlExecute(
                                '''UPDATE sent SET status='doingpubkeypow' WHERE toaddress=? AND status='msgqueued' ''',
                                toaddress)
                            shared.UISignalQueue.put(('updateSentItemStatusByToAddress', (
                                toaddress, tr.translateText("MainWindow",'Sending a request for the recipient\'s encryption key.'))))
                            self.requestPubKey(toaddress)
                            continue #on with the next msg on which we can do some work
            
            # At this point we know that we have the necessary pubkey in the pubkeys table.
            
            if retryNumber == 0:
                if TTL > 28 * 24 * 60 * 60:
                    TTL = 28 * 24 * 60 * 60
            else:
                TTL = 28 * 24 * 60 * 60 
            TTL = int(TTL + random.randrange(-300, 300))# add some randomness to the TTL
            embeddedTime = int(time.time() + TTL)
            
            if not shared.config.has_section(toaddress): # if we aren't sending this to ourselves or a chan
                shared.ackdataForWhichImWatching[ackdata] = 0
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                    ackdata, tr.translateText("MainWindow", "Looking up the receiver\'s public key"))))
                with shared.printLock:
                    print 'Sending a message. First 150 characters of message:', repr(message[:150])

                # Let us fetch the recipient's public key out of our database. If
                # the required proof of work difficulty is too hard then we'll
                # abort.
                queryreturn = sqlQuery(
                    'SELECT transmitdata FROM pubkeys WHERE address=?',
                    toaddress)
                for row in queryreturn:
                    pubkeyPayload, = row

                # The pubkey message is stored with the following items all appended:
                #    -address version
                #    -stream number
                #    -behavior bitfield
                #    -pub signing key
                #    -pub encryption key
                #    -nonce trials per byte (if address version is >= 3) 
                #    -length extra bytes (if address version is >= 3)

                readPosition = 1  # to bypass the address version whose length is definitely 1
                streamNumber, streamNumberLength = decodeVarint(
                    pubkeyPayload[readPosition:readPosition + 10])
                readPosition += streamNumberLength
                behaviorBitfield = pubkeyPayload[readPosition:readPosition + 4]
                # Mobile users may ask us to include their address's RIPE hash on a message
                # unencrypted. Before we actually do it the sending human must check a box
                # in the settings menu to allow it.
                if shared.isBitSetWithinBitfield(behaviorBitfield,30): # if receiver is a mobile device who expects that their address RIPE is included unencrypted on the front of the message..
                    if not shared.safeConfigGetBoolean('bitmessagesettings','willinglysendtomobile'): # if we are Not willing to include the receiver's RIPE hash on the message..
                        logger.info('The receiver is a mobile user but the sender (you) has not selected that you are willing to send to mobiles. Aborting send.')
                        shared.UISignalQueue.put(('updateSentItemStatusByAckdata',(ackdata,tr.translateText("MainWindow",'Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1').arg(l10n.formatTimestamp()))))
                        # if the human changes their setting and then sends another message or restarts their client, this one will send at that time.
                        continue
                readPosition += 4  # to bypass the bitfield of behaviors
                # pubSigningKeyBase256 = pubkeyPayload[readPosition:readPosition+64] # We don't use this key for anything here.
                readPosition += 64
                pubEncryptionKeyBase256 = pubkeyPayload[
                    readPosition:readPosition + 64]
                readPosition += 64

                # Let us fetch the amount of work required by the recipient.
                if toAddressVersionNumber == 2:
                    requiredAverageProofOfWorkNonceTrialsPerByte = shared.networkDefaultProofOfWorkNonceTrialsPerByte
                    requiredPayloadLengthExtraBytes = shared.networkDefaultPayloadLengthExtraBytes
                    shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                        ackdata, tr.translateText("MainWindow", "Doing work necessary to send message.\nThere is no required difficulty for version 2 addresses like this."))))
                elif toAddressVersionNumber >= 3:
                    requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = decodeVarint(
                        pubkeyPayload[readPosition:readPosition + 10])
                    readPosition += varintLength
                    requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                        pubkeyPayload[readPosition:readPosition + 10])
                    readPosition += varintLength
                    if requiredAverageProofOfWorkNonceTrialsPerByte < shared.networkDefaultProofOfWorkNonceTrialsPerByte:  # We still have to meet a minimum POW difficulty regardless of what they say is allowed in order to get our message to propagate through the network.
                        requiredAverageProofOfWorkNonceTrialsPerByte = shared.networkDefaultProofOfWorkNonceTrialsPerByte
                    if requiredPayloadLengthExtraBytes < shared.networkDefaultPayloadLengthExtraBytes:
                        requiredPayloadLengthExtraBytes = shared.networkDefaultPayloadLengthExtraBytes
                    logger.debug('Using averageProofOfWorkNonceTrialsPerByte: %s and payloadLengthExtraBytes: %s.' % (requiredAverageProofOfWorkNonceTrialsPerByte, requiredPayloadLengthExtraBytes))
                    shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Doing work necessary to send message.\nReceiver\'s required difficulty: %1 and %2").arg(str(float(
                        requiredAverageProofOfWorkNonceTrialsPerByte) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)).arg(str(float(requiredPayloadLengthExtraBytes) / shared.networkDefaultPayloadLengthExtraBytes)))))
                    if status != 'forcepow':
                        if (requiredAverageProofOfWorkNonceTrialsPerByte > shared.config.getint('bitmessagesettings', 'maxacceptablenoncetrialsperbyte') and shared.config.getint('bitmessagesettings', 'maxacceptablenoncetrialsperbyte') != 0) or (requiredPayloadLengthExtraBytes > shared.config.getint('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes') and shared.config.getint('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes') != 0):
                            # The demanded difficulty is more than we are willing
                            # to do.
                            sqlExecute(
                                '''UPDATE sent SET status='toodifficult' WHERE ackdata=? ''',
                                ackdata)
                            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do. %3").arg(str(float(requiredAverageProofOfWorkNonceTrialsPerByte) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)).arg(str(float(
                                requiredPayloadLengthExtraBytes) / shared.networkDefaultPayloadLengthExtraBytes)).arg(l10n.formatTimestamp()))))
                            continue
            else: # if we are sending a message to ourselves or a chan..
                with shared.printLock:
                    print 'Sending a message. First 150 characters of message:', repr(message[:150])
                behaviorBitfield = '\x00\x00\x00\x01'

                try:
                    privEncryptionKeyBase58 = shared.config.get(
                        toaddress, 'privencryptionkey')
                except Exception as err:
                    shared.UISignalQueue.put(('updateSentItemStatusByAckdata',(ackdata,tr.translateText("MainWindow",'Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1').arg(l10n.formatTimestamp()))))
                    with shared.printLock:
                        sys.stderr.write(
                            'Error within sendMsg. Could not read the keys from the keys.dat file for our own address. %s\n' % err)
                    continue
                privEncryptionKeyHex = shared.decodeWalletImportFormat(
                    privEncryptionKeyBase58).encode('hex')
                pubEncryptionKeyBase256 = highlevelcrypto.privToPub(
                    privEncryptionKeyHex).decode('hex')[1:]
                requiredAverageProofOfWorkNonceTrialsPerByte = shared.networkDefaultProofOfWorkNonceTrialsPerByte
                requiredPayloadLengthExtraBytes = shared.networkDefaultPayloadLengthExtraBytes
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                    ackdata, tr.translateText("MainWindow", "Doing work necessary to send message."))))

            # Now we can start to assemble our message.
            payload = encodeVarint(fromAddressVersionNumber)
            payload += encodeVarint(fromStreamNumber)
            payload += '\x00\x00\x00\x01'  # Bitfield of features and behaviors that can be expected from me. (See https://bitmessage.org/wiki/Protocol_specification#Pubkey_bitfield_features  )

            # We need to convert our private keys to public keys in order
            # to include them.
            try:
                privSigningKeyBase58 = shared.config.get(
                    fromaddress, 'privsigningkey')
                privEncryptionKeyBase58 = shared.config.get(
                    fromaddress, 'privencryptionkey')
            except:
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                    ackdata, tr.translateText("MainWindow", "Error! Could not find sender address (your address) in the keys.dat file."))))
                continue

            privSigningKeyHex = shared.decodeWalletImportFormat(
                privSigningKeyBase58).encode('hex')
            privEncryptionKeyHex = shared.decodeWalletImportFormat(
                privEncryptionKeyBase58).encode('hex')

            pubSigningKey = highlevelcrypto.privToPub(
                privSigningKeyHex).decode('hex')
            pubEncryptionKey = highlevelcrypto.privToPub(
                privEncryptionKeyHex).decode('hex')

            payload += pubSigningKey[
                1:]  # The \x04 on the beginning of the public keys are not sent. This way there is only one acceptable way to encode and send a public key.
            payload += pubEncryptionKey[1:]

            if fromAddressVersionNumber >= 3:
                # If the receiver of our message is in our address book,
                # subscriptions list, or whitelist then we will allow them to
                # do the network-minimum proof of work. Let us check to see if
                # the receiver is in any of those lists.
                if shared.isAddressInMyAddressBookSubscriptionsListOrWhitelist(toaddress):
                    payload += encodeVarint(
                        shared.networkDefaultProofOfWorkNonceTrialsPerByte)
                    payload += encodeVarint(
                        shared.networkDefaultPayloadLengthExtraBytes)
                else:
                    payload += encodeVarint(shared.config.getint(
                        fromaddress, 'noncetrialsperbyte'))
                    payload += encodeVarint(shared.config.getint(
                        fromaddress, 'payloadlengthextrabytes'))

            payload += toRipe  # This hash will be checked by the receiver of the message to verify that toRipe belongs to them. This prevents a Surreptitious Forwarding Attack.
            payload += '\x02'  # Type 2 is simple UTF-8 message encoding as specified on the Protocol Specification on the Bitmessage Wiki.
            messageToTransmit = 'Subject:' + \
                subject + '\n' + 'Body:' + message
            payload += encodeVarint(len(messageToTransmit))
            payload += messageToTransmit
            if shared.config.has_section(toaddress):
                with shared.printLock:
                    print 'Not bothering to include ackdata because we are sending to ourselves or a chan.'
                fullAckPayload = ''
            elif not shared.isBitSetWithinBitfield(behaviorBitfield,31):
                with shared.printLock:
                    print 'Not bothering to include ackdata because the receiver said that they won\'t relay it anyway.'
                fullAckPayload = ''                    
            else:
                fullAckPayload = self.generateFullAckMessage(
                    ackdata, toStreamNumber, TTL)  # The fullAckPayload is a normal msg protocol message with the proof of work already completed that the receiver of this message can easily send out.
            payload += encodeVarint(len(fullAckPayload))
            payload += fullAckPayload
            dataToSign = pack('>Q', embeddedTime) + '\x00\x00\x00\x02' + encodeVarint(1) + encodeVarint(toStreamNumber) + payload 
            signature = highlevelcrypto.sign(dataToSign, privSigningKeyHex)
            payload += encodeVarint(len(signature))
            payload += signature

            # We have assembled the data that will be encrypted.
            try:
                encrypted = highlevelcrypto.encrypt(payload,"04"+pubEncryptionKeyBase256.encode('hex'))
            except:
                sqlExecute('''UPDATE sent SET status='badkey' WHERE ackdata=?''', ackdata)
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata',(ackdata,tr.translateText("MainWindow",'Problem: The recipient\'s encryption key is no good. Could not encrypt message. %1').arg(l10n.formatTimestamp()))))
                continue
            
            encryptedPayload = pack('>Q', embeddedTime)
            encryptedPayload += '\x00\x00\x00\x02' # object type: msg
            encryptedPayload += encodeVarint(1) # msg version
            encryptedPayload += encodeVarint(toStreamNumber) + encrypted
            target = 2 ** 64 / (requiredAverageProofOfWorkNonceTrialsPerByte*(len(encryptedPayload) + 8 + requiredPayloadLengthExtraBytes + ((TTL*(len(encryptedPayload)+8+requiredPayloadLengthExtraBytes))/(2 ** 16))))
            with shared.printLock:
                print '(For msg message) Doing proof of work. Total required difficulty:', float(requiredAverageProofOfWorkNonceTrialsPerByte) / shared.networkDefaultProofOfWorkNonceTrialsPerByte, 'Required small message difficulty:', float(requiredPayloadLengthExtraBytes) / shared.networkDefaultPayloadLengthExtraBytes

            powStartTime = time.time()
            initialHash = hashlib.sha512(encryptedPayload).digest()
            trialValue, nonce = proofofwork.run(target, initialHash)
            with shared.printLock:
                print '(For msg message) Found proof of work', trialValue, 'Nonce:', nonce
                try:
                    print 'POW took', int(time.time() - powStartTime), 'seconds.', nonce / (time.time() - powStartTime), 'nonce trials per second.'
                except:
                    pass

            encryptedPayload = pack('>Q', nonce) + encryptedPayload
            
            # Sanity check. The encryptedPayload size should never be larger than 256 KiB. There should
            # be checks elsewhere in the code to not let the user try to send a message this large
            # until we implement message continuation. 
            if len(encryptedPayload) > 2 ** 18: # 256 KiB
                logger.critical('This msg object is too large to send. This should never happen. Object size: %s' % len(encryptedPayload))
                continue

            inventoryHash = calculateInventoryHash(encryptedPayload)
            objectType = 2
            shared.inventory[inventoryHash] = (
                objectType, toStreamNumber, encryptedPayload, embeddedTime, '')
            shared.inventorySets[toStreamNumber].add(inventoryHash)
            if shared.config.has_section(toaddress):
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Message sent. Sent on %1").arg(l10n.formatTimestamp()))))
            else:
                # not sending to a chan or one of my addresses
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Message sent. Waiting for acknowledgement. Sent on %1").arg(l10n.formatTimestamp()))))
            print 'Broadcasting inv for my msg(within sendmsg function):', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                toStreamNumber, 'advertiseobject', inventoryHash))

            # Update the sent message in the sent table with the necessary information.
            if shared.config.has_section(toaddress):
                newStatus = 'msgsentnoackexpected'
            else:
                newStatus = 'msgsent'
            if retryNumber == 0:
                sleepTill = int(time.time()) + TTL
            else:
                sleepTill = int(time.time()) + 28*24*60*60 * 2**retryNumber
            sqlExecute('''UPDATE sent SET msgid=?, status=?, retrynumber=?, sleeptill=?, lastactiontime=? WHERE ackdata=?''',
                       inventoryHash,
                       newStatus,
                       retryNumber+1,
                       sleepTill,
                       int(time.time()),
                       ackdata)

            # If we are sending to ourselves or a chan, let's put the message in
            # our own inbox.
            if shared.config.has_section(toaddress):
                sigHash = hashlib.sha512(hashlib.sha512(signature).digest()).digest()[32:] # Used to detect and ignore duplicate messages in our inbox
                t = (inventoryHash, toaddress, fromaddress, subject, int(
                    time.time()), message, 'inbox', 2, 0, sigHash)
                helper_inbox.insert(t)

                shared.UISignalQueue.put(('displayNewInboxMessage', (
                    inventoryHash, toaddress, fromaddress, subject, message)))

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

    def requestPubKey(self, toAddress):
        toStatus, addressVersionNumber, streamNumber, ripe = decodeAddress(
            toAddress)
        if toStatus != 'success':
            with shared.printLock:
                sys.stderr.write('Very abnormal error occurred in requestPubKey. toAddress is: ' + repr(
                    toAddress) + '. Please report this error to Atheros.')
            return
        
        queryReturn = sqlQuery(
            '''SELECT retrynumber FROM sent WHERE toaddress=? AND (status='doingpubkeypow' OR status='awaitingpubkey') LIMIT 1''', 
            toAddress)
        if len(queryReturn) == 0:
            logger.critical("BUG: Why are we requesting the pubkey for %s if there are no messages in the sent folder to that address?" % toAddress)
            return
        retryNumber = queryReturn[0][0]

        if addressVersionNumber <= 3:
            shared.neededPubkeys[toAddress] = 0
        elif addressVersionNumber >= 4:
            # If the user just clicked 'send' then the tag (and other information) will already
            # be in the neededPubkeys dictionary. But if we are recovering from a restart
            # of the client then we have to put it in now. 
            privEncryptionKey = hashlib.sha512(hashlib.sha512(encodeVarint(addressVersionNumber)+encodeVarint(streamNumber)+ripe).digest()).digest()[:32] # Note that this is the first half of the sha512 hash.
            tag = hashlib.sha512(hashlib.sha512(encodeVarint(addressVersionNumber)+encodeVarint(streamNumber)+ripe).digest()).digest()[32:] # Note that this is the second half of the sha512 hash.
            if tag not in shared.neededPubkeys:
                shared.neededPubkeys[tag] = (toAddress, highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex'))) # We'll need this for when we receive a pubkey reply: it will be encrypted and we'll need to decrypt it.
        
        if retryNumber == 0:
            TTL = 2.5*24*60*60 # 2.5 days. This was chosen fairly arbitrarily. 
        else:
            TTL = 28*24*60*60
        TTL = TTL + random.randrange(-300, 300) # add some randomness to the TTL
        embeddedTime = int(time.time() + TTL)
        payload = pack('>Q', embeddedTime)
        payload += '\x00\x00\x00\x00' # object type: getpubkey
        payload += encodeVarint(addressVersionNumber)
        payload += encodeVarint(streamNumber)
        if addressVersionNumber <= 3:
            payload += ripe
            with shared.printLock:
                print 'making request for pubkey with ripe:', ripe.encode('hex')
        else:
            payload += tag
            with shared.printLock:
                print 'making request for v4 pubkey with tag:', tag.encode('hex')

        # print 'trial value', trialValue
        statusbar = 'Doing the computations necessary to request the recipient\'s public key.'
        shared.UISignalQueue.put(('updateStatusBar', statusbar))
        shared.UISignalQueue.put(('updateSentItemStatusByToAddress', (
            toAddress, tr.translateText("MainWindow",'Doing work necessary to request encryption key.'))))
        
        target = 2 ** 64 / (shared.networkDefaultProofOfWorkNonceTrialsPerByte*(len(payload) + 8 + shared.networkDefaultPayloadLengthExtraBytes + ((TTL*(len(payload)+8+shared.networkDefaultPayloadLengthExtraBytes))/(2 ** 16))))
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        with shared.printLock:
            print 'Found proof of work', trialValue, 'Nonce:', nonce

        payload = pack('>Q', nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 1
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime, '')
        shared.inventorySets[streamNumber].add(inventoryHash)
        print 'sending inv (for the getpubkey message)'
        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))
        
        if retryNumber == 0:
            sleeptill = int(time.time()) + TTL
        else:
            sleeptill = int(time.time()) + 28*24*60*60 * 2**retryNumber
        sqlExecute(
            '''UPDATE sent SET lastactiontime=?, status='awaitingpubkey', retrynumber=?, sleeptill=? WHERE toaddress=? AND (status='doingpubkeypow' OR status='awaitingpubkey') ''',
            int(time.time()),
            retryNumber+1,
            sleeptill,
            toAddress)

        shared.UISignalQueue.put((
            'updateStatusBar', tr.translateText("MainWindow",'Broadcasting the public key request. This program will auto-retry if they are offline.')))
        shared.UISignalQueue.put(('updateSentItemStatusByToAddress', (toAddress, tr.translateText("MainWindow",'Sending public key request. Waiting for reply. Requested at %1').arg(l10n.formatTimestamp()))))

    def generateFullAckMessage(self, ackdata, toStreamNumber, TTL):
        
        # It might be perfectly fine to just use the same TTL for
        # the ackdata that we use for the message. But I would rather
        # it be more difficult for attackers to associate ackData with 
        # the associated msg object. However, users would want the TTL
        # of the acknowledgement to be about the same as they set
        # for the message itself. So let's set the TTL of the 
        # acknowledgement to be in one of three 'buckets': 1 hour, 7 
        # days, or 28 days, whichever is relatively close to what the 
        # user specified.
        if TTL < 24*60*60: # 1 day
            TTL = 24*60*60 # 1 day
        elif TTL < 7*24*60*60: # 1 week
            TTL = 7*24*60*60 # 1 week
        else:
            TTL = 28*24*60*60 # 4 weeks
        TTL = int(TTL + random.randrange(-300, 300)) # Add some randomness to the TTL
        embeddedTime = int(time.time() + TTL)
        payload = pack('>Q', (embeddedTime))
        payload += '\x00\x00\x00\x02' # object type: msg
        payload += encodeVarint(1) # msg version
        payload += encodeVarint(toStreamNumber) + ackdata
        
        target = 2 ** 64 / (shared.networkDefaultProofOfWorkNonceTrialsPerByte*(len(payload) + 8 + shared.networkDefaultPayloadLengthExtraBytes + ((TTL*(len(payload)+8+shared.networkDefaultPayloadLengthExtraBytes))/(2 ** 16))))
        with shared.printLock:
            print '(For ack message) Doing proof of work. TTL set to', TTL

        powStartTime = time.time()
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        with shared.printLock:
            print '(For ack message) Found proof of work', trialValue, 'Nonce:', nonce
            try:
                print 'POW took', int(time.time() - powStartTime), 'seconds.', nonce / (time.time() - powStartTime), 'nonce trials per second.'
            except:
                pass

        payload = pack('>Q', nonce) + payload
        return shared.CreatePacket('object', payload)
