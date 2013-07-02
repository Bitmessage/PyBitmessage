doTimingAttackMitigation = True

import time
import threading
import shared
import hashlib
import socket
import pickle
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
import tr
#from bitmessagemain import shared.lengthOfTimeToLeaveObjectsInInventory, shared.lengthOfTimeToHoldOnToAllPubkeys, shared.maximumAgeOfAnObjectThatIAmWillingToAccept, shared.maximumAgeOfObjectsThatIAdvertiseToOthers, shared.maximumAgeOfNodesThatIAdvertiseToOthers, shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer, shared.neededPubkeys

# This thread is created either by the synSenderThread(for outgoing
# connections) or the singleListenerThread(for incoming connectiosn).

class receiveDataThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.data = ''
        self.verackSent = False
        self.verackReceived = False

    def setup(
        self,
        sock,
        HOST,
        port,
        streamNumber,
            someObjectsOfWhichThisRemoteNodeIsAlreadyAware,
            selfInitiatedConnections):
        self.sock = sock
        self.HOST = HOST
        self.PORT = port
        self.streamNumber = streamNumber
        self.payloadLength = 0  # This is the protocol payload length thus it doesn't include the 24 byte message header
        self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave = {}
        self.selfInitiatedConnections = selfInitiatedConnections
        shared.connectedHostsList[
            self.HOST] = 0  # The very fact that this receiveData thread exists shows that we are connected to the remote host. Let's add it to this list so that an outgoingSynSender thread doesn't try to connect to it.
        self.connectionIsOrWasFullyEstablished = False  # set to true after the remote node and I accept each other's version messages. This is needed to allow the user interface to accurately reflect the current number of connections.
        if self.streamNumber == -1:  # This was an incoming connection. Send out a version message if we accept the other node's version message.
            self.initiatedConnection = False
        else:
            self.initiatedConnection = True
            self.selfInitiatedConnections[streamNumber][self] = 0
        self.ackDataThatWeHaveYetToSend = [
        ]  # When we receive a message bound for us, we store the acknowledgement that we need to send (the ackdata) here until we are done processing all other data received from this peer.
        self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware = someObjectsOfWhichThisRemoteNodeIsAlreadyAware

    def run(self):
        shared.printLock.acquire()
        print 'ID of the receiveDataThread is', str(id(self)) + '. The size of the shared.connectedHostsList is now', len(shared.connectedHostsList)
        shared.printLock.release()
        while True:
            dataLen = len(self.data)
            try:
                self.data += self.sock.recv(4096)
            except socket.timeout:
                shared.printLock.acquire()
                print 'Timeout occurred waiting for data from', self.HOST + '. Closing receiveData thread. (ID:', str(id(self)) + ')'
                shared.printLock.release()
                break
            except Exception as err:
                shared.printLock.acquire()
                print 'sock.recv error. Closing receiveData thread (HOST:', self.HOST, 'ID:', str(id(self)) + ').', err
                shared.printLock.release()
                break
            # print 'Received', repr(self.data)
            if len(self.data) == dataLen:
                shared.printLock.acquire()
                print 'Connection to', self.HOST, 'closed. Closing receiveData thread. (ID:', str(id(self)) + ')'
                shared.printLock.release()
                break
            else:
                self.processData()

        try:
            del self.selfInitiatedConnections[self.streamNumber][self]
            shared.printLock.acquire()
            print 'removed self (a receiveDataThread) from selfInitiatedConnections'
            shared.printLock.release()
        except:
            pass
        shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
        try:
            del shared.connectedHostsList[self.HOST]
        except Exception as err:
            shared.printLock.acquire()
            print 'Could not delete', self.HOST, 'from shared.connectedHostsList.', err
            shared.printLock.release()
        try:
            del shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                self.HOST]
        except:
            pass
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        shared.printLock.acquire()
        print 'The size of the connectedHostsList is now:', len(shared.connectedHostsList)
        shared.printLock.release()

    def processData(self):
        # if shared.verbose >= 3:
            # shared.printLock.acquire()
            # print 'self.data is currently ', repr(self.data)
            # shared.printLock.release()
        if len(self.data) < 20:  # if so little of the data has arrived that we can't even unpack the payload length
            return
        if self.data[0:4] != '\xe9\xbe\xb4\xd9':
            if shared.verbose >= 1:
                shared.printLock.acquire()
                print 'The magic bytes were not correct. First 40 bytes of data: ' + repr(self.data[0:40])
                shared.printLock.release()
            self.data = ""
            return
        self.payloadLength, = unpack('>L', self.data[16:20])
        if len(self.data) < self.payloadLength + 24:  # check if the whole message has arrived yet.
            return
        if self.data[20:24] != hashlib.sha512(self.data[24:self.payloadLength + 24]).digest()[0:4]:  # test the checksum in the message. If it is correct...
            print 'Checksum incorrect. Clearing this message.'
            self.data = self.data[self.payloadLength + 24:]
            self.processData()
            return
        # The time we've last seen this node is obviously right now since we
        # just received valid data from it. So update the knownNodes list so
        # that other peers can be made aware of its existance.
        if self.initiatedConnection and self.connectionIsOrWasFullyEstablished:  # The remote port is only something we should share with others if it is the remote node's incoming port (rather than some random operating-system-assigned outgoing port).
            shared.knownNodesLock.acquire()
            shared.knownNodes[self.streamNumber][
                self.HOST] = (self.PORT, int(time.time()))
            shared.knownNodesLock.release()
        if self.payloadLength <= 180000000:  # If the size of the message is greater than 180MB, ignore it. (I get memory errors when processing messages much larger than this though it is concievable that this value will have to be lowered if some systems are less tolarant of large messages.)
            remoteCommand = self.data[4:16]
            shared.printLock.acquire()
            print 'remoteCommand', repr(remoteCommand.replace('\x00', '')), ' from', self.HOST
            shared.printLock.release()
            if remoteCommand == 'version\x00\x00\x00\x00\x00':
                self.recversion(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'verack\x00\x00\x00\x00\x00\x00':
                self.recverack()
            elif remoteCommand == 'addr\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recaddr(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'getpubkey\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recgetpubkey(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'pubkey\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recpubkey(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recinv(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'getdata\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recgetdata(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recmsg(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'broadcast\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recbroadcast(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'ping\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.sendpong()
            elif remoteCommand == 'pong\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                pass
            elif remoteCommand == 'alert\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                pass

        self.data = self.data[
            self.payloadLength + 24:]  # take this message out and then process the next message
        if self.data == '':
            while len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 0:
                random.seed()
                objectHash, = random.sample(
                    self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave, 1)
                if objectHash in shared.inventory:
                    shared.printLock.acquire()
                    print 'Inventory (in memory) already has object listed in inv message.'
                    shared.printLock.release()
                    del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        objectHash]
                elif shared.isInSqlInventory(objectHash):
                    if shared.verbose >= 3:
                        shared.printLock.acquire()
                        print 'Inventory (SQL on disk) already has object listed in inv message.'
                        shared.printLock.release()
                    del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        objectHash]
                else:
                    self.sendgetdata(objectHash)
                    del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        objectHash]  # It is possible that the remote node doesn't respond with the object. In that case, we'll very likely get it from someone else anyway.
                    if len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) == 0:
                        shared.printLock.acquire()
                        print '(concerning', self.HOST + ')', 'number of objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave is now', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)
                        shared.printLock.release()
                        try:
                            del shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                                self.HOST]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                        except:
                            pass
                    break
                if len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) == 0:
                    shared.printLock.acquire()
                    print '(concerning', self.HOST + ')', 'number of objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave is now', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)
                    shared.printLock.release()
                    try:
                        del shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                            self.HOST]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                    except:
                        pass
            if len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 0:
                shared.printLock.acquire()
                print '(concerning', self.HOST + ')', 'number of objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave is now', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)
                shared.printLock.release()
                shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[self.HOST] = len(
                    self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
            if len(self.ackDataThatWeHaveYetToSend) > 0:
                self.data = self.ackDataThatWeHaveYetToSend.pop()
        self.processData()

    def isProofOfWorkSufficient(
        self,
        data,
        nonceTrialsPerByte=0,
            payloadLengthExtraBytes=0):
        if nonceTrialsPerByte < shared.networkDefaultProofOfWorkNonceTrialsPerByte:
            nonceTrialsPerByte = shared.networkDefaultProofOfWorkNonceTrialsPerByte
        if payloadLengthExtraBytes < shared.networkDefaultPayloadLengthExtraBytes:
            payloadLengthExtraBytes = shared.networkDefaultPayloadLengthExtraBytes
        POW, = unpack('>Q', hashlib.sha512(hashlib.sha512(data[
                      :8] + hashlib.sha512(data[8:]).digest()).digest()).digest()[0:8])
        # print 'POW:', POW
        return POW <= 2 ** 64 / ((len(data) + payloadLengthExtraBytes) * (nonceTrialsPerByte))

    def sendpong(self):
        print 'Sending pong'
        try:
            self.sock.sendall(
                '\xE9\xBE\xB4\xD9\x70\x6F\x6E\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            print 'sock.sendall error:', err
            shared.printLock.release()

    def recverack(self):
        print 'verack received'
        self.verackReceived = True
        if self.verackSent:
            # We have thus both sent and received a verack.
            self.connectionFullyEstablished()

    def connectionFullyEstablished(self):
        self.connectionIsOrWasFullyEstablished = True
        if not self.initiatedConnection:
            shared.UISignalQueue.put(('setStatusIcon', 'green'))
        self.sock.settimeout(
            600)  # We'll send out a pong every 5 minutes to make sure the connection stays alive if there has been no other traffic to send lately.
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        remoteNodeIncomingPort, remoteNodeSeenTime = shared.knownNodes[
            self.streamNumber][self.HOST]
        shared.printLock.acquire()
        print 'Connection fully established with', self.HOST, remoteNodeIncomingPort
        print 'The size of the connectedHostsList is now', len(shared.connectedHostsList)
        print 'The length of sendDataQueues is now:', len(shared.sendDataQueues)
        print 'broadcasting addr from within connectionFullyEstablished function.'
        shared.printLock.release()
        self.broadcastaddr([(int(time.time()), self.streamNumber, 1, self.HOST,
                           remoteNodeIncomingPort)])  # This lets all of our peers know about this new node.
        self.sendaddr()  # This is one large addr message to this one peer.
        if not self.initiatedConnection and len(shared.connectedHostsList) > 200:
            shared.printLock.acquire()
            print 'We are connected to too many people. Closing connection.'
            shared.printLock.release()
            shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
            return
        self.sendBigInv()

    def sendBigInv(self):
        shared.sqlLock.acquire()
        # Select all hashes which are younger than two days old and in this
        # stream.
        t = (int(time.time()) - shared.maximumAgeOfObjectsThatIAdvertiseToOthers, int(
            time.time()) - shared.lengthOfTimeToHoldOnToAllPubkeys, self.streamNumber)
        shared.sqlSubmitQueue.put(
            '''SELECT hash FROM inventory WHERE ((receivedtime>? and objecttype<>'pubkey') or (receivedtime>? and objecttype='pubkey')) and streamnumber=?''')
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        bigInvList = {}
        for row in queryreturn:
            hash, = row
            if hash not in self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware:
                bigInvList[hash] = 0
        # We also have messages in our inventory in memory (which is a python
        # dictionary). Let's fetch those too.
        for hash, storedValue in shared.inventory.items():
            if hash not in self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware:
                objectType, streamNumber, payload, receivedTime = storedValue
                if streamNumber == self.streamNumber and receivedTime > int(time.time()) - shared.maximumAgeOfObjectsThatIAdvertiseToOthers:
                    bigInvList[hash] = 0
        numberOfObjectsInInvMessage = 0
        payload = ''
        # Now let us start appending all of these hashes together. They will be
        # sent out in a big inv message to our new peer.
        for hash, storedValue in bigInvList.items():
            payload += hash
            numberOfObjectsInInvMessage += 1
            if numberOfObjectsInInvMessage >= 50000:  # We can only send a max of 50000 items per inv message but we may have more objects to advertise. They must be split up into multiple inv messages.
                self.sendinvMessageToJustThisOnePeer(
                    numberOfObjectsInInvMessage, payload)
                payload = ''
                numberOfObjectsInInvMessage = 0
        if numberOfObjectsInInvMessage > 0:
            self.sendinvMessageToJustThisOnePeer(
                numberOfObjectsInInvMessage, payload)

    # Self explanatory. Notice that there is also a broadcastinv function for
    # broadcasting invs to everyone in our stream.
    def sendinvMessageToJustThisOnePeer(self, numberOfObjects, payload):
        payload = encodeVarint(numberOfObjects) + payload
        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData += pack('>L', len(payload))
        headerData += hashlib.sha512(payload).digest()[:4]
        shared.printLock.acquire()
        print 'Sending huge inv message with', numberOfObjects, 'objects to just this one peer'
        shared.printLock.release()
        try:
            self.sock.sendall(headerData + payload)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            print 'sock.sendall error:', err
            shared.printLock.release()

    # We have received a broadcast message
    def recbroadcast(self, data):
        self.messageProcessingStartTime = time.time()
        # First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in broadcast message insufficient.'
            return
        readPosition = 8  # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime > (int(time.time()) + 10800):  # prevent funny business
            print 'The embedded time in this broadcast message is more than three hours in the future. That doesn\'t make sense. Ignoring message.'
            return
        if embeddedTime < (int(time.time()) - shared.maximumAgeOfAnObjectThatIAmWillingToAccept):
            print 'The embedded time in this broadcast message is too old. Ignoring message.'
            return
        if len(data) < 180:
            print 'The payload length of this broadcast packet is unreasonably low. Someone is probably trying funny business. Ignoring message.'
            return
        # Let us check to make sure the stream number is correct (thus
        # preventing an individual from sending broadcasts out on the wrong
        # streams or all streams).
        broadcastVersion, broadcastVersionLength = decodeVarint(
            data[readPosition:readPosition + 10])
        if broadcastVersion >= 2:
            streamNumber, streamNumberLength = decodeVarint(data[
                                                            readPosition + broadcastVersionLength:readPosition + broadcastVersionLength + 10])
            if streamNumber != self.streamNumber:
                print 'The stream number encoded in this broadcast message (' + str(streamNumber) + ') does not match the stream number on which it was received. Ignoring it.'
                return

        shared.inventoryLock.acquire()
        self.inventoryHash = calculateInventoryHash(data)
        if self.inventoryHash in shared.inventory:
            print 'We have already received this broadcast object. Ignoring.'
            shared.inventoryLock.release()
            return
        elif shared.isInSqlInventory(self.inventoryHash):
            print 'We have already received this broadcast object (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return
        # It is valid so far. Let's let our peers know about it.
        objectType = 'broadcast'
        shared.inventory[self.inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        self.broadcastinv(self.inventoryHash)
        shared.UISignalQueue.put((
            'incrementNumberOfBroadcastsProcessed', 'no data'))

        self.processbroadcast(
            readPosition, data)  # When this function returns, we will have either successfully processed this broadcast because we are interested in it, ignored it because we aren't interested in it, or found problem with the broadcast that warranted ignoring it.

        # Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. If we
        # haven't used the specified amount of time, we shall sleep. These
        # values are mostly the same values used for msg messages although
        # broadcast messages are processed faster.
        if len(data) > 100000000:  # Size is greater than 100 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 100  # seconds.
        elif len(data) > 10000000:  # Between 100 and 10 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 20  # seconds.
        elif len(data) > 1000000:  # Between 10 and 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = 3  # seconds.
        else:  # Less than 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = .6  # seconds.

        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - \
            (time.time() - self.messageProcessingStartTime)
        if sleepTime > 0 and doTimingAttackMitigation:
            shared.printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            shared.printLock.release()
            time.sleep(sleepTime)
        shared.printLock.acquire()
        print 'Total message processing time:', time.time() - self.messageProcessingStartTime, 'seconds.'
        shared.printLock.release()

    # A broadcast message has a valid time and POW and requires processing.
    # The recbroadcast function calls this one.
    def processbroadcast(self, readPosition, data):
        broadcastVersion, broadcastVersionLength = decodeVarint(
            data[readPosition:readPosition + 9])
        readPosition += broadcastVersionLength
        if broadcastVersion < 1 or broadcastVersion > 2:
            print 'Cannot decode incoming broadcast versions higher than 2. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.'
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
                    shared.printLock.acquire()
                    print 'Time spent deciding that we are not interested in this v1 broadcast:', time.time() - self.messageProcessingStartTime
                    shared.printLock.release()
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

                # Let's store the public key in case we want to reply to this person.
                # We don't have the correct nonce or time (which would let us
                # send out a pubkey message) so we'll just fill it with 1's. We
                # won't be able to send this pubkey to others (without doing
                # the proof of work ourselves, which this program is programmed
                # to not do.)
                t = (ripe.digest(), '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + data[
                     beginningOfPubkeyPosition:endOfPubkeyPosition], int(time.time()), 'yes')
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
                shared.sqlSubmitQueue.put(t)
                shared.sqlReturnQueue.get()
                shared.sqlSubmitQueue.put('commit')
                shared.sqlLock.release()
                # shared.workerQueue.put(('newpubkey',(sendersAddressVersion,sendersStream,ripe.digest())))
                # This will check to see whether we happen to be awaiting this
                # pubkey in order to send a message. If we are, it will do the
                # POW and send it.
                self.possibleNewPubkey(ripe.digest())

                fromAddress = encodeAddress(
                    sendersAddressVersion, sendersStream, ripe.digest())
                shared.printLock.acquire()
                print 'fromAddress:', fromAddress
                shared.printLock.release()
                if messageEncodingType == 2:
                    bodyPositionIndex = string.find(message, '\nBody:')
                    if bodyPositionIndex > 1:
                        subject = message[8:bodyPositionIndex]
                        body = message[bodyPositionIndex + 6:]
                    else:
                        subject = ''
                        body = message
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
                    
                    t = (self.inventoryHash, toAddress, fromAddress, subject, int(
                        time.time()), body, 'inbox', messageEncodingType, 0)
                    helper_inbox.insert(t)
                    
                    shared.UISignalQueue.put(('displayNewInboxMessage', (
                        self.inventoryHash, toAddress, fromAddress, subject, body)))

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
                shared.printLock.acquire()
                print 'Time spent processing this interesting broadcast:', time.time() - self.messageProcessingStartTime
                shared.printLock.release()
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
                shared.printLock.acquire()
                print 'Length of time program spent failing to decrypt this v2 broadcast:', time.time() - self.messageProcessingStartTime, 'seconds.'
                shared.printLock.release()
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
            t = (ripe.digest(), '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + decryptedData[
                 beginningOfPubkeyPosition:endOfPubkeyPosition], int(time.time()), 'yes')
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(sendersAddressVersion,sendersStream,ripe.digest())))
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(ripe.digest())

            fromAddress = encodeAddress(
                sendersAddressVersion, sendersStream, ripe.digest())
            shared.printLock.acquire()
            print 'fromAddress:', fromAddress
            shared.printLock.release()
            if messageEncodingType == 2:
                bodyPositionIndex = string.find(message, '\nBody:')
                if bodyPositionIndex > 1:
                    subject = message[8:bodyPositionIndex]
                    body = message[bodyPositionIndex + 6:]
                else:
                    subject = ''
                    body = message
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
                
                t = (self.inventoryHash, toAddress, fromAddress, subject, int(
                    time.time()), body, 'inbox', messageEncodingType, 0)
                helper_inbox.insert(t)
                
                shared.UISignalQueue.put(('displayNewInboxMessage', (
                    self.inventoryHash, toAddress, fromAddress, subject, body)))

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
            shared.printLock.acquire()
            print 'Time spent processing this interesting broadcast:', time.time() - self.messageProcessingStartTime
            shared.printLock.release()

    # We have received a msg message.
    def recmsg(self, data):
        self.messageProcessingStartTime = time.time()
        # First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in msg message insufficient.'
            return

        readPosition = 8
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
        if streamNumberAsClaimedByMsg != self.streamNumber:
            print 'The stream number encoded in this msg (' + str(streamNumberAsClaimedByMsg) + ') message does not match the stream number on which it was received. Ignoring it.'
            return
        readPosition += streamNumberAsClaimedByMsgLength
        self.inventoryHash = calculateInventoryHash(data)
        shared.inventoryLock.acquire()
        if self.inventoryHash in shared.inventory:
            print 'We have already received this msg message. Ignoring.'
            shared.inventoryLock.release()
            return
        elif shared.isInSqlInventory(self.inventoryHash):
            print 'We have already received this msg message (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return
        # This msg message is valid. Let's let our peers know about it.
        objectType = 'msg'
        shared.inventory[self.inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        self.broadcastinv(self.inventoryHash)
        shared.UISignalQueue.put((
            'incrementNumberOfMessagesProcessed', 'no data'))

        self.processmsg(
            readPosition, data)  # When this function returns, we will have either successfully processed the message bound for us, ignored it because it isn't bound for us, or found problem with the message that warranted ignoring it.

        # Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. If we
        # haven't used the specified amount of time, we shall sleep. These
        # values are based on test timings and you may change them at-will.
        if len(data) > 100000000:  # Size is greater than 100 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 100  # seconds. Actual length of time it took my computer to decrypt and verify the signature of a 100 MB message: 3.7 seconds.
        elif len(data) > 10000000:  # Between 100 and 10 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 20  # seconds. Actual length of time it took my computer to decrypt and verify the signature of a 10 MB message: 0.53 seconds. Actual length of time it takes in practice when processing a real message: 1.44 seconds.
        elif len(data) > 1000000:  # Between 10 and 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = 3  # seconds. Actual length of time it took my computer to decrypt and verify the signature of a 1 MB message: 0.18 seconds. Actual length of time it takes in practice when processing a real message: 0.30 seconds.
        else:  # Less than 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = .6  # seconds. Actual length of time it took my computer to decrypt and verify the signature of a 100 KB message: 0.15 seconds. Actual length of time it takes in practice when processing a real message: 0.25 seconds.

        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - \
            (time.time() - self.messageProcessingStartTime)
        if sleepTime > 0 and doTimingAttackMitigation:
            shared.printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            shared.printLock.release()
            time.sleep(sleepTime)
        shared.printLock.acquire()
        print 'Total message processing time:', time.time() - self.messageProcessingStartTime, 'seconds.'
        shared.printLock.release()

    # A msg message has a valid time and POW and requires processing. The
    # recmsg function calls this one.
    def processmsg(self, readPosition, encryptedData):
        initialDecryptionSuccessful = False
        # Let's check whether this is a message acknowledgement bound for us.
        if encryptedData[readPosition:] in shared.ackdataForWhichImWatching:
            shared.printLock.acquire()
            print 'This msg IS an acknowledgement bound for me.'
            shared.printLock.release()
            del shared.ackdataForWhichImWatching[encryptedData[readPosition:]]
            t = ('ackreceived', encryptedData[readPosition:])
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                'UPDATE sent SET status=? WHERE ackdata=?')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (encryptedData[readPosition:], tr.translateText("MainWindow",'Acknowledgement of the message received. %1').arg(unicode(
                time.strftime(shared.config.get('bitmessagesettings', 'timeformat'), time.localtime(int(time.time()))), 'utf-8')))))
            return
        else:
            shared.printLock.acquire()
            print 'This was NOT an acknowledgement bound for me.'
            # print 'shared.ackdataForWhichImWatching', shared.ackdataForWhichImWatching
            shared.printLock.release()

        # This is not an acknowledgement bound for me. See if it is a message
        # bound for me by trying to decrypt it with my private keys.
        for key, cryptorObject in shared.myECCryptorObjects.items():
            try:
                decryptedData = cryptorObject.decrypt(
                    encryptedData[readPosition:])
                toRipe = key  # This is the RIPE hash of my pubkeys. We need this below to compare to the destination_ripe included in the encrypted data.
                initialDecryptionSuccessful = True
                print 'EC decryption successful using key associated with ripe hash:', key.encode('hex')
                break
            except Exception as err:
                pass
                # print 'cryptorObject.decrypt Exception:', err
        if not initialDecryptionSuccessful:
            # This is not a message bound for me.
            shared.printLock.acquire()
            print 'Length of time program spent failing to decrypt this message:', time.time() - self.messageProcessingStartTime, 'seconds.'
            shared.printLock.release()
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
            if sendersAddressVersionNumber >= 4:
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
                shared.printLock.acquire()
                print 'The original sender of this message did not send it to you. Someone is attempting a Surreptitious Forwarding Attack.'
                print 'See: http://world.std.com/~dtd/sign_encrypt/sign_encrypt7.html'
                print 'your toRipe:', toRipe.encode('hex')
                print 'embedded destination toRipe:', decryptedData[readPosition:readPosition + 20].encode('hex')
                shared.printLock.release()
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
            shared.printLock.acquire()
            print 'As a matter of intellectual curiosity, here is the Bitcoin address associated with the keys owned by the other person:', helper_bitcoin.calculateBitcoinAddressFromPubkey(pubSigningKey), '  ..and here is the testnet address:', helper_bitcoin.calculateTestnetAddressFromPubkey(pubSigningKey), '. The other person must take their private signing key from Bitmessage and import it into Bitcoin (or a service like Blockchain.info) for it to be of any use. Do not use this unless you know what you are doing.'
            shared.printLock.release()
            # calculate the fromRipe.
            sha = hashlib.new('sha512')
            sha.update(pubSigningKey + pubEncryptionKey)
            ripe = hashlib.new('ripemd160')
            ripe.update(sha.digest())
            # Let's store the public key in case we want to reply to this
            # person.
            t = (ripe.digest(), '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + decryptedData[
                 messageVersionLength:endOfThePublicKeyPosition], int(time.time()), 'yes')
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(sendersAddressVersionNumber,sendersStreamNumber,ripe.digest())))
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(ripe.digest())
            fromAddress = encodeAddress(
                sendersAddressVersionNumber, sendersStreamNumber, ripe.digest())
            # If this message is bound for one of my version 3 addresses (or
            # higher), then we must check to make sure it meets our demanded
            # proof of work requirement.
            if decodeAddress(toAddress)[1] >= 3:  # If the toAddress version number is 3 or higher:
                if not shared.isAddressInMyAddressBookSubscriptionsListOrWhitelist(fromAddress):  # If I'm not friendly with this person:
                    requiredNonceTrialsPerByte = shared.config.getint(
                        toAddress, 'noncetrialsperbyte')
                    requiredPayloadLengthExtraBytes = shared.config.getint(
                        toAddress, 'payloadlengthextrabytes')
                    if not self.isProofOfWorkSufficient(encryptedData, requiredNonceTrialsPerByte, requiredPayloadLengthExtraBytes):
                        print 'Proof of work in msg message insufficient only because it does not meet our higher requirement.'
                        return
            blockMessage = False  # Gets set to True if the user shouldn't see the message according to black or white lists.
            if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':  # If we are using a blacklist
                t = (fromAddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''SELECT label FROM blacklist where address=? and enabled='1' ''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn != []:
                    shared.printLock.acquire()
                    print 'Message ignored because address is in blacklist.'
                    shared.printLock.release()
                    blockMessage = True
            else:  # We're using a whitelist
                t = (fromAddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''SELECT label FROM whitelist where address=? and enabled='1' ''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn == []:
                    print 'Message ignored because address not in whitelist.'
                    blockMessage = True
            if not blockMessage:
                print 'fromAddress:', fromAddress
                print 'First 150 characters of message:', repr(message[:150])

                toLabel = shared.config.get(toAddress, 'label')
                if toLabel == '':
                    toLabel = toAddress

                if messageEncodingType == 2:
                    bodyPositionIndex = string.find(message, '\nBody:')
                    if bodyPositionIndex > 1:
                        subject = message[8:bodyPositionIndex]
                        subject = subject[
                            :500]  # Only save and show the first 500 characters of the subject. Any more is probably an attak.
                        body = message[bodyPositionIndex + 6:]
                    else:
                        subject = ''
                        body = message
                elif messageEncodingType == 1:
                    body = message
                    subject = ''
                elif messageEncodingType == 0:
                    print 'messageEncodingType == 0. Doing nothing with the message. They probably just sent it so that we would store their public key or send their ack data for them.'
                else:
                    body = 'Unknown encoding type.\n\n' + repr(message)
                    subject = ''
                if messageEncodingType != 0:
                    t = (self.inventoryHash, toAddress, fromAddress, subject, int(
                        time.time()), body, 'inbox', messageEncodingType, 0)
                    helper_inbox.insert(t)
                    
                    shared.UISignalQueue.put(('displayNewInboxMessage', (
                        self.inventoryHash, toAddress, fromAddress, subject, body)))

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
                self.ackDataThatWeHaveYetToSend.append(
                    ackData)  # When we have processed all data, the processData function will pop the ackData out and process it as if it is a message received from our peer.
            # Display timing data
            timeRequiredToAttemptToDecryptMessage = time.time(
            ) - self.messageProcessingStartTime
            shared.successfullyDecryptMessageTimings.append(
                timeRequiredToAttemptToDecryptMessage)
            sum = 0
            for item in shared.successfullyDecryptMessageTimings:
                sum += item
            shared.printLock.acquire()
            print 'Time to decrypt this message successfully:', timeRequiredToAttemptToDecryptMessage
            print 'Average time for all message decryption successes since startup:', sum / len(shared.successfullyDecryptMessageTimings)
            shared.printLock.release()

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
        return True

    def addMailingListNameToSubject(self, subject, mailingListName):
        subject = subject.strip()
        if subject[:3] == 'Re:' or subject[:3] == 'RE:':
            subject = subject[3:].strip()
        if '[' + mailingListName + ']' in subject:
            return subject
        else:
            return '[' + mailingListName + '] ' + subject

    def possibleNewPubkey(self, toRipe):
        if toRipe in shared.neededPubkeys:
            print 'We have been awaiting the arrival of this pubkey.'
            del shared.neededPubkeys[toRipe]
            t = (toRipe,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND (status='awaitingpubkey' or status='doingpubkeypow') and folder='sent' ''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.workerQueue.put(('sendmessage', ''))
        else:
            shared.printLock.acquire()
            print 'We don\'t need this pub key. We didn\'t ask for it. Pubkey hash:', toRipe.encode('hex')
            shared.printLock.release()

    # We have received a pubkey
    def recpubkey(self, data):
        self.pubkeyProcessingStartTime = time.time()
        if len(data) < 146 or len(data) > 600:  # sanity check
            return
        # We must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in pubkey message insufficient.'
            return

        readPosition = 8  # for the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime < int(time.time()) - shared.lengthOfTimeToHoldOnToAllPubkeys:
            shared.printLock.acquire()
            print 'The embedded time in this pubkey message is too old. Ignoring. Embedded time is:', embeddedTime
            shared.printLock.release()
            return
        if embeddedTime > int(time.time()) + 10800:
            shared.printLock.acquire()
            print 'The embedded time in this pubkey message more than several hours in the future. This is irrational. Ignoring message.'
            shared.printLock.release()
            return
        addressVersion, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        if self.streamNumber != streamNumber:
            print 'stream number embedded in this pubkey doesn\'t match our stream number. Ignoring.'
            return

        inventoryHash = calculateInventoryHash(data)
        shared.inventoryLock.acquire()
        if inventoryHash in shared.inventory:
            print 'We have already received this pubkey. Ignoring it.'
            shared.inventoryLock.release()
            return
        elif shared.isInSqlInventory(inventoryHash):
            print 'We have already received this pubkey (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return
        objectType = 'pubkey'
        shared.inventory[inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        self.broadcastinv(inventoryHash)
        shared.UISignalQueue.put((
            'incrementNumberOfPubkeysProcessed', 'no data'))

        self.processpubkey(data)

        lengthOfTimeWeShouldUseToProcessThisMessage = .2
        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - \
            (time.time() - self.pubkeyProcessingStartTime)
        if sleepTime > 0 and doTimingAttackMitigation:
            shared.printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            shared.printLock.release()
            time.sleep(sleepTime)
        shared.printLock.acquire()
        print 'Total pubkey processing time:', time.time() - self.pubkeyProcessingStartTime, 'seconds.'
        shared.printLock.release()

    def processpubkey(self, data):
        readPosition = 8  # for the nonce
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
        if addressVersion >= 4 or addressVersion == 1:
            shared.printLock.acquire()
            print 'This version of Bitmessage cannot handle version', addressVersion, 'addresses.'
            shared.printLock.release()
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

            shared.printLock.acquire()
            print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
            print 'ripe', ripe.encode('hex')
            print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
            print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')
            shared.printLock.release()

            t = (ripe,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT usedpersonally FROM pubkeys WHERE hash=? AND usedpersonally='yes' ''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                print 'We HAVE used this pubkey personally. Updating time.'
                t = (ripe, data, embeddedTime, 'yes')
            else:
                print 'We have NOT used this pubkey personally. Inserting in database.'
                t = (ripe, data, embeddedTime, 'no')
                     # This will also update the embeddedTime.
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))
            self.possibleNewPubkey(ripe)
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

            shared.printLock.acquire()
            print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
            print 'ripe', ripe.encode('hex')
            print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
            print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')
            shared.printLock.release()

            t = (ripe,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT usedpersonally FROM pubkeys WHERE hash=? AND usedpersonally='yes' ''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                print 'We HAVE used this pubkey personally. Updating time.'
                t = (ripe, data, embeddedTime, 'yes')
            else:
                print 'We have NOT used this pubkey personally. Inserting in database.'
                t = (ripe, data, embeddedTime, 'no')
                     # This will also update the embeddedTime.
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))
            self.possibleNewPubkey(ripe)

    # We have received a getpubkey message
    def recgetpubkey(self, data):
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in getpubkey message insufficient.'
            return
        if len(data) < 34:
            print 'getpubkey message doesn\'t contain enough data. Ignoring.'
            return
        readPosition = 8  # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime > int(time.time()) + 10800:
            print 'The time in this getpubkey message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time()) - shared.maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in this getpubkey message is too old. Ignoring it. Time:', embeddedTime
            return
        requestedAddressVersionNumber, addressVersionLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += addressVersionLength
        streamNumber, streamNumberLength = decodeVarint(
            data[readPosition:readPosition + 10])
        if streamNumber != self.streamNumber:
            print 'The streamNumber', streamNumber, 'doesn\'t match our stream number:', self.streamNumber
            return
        readPosition += streamNumberLength

        inventoryHash = calculateInventoryHash(data)
        shared.inventoryLock.acquire()
        if inventoryHash in shared.inventory:
            print 'We have already received this getpubkey request. Ignoring it.'
            shared.inventoryLock.release()
            return
        elif shared.isInSqlInventory(inventoryHash):
            print 'We have already received this getpubkey request (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return

        objectType = 'getpubkey'
        shared.inventory[inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        # This getpubkey request is valid so far. Forward to peers.
        self.broadcastinv(inventoryHash)

        if requestedAddressVersionNumber == 0:
            print 'The requestedAddressVersionNumber of the pubkey request is zero. That doesn\'t make any sense. Ignoring it.'
            return
        elif requestedAddressVersionNumber == 1:
            print 'The requestedAddressVersionNumber of the pubkey request is 1 which isn\'t supported anymore. Ignoring it.'
            return
        elif requestedAddressVersionNumber > 3:
            print 'The requestedAddressVersionNumber of the pubkey request is too high. Can\'t understand. Ignoring it.'
            return

        requestedHash = data[readPosition:readPosition + 20]
        if len(requestedHash) != 20:
            print 'The length of the requested hash is not 20 bytes. Something is wrong. Ignoring.'
            return
        print 'the hash requested in this getpubkey request is:', requestedHash.encode('hex')

        if requestedHash in shared.myAddressesByHash:  # if this address hash is one of mine
            if decodeAddress(shared.myAddressesByHash[requestedHash])[1] != requestedAddressVersionNumber:
                shared.printLock.acquire()
                sys.stderr.write(
                    '(Within the recgetpubkey function) Someone requested one of my pubkeys but the requestedAddressVersionNumber doesn\'t match my actual address version number. That shouldn\'t have happened. Ignoring.\n')
                shared.printLock.release()
                return
            try:
                lastPubkeySendTime = int(shared.config.get(
                    shared.myAddressesByHash[requestedHash], 'lastpubkeysendtime'))
            except:
                lastPubkeySendTime = 0
            if lastPubkeySendTime < time.time() - shared.lengthOfTimeToHoldOnToAllPubkeys:  # If the last time we sent our pubkey was at least 28 days ago...
                shared.printLock.acquire()
                print 'Found getpubkey-requested-hash in my list of EC hashes. Telling Worker thread to do the POW for a pubkey message and send it out.'
                shared.printLock.release()
                if requestedAddressVersionNumber == 2:
                    shared.workerQueue.put((
                        'doPOWForMyV2Pubkey', requestedHash))
                elif requestedAddressVersionNumber == 3:
                    shared.workerQueue.put((
                        'doPOWForMyV3Pubkey', requestedHash))
            else:
                shared.printLock.acquire()
                print 'Found getpubkey-requested-hash in my list of EC hashes BUT we already sent it recently. Ignoring request. The lastPubkeySendTime is:', lastPubkeySendTime
                shared.printLock.release()
        else:
            shared.printLock.acquire()
            print 'This getpubkey request is not for any of my keys.'
            shared.printLock.release()

    # We have received an inv message
    def recinv(self, data):
        totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave = 0  # ..from all peers, counting duplicates seperately (because they take up memory)
        if len(shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer) > 0:
            for key, value in shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer.items():
                totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave += value
            shared.printLock.acquire()
            print 'number of keys(hosts) in shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer:', len(shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer)
            print 'totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave = ', totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave
            shared.printLock.release()
        numberOfItemsInInv, lengthOfVarint = decodeVarint(data[:10])
        if numberOfItemsInInv > 50000:
            sys.stderr.write('Too many items in inv message!')
            return
        if len(data) < lengthOfVarint + (numberOfItemsInInv * 32):
            print 'inv message doesn\'t contain enough data. Ignoring.'
            return
        if numberOfItemsInInv == 1:  # we'll just request this data from the person who advertised the object.
            if totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave > 200000 and len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 1000:  # inv flooding attack mitigation
                shared.printLock.acquire()
                print 'We already have', totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave, 'items yet to retrieve from peers and over 1000 from this node in particular. Ignoring this inv message.'
                shared.printLock.release()
                return
            self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware[
                data[lengthOfVarint:32 + lengthOfVarint]] = 0
            if data[lengthOfVarint:32 + lengthOfVarint] in shared.inventory:
                shared.printLock.acquire()
                print 'Inventory (in memory) has inventory item already.'
                shared.printLock.release()
            elif shared.isInSqlInventory(data[lengthOfVarint:32 + lengthOfVarint]):
                print 'Inventory (SQL on disk) has inventory item already.'
            else:
                self.sendgetdata(data[lengthOfVarint:32 + lengthOfVarint])
        else:
            print 'inv message lists', numberOfItemsInInv, 'objects.'
            for i in range(numberOfItemsInInv):  # upon finishing dealing with an incoming message, the receiveDataThread will request a random object from the peer. This way if we get multiple inv messages from multiple peers which list mostly the same objects, we will make getdata requests for different random objects from the various peers.
                if len(data[lengthOfVarint + (32 * i):32 + lengthOfVarint + (32 * i)]) == 32:  # The length of an inventory hash should be 32. If it isn't 32 then the remote node is either badly programmed or behaving nefariously.
                    if totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave > 200000 and len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 1000:  # inv flooding attack mitigation
                        shared.printLock.acquire()
                        print 'We already have', totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave, 'items yet to retrieve from peers and over', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave), 'from this node in particular. Ignoring the rest of this inv message.'
                        shared.printLock.release()
                        break
                    self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware[data[
                        lengthOfVarint + (32 * i):32 + lengthOfVarint + (32 * i)]] = 0
                    self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        data[lengthOfVarint + (32 * i):32 + lengthOfVarint + (32 * i)]] = 0
            shared.numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                self.HOST] = len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)

    # Send a getdata message to our peer to request the object with the given
    # hash
    def sendgetdata(self, hash):
        shared.printLock.acquire()
        print 'sending getdata to retrieve object with hash:', hash.encode('hex')
        shared.printLock.release()
        payload = '\x01' + hash
        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'getdata\x00\x00\x00\x00\x00'
        headerData += pack('>L', len(
            payload))  # payload length. Note that we add an extra 8 for the nonce.
        headerData += hashlib.sha512(payload).digest()[:4]
        try:
            self.sock.sendall(headerData + payload)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            print 'sock.sendall error:', err
            shared.printLock.release()

    # We have received a getdata request from our peer
    def recgetdata(self, data):
        numberOfRequestedInventoryItems, lengthOfVarint = decodeVarint(
            data[:10])
        if len(data) < lengthOfVarint + (32 * numberOfRequestedInventoryItems):
            print 'getdata message does not contain enough data. Ignoring.'
            return
        for i in xrange(numberOfRequestedInventoryItems):
            hash = data[lengthOfVarint + (
                i * 32):32 + lengthOfVarint + (i * 32)]
            shared.printLock.acquire()
            print 'received getdata request for item:', hash.encode('hex')
            shared.printLock.release()
            # print 'inventory is', shared.inventory
            if hash in shared.inventory:
                objectType, streamNumber, payload, receivedTime = shared.inventory[
                    hash]
                self.sendData(objectType, payload)
            else:
                t = (hash,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''select objecttype, payload from inventory where hash=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn != []:
                    for row in queryreturn:
                        objectType, payload = row
                    self.sendData(objectType, payload)
                else:
                    print 'Someone asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. That shouldn\'t have happened.'

    # Our peer has requested (in a getdata message) that we send an object.
    def sendData(self, objectType, payload):
        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
        if objectType == 'pubkey':
            shared.printLock.acquire()
            print 'sending pubkey'
            shared.printLock.release()
            headerData += 'pubkey\x00\x00\x00\x00\x00\x00'
        elif objectType == 'getpubkey' or objectType == 'pubkeyrequest':
            shared.printLock.acquire()
            print 'sending getpubkey'
            shared.printLock.release()
            headerData += 'getpubkey\x00\x00\x00'
        elif objectType == 'msg':
            shared.printLock.acquire()
            print 'sending msg'
            shared.printLock.release()
            headerData += 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        elif objectType == 'broadcast':
            shared.printLock.acquire()
            print 'sending broadcast'
            shared.printLock.release()
            headerData += 'broadcast\x00\x00\x00'
        else:
            sys.stderr.write(
                'Error: sendData has been asked to send a strange objectType: %s\n' % str(objectType))
            return
        headerData += pack('>L', len(payload))  # payload length.
        headerData += hashlib.sha512(payload).digest()[:4]
        try:
            self.sock.sendall(headerData + payload)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            print 'sock.sendall error:', err
            shared.printLock.release()

    # Send an inv message with just one hash to all of our peers
    def broadcastinv(self, hash):
        shared.printLock.acquire()
        print 'broadcasting inv with hash:', hash.encode('hex')
        shared.printLock.release()
        shared.broadcastToSendDataQueues((self.streamNumber, 'sendinv', hash))

    # We have received an addr message.
    def recaddr(self, data):
        listOfAddressDetailsToBroadcastToPeers = []
        numberOfAddressesIncluded = 0
        numberOfAddressesIncluded, lengthOfNumberOfAddresses = decodeVarint(
            data[:10])

        if shared.verbose >= 1:
            shared.printLock.acquire()
            print 'addr message contains', numberOfAddressesIncluded, 'IP addresses.'
            shared.printLock.release()

        if self.remoteProtocolVersion == 1:
            if numberOfAddressesIncluded > 1000 or numberOfAddressesIncluded == 0:
                return
            if len(data) != lengthOfNumberOfAddresses + (34 * numberOfAddressesIncluded):
                print 'addr message does not contain the correct amount of data. Ignoring.'
                return

            needToWriteKnownNodesToDisk = False
            for i in range(0, numberOfAddressesIncluded):
                try:
                    if data[16 + lengthOfNumberOfAddresses + (34 * i):28 + lengthOfNumberOfAddresses + (34 * i)] != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                        shared.printLock.acquire()
                        print 'Skipping IPv6 address.', repr(data[16 + lengthOfNumberOfAddresses + (34 * i):28 + lengthOfNumberOfAddresses + (34 * i)])
                        shared.printLock.release()
                        continue
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (to test for an IPv6 address). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrStream, = unpack('>I', data[4 + lengthOfNumberOfAddresses + (
                        34 * i):8 + lengthOfNumberOfAddresses + (34 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrStream). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.
                if recaddrStream == 0:
                    continue
                if recaddrStream != self.streamNumber and recaddrStream != (self.streamNumber * 2) and recaddrStream != ((self.streamNumber * 2) + 1):  # if the embedded stream number is not in my stream or either of my child streams then ignore it. Someone might be trying funny business.
                    continue
                try:
                    recaddrServices, = unpack('>Q', data[8 + lengthOfNumberOfAddresses + (
                        34 * i):16 + lengthOfNumberOfAddresses + (34 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrServices). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrPort, = unpack('>H', data[32 + lengthOfNumberOfAddresses + (
                        34 * i):34 + lengthOfNumberOfAddresses + (34 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrPort). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.
                # print 'Within recaddr(): IP', recaddrIP, ', Port',
                # recaddrPort, ', i', i
                hostFromAddrMessage = socket.inet_ntoa(data[
                                                       28 + lengthOfNumberOfAddresses + (34 * i):32 + lengthOfNumberOfAddresses + (34 * i)])
                # print 'hostFromAddrMessage', hostFromAddrMessage
                if data[28 + lengthOfNumberOfAddresses + (34 * i)] == '\x7F':
                    print 'Ignoring IP address in loopback range:', hostFromAddrMessage
                    continue
                if helper_generic.isHostInPrivateIPRange(hostFromAddrMessage):
                    print 'Ignoring IP address in private range:', hostFromAddrMessage
                    continue
                timeSomeoneElseReceivedMessageFromThisNode, = unpack('>I', data[lengthOfNumberOfAddresses + (
                    34 * i):4 + lengthOfNumberOfAddresses + (34 * i)])  # This is the 'time' value in the received addr message.
                if recaddrStream not in shared.knownNodes:  # knownNodes is a dictionary of dictionaries with one outer dictionary for each stream. If the outer stream dictionary doesn't exist yet then we must make it.
                    shared.knownNodesLock.acquire()
                    shared.knownNodes[recaddrStream] = {}
                    shared.knownNodesLock.release()
                if hostFromAddrMessage not in shared.knownNodes[recaddrStream]:
                    if len(shared.knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time()) - 10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800):  # If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            recaddrPort, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        needToWriteKnownNodesToDisk = True
                        hostDetails = (
                            timeSomeoneElseReceivedMessageFromThisNode,
                            recaddrStream, recaddrServices, hostFromAddrMessage, recaddrPort)
                        listOfAddressDetailsToBroadcastToPeers.append(
                            hostDetails)
                else:
                    PORT, timeLastReceivedMessageFromThisNode = shared.knownNodes[recaddrStream][
                        hostFromAddrMessage]  # PORT in this case is either the port we used to connect to the remote node, or the port that was specified by someone else in a past addr message.
                    if (timeLastReceivedMessageFromThisNode < timeSomeoneElseReceivedMessageFromThisNode) and (timeSomeoneElseReceivedMessageFromThisNode < int(time.time())):
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            PORT, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        if PORT != recaddrPort:
                            print 'Strange occurance: The port specified in an addr message', str(recaddrPort), 'does not match the port', str(PORT), 'that this program (or some other peer) used to connect to it', str(hostFromAddrMessage), '. Perhaps they changed their port or are using a strange NAT configuration.'
            if needToWriteKnownNodesToDisk:  # Runs if any nodes were new to us. Also, share those nodes with our peers.
                shared.knownNodesLock.acquire()
                output = open(shared.appdata + 'knownnodes.dat', 'wb')
                pickle.dump(shared.knownNodes, output)
                output.close()
                shared.knownNodesLock.release()
                self.broadcastaddr(
                    listOfAddressDetailsToBroadcastToPeers)  # no longer broadcast
            shared.printLock.acquire()
            print 'knownNodes currently has', len(shared.knownNodes[self.streamNumber]), 'nodes for this stream.'
            shared.printLock.release()
        elif self.remoteProtocolVersion >= 2:  # The difference is that in protocol version 2, network addresses use 64 bit times rather than 32 bit times.
            if numberOfAddressesIncluded > 1000 or numberOfAddressesIncluded == 0:
                return
            if len(data) != lengthOfNumberOfAddresses + (38 * numberOfAddressesIncluded):
                print 'addr message does not contain the correct amount of data. Ignoring.'
                return

            needToWriteKnownNodesToDisk = False
            for i in range(0, numberOfAddressesIncluded):
                try:
                    if data[20 + lengthOfNumberOfAddresses + (38 * i):32 + lengthOfNumberOfAddresses + (38 * i)] != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                        shared.printLock.acquire()
                        print 'Skipping IPv6 address.', repr(data[20 + lengthOfNumberOfAddresses + (38 * i):32 + lengthOfNumberOfAddresses + (38 * i)])
                        shared.printLock.release()
                        continue
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (to test for an IPv6 address). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrStream, = unpack('>I', data[8 + lengthOfNumberOfAddresses + (
                        38 * i):12 + lengthOfNumberOfAddresses + (38 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrStream). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.
                if recaddrStream == 0:
                    continue
                if recaddrStream != self.streamNumber and recaddrStream != (self.streamNumber * 2) and recaddrStream != ((self.streamNumber * 2) + 1):  # if the embedded stream number is not in my stream or either of my child streams then ignore it. Someone might be trying funny business.
                    continue
                try:
                    recaddrServices, = unpack('>Q', data[12 + lengthOfNumberOfAddresses + (
                        38 * i):20 + lengthOfNumberOfAddresses + (38 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrServices). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrPort, = unpack('>H', data[36 + lengthOfNumberOfAddresses + (
                        38 * i):38 + lengthOfNumberOfAddresses + (38 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrPort). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.
                # print 'Within recaddr(): IP', recaddrIP, ', Port',
                # recaddrPort, ', i', i
                hostFromAddrMessage = socket.inet_ntoa(data[
                                                       32 + lengthOfNumberOfAddresses + (38 * i):36 + lengthOfNumberOfAddresses + (38 * i)])
                # print 'hostFromAddrMessage', hostFromAddrMessage
                if data[32 + lengthOfNumberOfAddresses + (38 * i)] == '\x7F':
                    print 'Ignoring IP address in loopback range:', hostFromAddrMessage
                    continue
                if data[32 + lengthOfNumberOfAddresses + (38 * i)] == '\x0A':
                    print 'Ignoring IP address in private range:', hostFromAddrMessage
                    continue
                if data[32 + lengthOfNumberOfAddresses + (38 * i):34 + lengthOfNumberOfAddresses + (38 * i)] == '\xC0A8':
                    print 'Ignoring IP address in private range:', hostFromAddrMessage
                    continue
                timeSomeoneElseReceivedMessageFromThisNode, = unpack('>Q', data[lengthOfNumberOfAddresses + (
                    38 * i):8 + lengthOfNumberOfAddresses + (38 * i)])  # This is the 'time' value in the received addr message. 64-bit.
                if recaddrStream not in shared.knownNodes:  # knownNodes is a dictionary of dictionaries with one outer dictionary for each stream. If the outer stream dictionary doesn't exist yet then we must make it.
                    shared.knownNodesLock.acquire()
                    shared.knownNodes[recaddrStream] = {}
                    shared.knownNodesLock.release()
                if hostFromAddrMessage not in shared.knownNodes[recaddrStream]:
                    if len(shared.knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time()) - 10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800):  # If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            recaddrPort, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        shared.printLock.acquire()
                        print 'added new node', hostFromAddrMessage, 'to knownNodes in stream', recaddrStream
                        shared.printLock.release()
                        needToWriteKnownNodesToDisk = True
                        hostDetails = (
                            timeSomeoneElseReceivedMessageFromThisNode,
                            recaddrStream, recaddrServices, hostFromAddrMessage, recaddrPort)
                        listOfAddressDetailsToBroadcastToPeers.append(
                            hostDetails)
                else:
                    PORT, timeLastReceivedMessageFromThisNode = shared.knownNodes[recaddrStream][
                        hostFromAddrMessage]  # PORT in this case is either the port we used to connect to the remote node, or the port that was specified by someone else in a past addr message.
                    if (timeLastReceivedMessageFromThisNode < timeSomeoneElseReceivedMessageFromThisNode) and (timeSomeoneElseReceivedMessageFromThisNode < int(time.time())):
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            PORT, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        if PORT != recaddrPort:
                            print 'Strange occurance: The port specified in an addr message', str(recaddrPort), 'does not match the port', str(PORT), 'that this program (or some other peer) used to connect to it', str(hostFromAddrMessage), '. Perhaps they changed their port or are using a strange NAT configuration.'
            if needToWriteKnownNodesToDisk:  # Runs if any nodes were new to us. Also, share those nodes with our peers.
                shared.knownNodesLock.acquire()
                output = open(shared.appdata + 'knownnodes.dat', 'wb')
                pickle.dump(shared.knownNodes, output)
                output.close()
                shared.knownNodesLock.release()
                self.broadcastaddr(listOfAddressDetailsToBroadcastToPeers)
            shared.printLock.acquire()
            print 'knownNodes currently has', len(shared.knownNodes[self.streamNumber]), 'nodes for this stream.'
            shared.printLock.release()

    # Function runs when we want to broadcast an addr message to all of our
    # peers. Runs when we learn of nodes that we didn't previously know about
    # and want to share them with our peers.
    def broadcastaddr(self, listOfAddressDetailsToBroadcastToPeers):
        numberOfAddressesInAddrMessage = len(
            listOfAddressDetailsToBroadcastToPeers)
        payload = ''
        for hostDetails in listOfAddressDetailsToBroadcastToPeers:
            timeLastReceivedMessageFromThisNode, streamNumber, services, host, port = hostDetails
            payload += pack(
                '>Q', timeLastReceivedMessageFromThisNode)  # now uses 64-bit time
            payload += pack('>I', streamNumber)
            payload += pack(
                '>q', services)  # service bit flags offered by this node
            payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                socket.inet_aton(host)
            payload += pack('>H', port)  # remote port

        payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
        datatosend = '\xE9\xBE\xB4\xD9addr\x00\x00\x00\x00\x00\x00\x00\x00'
        datatosend = datatosend + pack('>L', len(payload))  # payload length
        datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
        datatosend = datatosend + payload

        if shared.verbose >= 1:
            shared.printLock.acquire()
            print 'Broadcasting addr with', numberOfAddressesInAddrMessage, 'entries.'
            shared.printLock.release()
        shared.broadcastToSendDataQueues((
            self.streamNumber, 'sendaddr', datatosend))

    # Send a big addr message to our peer
    def sendaddr(self):
        addrsInMyStream = {}
        addrsInChildStreamLeft = {}
        addrsInChildStreamRight = {}
        # print 'knownNodes', shared.knownNodes

        # We are going to share a maximum number of 1000 addrs with our peer.
        # 500 from this stream, 250 from the left child stream, and 250 from
        # the right child stream.
        shared.knownNodesLock.acquire()
        if len(shared.knownNodes[self.streamNumber]) > 0:
            for i in range(500):
                random.seed()
                HOST, = random.sample(shared.knownNodes[self.streamNumber], 1)
                if helper_generic.isHostInPrivateIPRange(HOST):
                    continue
                addrsInMyStream[HOST] = shared.knownNodes[
                    self.streamNumber][HOST]
        if len(shared.knownNodes[self.streamNumber * 2]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(shared.knownNodes[
                                      self.streamNumber * 2], 1)
                if helper_generic.isHostInPrivateIPRange(HOST):
                    continue
                addrsInChildStreamLeft[HOST] = shared.knownNodes[
                    self.streamNumber * 2][HOST]
        if len(shared.knownNodes[(self.streamNumber * 2) + 1]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(shared.knownNodes[
                                      (self.streamNumber * 2) + 1], 1)
                if helper_generic.isHostInPrivateIPRange(HOST):
                    continue
                addrsInChildStreamRight[HOST] = shared.knownNodes[
                    (self.streamNumber * 2) + 1][HOST]
        shared.knownNodesLock.release()
        numberOfAddressesInAddrMessage = 0
        payload = ''
        # print 'addrsInMyStream.items()', addrsInMyStream.items()
        for HOST, value in addrsInMyStream.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers):  # If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', self.streamNumber)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                    socket.inet_aton(HOST)
                payload += pack('>H', PORT)  # remote port
        for HOST, value in addrsInChildStreamLeft.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers):  # If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', self.streamNumber * 2)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                    socket.inet_aton(HOST)
                payload += pack('>H', PORT)  # remote port
        for HOST, value in addrsInChildStreamRight.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time()) - shared.maximumAgeOfNodesThatIAdvertiseToOthers):  # If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', (self.streamNumber * 2) + 1)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                    socket.inet_aton(HOST)
                payload += pack('>H', PORT)  # remote port

        payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
        datatosend = '\xE9\xBE\xB4\xD9addr\x00\x00\x00\x00\x00\x00\x00\x00'
        datatosend = datatosend + pack('>L', len(payload))  # payload length
        datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
        datatosend = datatosend + payload
        try:
            self.sock.sendall(datatosend)
            if shared.verbose >= 1:
                shared.printLock.acquire()
                print 'Sending addr with', numberOfAddressesInAddrMessage, 'entries.'
                shared.printLock.release()
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            print 'sock.sendall error:', err
            shared.printLock.release()

    # We have received a version message
    def recversion(self, data):
        if len(data) < 83:
            # This version message is unreasonably short. Forget it.
            return
        elif not self.verackSent:
            self.remoteProtocolVersion, = unpack('>L', data[:4])
            if self.remoteProtocolVersion <= 1:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
                shared.printLock.acquire()
                print 'Closing connection to old protocol version 1 node: ', self.HOST
                shared.printLock.release()
                return
            # print 'remoteProtocolVersion', self.remoteProtocolVersion
            self.myExternalIP = socket.inet_ntoa(data[40:44])
            # print 'myExternalIP', self.myExternalIP
            self.remoteNodeIncomingPort, = unpack('>H', data[70:72])
            # print 'remoteNodeIncomingPort', self.remoteNodeIncomingPort
            useragentLength, lengthOfUseragentVarint = decodeVarint(
                data[80:84])
            readPosition = 80 + lengthOfUseragentVarint
            useragent = data[readPosition:readPosition + useragentLength]
            readPosition += useragentLength
            numberOfStreamsInVersionMessage, lengthOfNumberOfStreamsInVersionMessage = decodeVarint(
                data[readPosition:])
            readPosition += lengthOfNumberOfStreamsInVersionMessage
            self.streamNumber, lengthOfRemoteStreamNumber = decodeVarint(
                data[readPosition:])
            shared.printLock.acquire()
            print 'Remote node useragent:', useragent, '  stream number:', self.streamNumber
            shared.printLock.release()
            if self.streamNumber != 1:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
                shared.printLock.acquire()
                print 'Closed connection to', self.HOST, 'because they are interested in stream', self.streamNumber, '.'
                shared.printLock.release()
                return
            shared.connectedHostsList[
                self.HOST] = 1  # We use this data structure to not only keep track of what hosts we are connected to so that we don't try to connect to them again, but also to list the connections count on the Network Status tab.
            # If this was an incoming connection, then the sendData thread
            # doesn't know the stream. We have to set it.
            if not self.initiatedConnection:
                shared.broadcastToSendDataQueues((
                    0, 'setStreamNumber', (self.HOST, self.streamNumber)))
            if data[72:80] == shared.eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
                shared.printLock.acquire()
                print 'Closing connection to myself: ', self.HOST
                shared.printLock.release()
                return
            shared.broadcastToSendDataQueues((0, 'setRemoteProtocolVersion', (
                self.HOST, self.remoteProtocolVersion)))

            shared.knownNodesLock.acquire()
            shared.knownNodes[self.streamNumber][self.HOST] = (
                self.remoteNodeIncomingPort, int(time.time()))
            output = open(shared.appdata + 'knownnodes.dat', 'wb')
            pickle.dump(shared.knownNodes, output)
            output.close()
            shared.knownNodesLock.release()

            self.sendverack()
            if self.initiatedConnection == False:
                self.sendversion()

    # Sends a version message
    def sendversion(self):
        shared.printLock.acquire()
        print 'Sending version message'
        shared.printLock.release()
        try:
            self.sock.sendall(shared.assembleVersionMessage(
                self.HOST, self.PORT, self.streamNumber))
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            print 'sock.sendall error:', err
            shared.printLock.release()

    # Sends a verack message
    def sendverack(self):
        shared.printLock.acquire()
        print 'Sending verack'
        shared.printLock.release()
        try:
            self.sock.sendall(
                '\xE9\xBE\xB4\xD9\x76\x65\x72\x61\x63\x6B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            print 'sock.sendall error:', err
            shared.printLock.release()
                                                                                                             # cf
                                                                                                             # 83
                                                                                                             # e1
                                                                                                             # 35
        self.verackSent = True
        if self.verackReceived:
            self.connectionFullyEstablished()
