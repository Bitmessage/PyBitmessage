doTimingAttackMitigation = False

import base64
import datetime
import errno
import math
import time
import threading
import shared
import hashlib
import os
import select
import socket
import random
import ssl
from struct import unpack, pack
import sys
import traceback
from binascii import hexlify
#import string
#from subprocess import call  # used when the API must execute an outside program
#from pyelliptic.openssl import OpenSSL

#import highlevelcrypto
from addresses import *
from class_objectHashHolder import objectHashHolder
from helper_generic import addDataPadding, isHostInPrivateIPRange
from helper_sql import sqlQuery
from debug import logger
import tr

# This thread is created either by the synSenderThread(for outgoing
# connections) or the singleListenerThread(for incoming connections).

class receiveDataThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name="receiveData")
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
        sendDataThreadQueue,
        objectHashHolderInstance):
        
        self.sock = sock
        self.peer = shared.Peer(HOST, port)
        self.name = "receiveData-" + self.peer.host.replace(":", ".") # ":" log parser field separator
        self.streamNumber = streamNumber
        self.objectsThatWeHaveYetToGetFromThisPeer = {}
        self.selfInitiatedConnections = selfInitiatedConnections
        self.sendDataThreadQueue = sendDataThreadQueue # used to send commands and data to the sendDataThread
        self.hostIdent = self.peer.port if ".onion" in shared.config.get('bitmessagesettings', 'onionhostname') and shared.checkSocksIP(self.peer.host) else self.peer.host
        shared.connectedHostsList[
            self.hostIdent] = 0  # The very fact that this receiveData thread exists shows that we are connected to the remote host. Let's add it to this list so that an outgoingSynSender thread doesn't try to connect to it.
        self.connectionIsOrWasFullyEstablished = False  # set to true after the remote node and I accept each other's version messages. This is needed to allow the user interface to accurately reflect the current number of connections.
        self.services = 0
        if self.streamNumber == -1:  # This was an incoming connection. Send out a version message if we accept the other node's version message.
            self.initiatedConnection = False
        else:
            self.initiatedConnection = True
            self.selfInitiatedConnections[streamNumber][self] = 0
        self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware = someObjectsOfWhichThisRemoteNodeIsAlreadyAware
        self.objectHashHolderInstance = objectHashHolderInstance
        self.startTime = time.time()

    def run(self):
        logger.debug('receiveDataThread starting. ID ' + str(id(self)) + '. The size of the shared.connectedHostsList is now ' + str(len(shared.connectedHostsList)))

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
                ssl = False
                if ((self.services & shared.NODE_SSL == shared.NODE_SSL) and
                    self.connectionIsOrWasFullyEstablished and
                    shared.haveSSL(not self.initiatedConnection)):
                    ssl = True
                    dataRecv = self.sslSock.recv(1024)
                else:
                    dataRecv = self.sock.recv(1024)
                self.data += dataRecv
                shared.numberOfBytesReceived += len(dataRecv) # for the 'network status' UI tab. The UI clears this value whenever it updates.
                shared.numberOfBytesReceivedLastSecond += len(dataRecv) # for the download rate limit
            except socket.timeout:
                logger.error ('Timeout occurred waiting for data from ' + str(self.peer) + '. Closing receiveData thread. (ID: ' + str(id(self)) + ')')
                break
            except Exception as err:
                if err.errno == 2 or (sys.platform == 'win32' and err.errno == 10035) or (sys.platform != 'win32' and err.errno == errno.EWOULDBLOCK):
                    if ssl:
                        select.select([self.sslSock], [], [])
                    else:
                        select.select([self.sock], [], [])
                    continue
                logger.error('sock.recv error. Closing receiveData thread (' + str(self.peer) + ', Thread ID: ' + str(id(self)) + ').' + str(err.errno) + "/" + str(err))
                if self.initiatedConnection and not self.connectionIsOrWasFullyEstablished:
                    shared.timeOffsetWrongCount += 1
                break
            # print 'Received', repr(self.data)
            if len(self.data) == dataLen: # If self.sock.recv returned no data:
                logger.debug('Connection to ' + str(self.peer) + ' closed. Closing receiveData thread. (ID: ' + str(id(self)) + ')')
                if self.initiatedConnection and not self.connectionIsOrWasFullyEstablished:
                    shared.timeOffsetWrongCount += 1
                break
            else:
                self.processData()

        try:
            del self.selfInitiatedConnections[self.streamNumber][self]
            logger.debug('removed self (a receiveDataThread) from selfInitiatedConnections')
        except:
            pass
        self.sendDataThreadQueue.put((0, 'shutdown','no data')) # commands the corresponding sendDataThread to shut itself down.
        try:
            del shared.connectedHostsList[self.hostIdent]
        except Exception as err:
            logger.error('Could not delete ' + str(self.hostIdent) + ' from shared.connectedHostsList.' + str(err))

        try:
            del shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                self.peer]
        except:
            pass
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        self.checkTimeOffsetNotification()
        logger.debug('receiveDataThread ending. ID ' + str(id(self)) + '. The size of the shared.connectedHostsList is now ' + str(len(shared.connectedHostsList)))

    def antiIntersectionDelay(self, initial = False):
        # estimated time for a small object to propagate across the whole network
        delay = math.ceil(math.log(len(shared.knownNodes[self.streamNumber]) + 2, 20)) * (0.2 + objectHashHolder.size/2)
        # +2 is to avoid problems with log(0) and log(1)
        # 20 is avg connected nodes count
        # 0.2 is avg message transmission time
        now = time.time()
        if initial and now - delay < self.startTime:
            logger.debug("Initial sleeping for %.2fs", delay - (now - self.startTime))
            time.sleep(delay - (now - self.startTime))
        elif not initial:
            logger.debug("Sleeping due to missing object for %.2fs", delay)
            time.sleep(delay)

    def checkTimeOffsetNotification(self):
        if shared.timeOffsetWrongCount >= 4 and not self.connectionIsOrWasFullyEstablished:
            shared.UISignalQueue.put(('updateStatusBar', tr._translate("MainWindow", "The time on your computer, %1, may be wrong. Please verify your settings.").arg(datetime.datetime.now().strftime("%H:%M:%S"))))

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
            logger.error('Checksum incorrect. Clearing this message.')
            self.data = self.data[payloadLength + shared.Header.size:]
            del magic,command,payloadLength,checksum,payload # better to clean up before the recursive call
            self.processData()
            return

        # The time we've last seen this node is obviously right now since we
        # just received valid data from it. So update the knownNodes list so
        # that other peers can be made aware of its existance.
        if self.initiatedConnection and self.connectionIsOrWasFullyEstablished:  # The remote port is only something we should share with others if it is the remote node's incoming port (rather than some random operating-system-assigned outgoing port).
            with shared.knownNodesLock:
                shared.knownNodes[self.streamNumber][self.peer] = int(time.time())
        
        #Strip the nulls
        command = command.rstrip('\x00')
        logger.debug('remoteCommand ' + repr(command) + ' from ' + str(self.peer))
        
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
                    logger.debug('Inventory already has object listed in inv message.')
                    del self.objectsThatWeHaveYetToGetFromThisPeer[objectHash]
                else:
                    # We don't have the object in our inventory. Let's request it.
                    self.sendgetdata(objectHash)
                    del self.objectsThatWeHaveYetToGetFromThisPeer[
                        objectHash]  # It is possible that the remote node might not respond with the object. In that case, we'll very likely get it from someone else anyway.
                    if len(self.objectsThatWeHaveYetToGetFromThisPeer) == 0:
                        logger.debug('(concerning' + str(self.peer) + ') number of objectsThatWeHaveYetToGetFromThisPeer is now 0')
                        try:
                            del shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                                self.peer]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                        except:
                            pass
                    break
                if len(self.objectsThatWeHaveYetToGetFromThisPeer) == 0:
                    # We had objectsThatWeHaveYetToGetFromThisPeer but the loop ran, they were all in our inventory, and now we don't have any to get anymore.
                    logger.debug('(concerning' + str(self.peer) + ') number of objectsThatWeHaveYetToGetFromThisPeer is now 0')
                    try:
                        del shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                            self.peer]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                    except:
                        pass
            if len(self.objectsThatWeHaveYetToGetFromThisPeer) > 0:
                logger.debug('(concerning' + str(self.peer) + ') number of objectsThatWeHaveYetToGetFromThisPeer is now ' + str(len(self.objectsThatWeHaveYetToGetFromThisPeer)))

                shared.numberOfObjectsThatWeHaveYetToGetPerPeer[self.peer] = len(
                    self.objectsThatWeHaveYetToGetFromThisPeer)  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
        self.processData()


    def sendpong(self):
        logger.debug('Sending pong')
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('pong')))


    def recverack(self):
        logger.debug('verack received')
        self.verackReceived = True
        if self.verackSent:
            # We have thus both sent and received a verack.
            self.connectionFullyEstablished()

    def connectionFullyEstablished(self):
        if self.connectionIsOrWasFullyEstablished:
            # there is no reason to run this function a second time
            return
        self.connectionIsOrWasFullyEstablished = True
        shared.timeOffsetWrongCount = 0

        self.sslSock = self.sock
        if ((self.services & shared.NODE_SSL == shared.NODE_SSL) and
            shared.haveSSL(not self.initiatedConnection)):
            logger.debug("Initialising TLS")
            self.sslSock = ssl.wrap_socket(self.sock, keyfile = os.path.join(shared.codePath(), 'sslkeys', 'key.pem'), certfile = os.path.join(shared.codePath(), 'sslkeys', 'cert.pem'), server_side = not self.initiatedConnection, ssl_version=ssl.PROTOCOL_TLSv1, do_handshake_on_connect=False, ciphers='AECDH-AES256-SHA')
            if hasattr(self.sslSock, "context"):
                self.sslSock.context.set_ecdh_curve("secp256k1")
            while True:
                try:
                    self.sslSock.do_handshake()
                    break
                except ssl.SSLError as e:
                    if e.errno == 2:
                        select.select([self.sslSock], [self.sslSock], [])
                    else:
                        break
                except:
                    break
        # Command the corresponding sendDataThread to set its own connectionIsOrWasFullyEstablished variable to True also
        self.sendDataThreadQueue.put((0, 'connectionIsOrWasFullyEstablished', (self.services, self.sslSock)))

        if not self.initiatedConnection:
            shared.clientHasReceivedIncomingConnections = True
            shared.UISignalQueue.put(('setStatusIcon', 'green'))
        self.sock.settimeout(
            600)  # We'll send out a pong every 5 minutes to make sure the connection stays alive if there has been no other traffic to send lately.
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        logger.debug('Connection fully established with ' + str(self.peer) + "\n" + \
            'The size of the connectedHostsList is now ' + str(len(shared.connectedHostsList)) + "\n" + \
            'The length of sendDataQueues is now: ' + str(len(shared.sendDataQueues)) + "\n" + \
            'broadcasting addr from within connectionFullyEstablished function.')

        # Let all of our peers know about this new node.
        dataToSend = (int(time.time()), self.streamNumber, 1, self.peer.host, self.remoteNodeIncomingPort)
        shared.broadcastToSendDataQueues((
            self.streamNumber, 'advertisepeer', dataToSend))

        self.sendaddr()  # This is one large addr message to this one peer.
        if not self.initiatedConnection and len(shared.connectedHostsList) > 200:
            logger.info ('We are connected to too many people. Closing connection.')

            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            return
        self.sendBigInv()

    def sendBigInv(self):
        # Select all hashes for objects in this stream.
        bigInvList = {}
        for hash in shared.inventory.unexpired_hashes_by_stream(self.streamNumber):
            if hash not in self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware and not self.objectHashHolderInstance.hasHash(hash):
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
        logger.debug('Sending huge inv message with ' + str(numberOfObjects) + ' objects to just this one peer')
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('inv', payload)))

    def _sleepForTimingAttackMitigation(self, sleepTime):
        # We don't need to do the timing attack mitigation if we are
        # only connected to the trusted peer because we can trust the
        # peer not to attack
        if sleepTime > 0 and doTimingAttackMitigation and shared.trustedPeer == None:
            logger.debug('Timing attack mitigation: Sleeping for ' + str(sleepTime) + ' seconds.')
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
            message += " This concerns object %s" % hexlify(inventoryVector)
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
            logger.debug('number of keys(hosts) in shared.numberOfObjectsThatWeHaveYetToGetPerPeer: ' + str(len(shared.numberOfObjectsThatWeHaveYetToGetPerPeer)) + "\n" + \
                'totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers = ' + str(totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers))

        numberOfItemsInInv, lengthOfVarint = decodeVarint(data[:10])
        if numberOfItemsInInv > 50000:
            sys.stderr.write('Too many items in inv message!')
            return
        if len(data) < lengthOfVarint + (numberOfItemsInInv * 32):
            logger.info('inv message doesn\'t contain enough data. Ignoring.')
            return
        if numberOfItemsInInv == 1:  # we'll just request this data from the person who advertised the object.
            if totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers > 200000 and len(self.objectsThatWeHaveYetToGetFromThisPeer) > 1000 and shared.trustedPeer == None:  # inv flooding attack mitigation
                logger.debug('We already have ' + str(totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers) + ' items yet to retrieve from peers and over 1000 from this node in particular. Ignoring this inv message.')
                return
            self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware[
                data[lengthOfVarint:32 + lengthOfVarint]] = 0
            shared.numberOfInventoryLookupsPerformed += 1
            if data[lengthOfVarint:32 + lengthOfVarint] in shared.inventory:
                logger.debug('Inventory has inventory item already.')
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
            objectsNewToMe = advertisedSet - shared.inventory.hashes_by_stream(self.streamNumber)
            logger.info('inv message lists %s objects. Of those %s are new to me. It took %s seconds to figure that out.', numberOfItemsInInv, len(objectsNewToMe), time.time()-startTime)
            for item in objectsNewToMe:  
                if totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers > 200000 and len(self.objectsThatWeHaveYetToGetFromThisPeer) > 1000 and shared.trustedPeer == None:  # inv flooding attack mitigation
                    logger.debug('We already have ' + str(totalNumberOfobjectsThatWeHaveYetToGetFromAllPeers) + ' items yet to retrieve from peers and over ' + str(len(self.objectsThatWeHaveYetToGetFromThisPeer)), ' from this node in particular. Ignoring the rest of this inv message.')
                    break
                self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware[item] = 0 # helps us keep from sending inv messages to peers that already know about the objects listed therein
                self.objectsThatWeHaveYetToGetFromThisPeer[item] = 0 # upon finishing dealing with an incoming message, the receiveDataThread will request a random object of from peer out of this data structure. This way if we get multiple inv messages from multiple peers which list mostly the same objects, we will make getdata requests for different random objects from the various peers.
            if len(self.objectsThatWeHaveYetToGetFromThisPeer) > 0:
                shared.numberOfObjectsThatWeHaveYetToGetPerPeer[
                    self.peer] = len(self.objectsThatWeHaveYetToGetFromThisPeer)

    # Send a getdata message to our peer to request the object with the given
    # hash
    def sendgetdata(self, hash):
        logger.debug('sending getdata to retrieve object with hash: ' + hexlify(hash))
        payload = '\x01' + hash
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('getdata', payload)))


    # We have received a getdata request from our peer
    def recgetdata(self, data):
        numberOfRequestedInventoryItems, lengthOfVarint = decodeVarint(
            data[:10])
        if len(data) < lengthOfVarint + (32 * numberOfRequestedInventoryItems):
            logger.debug('getdata message does not contain enough data. Ignoring.')
            return
        self.antiIntersectionDelay(True) # only handle getdata requests if we have been connected long enough
        for i in xrange(numberOfRequestedInventoryItems):
            hash = data[lengthOfVarint + (
                i * 32):32 + lengthOfVarint + (i * 32)]
            logger.debug('received getdata request for item:' + hexlify(hash))

            shared.numberOfInventoryLookupsPerformed += 1
            shared.inventoryLock.acquire()
            if self.objectHashHolderInstance.hasHash(hash):
                shared.inventoryLock.release()
                self.antiIntersectionDelay()
            else:
                shared.inventoryLock.release()
                if hash in shared.inventory:
                    self.sendObject(shared.inventory[hash].payload)
                else:
                    self.antiIntersectionDelay()
                    logger.warning('%s asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. We probably cleaned it out after advertising it but before they got around to asking for it.' % (self.peer,))

    # Our peer has requested (in a getdata message) that we send an object.
    def sendObject(self, payload):
        logger.debug('sending an object.')
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('object',payload)))

    def _checkIPAddress(self, host):
        if host[0:12] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
            hostStandardFormat = socket.inet_ntop(socket.AF_INET, host[12:])
            return self._checkIPv4Address(host[12:], hostStandardFormat)
        elif host[0:6] == '\xfd\x87\xd8\x7e\xeb\x43':
            # Onion, based on BMD/bitcoind
            hostStandardFormat = base64.b32encode(host[6:]).lower() + ".onion"
            return hostStandardFormat
        else:
            hostStandardFormat = socket.inet_ntop(socket.AF_INET6, host)
            if hostStandardFormat == "":
                # This can happen on Windows systems which are not 64-bit compatible 
                # so let us drop the IPv6 address. 
                return False
            return self._checkIPv6Address(host, hostStandardFormat)

    def _checkIPv4Address(self, host, hostStandardFormat):
        if host[0] == '\x7F': # 127/8
            logger.debug('Ignoring IP address in loopback range: ' + hostStandardFormat)
            return False
        if host[0] == '\x0A': # 10/8
            logger.debug('Ignoring IP address in private range: ' + hostStandardFormat)
            return False
        if host[0:2] == '\xC0\xA8': # 192.168/16
            logger.debug('Ignoring IP address in private range: ' + hostStandardFormat)
            return False
        if host[0:2] >= '\xAC\x10' and host[0:2] < '\xAC\x20': # 172.16/12
            logger.debug('Ignoring IP address in private range:' + hostStandardFormat)
            return False
        return hostStandardFormat

    def _checkIPv6Address(self, host, hostStandardFormat):
        if host == ('\x00' * 15) + '\x01':
            logger.debug('Ignoring loopback address: ' + hostStandardFormat)
            return False
        if host[0] == '\xFE' and (ord(host[1]) & 0xc0) == 0x80:
            logger.debug ('Ignoring local address: ' + hostStandardFormat)
            return False
        if (ord(host[0]) & 0xfe) == 0xfc:
            logger.debug ('Ignoring unique local address: ' + hostStandardFormat)
            return False
        return hostStandardFormat

    # We have received an addr message.
    def recaddr(self, data):
        numberOfAddressesIncluded, lengthOfNumberOfAddresses = decodeVarint(
            data[:10])

        if shared.verbose >= 1:
            logger.debug('addr message contains ' + str(numberOfAddressesIncluded) + ' IP addresses.')

        if numberOfAddressesIncluded > 1000 or numberOfAddressesIncluded == 0:
            return
        if len(data) != lengthOfNumberOfAddresses + (38 * numberOfAddressesIncluded):
            logger.debug('addr message does not contain the correct amount of data. Ignoring.')
            return

        for i in range(0, numberOfAddressesIncluded):
            fullHost = data[20 + lengthOfNumberOfAddresses + (38 * i):36 + lengthOfNumberOfAddresses + (38 * i)]
            recaddrStream, = unpack('>I', data[8 + lengthOfNumberOfAddresses + (
                38 * i):12 + lengthOfNumberOfAddresses + (38 * i)])
            if recaddrStream == 0:
                continue
            if recaddrStream != self.streamNumber and recaddrStream != (self.streamNumber * 2) and recaddrStream != ((self.streamNumber * 2) + 1):  # if the embedded stream number is not in my stream or either of my child streams then ignore it. Someone might be trying funny business.
                continue
            recaddrServices, = unpack('>Q', data[12 + lengthOfNumberOfAddresses + (
                38 * i):20 + lengthOfNumberOfAddresses + (38 * i)])
            recaddrPort, = unpack('>H', data[36 + lengthOfNumberOfAddresses + (
                38 * i):38 + lengthOfNumberOfAddresses + (38 * i)])
            hostStandardFormat = self._checkIPAddress(fullHost)
            if hostStandardFormat is False:
                continue
            if recaddrPort == 0:
                continue
            timeSomeoneElseReceivedMessageFromThisNode, = unpack('>Q', data[lengthOfNumberOfAddresses + (
                38 * i):8 + lengthOfNumberOfAddresses + (38 * i)])  # This is the 'time' value in the received addr message. 64-bit.
            if recaddrStream not in shared.knownNodes:  # knownNodes is a dictionary of dictionaries with one outer dictionary for each stream. If the outer stream dictionary doesn't exist yet then we must make it.
                with shared.knownNodesLock:
                    shared.knownNodes[recaddrStream] = {}
            peerFromAddrMessage = shared.Peer(hostStandardFormat, recaddrPort)
            if peerFromAddrMessage not in shared.knownNodes[recaddrStream]:
                if len(shared.knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time()) - 10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800):  # If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                    with shared.knownNodesLock:
                        shared.knownNodes[recaddrStream][peerFromAddrMessage] = timeSomeoneElseReceivedMessageFromThisNode
                    logger.debug('added new node ' + str(peerFromAddrMessage) + ' to knownNodes in stream ' + str(recaddrStream))

                    shared.needToWriteKnownNodesToDisk = True
                    hostDetails = (
                        timeSomeoneElseReceivedMessageFromThisNode,
                        recaddrStream, recaddrServices, hostStandardFormat, recaddrPort)
                    shared.broadcastToSendDataQueues((
                        self.streamNumber, 'advertisepeer', hostDetails))
            else:
                timeLastReceivedMessageFromThisNode = shared.knownNodes[recaddrStream][
                    peerFromAddrMessage]
                if (timeLastReceivedMessageFromThisNode < timeSomeoneElseReceivedMessageFromThisNode) and (timeSomeoneElseReceivedMessageFromThisNode < int(time.time())+900): # 900 seconds for wiggle-room in case other nodes' clocks aren't quite right.
                    with shared.knownNodesLock:
                        shared.knownNodes[recaddrStream][peerFromAddrMessage] = timeSomeoneElseReceivedMessageFromThisNode

        logger.debug('knownNodes currently has ' +  str(len(shared.knownNodes[self.streamNumber])) + ' nodes for this stream.')


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
        with shared.knownNodesLock:
            if len(shared.knownNodes[self.streamNumber]) > 0:
                ownPosition = random.randint(0, 499)
                sentOwn = False
                for i in range(500):
                    # if current connection is over a proxy, sent our own onion address at a random position
                    if ownPosition == i and ".onion" in shared.config.get("bitmessagesettings", "onionhostname") and \
                        hasattr(self.sock, "getproxytype") and self.sock.getproxytype() != "none" and not sentOwn:
                        peer = shared.Peer(shared.config.get("bitmessagesettings", "onionhostname"), shared.config.getint("bitmessagesettings", "onionport"))
                    else:
                    # still may contain own onion address, but we don't change it
                        peer, = random.sample(shared.knownNodes[self.streamNumber], 1)
                    if isHostInPrivateIPRange(peer.host):
                        continue
                    if peer.host == shared.config.get("bitmessagesettings", "onionhostname") and peer.port == shared.config.getint("bitmessagesettings", "onionport") :
                        sentOwn = True
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
        self.services, = unpack('>q', data[4:12])
        if self.remoteProtocolVersion < 3:
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            logger.debug ('Closing connection to old protocol version ' + str(self.remoteProtocolVersion) + ' node: ' + str(self.peer))
            return
        timestamp, = unpack('>Q', data[12:20])
        timeOffset = timestamp - int(time.time())
        if timeOffset > 3600:
            self.sendDataThreadQueue.put((0, 'sendRawData', shared.assembleErrorMessage(fatal=2, errorText="Your time is too far in the future compared to mine. Closing connection.")))
            logger.info("%s's time is too far in the future (%s seconds). Closing connection to it." % (self.peer, timeOffset))
            shared.timeOffsetWrongCount += 1
            time.sleep(2)
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            return
        elif timeOffset < -3600:
            self.sendDataThreadQueue.put((0, 'sendRawData', shared.assembleErrorMessage(fatal=2, errorText="Your time is too far in the past compared to mine. Closing connection.")))
            logger.info("%s's time is too far in the past (timeOffset %s seconds). Closing connection to it." % (self.peer, timeOffset))
            shared.timeOffsetWrongCount += 1
            time.sleep(2)
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            return 
        else:
            shared.timeOffsetWrongCount = 0
        self.checkTimeOffsetNotification()

        self.myExternalIP = socket.inet_ntoa(data[40:44])
        # print 'myExternalIP', self.myExternalIP
        self.remoteNodeIncomingPort, = unpack('>H', data[70:72])
        # print 'remoteNodeIncomingPort', self.remoteNodeIncomingPort
        useragentLength, lengthOfUseragentVarint = decodeVarint(
            data[80:84])
        readPosition = 80 + lengthOfUseragentVarint
        useragent = data[readPosition:readPosition + useragentLength]
        
        # version check
        try:
            userAgentName, userAgentVersion = useragent[1:-1].split(":", 2)
        except:
            userAgentName = useragent
            userAgentVersion = "0.0.0"
        if userAgentName == "PyBitmessage":
            myVersion = [int(n) for n in shared.softwareVersion.split(".")]
            try:
                remoteVersion = [int(n) for n in userAgentVersion.split(".")]
            except:
                remoteVersion = 0
            # remote is newer, but do not cross between stable and unstable
            try:
                if cmp(remoteVersion, myVersion) > 0 and \
                    (myVersion[1] % 2 == remoteVersion[1] % 2):
                    shared.UISignalQueue.put(('newVersionAvailable', remoteVersion))
            except:
                pass
                
        readPosition += useragentLength
        numberOfStreamsInVersionMessage, lengthOfNumberOfStreamsInVersionMessage = decodeVarint(
            data[readPosition:])
        readPosition += lengthOfNumberOfStreamsInVersionMessage
        self.streamNumber, lengthOfRemoteStreamNumber = decodeVarint(
            data[readPosition:])
        logger.debug('Remote node useragent: ' + useragent + '  stream number:' + str(self.streamNumber) + '  time offset: ' + str(timeOffset) + ' seconds.')

        if self.streamNumber != 1:
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            logger.debug ('Closed connection to ' + str(self.peer) + ' because they are interested in stream ' + str(self.streamNumber) + '.')
            return
        shared.connectedHostsList[
            self.hostIdent] = 1  # We use this data structure to not only keep track of what hosts we are connected to so that we don't try to connect to them again, but also to list the connections count on the Network Status tab.
        # If this was an incoming connection, then the sendDataThread
        # doesn't know the stream. We have to set it.
        if not self.initiatedConnection:
            self.sendDataThreadQueue.put((0, 'setStreamNumber', self.streamNumber))
        if data[72:80] == shared.eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
            self.sendDataThreadQueue.put((0, 'shutdown','no data'))
            logger.debug('Closing connection to myself: ' + str(self.peer))
            return
        
        # The other peer's protocol version is of interest to the sendDataThread but we learn of it
        # in this version message. Let us inform the sendDataThread.
        self.sendDataThreadQueue.put((0, 'setRemoteProtocolVersion', self.remoteProtocolVersion))

        if not isHostInPrivateIPRange(self.peer.host):
            with shared.knownNodesLock:
                shared.knownNodes[self.streamNumber][shared.Peer(self.peer.host, self.remoteNodeIncomingPort)] = int(time.time())
                if not self.initiatedConnection:
                    shared.knownNodes[self.streamNumber][shared.Peer(self.peer.host, self.remoteNodeIncomingPort)] -= 162000 # penalise inbound, 2 days minus 3 hours
                shared.needToWriteKnownNodesToDisk = True

        self.sendverack()
        if self.initiatedConnection == False:
            self.sendversion()

    # Sends a version message
    def sendversion(self):
        logger.debug('Sending version message')
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.assembleVersionMessage(
                self.peer.host, self.peer.port, self.streamNumber, not self.initiatedConnection)))


    # Sends a verack message
    def sendverack(self):
        logger.debug('Sending verack')
        self.sendDataThreadQueue.put((0, 'sendRawData', shared.CreatePacket('verack')))
        self.verackSent = True
        if self.verackReceived:
            self.connectionFullyEstablished()
