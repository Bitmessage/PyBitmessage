import time
import threading
import shared
import Queue
from struct import unpack, pack
import hashlib

import bitmessagemain

# Every connection to a peer has a sendDataThread (and also a
# receiveDataThread).
class sendDataThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.mailbox = Queue.Queue()
        shared.sendDataQueues.append(self.mailbox)
        shared.printLock.acquire()
        print 'The length of sendDataQueues at sendDataThread init is:', len(shared.sendDataQueues)
        shared.printLock.release()
        self.data = ''

    def setup(
        self,
        sock,
        HOST,
        PORT,
        streamNumber,
            objectsOfWhichThisRemoteNodeIsAlreadyAware):
        self.sock = sock
        self.HOST = HOST
        self.PORT = PORT
        self.streamNumber = streamNumber
        self.remoteProtocolVersion = - \
            1  # This must be set using setRemoteProtocolVersion command which is sent through the self.mailbox queue.
        self.lastTimeISentData = int(
            time.time())  # If this value increases beyond five minutes ago, we'll send a pong message to keep the connection alive.
        self.objectsOfWhichThisRemoteNodeIsAlreadyAware = objectsOfWhichThisRemoteNodeIsAlreadyAware
        shared.printLock.acquire()
        print 'The streamNumber of this sendDataThread (ID:', str(id(self)) + ') at setup() is', self.streamNumber
        shared.printLock.release()

    def sendVersionMessage(self):
        datatosend = bitmessagemain.assembleVersionMessage(
            self.HOST, self.PORT, self.streamNumber)  # the IP and port of the remote host, and my streamNumber.

        shared.printLock.acquire()
        print 'Sending version packet: ', repr(datatosend)
        shared.printLock.release()
        try:
            self.sock.sendall(datatosend)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()
        self.versionSent = 1

    def run(self):
        while True:
            deststream, command, data = self.mailbox.get()
            # shared.printLock.acquire()
            # print 'sendDataThread, destream:', deststream, ', Command:', command, ', ID:',id(self), ', HOST:', self.HOST
            # shared.printLock.release()

            if deststream == self.streamNumber or deststream == 0:
                if command == 'shutdown':
                    if data == self.HOST or data == 'all':
                        shared.printLock.acquire()
                        print 'sendDataThread (associated with', self.HOST, ') ID:', id(self), 'shutting down now.'
                        shared.printLock.release()
                        try:
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()
                        except:
                            pass
                        shared.sendDataQueues.remove(self.mailbox)
                        shared.printLock.acquire()
                        print 'len of sendDataQueues', len(shared.sendDataQueues)
                        shared.printLock.release()
                        break
                # When you receive an incoming connection, a sendDataThread is
                # created even though you don't yet know what stream number the
                # remote peer is interested in. They will tell you in a version
                # message and if you too are interested in that stream then you
                # will continue on with the connection and will set the
                # streamNumber of this send data thread here:
                elif command == 'setStreamNumber':
                    hostInMessage, specifiedStreamNumber = data
                    if hostInMessage == self.HOST:
                        shared.printLock.acquire()
                        print 'setting the stream number in the sendData thread (ID:', id(self), ') to', specifiedStreamNumber
                        shared.printLock.release()
                        self.streamNumber = specifiedStreamNumber
                elif command == 'setRemoteProtocolVersion':
                    hostInMessage, specifiedRemoteProtocolVersion = data
                    if hostInMessage == self.HOST:
                        shared.printLock.acquire()
                        print 'setting the remote node\'s protocol version in the sendData thread (ID:', id(self), ') to', specifiedRemoteProtocolVersion
                        shared.printLock.release()
                        self.remoteProtocolVersion = specifiedRemoteProtocolVersion
                elif command == 'sendaddr':
                    try:
                        # To prevent some network analysis, 'leak' the data out
                        # to our peer after waiting a random amount of time
                        # unless we have a long list of messages in our queue
                        # to send.
                        random.seed()
                        time.sleep(random.randrange(0, 10))
                        self.sock.sendall(data)
                        self.lastTimeISentData = int(time.time())
                    except:
                        print 'self.sock.sendall failed'
                        try:
                            self.sock.shutdown(socket.SHUT_RDWR)
                            self.sock.close()
                        except:
                            pass
                        shared.sendDataQueues.remove(self.mailbox)
                        print 'sendDataThread thread (ID:', str(id(self)) + ') ending now. Was connected to', self.HOST
                        break
                elif command == 'sendinv':
                    if data not in self.objectsOfWhichThisRemoteNodeIsAlreadyAware:
                        payload = '\x01' + data
                        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
                        headerData += 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        headerData += pack('>L', len(payload))
                        headerData += hashlib.sha512(payload).digest()[:4]
                        # To prevent some network analysis, 'leak' the data out
                        # to our peer after waiting a random amount of time
                        random.seed()
                        time.sleep(random.randrange(0, 10))
                        try:
                            self.sock.sendall(headerData + payload)
                            self.lastTimeISentData = int(time.time())
                        except:
                            print 'self.sock.sendall failed'
                            try:
                                self.sock.shutdown(socket.SHUT_RDWR)
                                self.sock.close()
                            except:
                                pass
                            shared.sendDataQueues.remove(self.mailbox)
                            print 'sendDataThread thread (ID:', str(id(self)) + ') ending now. Was connected to', self.HOST
                            break
                elif command == 'pong':
                    if self.lastTimeISentData < (int(time.time()) - 298):
                        # Send out a pong message to keep the connection alive.
                        shared.printLock.acquire()
                        print 'Sending pong to', self.HOST, 'to keep connection alive.'
                        shared.printLock.release()
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
                            shared.sendDataQueues.remove(self.mailbox)
                            print 'sendDataThread thread', self, 'ending now. Was connected to', self.HOST
                            break
            else:
                shared.printLock.acquire()
                print 'sendDataThread ID:', id(self), 'ignoring command', command, 'because the thread is not in stream', deststream
                shared.printLock.release()

