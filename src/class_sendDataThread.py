import time
import threading
import shared
import Queue
from struct import unpack, pack
import hashlib
import random
import sys
import socket

from helper_generic import addDataPadding
from class_objectHashHolder import *
from addresses import *
from debug import logger

# Every connection to a peer has a sendDataThread (and also a
# receiveDataThread).
class sendDataThread(threading.Thread):

    def __init__(self, sendDataThreadQueue):
        threading.Thread.__init__(self, name="sendData")
        self.sendDataThreadQueue = sendDataThreadQueue
        shared.sendDataQueues.append(self.sendDataThreadQueue)
        self.data = ''
        self.objectHashHolderInstance = objectHashHolder(self.sendDataThreadQueue)
        self.objectHashHolderInstance.start()
        self.connectionIsOrWasFullyEstablished = False


    def setup(
        self,
        sock,
        HOST,
        PORT,
        streamNumber,
            someObjectsOfWhichThisRemoteNodeIsAlreadyAware):
        self.sock = sock
        self.peer = shared.Peer(HOST, PORT)
        self.name = "sendData-" + self.peer.host
        self.streamNumber = streamNumber
        self.services = 0
        self.initiatedConnection = False
        self.remoteProtocolVersion = - \
            1  # This must be set using setRemoteProtocolVersion command which is sent through the self.sendDataThreadQueue queue.
        self.lastTimeISentData = int(
            time.time())  # If this value increases beyond five minutes ago, we'll send a pong message to keep the connection alive.
        self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware = someObjectsOfWhichThisRemoteNodeIsAlreadyAware
        if self.streamNumber == -1:  # This was an incoming connection.
            self.initiatedConnection = False
        else:
            self.initiatedConnection = True
        logger.debug('The streamNumber of this sendDataThread (ID: ' + str(id(self)) + ') at setup() is' + str(self.streamNumber))


    def sendVersionMessage(self):
        datatosend = shared.assembleVersionMessage(
            self.peer.host, self.peer.port, self.streamNumber, not self.initiatedConnection)  # the IP and port of the remote host, and my streamNumber.

        logger.debug('Sending version packet: ' + repr(datatosend))

        try:
            self.sendBytes(datatosend)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            logger.error('sock.sendall error: %s\n' % err)
            
        self.versionSent = 1

    def sendBytes(self, data):
        if shared.config.getint('bitmessagesettings', 'maxuploadrate') == 0:
            uploadRateLimitBytes = 999999999 # float("inf") doesn't work
        else:
            uploadRateLimitBytes = shared.config.getint('bitmessagesettings', 'maxuploadrate') * 1000
        with shared.sendDataLock:
            while data:
                while shared.numberOfBytesSentLastSecond >= uploadRateLimitBytes:
                    if int(time.time()) == shared.lastTimeWeResetBytesSent:
                        time.sleep(0.3)
                    else:
                        # It's a new second. Let us clear the shared.numberOfBytesSentLastSecond
                        shared.lastTimeWeResetBytesSent = int(time.time())
                        shared.numberOfBytesSentLastSecond = 0
                        # If the user raises or lowers the uploadRateLimit then we should make use of
                        # the new setting. If we are hitting the limit then we'll check here about 
                        # once per second.
                        if shared.config.getint('bitmessagesettings', 'maxuploadrate') == 0:
                            uploadRateLimitBytes = 999999999 # float("inf") doesn't work
                        else:
                            uploadRateLimitBytes = shared.config.getint('bitmessagesettings', 'maxuploadrate') * 1000
                if ((self.services & shared.NODE_SSL == shared.NODE_SSL) and
                    self.connectionIsOrWasFullyEstablished and
                    shared.haveSSL(not self.initiatedConnection)):
                    amountSent = self.sslSock.send(data[:1000])
                else:
                    amountSent = self.sock.send(data[:1000])
                shared.numberOfBytesSent += amountSent # used for the 'network status' tab in the UI
                shared.numberOfBytesSentLastSecond += amountSent
                self.lastTimeISentData = int(time.time())
                data = data[amountSent:]


    def run(self):
        logger.debug('sendDataThread starting. ID: ' + str(id(self)) + '. Number of queues in sendDataQueues: ' + str(len(shared.sendDataQueues)))
        while True:
            deststream, command, data = self.sendDataThreadQueue.get()

            if deststream == self.streamNumber or deststream == 0:
                if command == 'shutdown':
                    logger.debug('sendDataThread (associated with ' + str(self.peer) + ') ID: ' + str(id(self)) + ' shutting down now.')
                    break
                # When you receive an incoming connection, a sendDataThread is
                # created even though you don't yet know what stream number the
                # remote peer is interested in. They will tell you in a version
                # message and if you too are interested in that stream then you
                # will continue on with the connection and will set the
                # streamNumber of this send data thread here:
                elif command == 'setStreamNumber':
                    self.streamNumber = data
                    logger.debug('setting the stream number in the sendData thread (ID: ' + str(id(self)) + ') to ' + str(self.streamNumber))
                elif command == 'setRemoteProtocolVersion':
                    specifiedRemoteProtocolVersion = data
                    logger.debug('setting the remote node\'s protocol version in the sendDataThread (ID: ' + str(id(self)) + ') to ' + str(specifiedRemoteProtocolVersion))
                    self.remoteProtocolVersion = specifiedRemoteProtocolVersion
                elif command == 'advertisepeer':
                    self.objectHashHolderInstance.holdPeer(data)
                elif command == 'sendaddr':
                    if self.connectionIsOrWasFullyEstablished: # only send addr messages if we have sent and heard a verack from the remote node
                        numberOfAddressesInAddrMessage = len(data)
                        payload = ''
                        for hostDetails in data:
                            timeLastReceivedMessageFromThisNode, streamNumber, services, host, port = hostDetails
                            payload += pack(
                                '>Q', timeLastReceivedMessageFromThisNode)  # now uses 64-bit time
                            payload += pack('>I', streamNumber)
                            payload += pack(
                                '>q', services)  # service bit flags offered by this node
                            payload += shared.encodeHost(host)
                            payload += pack('>H', port)
    
                        payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
                        packet = shared.CreatePacket('addr', payload)
                        try:
                            self.sendBytes(packet)
                        except:
                            logger.error('sendaddr: self.sock.sendall failed')
                            break
                elif command == 'advertiseobject':
                    self.objectHashHolderInstance.holdHash(data)
                elif command == 'sendinv':
                    if self.connectionIsOrWasFullyEstablished: # only send inv messages if we have send and heard a verack from the remote node
                        payload = ''
                        for hash in data:
                            if hash not in self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware:
                                payload += hash
                        if payload != '':
                            payload = encodeVarint(len(payload)/32) + payload
                            packet = shared.CreatePacket('inv', payload)
                            try:
                                self.sendBytes(packet)
                            except:
                                logger.error('sendinv: self.sock.sendall failed')
                                break
                elif command == 'pong':
                    self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware.clear() # To save memory, let us clear this data structure from time to time. As its function is to help us keep from sending inv messages to peers which sent us the same inv message mere seconds earlier, it will be fine to clear this data structure from time to time.
                    if self.lastTimeISentData < (int(time.time()) - 298):
                        # Send out a pong message to keep the connection alive.
                        logger.debug('Sending pong to ' + str(self.peer) + ' to keep connection alive.')
                        packet = shared.CreatePacket('pong')
                        try:
                            self.sendBytes(packet)
                        except:
                            logger.error('send pong failed')
                            break
                elif command == 'sendRawData':
                    try:
                        self.sendBytes(data)
                    except:
                        logger.error('Sending of data to ' + str(self.peer) + ' failed. sendDataThread thread ' + str(self) + ' ending now.')
                        break
                elif command == 'connectionIsOrWasFullyEstablished':
                    self.connectionIsOrWasFullyEstablished = True
                    self.services, self.sslSock = data
            else:
                logger.error('sendDataThread ID: ' + str(id(self)) + ' ignoring command ' + command + ' because the thread is not in stream' + str(deststream))

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass
        shared.sendDataQueues.remove(self.sendDataThreadQueue)
        logger.info('sendDataThread ending. ID: ' + str(id(self)) + '. Number of queues in sendDataQueues: ' + str(len(shared.sendDataQueues)))
        self.objectHashHolderInstance.close()
