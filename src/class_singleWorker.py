import threading
import shared
import time
from time import strftime, localtime, gmtime
import random
from addresses import *
import highlevelcrypto
import proofofwork
import sys
from class_addressGenerator import pointMult
import tr
from debug import logger

# This thread, of which there is only one, does the heavy lifting:
# calculating POWs.


class singleWorker(threading.Thread):

    def __init__(self):
        # QThread.__init__(self, parent)
        threading.Thread.__init__(self)

    def run(self):
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''SELECT toripe FROM sent WHERE ((status='awaitingpubkey' OR status='doingpubkeypow') AND folder='sent')''')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            toripe, = row
            shared.neededPubkeys[toripe] = 0

        # Initialize the shared.ackdataForWhichImWatching data structure using data
        # from the sql database.
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''SELECT ackdata FROM sent where (status='msgsent' OR status='doingmsgpow')''')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:
            ackdata, = row
            print 'Watching for ackdata', ackdata.encode('hex')
            shared.ackdataForWhichImWatching[ackdata] = 0

        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''SELECT DISTINCT toaddress FROM sent WHERE (status='doingpubkeypow' AND folder='sent')''')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
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
                """elif command == 'newpubkey':
                    toAddressVersion,toStreamNumber,toRipe = data
                    if toRipe in shared.neededPubkeys:
                        print 'We have been awaiting the arrival of this pubkey.'
                        del shared.neededPubkeys[toRipe]
                        t = (toRipe,)
                        shared.sqlLock.acquire()
                        shared.sqlSubmitQueue.put('''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND status='awaitingpubkey' and folder='sent' ''')
                        shared.sqlSubmitQueue.put(t)
                        shared.sqlReturnQueue.get()
                        shared.sqlSubmitQueue.put('commit')
                        shared.sqlLock.release()
                        self.sendMsg()
                    else:
                        with shared.printLock:
                            print 'We don\'t need this pub key. We didn\'t ask for it. Pubkey hash:', toRipe.encode('hex')
                        """
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
        """t = (hash,payload,embeddedTime,'no')
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?)''')
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()"""

        inventoryHash = calculateInventoryHash(payload)
        objectType = 'pubkey'
        shared.inventory[inventoryHash] = (
            objectType, streamNumber, payload, embeddedTime)

        with shared.printLock:
            print 'broadcasting inv with hash:', inventoryHash.encode('hex')

        shared.broadcastToSendDataQueues((
            streamNumber, 'sendinv', inventoryHash))
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

        if not shared.safeConfigGetBoolean(myAddress, 'chan'):
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
                objectType, streamNumber, payload, embeddedTime)

            with shared.printLock:
                print 'broadcasting inv with hash:', inventoryHash.encode('hex')

            shared.broadcastToSendDataQueues((
                streamNumber, 'sendinv', inventoryHash))
            shared.UISignalQueue.put(('updateStatusBar', ''))
        # If this is a chan address then we won't send out the pubkey over the
        # network but rather will only store it in our pubkeys table so that
        # we can send messages to "ourselves".
        if shared.safeConfigGetBoolean(myAddress, 'chan'):
            payload = '\x00' * 8 + payload # Attach a fake nonce on the front
                # just so that it is in the correct format.
            t = (hash,payload,embeddedTime,'yes')
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
        shared.config.set(
            myAddress, 'lastpubkeysendtime', str(int(time.time())))
        with open(shared.appdata + 'keys.dat', 'wb') as configfile:
            shared.config.write(configfile)

    def sendBroadcast(self):
        shared.sqlLock.acquire()
        t = ('broadcastqueued',)
        shared.sqlSubmitQueue.put(
            '''SELECT fromaddress, subject, message, ackdata FROM sent WHERE status=? and folder='sent' ''')
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
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
            payload += encodeVarint(2)  # broadcast version
            payload += encodeVarint(streamNumber)

            dataToEncrypt = encodeVarint(2)  # broadcast version
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
            privEncryptionKey = hashlib.sha512(encodeVarint(
                addressVersionNumber) + encodeVarint(streamNumber) + ripe).digest()[:32]
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
                objectType, streamNumber, payload, int(time.time()))
            with shared.printLock:
                print 'sending inv (within sendBroadcast function) for object:', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                streamNumber, 'sendinv', inventoryHash))

            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Broadcast sent on %1").arg(unicode(
                strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))

            # Update the status of the message in the 'sent' table to have
            # a 'broadcastsent' status
            shared.sqlLock.acquire()
            t = (inventoryHash,'broadcastsent', int(
                time.time()), ackdata)
            shared.sqlSubmitQueue.put(
                'UPDATE sent SET msgid=?, status=?, lastactiontime=? WHERE ackdata=?')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
        

    def sendMsg(self):
        # Check to see if there are any messages queued to be sent
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''SELECT DISTINCT toaddress FROM sent WHERE (status='msgqueued' AND folder='sent')''')
        shared.sqlSubmitQueue.put('')
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:  # For each address to which we need to send a message, check to see if we have its pubkey already.
            toaddress, = row
            toripe = decodeAddress(toaddress)[3]
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT hash FROM pubkeys WHERE hash=? ''')
            shared.sqlSubmitQueue.put((toripe,))
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:  # If we have the needed pubkey, set the status to doingmsgpow (we'll do it further down)
                t = (toaddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''UPDATE sent SET status='doingmsgpow' WHERE toaddress=? AND status='msgqueued' ''')
                shared.sqlSubmitQueue.put(t)
                shared.sqlReturnQueue.get()
                shared.sqlSubmitQueue.put('commit')
                shared.sqlLock.release()
            else:  # We don't have the needed pubkey. Set the status to 'awaitingpubkey' and request it if we haven't already
                if toripe in shared.neededPubkeys:
                    # We already sent a request for the pubkey
                    t = (toaddress,)
                    shared.sqlLock.acquire()
                    shared.sqlSubmitQueue.put(
                        '''UPDATE sent SET status='awaitingpubkey' WHERE toaddress=? AND status='msgqueued' ''')
                    shared.sqlSubmitQueue.put(t)
                    shared.sqlReturnQueue.get()
                    shared.sqlSubmitQueue.put('commit')
                    shared.sqlLock.release()
                    shared.UISignalQueue.put(('updateSentItemStatusByHash', (
                        toripe, tr.translateText("MainWindow",'Encryption key was requested earlier.'))))
                else:
                    # We have not yet sent a request for the pubkey
                    t = (toaddress,)
                    shared.sqlLock.acquire()
                    shared.sqlSubmitQueue.put(
                        '''UPDATE sent SET status='doingpubkeypow' WHERE toaddress=? AND status='msgqueued' ''')
                    shared.sqlSubmitQueue.put(t)
                    shared.sqlReturnQueue.get()
                    shared.sqlSubmitQueue.put('commit')
                    shared.sqlLock.release()
                    shared.UISignalQueue.put(('updateSentItemStatusByHash', (
                        toripe, tr.translateText("MainWindow",'Sending a request for the recipient\'s encryption key.'))))
                    self.requestPubKey(toaddress)
        shared.sqlLock.acquire()
        # Get all messages that are ready to be sent, and also all messages
        # which we have sent in the last 28 days which were previously marked
        # as 'toodifficult'. If the user as raised the maximum acceptable
        # difficulty then those messages may now be sendable.
        shared.sqlSubmitQueue.put(
            '''SELECT toaddress, toripe, fromaddress, subject, message, ackdata, status FROM sent WHERE (status='doingmsgpow' or status='forcepow' or (status='toodifficult' and lastactiontime>?)) and folder='sent' ''')
        shared.sqlSubmitQueue.put((int(time.time()) - 2419200,))
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        for row in queryreturn:  # For each message we need to send..
            toaddress, toripe, fromaddress, subject, message, ackdata, status = row
            # There is a remote possibility that we may no longer have the
            # recipient's pubkey. Let us make sure we still have it or else the
            # sendMsg function will appear to freeze. This can happen if the
            # user sends a message but doesn't let the POW function finish,
            # then leaves their client off for a long time which could cause
            # the needed pubkey to expire and be deleted.
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT hash FROM pubkeys WHERE hash=? ''')
            shared.sqlSubmitQueue.put((toripe,))
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn == [] and toripe not in shared.neededPubkeys:
                # We no longer have the needed pubkey and we haven't requested
                # it.
                with shared.printLock:
                    sys.stderr.write(
                        'For some reason, the status of a message in our outbox is \'doingmsgpow\' even though we lack the pubkey. Here is the RIPE hash of the needed pubkey: %s\n' % toripe.encode('hex'))

                t = (toaddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''UPDATE sent SET status='msgqueued' WHERE toaddress=? AND status='doingmsgpow' ''')
                shared.sqlSubmitQueue.put(t)
                shared.sqlReturnQueue.get()
                shared.sqlSubmitQueue.put('commit')
                shared.sqlLock.release()
                shared.UISignalQueue.put(('updateSentItemStatusByHash', (
                    toripe, tr.translateText("MainWindow",'Sending a request for the recipient\'s encryption key.'))))
                self.requestPubKey(toaddress)
                continue
            shared.ackdataForWhichImWatching[ackdata] = 0
            toStatus, toAddressVersionNumber, toStreamNumber, toHash = decodeAddress(
                toaddress)
            fromStatus, fromAddressVersionNumber, fromStreamNumber, fromHash = decodeAddress(
                fromaddress)
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (
                ackdata, tr.translateText("MainWindow", "Looking up the receiver\'s public key"))))
            with shared.printLock:
                print 'Found a message in our database that needs to be sent with this pubkey.'
                print 'First 150 characters of message:', repr(message[:150])


            # mark the pubkey as 'usedpersonally' so that we don't ever delete
            # it.
            shared.sqlLock.acquire()
            t = (toripe,)
            shared.sqlSubmitQueue.put(
                '''UPDATE pubkeys SET usedpersonally='yes' WHERE hash=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            # Let us fetch the recipient's public key out of our database. If
            # the required proof of work difficulty is too hard then we'll
            # abort.
            shared.sqlSubmitQueue.put(
                'SELECT transmitdata FROM pubkeys WHERE hash=?')
            shared.sqlSubmitQueue.put((toripe,))
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
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
            readPosition = 8  # to bypass the nonce
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
            elif toAddressVersionNumber == 3:
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
                        shared.sqlLock.acquire()
                        t = (ackdata,)
                        shared.sqlSubmitQueue.put(
                            '''UPDATE sent SET status='toodifficult' WHERE ackdata=? ''')
                        shared.sqlSubmitQueue.put(t)
                        shared.sqlReturnQueue.get()
                        shared.sqlSubmitQueue.put('commit')
                        shared.sqlLock.release()
                        shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do.").arg(str(float(requiredAverageProofOfWorkNonceTrialsPerByte) / shared.networkDefaultProofOfWorkNonceTrialsPerByte)).arg(str(float(
                            requiredPayloadLengthExtraBytes) / shared.networkDefaultPayloadLengthExtraBytes)).arg(unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))
                        continue


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

            if fromAddressVersionNumber == 3:
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
                if shared.safeConfigGetBoolean(toaddress, 'chan'):
                    with shared.printLock:
                        print 'Not bothering to generate ackdata because we are sending to a chan.'
                    fullAckPayload = ''
                elif not shared.isBitSetWithinBitfield(behaviorBitfield,31):
                    with shared.printLock:
                        print 'Not bothering to generate ackdata because the receiver said that they won\'t relay it anyway.'
                    fullAckPayload = ''                    
                else:
                    fullAckPayload = self.generateFullAckMessage(
                        ackdata, toStreamNumber, embeddedTime)  # The fullAckPayload is a normal msg protocol message with the proof of work already completed that the receiver of this message can easily send out.
                payload += encodeVarint(len(fullAckPayload))
                payload += fullAckPayload
                signature = highlevelcrypto.sign(payload, privSigningKeyHex)
                payload += encodeVarint(len(signature))
                payload += signature


            # We have assembled the data that will be encrypted.
            try:
                encrypted = highlevelcrypto.encrypt(payload,"04"+pubEncryptionKeyBase256.encode('hex'))
            except:
                shared.sqlLock.acquire()
                t = (ackdata,)
                shared.sqlSubmitQueue.put('''UPDATE sent SET status='badkey' WHERE ackdata=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlSubmitQueue.put('commit')
                shared.sqlLock.release()
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
                objectType, toStreamNumber, encryptedPayload, int(time.time()))
            if shared.safeConfigGetBoolean(toaddress, 'chan'):
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Message sent. Sent on %1").arg(unicode(
                    strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))
            else:
                # not sending to a chan
                shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (ackdata, tr.translateText("MainWindow", "Message sent. Waiting on acknowledgement. Sent on %1").arg(unicode(
                    strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))
            print 'Broadcasting inv for my msg(within sendmsg function):', inventoryHash.encode('hex')
            shared.broadcastToSendDataQueues((
                streamNumber, 'sendinv', inventoryHash))

            # Update the status of the message in the 'sent' table to have a
            # 'msgsent' status or 'msgsentnoackexpected' status.
            if shared.safeConfigGetBoolean(toaddress, 'chan'):
                newStatus = 'msgsentnoackexpected'
            else:
                newStatus = 'msgsent'
            shared.sqlLock.acquire()
            t = (inventoryHash,newStatus,ackdata,)
            shared.sqlSubmitQueue.put('''UPDATE sent SET msgid=?, status=? WHERE ackdata=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()

    def requestPubKey(self, toAddress):
        toStatus, addressVersionNumber, streamNumber, ripe = decodeAddress(
            toAddress)
        if toStatus != 'success':
            with shared.printLock:
                sys.stderr.write('Very abnormal error occurred in requestPubKey. toAddress is: ' + repr(
                    toAddress) + '. Please report this error to Atheros.')

            return
        shared.neededPubkeys[ripe] = 0
        payload = pack('>Q', (int(time.time()) + random.randrange(
            -300, 300)))  # the current time plus or minus five minutes.
        payload += encodeVarint(addressVersionNumber)
        payload += encodeVarint(streamNumber)
        payload += ripe
        with shared.printLock:
            print 'making request for pubkey with ripe:', ripe.encode('hex')

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
            objectType, streamNumber, payload, int(time.time()))
        print 'sending inv (for the getpubkey message)'
        shared.broadcastToSendDataQueues((
            streamNumber, 'sendinv', inventoryHash))

        t = (toAddress,)
        shared.sqlLock.acquire()
        shared.sqlSubmitQueue.put(
            '''UPDATE sent SET status='awaitingpubkey' WHERE toaddress=? AND status='doingpubkeypow' ''')
        shared.sqlSubmitQueue.put(t)
        shared.sqlReturnQueue.get()
        shared.sqlSubmitQueue.put('commit')
        shared.sqlLock.release()

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
