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

# Every connection to a peer has a sendDataThread (and also a
# receiveDataThread).
class sendDataThread(threading.Thread):

    def __init__(self, sendDataThreadQueue):
        threading.Thread.__init__(self)
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
        self.streamNumber = streamNumber
        self.remoteProtocolVersion = - \
            1  # This must be set using setRemoteProtocolVersion command which is sent through the self.sendDataThreadQueue queue.
        self.lastTimeISentData = int(
            time.time())  # If this value increases beyond five minutes ago, we'll send a pong message to keep the connection alive.
        self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware = someObjectsOfWhichThisRemoteNodeIsAlreadyAware
        with shared.printLock:
            print 'The streamNumber of this sendDataThread (ID:', str(id(self)) + ') at setup() is', self.streamNumber


    def sendVersionMessage(self):
        datatosend = shared.assembleVersionMessage(
            self.peer.host, self.peer.port, self.streamNumber)  # the IP and port of the remote host, and my streamNumber.

        with shared.printLock:
            print 'Sending version packet: ', repr(datatosend)

        try:
            self.sendBytes(datatosend)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            with shared.printLock:
                sys.stderr.write('sock.sendall error: %s\n' % err)
            
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
                numberOfBytesWeMaySend = uploadRateLimitBytes - shared.numberOfBytesSentLastSecond
                self.sock.sendall(data[:numberOfBytesWeMaySend])
                shared.numberOfBytesSent += len(data[:numberOfBytesWeMaySend]) # used for the 'network status' tab in the UI
                shared.numberOfBytesSentLastSecond += len(data[:numberOfBytesWeMaySend])
                self.lastTimeISentData = int(time.time())
                data = data[numberOfBytesWeMaySend:]


    def run(self):
        with shared.printLock:
            print 'sendDataThread starting. ID:', str(id(self))+'. Number of queues in sendDataQueues:', len(shared.sendDataQueues)
        while True:
            deststream, command, data = self.sendDataThreadQueue.get()

            if deststream == self.streamNumber or deststream == 0:
                if command == 'shutdown':
                    with shared.printLock:
                        print 'sendDataThread (associated with', self.peer, ') ID:', id(self), 'shutting down now.'
                    break
                # When you receive an incoming connection, a sendDataThread is
                # created even though you don't yet know what stream number the
                # remote peer is interested in. They will tell you in a version
                # message and if you too are interested in that stream then you
                # will continue on with the connection and will set the
                # streamNumber of this send data thread here:
                elif command == 'setStreamNumber':
                    self.streamNumber = data
                    with shared.printLock:
                        print 'setting the stream number in the sendData thread (ID:', id(self), ') to', self.streamNumber 
                elif command == 'setRemoteProtocolVersion':
                    specifiedRemoteProtocolVersion = data
                    with shared.printLock:
                        print 'setting the remote node\'s protocol version in the sendDataThread (ID:', id(self), ') to', specifiedRemoteProtocolVersion
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
                            with shared.printLock:
                                print 'sendaddr: self.sock.sendall failed'
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
                                with shared.printLock:
                                    print 'sendinv: self.sock.sendall failed'
                                break
                elif command == 'pong':
                    self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware.clear() # To save memory, let us clear this data structure from time to time. As its function is to help us keep from sending inv messages to peers which sent us the same inv message mere seconds earlier, it will be fine to clear this data structure from time to time.
                    if self.lastTimeISentData < (int(time.time()) - 298):
                        # Send out a pong message to keep the connection alive.
                        with shared.printLock:
                            print 'Sending pong to', self.peer, 'to keep connection alive.'
                        packet = shared.CreatePacket('pong')
                        try:
                            self.sendBytes(packet)
                        except:
                            with shared.printLock:
                                print 'send pong failed'
                            break
                elif command == 'sendRawData':
                    try:
                        self.sendBytes(data)
                    except:
                        with shared.printLock:
                            print 'Sending of data to', self.peer, 'failed. sendDataThread thread', self, 'ending now.' 
                        break
                elif command == 'connectionIsOrWasFullyEstablished':
                    self.connectionIsOrWasFullyEstablished = True
            else:
                with shared.printLock:
                    print 'sendDataThread ID:', id(self), 'ignoring command', command, 'because the thread is not in stream', deststream

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass
        shared.sendDataQueues.remove(self.sendDataThreadQueue)
        with shared.printLock:
            print 'sendDataThread ending. ID:', str(id(self))+'. Number of queues in sendDataQueues:', len(shared.sendDataQueues)
        self.objectHashHolderInstance.close()
