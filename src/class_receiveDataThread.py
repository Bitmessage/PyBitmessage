doTimingAttackMitigation = True

import time
import threading
import shared
import hashlib
import socket
import random
from struct import unpack, pack
import sys
#import string
#from subprocess import call  # used when the API must execute an outside program
#from pyelliptic.openssl import OpenSSL

#import highlevelcrypto
from addresses import *
import helper_generic
#import helper_bitcoin
#import helper_inbox
#import helper_sent
from helper_sql import *
#import tr
from debug import logger
#from bitmessagemain import shared.lengthOfTimeToLeaveObjectsInInventory, shared.lengthOfTimeToHoldOnToAllPubkeys, shared.maximumAgeOfAnObjectThatIAmWillingToAccept, shared.maximumAgeOfObjectsThatIAdvertiseToOthers, shared.maximumAgeOfNodesThatIAdvertiseToOthers, shared.numberOfObjectsThatWeHaveYetToGetPerPeer, shared.neededPubkeys

# This thread is created either by the synSenderThread(for outgoing
# connections) or the singleListenerThread(for incoming connections).

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
        selfInitiatedConnections,
        sendDataThreadQueue):
        
        self.sock = sock
        self.peer = shared.Peer(HOST, port)
        self.streamNumber = streamNumber
        self.payloadLength = 0  # This is the protocol payload length thus it doesn't include the 24 byte message header
        self.objectsThatWeHaveYetToGetFromThisPeer = {}
        self.selfInitiatedConnections = selfInitiatedConnections
        self.sendDataThreadQueue = sendDataThreadQueue # used to send commands and data to the sendDataThread
        shared.connectedHostsList[
            self.peer.host] = 0  # The very fact that this receiveData thread exists shows that we are connected to the remote host. Let's add it to this list so that an outgoingSynSender thread doesn't try to connect to it.
        self.connectionIsOrWasFullyEstablished = False  # set to true after the remote node and I accept each other's version messages. This is needed to allow the user interface to accurately reflect the current number of connections.
        if self.streamNumber == -1:  # This was an incoming connection. Send out a version message if we accept the other node's version message.
            self.initiatedConnection = False
        else:
            self.initiatedConnection = True
            self.selfInitiatedConnections[streamNumber][self] = 0
        self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware = someObjectsOfWhichThisRemoteNodeIsAlreadyAware

    def run(self):
        with shared.printLock:
            print 'ID of the receiveDataThread is', str(id(self)) + '. The size of the shared.connectedHostsList is now', len(shared.connectedHostsList)

        while True:
            dataLen = len(self.data)
            try:
                self.data += self.sock.recv(4096)
            except socket.timeout:
                with shared.printLock:
                    print 'Timeout occurred waiting for data from', self.peer, '. Closing receiveData thread. (ID:', str(id(self)) + ')'
                break
            except Exception as err:
                with shared.printLock:
                    print 'sock.recv error. Closing receiveData thread (HOST:', self.peer, 'ID:', str(id(self)) + ').', err
                break
            # print 'Received', repr(self.data)
            if len(self.data) == dataLen: # If self.sock.recv returned no data:
                with shared.printLock:
                    print 'Connection to', self.peer, 'closed. Closing receiveData thread. (ID:', str(id(self)) + ')'
                break
            else:
                self.processData()

        try:
            del self.selfInitiatedConnections[self.streamNumber][self]
            with shared.printLock:
                print 'removed self (a receiveDataThread) from selfInitiatedConnections'
        except:
            pass
        shared.broadcastToSendDataQueues((0, 'shutdown', self.peer)) # commands the corresponding sendDataThread to shut itself down.
        try:
            del shared.connectedHostsList[self.peer.host]
        except Exception as err:
            with shared.printLock:
                print 'Could not delete', self.peer.host, 'from shared.connectedHostsList.', err

        try:
            del shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                self.peer]
        except:
            pass
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        with shared.printLock:
            print 'The size of the connectedHostsList is now:', len(shared.connectedHostsList)


    def processData(self):
        # if shared.verbose >= 3:
            # with shared.printLock:
            #   print 'self.data is currently ', repr(self.data)
            #
        if len(self.data) < 24:  # if so little of the data has arrived that we can't even read the checksum then wait for more data.
            return
        if self.data[0:4] != '\xe9\xbe\xb4\xd9':
            if shared.verbose >= 1:
                with shared.printLock:
                    print 'The magic bytes were not correct. First 40 bytes of data: ' + repr(self.data[0:40])

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
            shared.knownNodes[self.streamNumber][self.peer] = int(time.time())
            shared.knownNodesLock.release()
        if self.payloadLength <= 180000000:  # If the size of the message is greater than 180MB, ignore it. (I get memory errors when processing messages much larger than this though it is concievable that this value will have to be lowered if some systems are less tolarant of large messages.)
            remoteCommand = self.data[4:16]
            with shared.printLock:
                print 'remoteCommand', repr(remoteCommand.replace('\x00', '')), ' from', self.peer

            if remoteCommand == 'version\x00\x00\x00\x00\x00':
                self.recversion(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'verack\x00\x00\x00\x00\x00\x00':
                self.recverack()
            elif remoteCommand == 'addr\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recaddr(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'getpubkey\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                shared.checkAndSharegetpubkeyWithPeers(self.data[24:self.payloadLength + 24])
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
            while len(self.objectsThatWeHaveYetToGetFromThisPeer) > 0:
                shared.numberOfInventoryLookupsPerformed += 1
                objectHash, = random.sample(
                    self.objectsThatWeHaveYetToGetFromThisPeer, 1)
                if objectHash in shared.inventory:
                    with shared.printLock:
                        print 'Inventory (in memory) already has object listed in inv message.'

                    del self.objectsThatWeHaveYetToGetFromThisPeer[
                        objectHash]
                elif shared.isInSqlInventory(objectHash):
                    if shared.verbose >= 3:
                        with shared.printLock:
                            print 'Inventory (SQL on disk) already has object listed in inv message.'

                    del self.objectsThatWeHaveYetToGetFromThisPeer[
                        objectHash]
                else:
                    self.sendgetdata(objectHash)
                    del self.objectsThatWeHaveYetToGetFromThisPeer[
                        objectHash]  # It is possible that the remote node might not respond with the object. In that case, we'll very likely get it from someone else anyway.
                    if len(self.objectsThatWeHaveYetToGetFromThisPeer) == 0:
                        with shared.printLock:
                            print '(concerning', str(self.peer) + ')', 'number of objectsThatWeHaveYetToGetFromThisPeer is now', len(self.objectsThatWeHaveYetToGetFromThisPeer)

                        try:
                            del shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                                self.peer]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                        except:
                            pass
                    break
                if len(self.objectsThatWeHaveYetToGetFromThisPeer) == 0:
                    with shared.printLock:
                        print '(concerning', str(self.peer) + ')', 'number of objectsThatWeHaveYetToGetFromThisPeer is now', len(self.objectsThatWeHaveYetToGetFromThisPeer)

                    try:
                        del shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                            self.peer]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                    except:
                        pass
            if len(self.objectsThatWeHaveYetToGetFromThisPeer) > 0:
                with shared.printLock:
                    print '(concerning', str(self.peer) + ')', 'number of objectsThatWeHaveYetToGetFromThisPeer is now', len(self.objectsThatWeHaveYetToGetFromThisPeer)

                shared.numberOfObjectsThatWeHaveYetToGetPerPeer[self.peer] = len(
                    self.objectsThatWeHaveYetToGetFromThisPeer)  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
        self.processData()


    def sendpong(self):
        print 'Sending pong'
        self.sendDataThreadQueue.put((0, 'sendRawData', '\xE9\xBE\xB4\xD9\x70\x6F\x6E\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35'))


    def recverack(self):
        print 'verack received'
        self.verackReceived = True
        if self.verackSent:
            # We have thus both sent and received a verack.
            self.connectionFullyEstablished()

    def connectionFullyEstablished(self):
        self.connectionIsOrWasFullyEstablished = True
        if not self.initiatedConnection:
            shared.clientHasReceivedIncomingConnections = True
            shared.UISignalQueue.put(('setStatusIcon', 'green'))
        self.sock.settimeout(
            600)  # We'll send out a pong every 5 minutes to make sure the connection stays alive if there has been no other traffic to send lately.
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        with shared.printLock:
            print 'Connection fully established with', self.peer
            print 'The size of the connectedHostsList is now', len(shared.connectedHostsList)
            print 'The length of sendDataQueues is now:', len(shared.sendDataQueues)
            print 'broadcasting addr from within connectionFullyEstablished function.'

        # Let all of our peers know about this new node.
        dataToSend = (int(time.time()), self.streamNumber, 1, self.peer.host, self.remoteNodeIncomingPort)
        shared.broadcastToSendDataQueues((
            self.streamNumber, 'advertisepeer', dataToSend))

        self.sendaddr()  # This is one large addr message to this one peer.
        if not self.initiatedConnection and len(shared.connectedHostsList) > 200:
            with shared.printLock:
                print 'We are connected to too many people. Closing connection.'

            shared.broadcastToSendDataQueues((0, 'shutdown', self.peer))
            return
        self.sendBigInv()

    def sendBigInv(self):
        # Select all hashes which are younger than two days old and in this
        # stream.
        queryreturn = sqlQuery(
            '''SELECT hash FROM inventory WHERE ((receivedtime>? and objecttype<>'pubkey') or (receivedtime>? and objecttype='pubkey')) and streamnumber=?''',
            int(time.time()) - shared.maximumAgeOfObjectsThatIAdvertiseToOthers,
            int(time.time()) - shared.lengthOfTimeToHoldOnToAllPubkeys,
            self.streamNumber)
        bigInvList = {}
        for row in queryreturn:
            hash, = row
            if hash not in self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware:
                bigInvList[hash] = 0
        # We also have messages in our inventory in memory (which is a python
        # dictionary). Let's fetch those too.
        with shared.inventoryLock:
            for hash, storedValue in shared.inventory.items():
                if hash not in self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware:
                    objectType, streamNumber, payload, receivedTime, tag = storedValue
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
        with shared.printLock:
            print 'Sending huge inv message with', numberOfObjects, 'objects to just this one peer'
        self.sendDataThreadQueue.put((0, 'sendRawData', headerData + payload))


    # We have received a broadcast message
    def recbroadcast(self, data):
        self.messageProcessingStartTime = time.time()

        shared.checkAndShareBroadcastWithPeers(data)

        """
        Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. Sleeping
        will help guarantee that we can process messages faster than a remote
        node can send them. If we fall behind, the attacker could observe that
        we are are slowing down the rate at which we request objects from the
        network which would indicate that we own a particular address (whichever
        one to which they are sending all of their attack messages). Note
        that if an attacker connects to a target with many connections, this
        mitigation mechanism might not be sufficient.
        """
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
            with shared.printLock:
                print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            time.sleep(sleepTime)

    # We have received a msg message.
    def recmsg(self, data):
        self.messageProcessingStartTime = time.time()

        shared.checkAndShareMsgWithPeers(data)

        """
        Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. Sleeping
        will help guarantee that we can process messages faster than a remote
        node can send them. If we fall behind, the attacker could observe that
        we are are slowing down the rate at which we request objects from the
        network which would indicate that we own a particular address (whichever
        one to which they are sending all of their attack messages). Note
        that if an attacker connects to a target with many connections, this
        mitigation mechanism might not be sufficient.
        """
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
            with shared.printLock:
                print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            time.sleep(sleepTime)

    # We have received a pubkey
    def recpubkey(self, data):
        self.pubkeyProcessingStartTime = time.time()

        shared.checkAndSharePubkeyWithPeers(data)

        lengthOfTimeWeShouldUseToProcessThisMessage = .1
        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - \
            (time.time() - self.pubkeyProcessingStartTime)
        if sleepTime > 0 and doTimingAttackMitigation:
            with shared.printLock:
                print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            time.sleep(sleepTime)


    # We have received an inv message
    def recinv(self, data):
        totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers = 0  # this counts duplicates seperately because they take up memory
        if len(shared.numberOfObjectsThatWeHaveYetToGetPerPeer) > 0:
            for key, value in shared.numberOfObjectsThatWeHaveYetToGetPerPeer.items():
                totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers += value
            with shared.printLock:
                print 'number of keys(hosts) in shared.numberOfObjectsThatWeHaveYetToGetPerPeer:', len(shared.numberOfObjectsThatWeHaveYetToGetPerPeer)
                print 'totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers = ', totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers

        numberOfItemsInInv, lengthOfVarint = decodeVarint(data[:10])
        if numberOfItemsInInv > 50000:
            sys.stderr.write('Too many items in inv message!')
            return
        if len(data) < lengthOfVarint + (numberOfItemsInInv * 32):
            print 'inv message doesn\'t contain enough data. Ignoring.'
            return
        if numberOfItemsInInv == 1:  # we'll just request this data from the person who advertised the object.
            if totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers > 200000 and len(self.objectsThatWeHaveYetToGetFromThisPeer) > 1000:  # inv flooding attack mitigation
                with shared.printLock:
                    print 'We already have', totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers, 'items yet to retrieve from peers and over 1000 from this node in particular. Ignoring this inv message.'
                return
            self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware[
                data[lengthOfVarint:32 + lengthOfVarint]] = 0
            shared.numberOfInventoryLookupsPerformed += 1
            if data[lengthOfVarint:32 + lengthOfVarint] in shared.inventory:
                with shared.printLock:
                    print 'Inventory (in memory) has inventory item already.'
            elif shared.isInSqlInventory(data[lengthOfVarint:32 + lengthOfVarint]):
                print 'Inventory (SQL on disk) has inventory item already.'
            else:
                self.sendgetdata(data[lengthOfVarint:32 + lengthOfVarint])
        else:
            # There are many items listed in this inv message. Let us create a
            # 'set' of objects we are aware of and a set of objects in this inv
            # message so that we can diff one from the other cheaply.
            startTime = time.time()
            advertisedSet = set()
            for i in range(numberOfItemsInInv):
                advertisedSet.add(data[lengthOfVarint + (32 * i):32 + lengthOfVarint + (32 * i)])
            objectsNewToMe = advertisedSet - shared.inventorySets[self.streamNumber]
            logger.info('inv message lists %s objects. Of those %s are new to me. It took %s seconds to figure that out.', numberOfItemsInInv, len(objectsNewToMe), time.time()-startTime)
            for item in objectsNewToMe:  
                if totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers > 200000 and len(self.objectsThatWeHaveYetToGetFromThisPeer) > 1000:  # inv flooding attack mitigation
                    with shared.printLock:
                        print 'We already have', totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers, 'items yet to retrieve from peers and over', len(self.objectsThatWeHaveYetToGetFromThisPeer), 'from this node in particular. Ignoring the rest of this inv message.'
                    break
                self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware[item] = 0 # helps us keep from sending inv messages to peers that already know about the objects listed therein
                self.objectsThatWeHaveYetToGetFromThisPeer[item] = 0 # upon finishing dealing with an incoming message, the receiveDataThread will request a random object of from peer out of this data structure. This way if we get multiple inv messages from multiple peers which list mostly the same objects, we will make getdata requests for different random objects from the various peers.
            if len(self.objectsThatWeHaveYetToGetFromThisPeer) > 0:
                shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                    self.peer] = len(self.objectsThatWeHaveYetToGetFromThisPeer)

    # Send a getdata message to our peer to request the object with the given
    # hash
    def sendgetdata(self, hash):
        with shared.printLock:
            print 'sending getdata to retrieve object with hash:', hash.encode('hex')

        payload = '\x01' + hash
        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'getdata\x00\x00\x00\x00\x00'
        headerData += pack('>L', len(
            payload))  # payload length. Note that we add an extra 8 for the nonce.
        headerData += hashlib.sha512(payload).digest()[:4]
        self.sendDataThreadQueue.put((0, 'sendRawData', headerData + payload))


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
            with shared.printLock:
                print 'received getdata request for item:', hash.encode('hex')

            shared.numberOfInventoryLookupsPerformed += 1
            shared.inventoryLock.acquire()
            if hash in shared.inventory:
                objectType, streamNumber, payload, receivedTime, tag = shared.inventory[
                    hash]
                shared.inventoryLock.release()
                self.sendData(objectType, payload)
            else:
                shared.inventoryLock.release()
                queryreturn = sqlQuery(
                    '''select objecttype, payload from inventory where hash=?''',
                    hash)
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
            with shared.printLock:
                print 'sending pubkey'

            headerData += 'pubkey\x00\x00\x00\x00\x00\x00'
        elif objectType == 'getpubkey' or objectType == 'pubkeyrequest':
            with shared.printLock:
                print 'sending getpubkey'

            headerData += 'getpubkey\x00\x00\x00'
        elif objectType == 'msg':
            with shared.printLock:
                print 'sending msg'

            headerData += 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        elif objectType == 'broadcast':
            with shared.printLock:
                print 'sending broadcast'

            headerData += 'broadcast\x00\x00\x00'
        else:
            sys.stderr.write(
                'Error: sendData has been asked to send a strange objectType: %s\n' % str(objectType))
            return
        headerData += pack('>L', len(payload))  # payload length.
        headerData += hashlib.sha512(payload).digest()[:4]
        self.sendDataThreadQueue.put((0, 'sendRawData', headerData + payload))


    # Advertise this object to all of our peers
    """def broadcastinv(self, hash):
        with shared.printLock:
            print 'broadcasting inv with hash:', hash.encode('hex')

        shared.broadcastToSendDataQueues((self.streamNumber, 'advertiseobject', hash))
    """
    # We have received an addr message.
    def recaddr(self, data):
        #listOfAddressDetailsToBroadcastToPeers = []
        numberOfAddressesIncluded = 0
        numberOfAddressesIncluded, lengthOfNumberOfAddresses = decodeVarint(
            data[:10])

        if shared.verbose >= 1:
            with shared.printLock:
                print 'addr message contains', numberOfAddressesIncluded, 'IP addresses.'

        if numberOfAddressesIncluded > 1000 or numberOfAddressesIncluded == 0:
            return
        if len(data) != lengthOfNumberOfAddresses + (38 * numberOfAddressesIncluded):
            print 'addr message does not contain the correct amount of data. Ignoring.'
            return

        for i in range(0, numberOfAddressesIncluded):
            try:
                if data[20 + lengthOfNumberOfAddresses + (38 * i):32 + lengthOfNumberOfAddresses + (38 * i)] != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                    with shared.printLock:
                       print 'Skipping IPv6 address.', repr(data[20 + lengthOfNumberOfAddresses + (38 * i):32 + lengthOfNumberOfAddresses + (38 * i)])
                    continue
            except Exception as err:
                with shared.printLock:
                   sys.stderr.write(
                       'ERROR TRYING TO UNPACK recaddr (to test for an IPv6 address). Message: %s\n' % str(err))
                break  # giving up on unpacking any more. We should still be connected however.

            try:
                recaddrStream, = unpack('>I', data[8 + lengthOfNumberOfAddresses + (
                    38 * i):12 + lengthOfNumberOfAddresses + (38 * i)])
            except Exception as err:
                with shared.printLock:
                   sys.stderr.write(
                       'ERROR TRYING TO UNPACK recaddr (recaddrStream). Message: %s\n' % str(err))
                break  # giving up on unpacking any more. We should still be connected however.
            if recaddrStream == 0:
                continue
            if recaddrStream != self.streamNumber and recaddrStream != (self.streamNumber * 2) and recaddrStream != ((self.streamNumber * 2) + 1):  # if the embedded stream number is not in my stream or either of my child streams then ignore it. Someone might be trying funny business.
                continue
            try:
                recaddrServices, = unpack('>Q', data[12 + lengthOfNumberOfAddresses + (
                    38 * i):20 + lengthOfNumberOfAddresses + (38 * i)])
            except Exception as err:
                with shared.printLock:
                   sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrServices). Message: %s\n' % str(err))
                break  # giving up on unpacking any more. We should still be connected however.

            try:
                recaddrPort, = unpack('>H', data[36 + lengthOfNumberOfAddresses + (
                    38 * i):38 + lengthOfNumberOfAddresses + (38 * i)])
            except Exception as err:
                with shared.printLock:
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrPort). Message: %s\n' % str(err))
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
            peerFromAddrMessage = shared.Peer(hostFromAddrMessage, recaddrPort)
            if peerFromAddrMessage not in shared.knownNodes[recaddrStream]:
                if len(shared.knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time()) - 10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800):  # If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                    shared.knownNodesLock.acquire()
                    shared.knownNodes[recaddrStream][peerFromAddrMessage] = (
                        timeSomeoneElseReceivedMessageFromThisNode)
                    shared.knownNodesLock.release()
                    with shared.printLock:
                        print 'added new node', peerFromAddrMessage, 'to knownNodes in stream', recaddrStream

                    shared.needToWriteKnownNodesToDisk = True
                    hostDetails = (
                        timeSomeoneElseReceivedMessageFromThisNode,
                        recaddrStream, recaddrServices, hostFromAddrMessage, recaddrPort)
                    #listOfAddressDetailsToBroadcastToPeers.append(hostDetails)
                    shared.broadcastToSendDataQueues((
                        self.streamNumber, 'advertisepeer', hostDetails))
            else:
                timeLastReceivedMessageFromThisNode = shared.knownNodes[recaddrStream][
                    peerFromAddrMessage]  # PORT in this case is either the port we used to connect to the remote node, or the port that was specified by someone else in a past addr message.
                if (timeLastReceivedMessageFromThisNode < timeSomeoneElseReceivedMessageFromThisNode) and (timeSomeoneElseReceivedMessageFromThisNode < int(time.time())):
                    shared.knownNodesLock.acquire()
                    shared.knownNodes[recaddrStream][peerFromAddrMessage] = timeSomeoneElseReceivedMessageFromThisNode
                    shared.knownNodesLock.release()

        #if listOfAddressDetailsToBroadcastToPeers != []:
        #    self.broadcastaddr(listOfAddressDetailsToBroadcastToPeers)
        with shared.printLock:
            print 'knownNodes currently has', len(shared.knownNodes[self.streamNumber]), 'nodes for this stream.'


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
                peer, = random.sample(shared.knownNodes[self.streamNumber], 1)
                if helper_generic.isHostInPrivateIPRange(peer.host):
                    continue
                addrsInMyStream[peer] = shared.knownNodes[
                    self.streamNumber][peer]
        if len(shared.knownNodes[self.streamNumber * 2]) > 0:
            for i in range(250):
                peer, = random.sample(shared.knownNodes[
                                      self.streamNumber * 2], 1)
                if helper_generic.isHostInPrivateIPRange(peer.host):
                    continue
                addrsInChildStreamLeft[peer] = shared.knownNodes[
                    self.streamNumber * 2][peer]
        if len(shared.knownNodes[(self.streamNumber * 2) + 1]) > 0:
            for i in range(250):
                peer, = random.sample(shared.knownNodes[
                                      (self.streamNumber * 2) + 1], 1)
                if helper_generic.isHostInPrivateIPRange(peer.host):
                    continue
                addrsInChildStreamRight[peer] = shared.knownNodes[
                    (self.streamNumber * 2) + 1][peer]
        shared.knownNodesLock.release()
        numberOfAddressesInAddrMessage = 0
        payload = ''
        # print 'addrsInMyStream.items()', addrsInMyStream.items()
        for (HOST, PORT), value in addrsInMyStream.items():
            timeLastReceivedMessageFromThisNode = value
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
        for (HOST, PORT), value in addrsInChildStreamLeft.items():
            timeLastReceivedMessageFromThisNode = value
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
        for (HOST, PORT), value in addrsInChildStreamRight.items():
            timeLastReceivedMessageFromThisNode = value
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
        self.sendDataThreadQueue.put((0, 'sendRawData', datatosend))


    # We have received a version message
    def recversion(self, data):
        if len(data) < 83:
            # This version message is unreasonably short. Forget it.
            return
        elif not self.verackSent:
            self.remoteProtocolVersion, = unpack('>L', data[:4])
            if self.remoteProtocolVersion <= 1:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.peer))
                with shared.printLock:
                    print 'Closing connection to old protocol version 1 node: ', self.peer
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
            with shared.printLock:
                print 'Remote node useragent:', useragent, '  stream number:', self.streamNumber

            if self.streamNumber != 1:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.peer))
                with shared.printLock:
                    print 'Closed connection to', self.peer, 'because they are interested in stream', self.streamNumber, '.'
                return
            shared.connectedHostsList[
                self.peer.host] = 1  # We use this data structure to not only keep track of what hosts we are connected to so that we don't try to connect to them again, but also to list the connections count on the Network Status tab.
            # If this was an incoming connection, then the sendData thread
            # doesn't know the stream. We have to set it.
            if not self.initiatedConnection:
                shared.broadcastToSendDataQueues((
                    0, 'setStreamNumber', (self.peer, self.streamNumber)))
            if data[72:80] == shared.eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.peer))
                with shared.printLock:
                    print 'Closing connection to myself: ', self.peer
                return
            self.sendDataThreadQueue.put((0, 'setRemoteProtocolVersion', self.remoteProtocolVersion))

            shared.knownNodesLock.acquire()
            shared.knownNodes[self.streamNumber][shared.Peer(self.peer.host, self.remoteNodeIncomingPort)] = int(time.time())
            shared.needToWriteKnownNodesToDisk = True
            shared.knownNodesLock.release()

            self.sendverack()
            if self.initiatedConnection == False:
                self.sendversion()

    # Sends a version message
    def sendversion(self):
        with shared.printLock:
            print 'Sending version message'
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.assembleVersionMessage(
                self.peer.host, self.peer.port, self.streamNumber)))


    # Sends a verack message
    def sendverack(self):
        with shared.printLock:
            print 'Sending verack'
        self.sendDataThreadQueue.put((0, 'sendRawData', '\xE9\xBE\xB4\xD9\x76\x65\x72\x61\x63\x6B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35'))
        self.verackSent = True
        if self.verackReceived:
            self.connectionFullyEstablished()
