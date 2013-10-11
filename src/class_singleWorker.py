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
from class_addressGenerator import pointMult
import tr
from debug import logger
from helper_sql import *
import helper_inbox

# This thread, of which there is only one, does the heavy lifting:
# calculating POWs.


class singleWorker(threading.Thread):

    def __init__(self):
        # QThread.__init__(self, parent)
        threading.Thread.__init__(self)

    def run(self):
        queryreturn = sqlQuery(
            '''SELECT toripe, toaddress FROM sent WHERE ((status='awaitingpubkey' OR status='doingpubkeypow') AND folder='sent')''')
        for row in queryreturn:
            toripe, toaddress = row
            toStatus, toAddressVersionNumber, toStreamNumber, toRipe = decodeAddress(toaddress)
            if toAddressVersionNumber <= 3 :
                shared.neededPubkeys[toripe] = 0
            elif toAddressVersionNumber >= 4:
                doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                    toAddressVersionNumber) + encodeVarint(toStreamNumber) + toRipe).digest()).digest()
                privEncryptionKey = doubleHashOfAddressData[:32] # Note that this is the first half of the sha512 hash.
                tag = doubleHashOfAddressData[32:]
                shared.neededPubkeys[tag] = highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex')) # We'll need this for when we receive a pubkey reply: it will be encrypted and we'll need to decrypt it.

        # Initialize the shared.ackdataForWhichImWatching data structure using data
        # from the sql database.
        queryreturn = sqlQuery(
            '''SELECT ackdata FROM sent where (status='msgsent' OR status='doingmsgpow')''')
        for row in queryreturn:
            ackdata, = row
            print 'Watching for ackdata', ackdata.encode('hex')
            shared.ackdataForWhichImWatching[ackdata] = 0

        queryreturn = sqlQuery(
            '''SELECT DISTINCT toaddress FROM sent WHERE (status='doingpubkeypow' AND folder='sent')''')
        for row in queryreturn:
            toaddress, = row
            self.requestPubKey(toaddress)

        time.sleep(
            10)  # give some time for the GUI to start before we start on existing POW tasks.

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
        embeddedTime = int(time.time() + random.randrange(
            -300, 300))  # the current time plus or minus five minutes
        payload = pack('>I', (embeddedTime))
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
        target = 2 ** 64 / ((len(payload) + shared.networkDefaultPayloadLengthExtraBytes +
                             8) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)
        print '(For pubkey message) Doing proof of work...'
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        print '(For pubkey message) Found proof of work', trialValue, 'Nonce:', nonce
        payload = pack('>Q', nonce) + payload

        inventoryHash = calculateInventoryHash(payload)
        objectType = 'pubkey'
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime,'')
        shared.inventorySets[streamNumber].add(inventoryHash)

        with shared.printLock:
            print 'broadcasting inv with hash:', inventoryHash.encode('hex')

        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))
        shared.UISignalQueue.put(('updateStatusBar', ''))
        shared.config.set(
            myAddress, 'lastpubkeysendtime', str(int(time.time())))
        with open(shared.appdata + 'keys.dat', 'wb') as configfile:
            shared.config.write(configfile)

    # If this isn't a chan address, this function assembles the pubkey data,
    # does the necessary POW and sends it out. If it *is* a chan then it
    # assembles the pubkey and stores is in the pubkey table so that we can
    # send messages to "ourselves".
    def sendOutOrStoreMyV3Pubkey(self, hash): 
        myAddress = shared.myAddressesByHash[hash]
        if shared.safeConfigGetBoolean(myAddress, 'chan'):
            with shared.printLock:
                print 'This is a chan address. Not sending pubkey.'
            return
        status, addressVersionNumber, streamNumber, hash = decodeAddress(
            myAddress)
        embeddedTime = int(time.time() + random.randrange(
            -300, 300))  # the current time plus or minus five minutes
        payload = pack('>I', (embeddedTime))
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
        target = 2 ** 64 / ((len(payload) + shared.networkDefaultPayloadLengthExtraBytes +
                             8) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)
        print '(For pubkey message) Doing proof of work...'
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        print '(For pubkey message) Found proof of work', trialValue, 'Nonce:', nonce

        payload = pack('>Q', nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 'pubkey'
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime,'')
        shared.inventorySets[streamNumber].add(inventoryHash)

        with shared.printLock:
            print 'broadcasting inv with hash:', inventoryHash.encode('hex')

        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))
        shared.UISignalQueue.put(('updateStatusBar', ''))
        shared.config.set(
            myAddress, 'lastpubkeysendtime', str(int(time.time())))
        with open(shared.appdata + 'keys.dat', 'wb') as configfile:
            shared.config.write(configfile)

    # If this isn't a chan address, this function assembles the pubkey data,
    # does the necessary POW and sends it out. 
    def sendOutOrStoreMyV4Pubkey(self, myAddress):
        if shared.safeConfigGetBoolean(myAddress, 'chan'):
            with shared.printLock:
                print 'This is a chan address. Not sending pubkey.'
            return
        status, addressVersionNumber, streamNumber, hash = decodeAddress(
            myAddress)
        embeddedTime = int(time.time() + random.randrange(
            -300, 300))  # the current time plus or minus five minutes
        payload = pack('>Q', (embeddedTime))
        payload += encodeVarint(addressVersionNumber)  # Address version number
        payload += encodeVarint(streamNumber)
        dataToStoreInOurPubkeysTable = payload # used if this is a chan. We'll add more data further down.

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

        dataToStoreInOurPubkeysTable += dataToEncrypt # dataToStoreInOurPubkeysTable is used if this is a chan

        signature = highlevelcrypto.sign(payload + dataToEncrypt, privSigningKeyHex)
        dataToEncrypt += encodeVarint(len(signature))
        dataToEncrypt += signature

        # Let us encrypt the necessary data. We will use a hash of the data
        # contained in an address as a decryption key. This way in order to
        # read the public keys in a pubkey message, a node must know the address
        # first. We'll also tag, unencrypted, the pubkey with part of the hash
        # so that nodes know which pubkey object to try to decrypt when they
        # want to send a message.
        doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
            addressVersionNumber) + encodeVarint(streamNumber) + hash).digest()).digest()
        payload += doubleHashOfAddressData[32:] # the tag
        privEncryptionKey = doubleHashOfAddressData[:32]
        pubEncryptionKey = pointMult(privEncryptionKey)
        payload += highlevelcrypto.encrypt(
            dataToEncrypt, pubEncryptionKey.encode('hex'))

        # Do the POW for this pubkey message
        target = 2 ** 64 / ((len(payload) + shared.networkDefaultPayloadLengthExtraBytes +
                             8) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)
        print '(For pubkey message) Doing proof of work...'
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        print '(For pubkey message) Found proof of work', trialValue, 'Nonce:', nonce

        payload = pack('>Q', nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 'pubkey'
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime, doubleHashOfAddressData[32:])
        shared.inventorySets[streamNumber].add(inventoryHash)

        with shared.printLock:
            print 'broadcasting inv with hash:', inventoryHash.encode('hex')

        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))
        shared.UISignalQueue.put(('updateStatusBar', ''))
        shared.config.set(
            myAddress, 'lastpubkeysendtime', str(int(time.time())))
        with open(shared.appdata + 'keys.dat', 'wb') as configfile:
            shared.config.write(configfile)

    def sendBroadcast(self):
        queryreturn = sqlQuery(
            '''SELECT fromaddress, subject, message, ackdata FROM sent WHERE status=? and folder='sent' ''', 'broadcastqueued')
        for row in queryreturn:
            fromaddress, subject, body, ackdata = row
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

            payload = pack('>Q', (int(time.time()) + random.randrange(
                -300, 300)))  # the current time plus or minus five minutes
            if addressVersionNumber <= 3:
                payload += encodeVarint(2)  # broadcast version
            else:
                payload += encodeVarint(3)  # broadcast version
            payload += encodeVarint(streamNumber)
            if addressVersionNumber >= 4:
                doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                    addressVersionNumber) + encodeVarint(streamNumber) + ripe).digest()).digest()
                payload += doubleHashOfAddressData[32:]  # the tag

            if addressVersionNumber <= 3:
                dataToEncrypt = encodeVarint(2)  # broadcast version
            else:
                dataToEncrypt = encodeVarint(3)  # broadcast version
            dataToEncrypt += encodeVarint(addressVersionNumber)
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
            signature = highlevelcrypto.sign(
                dataToEncrypt, privSigningKeyHex)
            dataToEncrypt += encodeVarint(len(signature))
            dataToEncrypt += signature

            # Encrypt the broadcast with the information contained in the broadcaster's address. Anyone who knows the address can generate 
            # the private encryption key to decrypt the broadcast. This provides virtually no privacy; its purpose is to keep questionable 
            # and illegal content from flowing through the Internet connections and being stored on the disk of 3rd parties. 
            if addressVersionNumber <= 3:
                privEncryptionKey = hashlib.sha512(encodeVarint(
                    addressVersionNumber) + encodeVarint(streamNumber) + ripe).digest()[:32]
            else:
                privEncryptionKey = doubleHashOfAddressData[:32]
            pubEncryptionKey = pointMult(privEncryptionKey)
            payload += highlevelcrypto.encrypt(
                dataToEncrypt, pubEncryptionKey.encode('hex'))

            target = 2 ** 64 / ((len(
                payload) + shared.networkDefaultPayloadLengthExtraBytes + 8) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)
            print '(For broadcast message) Doing proof of work...'
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                ackdata, tr.translateText("MainWindow", "Doing work necessary to send broadcast..."))))
            initialHash = hashlib.sha512(payload).digest()
            trialValue, nonce = proofofwork.run(target, initialHash)
            print '(For broadcast message) Found proof of work', trialValue, 'Nonce:', nonce

            payload = pack('>Q', nonce) + payload

            inventoryHash = calculateInventoryHash(payload)
            objectType = 'broadcast'
            shared.inventory[inventoryHash] = (
                objectType, streamNumber, payload, int(time.time()),'')
            shared.inventorySets[streamNumber].add(inventoryHash)
            with shared.printLock:
                print 'sending inv (within sendBroadcast function) for object:', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                streamNumber, 'advertiseobject', inventoryHash))

            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Broadcast sent on %1").arg(unicode(
                strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))

            # Update the status of the message in the 'sent' table to have
            # a 'broadcastsent' status
            sqlExecute(
                'UPDATE sent SET msgid=?, status=?, lastactiontime=? WHERE ackdata=?',
                inventoryHash,
                'broadcastsent',
                int(time.time()),
                ackdata)
        

    def sendMsg(self):
        # Check to see if there are any messages queued to be sent
        queryreturn = sqlQuery(
            '''SELECT DISTINCT toaddress FROM sent WHERE (status='msgqueued' AND folder='sent')''')
        for row in queryreturn:  # For each address to which we need to send a message, check to see if we have its pubkey already.
            toaddress, = row
            status, toAddressVersion, toStreamNumber, toRipe = decodeAddress(toaddress)
            # If we are sending a message to ourselves or a chan then we won't need an entry in the pubkeys table; we can calculate the needed pubkey using the private keys in our keys.dat file.
            if shared.config.has_section(toaddress):
                sqlExecute(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toaddress=? AND status='msgqueued' ''',
                    toaddress)
                continue
            queryreturn = sqlQuery(
                '''SELECT hash FROM pubkeys WHERE hash=? AND addressversion=?''', toRipe, toAddressVersion)
            if queryreturn != []:  # If we have the needed pubkey in the pubkey table already, set the status to doingmsgpow (we'll do it further down)
                sqlExecute(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toaddress=? AND status='msgqueued' ''',
                    toaddress)
            else:  # We don't have the needed pubkey in the pubkey table already.
                if toAddressVersion <= 3:
                    toTag = ''
                else:
                    toTag = hashlib.sha512(hashlib.sha512(encodeVarint(toAddressVersion)+encodeVarint(toStreamNumber)+toRipe).digest()).digest()[32:]
                if toRipe in shared.neededPubkeys or toTag in shared.neededPubkeys:
                    # We already sent a request for the pubkey
                    sqlExecute(
                        '''UPDATE sent SET status='awaitingpubkey' WHERE toaddress=? AND status='msgqueued' ''', toaddress)
                    shared.UISignalQueue.put(('updateSentItemStatusByHash', (
                        toRipe, tr.translateText("MainWindow",'Encryption key was requested earlier.'))))
                else:
                    # We have not yet sent a request for the pubkey
                    needToRequestPubkey = True
                    if toAddressVersion >= 4: # If we are trying to send to address version >= 4 then the needed pubkey might be encrypted in the inventory.
                        # If we have it we'll need to decrypt it and put it in the pubkeys table.
                        queryreturn = sqlQuery(
                            '''SELECT payload FROM inventory WHERE objecttype='pubkey' and tag=? ''', toTag)
                        if queryreturn != []: # if there was a pubkey in our inventory with the correct tag, we need to try to decrypt it.
                            for row in queryreturn:
                                data, = row
                                if shared.decryptAndCheckPubkeyPayload(data[8:], toaddress) == 'successful':
                                    needToRequestPubkey = False
                                    print 'debug. successfully decrypted and checked pubkey from sql inventory.' #testing
                                    sqlExecute(
                                        '''UPDATE sent SET status='doingmsgpow' WHERE toaddress=? AND status='msgqueued' ''',
                                        toaddress)
                                    break
                                else: # There was something wrong with this pubkey even though it had the correct tag- almost certainly because of malicious behavior or a badly programmed client.
                                    continue
                        if needToRequestPubkey: # Obviously we had no success looking in the sql inventory. Let's look through the memory inventory.
                            with shared.inventoryLock:
                                for hash, storedValue in shared.inventory.items():
                                    objectType, streamNumber, payload, receivedTime, tag = storedValue
                                    if objectType == 'pubkey' and tag == toTag:
                                        result = shared.decryptAndCheckPubkeyPayload(payload[8:], toaddress) #if valid, this function also puts it in the pubkeys table.
                                        if result == 'successful':
                                            print 'debug. successfully decrypted and checked pubkey from memory inventory.'
                                            needToRequestPubkey = False
                                            sqlExecute(
                                                '''UPDATE sent SET status='doingmsgpow' WHERE toaddress=? AND status='msgqueued' ''',
                                                toaddress)
                                            break
                    if needToRequestPubkey:
                        sqlExecute(
                            '''UPDATE sent SET status='doingpubkeypow' WHERE toaddress=? AND status='msgqueued' ''',
                            toaddress)
                        shared.UISignalQueue.put(('updateSentItemStatusByHash', (
                            toRipe, tr.translateText("MainWindow",'Sending a request for the recipient\'s encryption key.'))))
                        self.requestPubKey(toaddress)
        # Get all messages that are ready to be sent, and also all messages
        # which we have sent in the last 28 days which were previously marked
        # as 'toodifficult'. If the user as raised the maximum acceptable
        # difficulty then those messages may now be sendable.
        queryreturn = sqlQuery(
            '''SELECT toaddress, toripe, fromaddress, subject, message, ackdata, status FROM sent WHERE (status='doingmsgpow' or status='forcepow' or (status='toodifficult' and lastactiontime>?)) and folder='sent' ''',
            int(time.time()) - 2419200)
        for row in queryreturn:  # For each message we need to send..
            toaddress, toripe, fromaddress, subject, message, ackdata, status = row
            toStatus, toAddressVersionNumber, toStreamNumber, toHash = decodeAddress(
                toaddress)
            fromStatus, fromAddressVersionNumber, fromStreamNumber, fromHash = decodeAddress(
                fromaddress)

            if not shared.config.has_section(toaddress):
                # There is a remote possibility that we may no longer have the
                # recipient's pubkey. Let us make sure we still have it or else the
                # sendMsg function will appear to freeze. This can happen if the
                # user sends a message but doesn't let the POW function finish,
                # then leaves their client off for a long time which could cause
                # the needed pubkey to expire and be deleted.
                queryreturn = sqlQuery(
                    '''SELECT hash FROM pubkeys WHERE hash=? AND addressversion=?''',
                    toripe,
                    toAddressVersionNumber)
                if queryreturn == [] and toripe not in shared.neededPubkeys:
                    # We no longer have the needed pubkey and we haven't requested
                    # it.
                    with shared.printLock:
                        sys.stderr.write(
                            'For some reason, the status of a message in our outbox is \'doingmsgpow\' even though we lack the pubkey. Here is the RIPE hash of the needed pubkey: %s\n' % toripe.encode('hex'))
                    sqlExecute(
                        '''UPDATE sent SET status='doingpubkeypow' WHERE toaddress=? AND status='doingmsgpow' ''', toaddress)
                    shared.UISignalQueue.put(('updateSentItemStatusByHash', (
                        toripe, tr.translateText("MainWindow",'Sending a request for the recipient\'s encryption key.'))))
                    self.requestPubKey(toaddress)
                    continue
                shared.ackdataForWhichImWatching[ackdata] = 0
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                    ackdata, tr.translateText("MainWindow", "Looking up the receiver\'s public key"))))
                with shared.printLock:
                    print 'Sending a message. First 150 characters of message:', repr(message[:150])


                # mark the pubkey as 'usedpersonally' so that we don't ever delete
                # it.
                sqlExecute(
                    '''UPDATE pubkeys SET usedpersonally='yes' WHERE hash=? and addressversion=?''',
                    toripe,
                    toAddressVersionNumber)
                # Let us fetch the recipient's public key out of our database. If
                # the required proof of work difficulty is too hard then we'll
                # abort.
                queryreturn = sqlQuery(
                    'SELECT transmitdata FROM pubkeys WHERE hash=? and addressversion=?',
                    toripe,
                    toAddressVersionNumber)
                if queryreturn == []:
                    with shared.printLock:
                        sys.stderr.write(
                            '(within sendMsg) The needed pubkey was not found. This should never happen. Aborting send.\n')

                    return
                for row in queryreturn:
                    pubkeyPayload, = row

                # The pubkey message is stored the way we originally received it
                # which means that we need to read beyond things like the nonce and
                # time to get to the actual public keys.
                if toAddressVersionNumber <= 3:
                    readPosition = 8  # to bypass the nonce
                elif toAddressVersionNumber >= 4:
                    readPosition = 0 # the nonce is not included here so we don't need to skip over it.
                pubkeyEmbeddedTime, = unpack(
                    '>I', pubkeyPayload[readPosition:readPosition + 4])
                # This section is used for the transition from 32 bit time to 64
                # bit time in the protocol.
                if pubkeyEmbeddedTime == 0:
                    pubkeyEmbeddedTime, = unpack(
                        '>Q', pubkeyPayload[readPosition:readPosition + 8])
                    readPosition += 8
                else:
                    readPosition += 4
                readPosition += 1  # to bypass the address version whose length is definitely 1
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
                        shared.UISignalQueue.put(('updateSentItemStatusByAckdata',(ackdata,tr.translateText("MainWindow",'Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1').arg(unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))),'utf-8')))))
                        # if the human changes their setting and then sends another message or restarts their client, this one will send at that time.
                        continue
                readPosition += 4  # to bypass the bitfield of behaviors
                # pubSigningKeyBase256 =
                # pubkeyPayload[readPosition:readPosition+64] #We don't use this
                # key for anything here.
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
                    shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Doing work necessary to send message.\nReceiver\'s required difficulty: %1 and %2").arg(str(float(
                        requiredAverageProofOfWorkNonceTrialsPerByte) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)).arg(str(float(requiredPayloadLengthExtraBytes) / shared.networkDefaultPayloadLengthExtraBytes)))))
                    if status != 'forcepow':
                        if (requiredAverageProofOfWorkNonceTrialsPerByte > shared.config.getint('bitmessagesettings', 'maxacceptablenoncetrialsperbyte') and shared.config.getint('bitmessagesettings', 'maxacceptablenoncetrialsperbyte') != 0) or (requiredPayloadLengthExtraBytes > shared.config.getint('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes') and shared.config.getint('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes') != 0):
                            # The demanded difficulty is more than we are willing
                            # to do.
                            sqlExecute(
                                '''UPDATE sent SET status='toodifficult' WHERE ackdata=? ''',
                                ackdata)
                            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do.").arg(str(float(requiredAverageProofOfWorkNonceTrialsPerByte) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)).arg(str(float(
                                requiredPayloadLengthExtraBytes) / shared.networkDefaultPayloadLengthExtraBytes)).arg(unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))
                            continue
            else: # if we are sending a message to ourselves or a chan..
                with shared.printLock:
                    print 'Sending a message. First 150 characters of message:', repr(message[:150])
                behaviorBitfield = '\x00\x00\x00\x01'

                try:
                    privEncryptionKeyBase58 = shared.config.get(
                        toaddress, 'privencryptionkey')
                except Exception as err:
                    shared.UISignalQueue.put(('updateSentItemStatusByAckdata',(ackdata,tr.translateText("MainWindow",'Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1').arg(unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))),'utf-8')))))
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

            embeddedTime = pack('>Q', (int(time.time()) + random.randrange(
                -300, 300)))  # the current time plus or minus five minutes. We will use this time both for our message and for the ackdata packed within our message.
            if fromAddressVersionNumber == 2:
                payload = '\x01'  # Message version.
                payload += encodeVarint(fromAddressVersionNumber)
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

                payload += toHash  # This hash will be checked by the receiver of the message to verify that toHash belongs to them. This prevents a Surreptitious Forwarding Attack.
                payload += '\x02'  # Type 2 is simple UTF-8 message encoding as specified on the Protocol Specification on the Bitmessage Wiki.
                messageToTransmit = 'Subject:' + \
                    subject + '\n' + 'Body:' + message
                payload += encodeVarint(len(messageToTransmit))
                payload += messageToTransmit
                fullAckPayload = self.generateFullAckMessage(
                    ackdata, toStreamNumber, embeddedTime)  # The fullAckPayload is a normal msg protocol message with the proof of work already completed that the receiver of this message can easily send out.
                payload += encodeVarint(len(fullAckPayload))
                payload += fullAckPayload
                signature = highlevelcrypto.sign(payload, privSigningKeyHex)
                payload += encodeVarint(len(signature))
                payload += signature

            if fromAddressVersionNumber >= 3:
                payload = '\x01'  # Message version.
                payload += encodeVarint(fromAddressVersionNumber)
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

                payload += toHash  # This hash will be checked by the receiver of the message to verify that toHash belongs to them. This prevents a Surreptitious Forwarding Attack.
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
                        ackdata, toStreamNumber, embeddedTime)  # The fullAckPayload is a normal msg protocol message with the proof of work already completed that the receiver of this message can easily send out.
                payload += encodeVarint(len(fullAckPayload))
                payload += fullAckPayload
                signature = highlevelcrypto.sign(payload, privSigningKeyHex)
                payload += encodeVarint(len(signature))
                payload += signature

            print 'using pubEncryptionKey:', pubEncryptionKeyBase256.encode('hex')
            # We have assembled the data that will be encrypted.
            try:
                encrypted = highlevelcrypto.encrypt(payload,"04"+pubEncryptionKeyBase256.encode('hex'))
            except:
                sqlExecute('''UPDATE sent SET status='badkey' WHERE ackdata=?''', ackdata)
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata',(ackdata,tr.translateText("MainWindow",'Problem: The recipient\'s encryption key is no good. Could not encrypt message. %1').arg(unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))),'utf-8')))))
                continue
            encryptedPayload = embeddedTime + encodeVarint(toStreamNumber) + encrypted
            target = 2**64 / ((len(encryptedPayload)+requiredPayloadLengthExtraBytes+8) * requiredAverageProofOfWorkNonceTrialsPerByte)
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

            inventoryHash = calculateInventoryHash(encryptedPayload)
            objectType = 'msg'
            shared.inventory[inventoryHash] = (
                objectType, toStreamNumber, encryptedPayload, int(time.time()),'')
            shared.inventorySets[toStreamNumber].add(inventoryHash)
            if shared.config.has_section(toaddress):
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Message sent. Sent on %1").arg(unicode(
                    strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))
            else:
                # not sending to a chan or one of my addresses
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Message sent. Waiting on acknowledgement. Sent on %1").arg(unicode(
                    strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))
            print 'Broadcasting inv for my msg(within sendmsg function):', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                toStreamNumber, 'advertiseobject', inventoryHash))

            # Update the status of the message in the 'sent' table to have a
            # 'msgsent' status or 'msgsentnoackexpected' status.
            if shared.config.has_section(toaddress):
                newStatus = 'msgsentnoackexpected'
            else:
                newStatus = 'msgsent'
            sqlExecute('''UPDATE sent SET msgid=?, status=? WHERE ackdata=?''',
                       inventoryHash,newStatus,ackdata)

            # If we are sending to ourselves or a chan, let's put the message in
            # our own inbox.
            if shared.config.has_section(toaddress):
                t = (inventoryHash, toaddress, fromaddress, subject, int(
                    time.time()), message, 'inbox', 2, 0)
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
        if addressVersionNumber <= 3:
            shared.neededPubkeys[ripe] = 0
        elif addressVersionNumber >= 4:
            privEncryptionKey = hashlib.sha512(hashlib.sha512(encodeVarint(addressVersionNumber)+encodeVarint(streamNumber)+ripe).digest()).digest()[:32] # Note that this is the first half of the sha512 hash.
            tag = hashlib.sha512(hashlib.sha512(encodeVarint(addressVersionNumber)+encodeVarint(streamNumber)+ripe).digest()).digest()[32:] # Note that this is the second half of the sha512 hash.
            shared.neededPubkeys[tag] = highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex')) # We'll need this for when we receive a pubkey reply: it will be encrypted and we'll need to decrypt it.
        payload = pack('>Q', (int(time.time()) + random.randrange(
            -300, 300)))  # the current time plus or minus five minutes.
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
        shared.UISignalQueue.put(('updateSentItemStatusByHash', (
            ripe, tr.translateText("MainWindow",'Doing work necessary to request encryption key.'))))
        target = 2 ** 64 / ((len(payload) + shared.networkDefaultPayloadLengthExtraBytes +
                             8) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)
        initialHash = hashlib.sha512(payload).digest()
        trialValue, nonce = proofofwork.run(target, initialHash)
        with shared.printLock:
            print 'Found proof of work', trialValue, 'Nonce:', nonce


        payload = pack('>Q', nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 'getpubkey'
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, int(time.time()),'')
        shared.inventorySets[streamNumber].add(inventoryHash)
        print 'sending inv (for the getpubkey message)'
        shared.broadcastToSendDataQueues((
            streamNumber, 'advertiseobject', inventoryHash))

        sqlExecute(
            '''UPDATE sent SET status='awaitingpubkey' WHERE toaddress=? AND status='doingpubkeypow' ''',
            toAddress)

        shared.UISignalQueue.put((
            'updateStatusBar', tr.translateText("MainWindow",'Broacasting the public key request. This program will auto-retry if they are offline.')))
        shared.UISignalQueue.put(('updateSentItemStatusByHash', (ripe, tr.translateText("MainWindow",'Sending public key request. Waiting for reply. Requested at %1').arg(unicode(
            strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))

    def generateFullAckMessage(self, ackdata, toStreamNumber, embeddedTime):
        payload = embeddedTime + encodeVarint(toStreamNumber) + ackdata
        target = 2 ** 64 / ((len(payload) + shared.networkDefaultPayloadLengthExtraBytes +
                             8) * shared.networkDefaultProofOfWorkNonceTrialsPerByte)
        with shared.printLock:
            print '(For ack message) Doing proof of work...'

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
        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData += pack('>L', len(payload))
        headerData += hashlib.sha512(payload).digest()[:4]
        return headerData + payload
