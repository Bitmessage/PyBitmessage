doTimingAttackMitigation = True

import time
import threading
import shared
import hashlib
import socket
import random
from struct import unpack, pack
import sys
import traceback
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
            print 'receiveDataThread starting. ID', str(id(self)) + '. The size of the shared.connectedHostsList is now', len(shared.connectedHostsList)

        while True:
            if shared.config.getint('bitmessagesettings', 'maxdownloadrate') == 0:
                downloadRateLimitBytes = float("inf")
            else:
                downloadRateLimitBytes = shared.config.getint('bitmessagesettings', 'maxdownloadrate') * 1000
            with shared.receiveDataLock:
                while shared.numberOfBytesReceivedLastSecond >= downloadRateLimitBytes:
                    if int(time.time()) == shared.lastTimeWeResetBytesReceived:
                        # If it's still the same second that it was last time then sleep.
                        time.sleep(0.3)
                    else:
                        # It's a new second. Let us clear the shared.numberOfBytesReceivedLastSecond.
                        shared.lastTimeWeResetBytesReceived = int(time.time())
                        shared.numberOfBytesReceivedLastSecond = 0
            dataLen = len(self.data)
            try:
                dataRecv = self.sock.recv(1024)
                self.data += dataRecv
                shared.numberOfBytesReceived += len(dataRecv) # for the 'network status' UI tab. The UI clears this value whenever it updates.
                shared.numberOfBytesReceivedLastSecond += len(dataRecv) # for the download rate limit
            except socket.timeout:
                with shared.printLock:
                    print 'Timeout occurred waiting for data from', self.peer, '. Closing receiveData thread. (ID:', str(id(self)) + ')'
                break
            except Exception as err:
                with shared.printLock:
                    print 'sock.recv error. Closing receiveData thread (' + str(self.peer) + ', Thread ID:', str(id(self)) + ').', err
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
        self.sendDataThreadQueue.put((0, 'shutdown','no data')) # commands the corresponding sendDataThread to shut itself down.
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
            print 'receiveDataThread ending. ID', str(id(self)) + '. The size of the shared.connectedHostsList is now', len(shared.connectedHostsList)


    def processData(self):
        if len(self.data) < shared.Header.size:  # if so little of the data has arrived that we can't even read the checksum then wait for more data.
            return
        
        magic,command,payloadLength,checksum = shared.Header.unpack(self.data[:shared.Header.size])
        if magic != 0xE9BEB4D9:
            self.data = ""
            return
        if payloadLength > 1600100: # ~1.6 MB which is the maximum possible size of an inv message.
            logger.info('The incoming message, which we have not yet download, is too large. Ignoring it. (unfortunately there is no way to tell the other node to stop sending it except to disconnect.) Message size: %s' % payloadLength)
            self.data = self.data[payloadLength + shared.Header.size:]
            del magic,command,payloadLength,checksum # we don't need these anymore and better to clean them now before the recursive call rather than after
            self.processData()
            return
        if len(self.data) < payloadLength + shared.Header.size:  # check if the whole message has arrived yet.
            return
        payload = self.data[shared.Header.size:payloadLength + shared.Header.size]
        if checksum != hashlib.sha512(payload).digest()[0:4]:  # test the checksum in the message.
            print 'Checksum incorrect. Clearing this message.'
            self.data = self.data[payloadLength + shared.Header.size:]
            del magic,command,payloadLength,checksum,payload # better to clean up before the recursive call
            self.processData()
            return

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
        
        try:
            #TODO: Use a dispatcher here
            if command == 'error':
                self.recerror(payload)
            elif not self.connectionIsOrWasFullyEstablished:
                if command == 'version':
                    self.recversion(payload)
                elif command == 'verack':
                    self.recverack()
            else:
                if command == 'addr':
                    self.recaddr(payload)
                elif command == 'inv':
                    self.recinv(payload)
                elif command == 'getdata':
                    self.recgetdata(payload)
                elif command == 'object':
                    self.recobject(payload)
                elif command == 'ping':
                    self.sendpong(payload)
                #elif command == 'pong':
                #    pass
        except varintDecodeError as e:
            logger.debug("There was a problem with a varint while processing a message from the wire. Some details: %s" % e)
        except Exception as e:
            logger.critical("Critical error in a receiveDataThread: \n%s" % traceback.format_exc())
        
        del payload
        self.data = self.data[payloadLength + shared.Header.size:] # take this message out and then process the next message

        if self.data == '': # if there are no more messages
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
                    # We don't have the object in our inventory. Let's request it.
                    self.sendgetdata(objectHash)
                    del self.objectsThatWeHaveYetToGetFromThisPeer[
                        objectHash]  # It is possible that the remote node might not respond with the object. In that case, we'll very likely get it from someone else anyway.
                    if len(self.objectsThatWeHaveYetToGetFromThisPeer) == 0:
                        with shared.printLock:
                            print '(concerning', str(self.peer) + ')', 'number of objectsThatWeHaveYetToGetFromThisPeer is now 0'
                        try:
                            del shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                                self.peer]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                        except:
                            pass
                    break
                if len(self.objectsThatWeHaveYetToGetFromThisPeer) == 0:
                    # We had objectsThatWeHaveYetToGetFromThisPeer but the loop ran, they were all in our inventory, and now we don't have any to get anymore.
                    with shared.printLock:
                        print '(concerning', str(self.peer) + ')', 'number of objectsThatWeHaveYetToGetFromThisPeer is now 0'
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
        with shared.printLock:
            print 'Sending pong'
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('pong')))


    def recverack(self):
        with shared.printLock:
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

            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            return
        self.sendBigInv()

    def sendBigInv(self):
        # Select all hashes for objects in this stream.
        queryreturn = sqlQuery(
            '''SELECT hash FROM inventory WHERE expirestime>? and streamnumber=?''',
            int(time.time()),
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
                    objectType, streamNumber, payload, expiresTime, tag = storedValue
                    if streamNumber == self.streamNumber and expiresTime > int(time.time()):
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
            
    def recerror(self, data):
        """
        The remote node has been polite enough to send you an error message.
        """
        fatalStatus, readPosition = decodeVarint(data[:10])
        banTime, banTimeLength = decodeVarint(data[readPosition:readPosition+10])
        readPosition += banTimeLength
        inventoryVectorLength, inventoryVectorLengthLength = decodeVarint(data[readPosition:readPosition+10])
        if inventoryVectorLength > 100:
            return
        readPosition += inventoryVectorLengthLength
        inventoryVector = data[readPosition:readPosition+inventoryVectorLength]
        readPosition += inventoryVectorLength
        errorTextLength, errorTextLengthLength = decodeVarint(data[readPosition:readPosition+10])
        if errorTextLength > 1000:
            return 
        readPosition += errorTextLengthLength
        errorText = data[readPosition:readPosition+errorTextLength]
        if fatalStatus == 0:
            fatalHumanFriendly = 'Warning'
        elif fatalStatus == 1:
            fatalHumanFriendly = 'Error'
        elif fatalStatus == 2:
            fatalHumanFriendly = 'Fatal'
        message = '%s message received from %s: %s.' % (fatalHumanFriendly, self.peer, errorText)
        if inventoryVector:
            message += " This concerns object %s" % inventoryVector.encode('hex')
        if banTime > 0:
            message += " Remote node says that the ban time is %s" % banTime
        logger.error(message)


    def recobject(self, data):
        self.messageProcessingStartTime = time.time()
        lengthOfTimeWeShouldUseToProcessThisMessage = shared.checkAndShareObjectWithPeers(data)
        
        """
        Sleeping will help guarantee that we can process messages faster than a 
        remote node can send them. If we fall behind, the attacker could observe 
        that we are are slowing down the rate at which we request objects from the
        network which would indicate that we own a particular address (whichever
        one to which they are sending all of their attack messages). Note
        that if an attacker connects to a target with many connections, this
        mitigation mechanism might not be sufficient.
        """
        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - (time.time() - self.messageProcessingStartTime)
        self._sleepForTimingAttackMitigation(sleepTime)
    

    # We have received an inv message
    def recinv(self, data):
        totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers = 0  # this counts duplicates separately because they take up memory
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
                objectType, streamNumber, payload, expiresTime, tag = shared.inventory[hash]
                shared.inventoryLock.release()
                self.sendObject(payload)
            else:
                shared.inventoryLock.release()
                queryreturn = sqlQuery(
                    '''select payload from inventory where hash=? and expirestime>=?''',
                    hash,
                    int(time.time()))
                if queryreturn != []:
                    for row in queryreturn:
                        payload, = row
                    self.sendObject(payload)
                else:
                    logger.warning('%s asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. We probably cleaned it out after advertising it but before they got around to asking for it.' % self.peer)

    # Our peer has requested (in a getdata message) that we send an object.
    def sendObject(self, payload):
        with shared.printLock:
            print 'sending an object.'
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('object',payload)))


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
        if self.remoteProtocolVersion < 3:
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            with shared.printLock:
                print 'Closing connection to old protocol version',  self.remoteProtocolVersion, 'node: ', self.peer
            return
        timestamp, = unpack('>Q', data[12:20])
        timeOffset = timestamp - int(time.time())
        if timeOffset > 3600:
            self.sendDataThreadQueue.put((0, 'sendRawData', shared.assembleErrorMessage(fatal=2, errorText="Your time is too far in the future compared to mine. Closing connection.")))
            logger.info("%s's time is too far in the future (%s seconds). Closing connection to it." % (self.peer, timeOffset))
            time.sleep(2)
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            return
        if timeOffset < -3600:
            self.sendDataThreadQueue.put((0, 'sendRawData', shared.assembleErrorMessage(fatal=2, errorText="Your time is too far in the past compared to mine. Closing connection.")))
            logger.info("%s's time is too far in the past (timeOffset %s seconds). Closing connection to it." % (self.peer, timeOffset))
            time.sleep(2)
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            return 
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
            print 'Remote node useragent:', useragent, '  stream number:', self.streamNumber, '  time offset:', timeOffset, 'seconds.'

        if self.streamNumber != 1:
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            with shared.printLock:
                print 'Closed connection to', self.peer, 'because they are interested in stream', self.streamNumber, '.'
            return
        shared.connectedHostsList[
            self.peer.host] = 1  # We use this data structure to not only keep track of what hosts we are connected to so that we don't try to connect to them again, but also to list the connections count on the Network Status tab.
        # If this was an incoming connection, then the sendDataThread
        # doesn't know the stream. We have to set it.
        if not self.initiatedConnection:
            self.sendDataThreadQueue.put((0, 'setStreamNumber', self.streamNumber))
        if data[72:80] == shared.eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
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
