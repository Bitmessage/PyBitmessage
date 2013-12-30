import time
import threading
import shared
import Queue
from struct import unpack, pack
import hashlib
import random
import sys
import socket

from class_objectHashHolder import *
from addresses import *

# Every connection to a peer has a sendDataThread (and also a
# receiveDataThread).
class sendDataThread(threading.Thread):

    def __init__(self, sendDataThreadQueue):
        threading.Thread.__init__(self)
        self.sendDataThreadQueue = sendDataThreadQueue
        shared.sendDataQueues.append(self.sendDataThreadQueue)
        with shared.printLock:
            print 'The length of sendDataQueues at sendDataThread init is:', len(shared.sendDataQueues)

        self.data = ''
        self.objectHashHolderInstance = objectHashHolder(self.sendDataThreadQueue)
        self.objectHashHolderInstance.start()


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
            self.sock.sendall(datatosend)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            with shared.printLock:
                sys.stderr.write('sock.sendall error: %s\n' % err)
            
        self.versionSent = 1

    def run(self):
        while True:
            deststream, command, data = self.sendDataThreadQueue.get()

            if deststream == self.streamNumber or deststream == 0:
                if command == 'shutdown':
                    if data == self.peer or data == 'all':
                        with shared.printLock:
                            print 'sendDataThread (associated with', self.peer, ') ID:', id(self), 'shutting down now.'

                        try:
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()
                        except:
                            pass
                        shared.sendDataQueues.remove(self.sendDataThreadQueue)
                        with shared.printLock:
                            print 'len of sendDataQueues', len(shared.sendDataQueues)

                        break
                # When you receive an incoming connection, a sendDataThread is
                # created even though you don't yet know what stream number the
                # remote peer is interested in. They will tell you in a version
                # message and if you too are interested in that stream then you
                # will continue on with the connection and will set the
                # streamNumber of this send data thread here:
                elif command == 'setStreamNumber':
                    peerInMessage, specifiedStreamNumber = data
                    if peerInMessage == self.peer:
                        with shared.printLock:
                            print 'setting the stream number in the sendData thread (ID:', id(self), ') to', specifiedStreamNumber

                        self.streamNumber = specifiedStreamNumber
                elif command == 'setRemoteProtocolVersion':
                    specifiedRemoteProtocolVersion = data
                    with shared.printLock:
                        print 'setting the remote node\'s protocol version in the sendDataThread (ID:', id(self), ') to', specifiedRemoteProtocolVersion
                    self.remoteProtocolVersion = specifiedRemoteProtocolVersion
                elif command == 'advertisepeer':
                    self.objectHashHolderInstance.holdPeer(data)
                elif command == 'sendaddr':
                    numberOfAddressesInAddrMessage = len(
                        data)
                    payload = ''
                    for hostDetails in data:
                        timeLastReceivedMessageFromThisNode, streamNumber, services, host, port = hostDetails
                        payload += pack(
                            '>Q', timeLastReceivedMessageFromThisNode)  # now uses 64-bit time
                        payload += pack('>I', streamNumber)
                        payload += pack(
                            '>q', services)  # service bit flags offered by this node
                        payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                            socket.inet_aton(host)
                        payload += pack('>H', port)

                    payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
                    datatosend = '\xE9\xBE\xB4\xD9addr\x00\x00\x00\x00\x00\x00\x00\x00'
                    datatosend = datatosend + pack('>L', len(payload))  # payload length
                    datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
                    datatosend = datatosend + payload

                    try:
                        self.sock.sendall(datatosend)
                        self.lastTimeISentData = int(time.time())
                    except:
                        print 'sendaddr: self.sock.sendall failed'
                        try:
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()
                        except:
                            pass
                        shared.sendDataQueues.remove(self.sendDataThreadQueue)
                        print 'sendDataThread thread (ID:', str(id(self)) + ') ending now. Was connected to', self.peer
                        break
                elif command == 'advertiseobject':
                    self.objectHashHolderInstance.holdHash(data)
                elif command == 'sendinv':
                    payload = ''
                    for hash in data:
                        if hash not in self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware:
                            payload += hash
                    if payload != '':
                        payload = encodeVarint(len(payload)/32) + payload
                        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
                        headerData += 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        headerData += pack('>L', len(payload))
                        headerData += hashlib.sha512(payload).digest()[:4]
                        try:
                            self.sock.sendall(headerData + payload)
                            self.lastTimeISentData = int(time.time())
                        except:
                            print 'sendinv: self.sock.sendall failed'
                            try:
                                self.sock.shutdown(socket.SHUT_RDWR)
                                self.sock.close()
                            except:
                                pass
                            shared.sendDataQueues.remove(self.sendDataThreadQueue)
                            print 'sendDataThread thread (ID:', str(id(self)) + ') ending now. Was connected to', self.peer
                            break
                elif command == 'pong':
                    self.someObjectsOfWhichThisRemoteNodeIsAlreadyAware.clear() # To save memory, let us clear this data structure from time to time. As its function is to help us keep from sending inv messages to peers which sent us the same inv message mere seconds earlier, it will be fine to clear this data structure from time to time.
                    if self.lastTimeISentData < (int(time.time()) - 298):
                        # Send out a pong message to keep the connection alive.
                        with shared.printLock:
                            print 'Sending pong to', self.peer, 'to keep connection alive.'

                        try:
                            self.sock.sendall(
                                '\xE9\xBE\xB4\xD9\x70\x6F\x6E\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
                            self.lastTimeISentData = int(time.time())
                        except:
                            print 'send pong failed'
                            try:
                                self.sock.shutdown(socket.SHUT_RDWR)
                                self.sock.close()
                            except:
                                pass
                            shared.sendDataQueues.remove(self.sendDataThreadQueue)
                            print 'sendDataThread thread', self, 'ending now. Was connected to', self.peer
                            break
                elif command == 'sendRawData':
                    try:
                        self.sock.sendall(data)
                        self.lastTimeISentData = int(time.time())
                    except:
                        try:
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()
                        except:
                            pass
                        shared.sendDataQueues.remove(self.sendDataThreadQueue)
                        print 'Sending of data to', self.peer, 'failed. sendDataThread thread', self, 'ending now.' 
                        break
            else:
                with shared.printLock:
                    print 'sendDataThread ID:', id(self), 'ignoring command', command, 'because the thread is not in stream', deststream

        self.objectHashHolderInstance.close()
