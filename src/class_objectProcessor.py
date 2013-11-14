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

    def run(self):
        while True:
            data = shared.objectProcessorQueue.get()

            remoteCommand = data[4:16]
            if remoteCommand == 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                self.processmsg(data)

    def processmsg(self, data):
        """
        We know that the POW and time are correct as they were checked by the
        receiveDataThread.
        """
        readPosition = 8
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
                print 'Length of time program spent failing to decrypt this message:', time.time() - self.messageProcessingStartTime, 'seconds.'

        else:
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
                    if not self.isProofOfWorkSufficient(data, requiredNonceTrialsPerByte, requiredPayloadLengthExtraBytes):
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
                    ackdata = OpenSSL.rand(
                        32)  # We don't actually need the ackdata for acknowledgement since this is a broadcast message but we can use it to update the user interface when the POW is done generating.
                    toAddress = '[Broadcast subscribers]'
                    ripe = ''

                    t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                        time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
                    helper_sent.insert(t)

                    shared.UISignalQueue.put(('displayNewSentMessage', (
                        toAddress, '[Broadcast subscribers]', fromAddress, subject, message, ackdata)))
                    shared.workerQueue.put(('sendbroadcast', ''))

            if self.isAckDataValid(ackData):
                print 'ackData is valid. Will process it.'
                #self.ackDataThatWeHaveYetToSend.append(
                #    ackData)  # When we have processed all data, the processData function will pop the ackData out and process it as if it is a message received from our peer.
                shared.objectProcessorQueue.put(ackData)
            # Display timing data
            timeRequiredToAttemptToDecryptMessage = time.time(
            ) - self.messageProcessingStartTime
            shared.successfullyDecryptMessageTimings.append(
                timeRequiredToAttemptToDecryptMessage)
            sum = 0
            for item in shared.successfullyDecryptMessageTimings:
                sum += item
            with shared.printLock:
                print 'Time to decrypt this message successfully:', timeRequiredToAttemptToDecryptMessage
                print 'Average time for all message decryption successes since startup:', sum / len(shared.successfullyDecryptMessageTimings)

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

    def isAckDataValid(self, ackData):
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
        if ackData[4:16] != 'getpubkey\x00\x00\x00' and ackData[4:16] != 'pubkey\x00\x00\x00\x00\x00\x00' and ackData[4:16] != 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00' and ackData[4:16] != 'broadcast\x00\x00\x00':
            return False
        readPosition = 24 # bypass the network header
        if not shared.isProofOfWorkSufficient(ackData[readPosition:readPosition+10]):
            print 'Proof of work in msg message insufficient.'
            return

        readPosition += 8 # bypass the POW nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime > int(time.time()) + 10800:
            print 'The time in the msg message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time()) - shared.maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in the msg message is too old. Ignoring it. Time:', embeddedTime
            return
        streamNumberAsClaimedByMsg, streamNumberAsClaimedByMsgLength = decodeVarint(
            data[readPosition:readPosition + 9])
        if not streamNumberAsClaimedByMsg in shared.streamsInWhichIAmParticipating:
            print 'The stream number encoded in this msg (' + str(streamNumberAsClaimedByMsg) + ') message does not match a stream number on which it was received. Ignoring it.'
            return
        readPosition += streamNumberAsClaimedByMsgLength
        self.inventoryHash = calculateInventoryHash(data)
        shared.numberOfInventoryLookupsPerformed += 1
        shared.inventoryLock.acquire()
        if self.inventoryHash in shared.inventory:
            print 'We have already received this msg message. Ignoring.'
            shared.inventoryLock.release()
            return
        elif shared.isInSqlInventory(self.inventoryHash):
            print 'We have already received this msg message (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return
        ##################
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