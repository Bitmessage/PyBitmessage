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
from helper_generic import addDataPadding, isHostInPrivateIPRange
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
        if len(self.data) < shared.Header.size:  # if so little of the data has arrived that we can't even read the checksum then wait for more data.
            return
        #Use a memoryview so we don't copy data unnecessarily
        view = memoryview(self.data)
        magic,command,payloadLength,checksum = shared.Header.unpack(view[:shared.Header.size])
        view = view[shared.Header.size:]
        if magic != 0xE9BEB4D9:
            #if shared.verbose >= 1:
            #    with shared.printLock:
            #        print 'The magic bytes were not correct. First 40 bytes of data: ' + repr(self.data[0:40])

            self.data = ""
            return
        if payloadLength > 20000000:
            logger.info('The incoming message, which we have not yet download, is too large. Ignoring it. (unfortunately there is no way to tell the other node to stop sending it except to disconnect.) Message size: %s' % payloadLength)
            self.data = view[payloadLength:].tobytes()
            del view,magic,command,payloadLength,checksum # we don't need these anymore and better to clean them now before the recursive call rather than after
            self.processData()
            return
        if len(view) < payloadLength:  # check if the whole message has arrived yet.
            return
        payload = view[:payloadLength]
        if checksum != hashlib.sha512(payload).digest()[0:4]:  # test the checksum in the message.
            print 'Checksum incorrect. Clearing this message.'
            self.data = view[payloadLength:].tobytes()
            del view,magic,command,payloadLength,checksum,payload #again better to clean up before the recursive call
            self.processData()
            return
        
        #We can now revert back to bytestrings and take this message out
        payload = payload.tobytes()
        self.data = view[payloadLength:].tobytes()
        del view,magic,payloadLength,checksum
        # The time we've last seen this node is obviously right now since we
        # just received valid data from it. So update the knownNodes list so
        # that other peers can be made aware of its existance.
        if self.initiatedConnection and self.connectionIsOrWasFullyEstablished:  # The remote port is only something we should share with others if it is the remote node's incoming port (rather than some random operating-system-assigned outgoing port).
            shared.knownNodesLock.acquire()
            shared.knownNodes[self.streamNumber][self.peer] = int(time.time())
            shared.knownNodesLock.release()
        
        #Strip the nulls
        command = command.rstrip('\x00')
        with shared.printLock:
            print 'remoteCommand', repr(command), ' from', self.peer
        
        #TODO: Use a dispatcher here
        if not self.connectionIsOrWasFullyEstablished:
            if command == 'version':
                self.recversion(payload)
            elif command == 'verack':
                self.recverack()
        else:
            if command == 'addr':
                self.recaddr(payload)
            elif command == 'getpubkey':
                shared.checkAndSharegetpubkeyWithPeers(payload)
            elif command == 'pubkey':
                self.recpubkey(payload)
            elif command == 'inv':
                self.recinv(payload)
            elif command == 'getdata':
                self.recgetdata(payload)
            elif command == 'msg':
                self.recmsg(payload)
            elif command == 'broadcast':
                self.recbroadcast(payload)
            elif command == 'ping':
                self.sendpong(payload)
            #elif command == 'pong':
            #    pass
            #elif command == 'alert':
            #    pass

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
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('pong')))


    def recverack(self):
        print 'verack received'
        self.verackReceived = True
        if self.verackSent:
            # We have thus both sent and received a verack.
            self.connectionFullyEstablished()

    def connectionFullyEstablished(self):
        if self.connectionIsOrWasFullyEstablished:
            # there is no reason to run this function a second time
            return
        self.connectionIsOrWasFullyEstablished = True
        # Command the corresponding sendDataThread to set its own connectionIsOrWasFullyEstablished variable to True also
        self.sendDataThreadQueue.put((0, 'connectionIsOrWasFullyEstablished', 'no data'))
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
            if numberOfObjectsInInvMessage == 50000:  # We can only send a max of 50000 items per inv message but we may have more objects to advertise. They must be split up into multiple inv messages.
                self.sendinvMessageToJustThisOnePeer(
                    numberOfObjectsInInvMessage, payload)
                payload = ''
                numberOfObjectsInInvMessage = 0
        if numberOfObjectsInInvMessage > 0:
            self.sendinvMessageToJustThisOnePeer(
                numberOfObjectsInInvMessage, payload)

    # Used to send a big inv message when the connection with a node is 
    # first fully established. Notice that there is also a broadcastinv 
    # function for broadcasting invs to everyone in our stream.
    def sendinvMessageToJustThisOnePeer(self, numberOfObjects, payload):
        payload = encodeVarint(numberOfObjects) + payload
        with shared.printLock:
            print 'Sending huge inv message with', numberOfObjects, 'objects to just this one peer'
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('inv', payload)))

    def _sleepForTimingAttackMitigation(self, sleepTime):
        # We don't need to do the timing attack mitigation if we are
        # only connected to the trusted peer because we can trust the
        # peer not to attack
        if sleepTime > 0 and doTimingAttackMitigation and shared.trustedPeer == None:
            with shared.printLock:
                print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            time.sleep(sleepTime)

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
        self._sleepForTimingAttackMitigation(sleepTime)

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
        self._sleepForTimingAttackMitigation(sleepTime)

    # We have received a pubkey
    def recpubkey(self, data):
        self.pubkeyProcessingStartTime = time.time()

        shared.checkAndSharePubkeyWithPeers(data)

        lengthOfTimeWeShouldUseToProcessThisMessage = .1
        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - \
            (time.time() - self.pubkeyProcessingStartTime)
        self._sleepForTimingAttackMitigation(sleepTime)

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
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('getdata', payload)))


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
        if (objectType != 'pubkey' and
              objectType != 'getpubkey' and
              objectType != 'msg' and
              objectType != 'broadcast'):
            sys.stderr.write(
                'Error: sendData has been asked to send a strange objectType: %s\n' % str(objectType))
            return
        with shared.printLock:
            print 'sending', objectType
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket(objectType, payload)))


    def _checkIPv4Address(self, host, hostFromAddrMessage):
        # print 'hostFromAddrMessage', hostFromAddrMessage
        if host[0] == '\x7F':
            print 'Ignoring IP address in loopback range:', hostFromAddrMessage
            return False
        if host[0] == '\x0A':
            print 'Ignoring IP address in private range:', hostFromAddrMessage
            return False
        if host[0:2] == '\xC0\xA8':
            print 'Ignoring IP address in private range:', hostFromAddrMessage
            return False
        return True

    def _checkIPv6Address(self, host, hostFromAddrMessage):
        if host == ('\x00' * 15) + '\x01':
            print 'Ignoring loopback address:', hostFromAddrMessage
            return False
        if host[0] == '\xFE' and (ord(host[1]) & 0xc0) == 0x80:
            print 'Ignoring local address:', hostFromAddrMessage
            return False
        if (ord(host[0]) & 0xfe) == 0xfc:
            print 'Ignoring unique local address:', hostFromAddrMessage
            return False
        return True

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
                fullHost = data[20 + lengthOfNumberOfAddresses + (38 * i):36 + lengthOfNumberOfAddresses + (38 * i)]
            except Exception as err:
                with shared.printLock:
                   sys.stderr.write(
                       'ERROR TRYING TO UNPACK recaddr (recaddrHost). Message: %s\n' % str(err))
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
            if fullHost[0:12] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                ipv4Host = fullHost[12:]
                hostFromAddrMessage = socket.inet_ntop(socket.AF_INET, ipv4Host)
                if not self._checkIPv4Address(ipv4Host, hostFromAddrMessage):
                    continue
            else:
                hostFromAddrMessage = socket.inet_ntop(socket.AF_INET6, fullHost)
                if hostFromAddrMessage == "":
                    # This can happen on Windows systems which are not 64-bit compatible 
                    # so let us drop the IPv6 address. 
                    continue
                if not self._checkIPv6Address(fullHost, hostFromAddrMessage):
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


    # Send a huge addr message to our peer. This is only used 
    # when we fully establish a connection with a 
    # peer (with the full exchange of version and verack 
    # messages).
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
                if isHostInPrivateIPRange(peer.host):
                    continue
                addrsInMyStream[peer] = shared.knownNodes[
                    self.streamNumber][peer]
        if len(shared.knownNodes[self.streamNumber * 2]) > 0:
            for i in range(250):
                peer, = random.sample(shared.knownNodes[
                                      self.streamNumber * 2], 1)
                if isHostInPrivateIPRange(peer.host):
                    continue
                addrsInChildStreamLeft[peer] = shared.knownNodes[
                    self.streamNumber * 2][peer]
        if len(shared.knownNodes[(self.streamNumber * 2) + 1]) > 0:
            for i in range(250):
                peer, = random.sample(shared.knownNodes[
                                      (self.streamNumber * 2) + 1], 1)
                if isHostInPrivateIPRange(peer.host):
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
                payload += shared.encodeHost(HOST)
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
                payload += shared.encodeHost(HOST)
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
                payload += shared.encodeHost(HOST)
                payload += pack('>H', PORT)  # remote port

        payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('addr', payload)))


    # We have received a version message
    def recversion(self, data):
        if len(data) < 83:
            # This version message is unreasonably short. Forget it.
            return
        if self.verackSent:
            """
            We must have already processed the remote node's version message.
            There might be a time in the future when we Do want to process
            a new version message, like if the remote node wants to update
            the streams in which they are interested. But for now we'll
            ignore this version message
            """ 
            return
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
            self.sendDataThreadQueue.put((0, 'setStreamNumber', self.streamNumber))
        if data[72:80] == shared.eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
            shared.broadcastToSendDataQueues((0, 'shutdown', self.peer))
            with shared.printLock:
                print 'Closing connection to myself: ', self.peer
            return
        
        # The other peer's protocol version is of interest to the sendDataThread but we learn of it
        # in this version message. Let us inform the sendDataThread.
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
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('verack')))
        self.verackSent = True
        if self.verackReceived:
            self.connectionFullyEstablished()
