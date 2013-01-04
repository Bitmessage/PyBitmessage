# Copyright (c) 2012 Jonathan Warren
# Copyright (c) 2012 The Bitmessage developers
# Distributed under the MIT/X11 software license. See the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

#Right now, PyBitmessage only support connecting to stream 1. It doesn't yet contain logic to expand into further streams.

softwareVersion = '0.1.5'
verbose = 2
maximumAgeOfAnObjectThatIAmWillingToAccept = 216000 #Equals two days and 12 hours.
lengthOfTimeToLeaveObjectsInInventory = 237600 #Equals two days and 18 hours. This should be longer than maximumAgeOfAnObjectThatIAmWillingToAccept so that we don't process messages twice.
maximumAgeOfObjectsThatIAdvertiseToOthers = 216000 #Equals two days and 12 hours
maximumAgeOfNodesThatIAdvertiseToOthers = 10800 #Equals three hours


import sys
try:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
except Exception, err:
    print 'PyBitmessage requires PyQt. You can download it from http://www.riverbankcomputing.com/software/pyqt/download   or by searching Google for \'PyQt Download\' (without quotes).'
    print 'Error message:', err
    sys.exit()
import ConfigParser
from bitmessageui import *
from newaddressdialog import *
from newsubscriptiondialog import *
from settings import *
from about import *
from help import *
from iconglossary import *
from addresses import *
import Queue
from defaultKnownNodes import *
import time
import socket
import threading
import rsa
from rsa.bigfile import *
import hashlib
from struct import *
import pickle
import random
import sqlite3
import threading #used for the locks, not for the threads
import cStringIO
from time import strftime, localtime
import os
import string
import socks

#For each stream to which we connect, one outgoingSynSender thread will exist and will create 8 connections with peers.
class outgoingSynSender(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.selfInitiatedConnectionList = [] #This is a list of current connections (the thread pointers at least)
        self.alreadyAttemptedConnectionsList = [] #This is a list of nodes to which we have already attempted a connection

    def setup(self,streamNumber):
        self.streamNumber = streamNumber


    def run(self):
        time.sleep(1)
        resetTime = int(time.time()) #used below to clear out the alreadyAttemptedConnectionsList periodically so that we will retry connecting to hosts to which we have already tried to connect.
        while True:
            #time.sleep(999999)#I'm using this to prevent connections for testing.
            if len(self.selfInitiatedConnectionList) < 8: #maximum number of outgoing connections = 8
                random.seed()
                HOST, = random.sample(knownNodes[self.streamNumber],  1)
                while HOST in self.alreadyAttemptedConnectionsList or HOST in connectedHostsList:
                    #print 'choosing new sample'
                    random.seed()
                    HOST, = random.sample(knownNodes[self.streamNumber],  1)
                    time.sleep(1)
                    #Clear out the alreadyAttemptedConnectionsList every half hour so that this program will again attempt a connection to any nodes, even ones it has already tried.
                    if (int(time.time()) - resetTime) > 1800:
                        self.alreadyAttemptedConnectionsList = []
                        resetTime = int(time.time())
                self.alreadyAttemptedConnectionsList.append(HOST)
                PORT, timeNodeLastSeen = knownNodes[self.streamNumber][HOST]
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(20)
                if config.get('bitmessagesettings', 'socksproxytype') == 'none':
                    printLock.acquire()
                    print 'Trying an outgoing connection to', HOST, ':', PORT
                    printLock.release()
                    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                elif config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS4a':
                    printLock.acquire()
                    print '(Using SOCKS4a) Trying an outgoing connection to', HOST, ':', PORT
                    printLock.release()
                    proxytype = socks.PROXY_TYPE_SOCKS4
                    sockshostname = config.get('bitmessagesettings', 'sockshostname')
                    socksport = config.getint('bitmessagesettings', 'socksport')
                    rdns = True #Do domain name lookups through the proxy; though this setting doesn't really matter since we won't be doing any domain name lookups anyway.
                    if config.getboolean('bitmessagesettings', 'socksauthentication'):
                        socksusername = config.get('bitmessagesettings', 'socksusername')
                        sockspassword = config.get('bitmessagesettings', 'sockspassword')
                        sock.setproxy(proxytype, sockshostname, socksport, rdns, socksusername, sockspassword)
                    else:
                        sock.setproxy(proxytype, sockshostname, socksport, rdns)
                elif config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS5':
                    printLock.acquire()
                    print '(Using SOCKS5) Trying an outgoing connection to', HOST, ':', PORT
                    printLock.release()
                    proxytype = socks.PROXY_TYPE_SOCKS5
                    sockshostname = config.get('bitmessagesettings', 'sockshostname')
                    socksport = config.getint('bitmessagesettings', 'socksport')
                    rdns = True #Do domain name lookups through the proxy; though this setting doesn't really matter since we won't be doing any domain name lookups anyway.
                    if config.getboolean('bitmessagesettings', 'socksauthentication'):
                        socksusername = config.get('bitmessagesettings', 'socksusername')
                        sockspassword = config.get('bitmessagesettings', 'sockspassword')
                        sock.setproxy(proxytype, sockshostname, socksport, rdns, socksusername, sockspassword)
                    else:
                        sock.setproxy(proxytype, sockshostname, socksport, rdns)

                try:
                    sock.connect((HOST, PORT))
                    rd = receiveDataThread()
                    self.emit(SIGNAL("passObjectThrough(PyQt_PyObject)"),rd)
                    rd.setup(sock,HOST,PORT,self.streamNumber,self.selfInitiatedConnectionList)
                    rd.start()
                    printLock.acquire()
                    print self, 'connected to', HOST, 'during outgoing attempt.'
                    printLock.release()
                    
                    sd = sendDataThread()
                    sd.setup(sock,HOST,PORT,self.streamNumber)
                    sd.start()
                    sd.sendVersionMessage()

                except socks.GeneralProxyError, err:
                    print 'Could NOT connect to', HOST, 'during outgoing attempt.', err
                    PORT, timeLastSeen = knownNodes[self.streamNumber][HOST]
                    if (int(time.time())-timeLastSeen) > 172800 and len(knownNodes[self.streamNumber]) > 1000: # for nodes older than 48 hours old if we have more than 1000 hosts in our list, delete from the knownNodes data-structure.
                        del knownNodes[self.streamNumber][HOST]
                        print 'deleting ', HOST, 'from knownNodes because it is more than 48 hours old and we could not connect to it.'
                except socks.Socks5AuthError, err:
                    self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"SOCKS5 Authentication problem: "+str(err))
                except socks.Socks5Error, err:
                    pass
                    print 'SOCKS5 error. (It is possible that the server wants authentication).)' ,str(err)
                    #self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"SOCKS5 error. Server might require authentication. "+str(err))
                except socks.Socks4Error, err:
                    print 'Socks4Error:', err
                    #self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"SOCKS4 error: "+str(err))
                except socket.error, err:
                    if config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
                        print 'Bitmessage MIGHT be having trouble connecting to the SOCKS server. '+str(err)
                        #self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"Problem: Bitmessage can not connect to the SOCKS server. "+str(err))
                    else:
                        print 'Could NOT connect to', HOST, 'during outgoing attempt.', err
                        PORT, timeLastSeen = knownNodes[self.streamNumber][HOST]
                        if (int(time.time())-timeLastSeen) > 172800 and len(knownNodes[self.streamNumber]) > 1000: # for nodes older than 48 hours old if we have more than 1000 hosts in our list, delete from the knownNodes data-structure.
                            del knownNodes[self.streamNumber][HOST]
                            print 'deleting ', HOST, 'from knownNodes because it is more than 48 hours old and we could not connect to it.'
                except Exception, err:
                    print 'An exception has occurred in the outgoingSynSender thread that was not caught by other exception types:', err
            time.sleep(1)

#Only one singleListener thread will ever exist. It creates the receiveDataThread and sendDataThread for each incoming connection. Note that it cannot set the stream number because it is not known yet- the other node will have to tell us its stream number in a version message. If we don't care about their stream, we will close the connection (within the recversion function of the recieveData thread)
class singleListener(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        

    def run(self):
        #We don't want to accept incoming connections if the user is using a SOCKS proxy. If they eventually select proxy 'none' then this will start listening for connections.
        while config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
            time.sleep(300)

        print 'bitmessage listener running'
        HOST = '' # Symbolic name meaning all available interfaces
        PORT = config.getint('bitmessagesettings', 'port')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #This option apparently avoids the TIME_WAIT state so that we can rebind faster
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(2)
        self.incomingConnectionList = [] #This list isn't used for anything. The reason it exists is because receiveData threads expect that a list be passed to them. They expect this because the outgoingSynSender thread DOES use a similar list to keep track of the number of outgoing connections it has created.


        while True:
            #We don't want to accept incoming connections if the user is using a SOCKS proxy. If they eventually select proxy 'none' then this will start listening for connections.
            while config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
                time.sleep(10)
            a,(HOST,PORT) = sock.accept()
            #Users are finding that if they run more than one node in the same network (thus with the same public IP), they can not connect with the second node. This is because this section of code won't accept the connection from the same IP. This problem will go away when the Bitmessage network grows behond being tiny but in the mean time, I'll comment out this code section.
            """while HOST in connectedHostsList:
                print 'incoming connection is from a host in connectedHostsList (we are already connected to it). Ignoring it.'
                a.close()
                a,(HOST,PORT) = sock.accept()"""
            rd = receiveDataThread()
            self.emit(SIGNAL("passObjectThrough(PyQt_PyObject)"),rd)
            rd.setup(a,HOST,PORT,-1,self.incomingConnectionList)
            printLock.acquire()
            print self, 'connected to', HOST,'during INCOMING request.'
            printLock.release()
            rd.start()

            sd = sendDataThread()
            sd.setup(a,HOST,PORT,-1)
            sd.start()


#This thread is created either by the synSenderThread(for outgoing connections) or the singleListenerThread(for incoming connectiosn).
class receiveDataThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.data = ''
        self.verackSent = False
        self.verackReceived = False

    def setup(self,sock,HOST,port,streamNumber,selfInitiatedConnectionList):
        self.sock = sock
        self.HOST = HOST
        self.PORT = port
        self.sock.settimeout(600) #We'll send out a pong every 5 minutes to make sure the connection stays alive if there has been no other traffic to send lately.
        self.streamNumber = streamNumber
        self.selfInitiatedConnectionList = selfInitiatedConnectionList
        self.selfInitiatedConnectionList.append(self)
        self.payloadLength = 0
        self.receivedgetbiginv = False
        self.objectsThatWeHaveYetToGet = {}
        connectedHostsList[self.HOST] = 0
        self.connectionIsOrWasFullyEstablished = False #set to true after the remote node and I accept each other's version messages. This is needed to allow the user interface to accurately reflect the current number of connections.
        if self.streamNumber == -1: #This was an incoming connection. Send out a version message if we accept the other node's version message.
            self.initiatedConnection = False
        else:
            self.initiatedConnection = True
        self.ackDataThatWeHaveYetToSend = [] #When we receive a message bound for us, we store the acknowledgement that we need to send (the ackdata) here until we are done processing all other data received from this peer.


    def run(self):

        while True:
            try:
                self.data = self.data + self.sock.recv(65536)
            except socket.timeout:
                printLock.acquire()
                print 'Timeout occurred waiting for data. Closing thread.'
                printLock.release()
                break
            except Exception, err:
                printLock.acquire()
                print 'sock.recv error. Closing receiveData thread.', err
                printLock.release()
                break
            #print 'Received', repr(self.data)
            if self.data == "":
                printLock.acquire()
                print 'Connection closed.'
                printLock.release()
                break
            else:
                self.processData()
                
                

        try:
            self.sock.close()
        except Exception, err:
            print 'Within receiveDataThread run(), self.sock.close() failed.', err
        
        try:
            self.selfInitiatedConnectionList.remove(self)
            print 'removed self from ConnectionList'
        except:
            pass
        broadcastToSendDataQueues((self.streamNumber, 'shutdown', self.HOST))
        if self.connectionIsOrWasFullyEstablished: #We don't want to decrement the number of connections and show the result if we never incremented it in the first place (which we only do if the connection is fully established- meaning that both nodes accepted each other's version packets.)
            connectionsCountLock.acquire()
            connectionsCount[self.streamNumber] -= 1
            self.emit(SIGNAL("updateNetworkStatusTab(PyQt_PyObject,PyQt_PyObject)"),self.streamNumber,connectionsCount[self.streamNumber])
            connectionsCountLock.release()
        try:
            del connectedHostsList[self.HOST]
        except Exception, err:
            print 'Could not delete', self.HOST, 'from connectedHostsList.', err
       
    def processData(self):
        global verbose
        #if verbose >= 2:
            #printLock.acquire()
            #print 'self.data is currently ', repr(self.data)
            #printLock.release()
        if self.data == "":
            pass
        elif self.data[0:4] != '\xe9\xbe\xb4\xd9':
            self.data = ""
            if verbose >= 2:
                printLock.acquire()
                sys.stderr.write('The magic bytes were not correct.\n')
                printLock.release()
        elif len(self.data) < 20: #if so little of the data has arrived that we can't even unpack the payload length
            pass
        else:
            self.payloadLength, = unpack('>L',self.data[16:20])
            if len(self.data) >= self.payloadLength: #check if the whole message has arrived yet. If it has,...
                if self.data[20:24] == hashlib.sha512(self.data[24:self.payloadLength+24]).digest()[0:4]:#test the checksum in the message. If it is correct...
                    #print 'message checksum is correct'
                    #The time we've last seen this node is obviously right now since we just received valid data from it. So update the knownNodes list so that other peers can be made aware of its existance.
                    if self.initiatedConnection: #The remote port is only something we should share with others if it is the remote node's incoming port (rather than some random operating-system-assigned outgoing port).
                        knownNodes[self.streamNumber][self.HOST] = (self.PORT,int(time.time()))
                    remoteCommand = self.data[4:16]
                    if verbose >= 2:
                        printLock.acquire()
                        print 'remoteCommand ', remoteCommand, 'from', self.HOST
                        printLock.release()
                    if remoteCommand == 'version\x00\x00\x00\x00\x00':
                        self.recversion()
                    elif remoteCommand == 'verack\x00\x00\x00\x00\x00\x00':
                        self.recverack()
                    elif remoteCommand == 'addr\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.recaddr()
                    elif remoteCommand == 'getpubkey\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.recgetpubkey()
                    elif remoteCommand == 'pubkey\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.recpubkey()
                    elif remoteCommand == 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.recinv()
                    elif remoteCommand == 'getdata\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.recgetdata()
                    elif remoteCommand == 'getbiginv\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.sendBigInv()
                    elif remoteCommand == 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.recmsg()
                    elif remoteCommand == 'broadcast\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.recbroadcast()
                    elif remoteCommand == 'getaddr\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.sendaddr()
                    elif remoteCommand == 'ping\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        self.sendpong()
                    elif remoteCommand == 'pong\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        pass
                    elif remoteCommand == 'alert\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                        pass

                    self.data = self.data[self.payloadLength+24:]#take this message out and then process the next message
                    if self.data == '':
                        while len(self.objectsThatWeHaveYetToGet) > 0:
                            random.seed()
                            objectHash, = random.sample(self.objectsThatWeHaveYetToGet,  1)
                            if objectHash in inventory:
                                print 'Inventory (in memory) already has object listed in inv message.'
                                del self.objectsThatWeHaveYetToGet[objectHash]
                            elif isInSqlInventory(objectHash):
                                print 'Inventory (SQL on disk) already has object listed in inv message.'
                                del self.objectsThatWeHaveYetToGet[objectHash]
                            else:
                                print 'processData function making request for object:', repr(objectHash)
                                self.sendgetdata(objectHash)
                                del self.objectsThatWeHaveYetToGet[objectHash] #It is possible that the remote node doesn't respond with the object. In that case, we'll very likely get it from someone else anyway.
                                break
                        if len(self.objectsThatWeHaveYetToGet) > 0:
                            printLock.acquire()
                            print 'within processData, number of objectsThatWeHaveYetToGet is now', len(self.objectsThatWeHaveYetToGet)
                            printLock.release()
                        if len(self.ackDataThatWeHaveYetToSend) > 0:
                            self.data = self.ackDataThatWeHaveYetToSend.pop()
                    self.processData()
                else:
                    print 'Checksum incorrect. Clearing this message.'
                    self.data = self.data[self.payloadLength+24:]

    def isProofOfWorkSufficient(self):
        POW, = unpack('>Q',hashlib.sha512(hashlib.sha512(self.data[24:32]+ hashlib.sha512(self.data[32:24+self.payloadLength]).digest()).digest()).digest()[0:8])
        #print 'POW:', POW
        #Notice that I have divided the averageProofOfWorkNonceTrialsPerByte by two. This makes the POW requirement easier. This gives us wiggle-room: if we decide that we want to make the POW easier, the change won't obsolete old clients because they already expect a lower POW. If we decide that the current work done by clients feels approperate then we can remove this division by 2 and make the requirement match what is actually done by a sending node. If we want to raise the POW requirement then old nodes will HAVE to upgrade no matter what.
        return POW < 2**64 / ((self.payloadLength+payloadLengthExtraBytes) * (averageProofOfWorkNonceTrialsPerByte/2))

    def sendpong(self):
        print 'Sending pong'
        self.sock.sendall('\xE9\xBE\xB4\xD9\x70\x6F\x6E\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')

    def recverack(self):
        print 'verack received'
        self.verackReceived = True
        if self.verackSent == True:
            #We have thus both sent and received a verack.
            self.connectionFullyEstablished()

    def connectionFullyEstablished(self):
        self.connectionIsOrWasFullyEstablished = True
        if not self.initiatedConnection:
            self.emit(SIGNAL("setStatusIcon(PyQt_PyObject)"),'green')
        #Update the 'Network Status' tab
        connectionsCountLock.acquire()
        connectionsCount[self.streamNumber] += 1
        self.emit(SIGNAL("updateNetworkStatusTab(PyQt_PyObject,PyQt_PyObject)"),self.streamNumber,connectionsCount[self.streamNumber])
        connectionsCountLock.release()
        remoteNodeIncomingPort, remoteNodeSeenTime = knownNodes[self.streamNumber][self.HOST]
        printLock.acquire()
        print 'Connection fully established with', self.HOST, remoteNodeIncomingPort
        print 'broadcasting addr from within connectionFullyEstablished function.'
        printLock.release()
        self.broadcastaddr([(int(time.time()), self.streamNumber, 1, self.HOST, remoteNodeIncomingPort)]) #This lets all of our peers know about this new node.
        self.sendaddr() #This is one addr message to this one peer.
        if connectionsCount[self.streamNumber] > 150:
            print 'We are connected to too many people. Closing connection.'
            self.sock.close()
            return
        self.sendBigInv()

    def sendBigInv(self): #I used capitals in for this function name because there is no such Bitmessage command as 'biginv'.
        if self.receivedgetbiginv:
            print 'We have already sent a big inv message to this peer. Ignoring request.'
            return
        else:
            self.receivedgetbiginv = True
            sqlLock.acquire()
            #Select all hashes which are younger than two days old and in this stream.
            t = (int(time.time())-maximumAgeOfObjectsThatIAdvertiseToOthers,self.streamNumber)
            sqlSubmitQueue.put('''SELECT hash FROM inventory WHERE receivedtime>? and streamnumber=?''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()      
            print 'sendBigInv pulled', len(queryreturn), 'items from SQL inventory.'
            bigInvList = {}
            for row in queryreturn:
                hash, = row
                bigInvList[hash] = 0
            #print 'bigInvList:', bigInvList
            for hash, storedValue in inventory.items():
                objectType, streamNumber, payload, receivedTime = storedValue
                if streamNumber == self.streamNumber and receivedTime > int(time.time())-maximumAgeOfObjectsThatIAdvertiseToOthers:
                    bigInvList[hash] = 0
            numberOfObjectsInInvMessage = 0
            payload = ''
            for hash, storedValue in bigInvList.items():
                payload += hash
                numberOfObjectsInInvMessage += 1
                if numberOfObjectsInInvMessage >= 50000: #We can only send a max of 50000 items per inv message but we may have more objects to advertise. They must be split up into multiple inv messages.
                    sendinvMessageToJustThisOnePeer(numberOfObjectsInInvMessage,payload)
                    payload = ''
                    numberOfObjectsInInvMessage = 0
            if numberOfObjectsInInvMessage > 0:
                self.sendinvMessageToJustThisOnePeer(numberOfObjectsInInvMessage,payload)
                
    #Self explanatory. Notice that there is also a broadcastinv function for broadcasting invs to everyone in our stream.
    def sendinvMessageToJustThisOnePeer(self,numberOfObjects,payload):
        payload = encodeVarint(numberOfObjects) + payload
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData = headerData + 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData = headerData + pack('>L',len(payload))
        headerData = headerData + hashlib.sha512(payload).digest()[:4]
        print 'Sending inv message to just this one peer'
        self.sock.send(headerData + payload)

    #We have received a broadcast message
    def recbroadcast(self):
        #First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient():
            print 'Proof of work in broadcast message insufficient.'
            return
        embeddedTime, = unpack('>I',self.data[32:36])
        if embeddedTime > (int(time.time())+10800): #prevent funny business
            print 'The embedded time in this broadcast message is more than three hours in the future. That doesn\'t make sense. Ignoring message.'
            return
        if embeddedTime < (int(time.time())-maximumAgeOfAnObjectThatIAmWillingToAccept):
            print 'The embedded time in this broadcast message is too old. Ignoring message.'
            return
        if self.payloadLength < 66:
            print 'The payload length of this broadcast packet is unreasonably low. Someone is probably trying funny business. Ignoring message.'
            return
        inventoryLock.acquire()
        inventoryHash = calculateInventoryHash(self.data[24:self.payloadLength+24])
        if inventoryHash in inventory:
            print 'We have already received this broadcast object. Ignoring.'
            inventoryLock.release()
            return
        elif isInSqlInventory(inventoryHash):
            print 'We have already received this broadcast object (it is stored on disk in the SQL inventory). Ignoring it.'
            inventoryLock.release()
            return
        #It is valid so far. Let's let our peers know about it.
        objectType = 'broadcast'
        inventory[inventoryHash] = (objectType, self.streamNumber, self.data[24:self.payloadLength+24], embeddedTime)
        inventoryLock.release()
        self.broadcastinv(inventoryHash)
        self.emit(SIGNAL("incrementNumberOfBroadcastsProcessed()"))
        
        readPosition = 36
        broadcastVersion, broadcastVersionLength = decodeVarint(self.data[readPosition:readPosition+9])
        if broadcastVersion <> 1:
            #Cannot decode incoming broadcast versions higher than 1. Assuming the sender isn\' being silly, you should upgrade Bitmessage because this message shall be ignored.
            return
        readPosition += broadcastVersionLength
        sendersAddressVersion, sendersAddressVersionLength = decodeVarint(self.data[readPosition:readPosition+9])
        if sendersAddressVersion <> 1:
            #Cannot decode senderAddressVersion higher than 1. Assuming the sender isn\' being silly, you should upgrade Bitmessage because this message shall be ignored.
            return
        readPosition += sendersAddressVersionLength
        sendersStream, sendersStreamLength = decodeVarint(self.data[readPosition:readPosition+9])
        if sendersStream <= 0:
            return
        readPosition += sendersStreamLength
        sendersHash = self.data[readPosition:readPosition+20]
        if sendersHash not in broadcastSendersForWhichImWatching:
            return
        #At this point, this message claims to be from sendersHash and we are interested in it. We still have to hash the public key to make sure it is truly the key that matches the hash, and also check the signiture.
        readPosition += 20
        nLength, nLengthLength = decodeVarint(self.data[readPosition:readPosition+9])
        if nLength < 1:
            return
        readPosition += nLengthLength
        nString = self.data[readPosition:readPosition+nLength]
        readPosition += nLength
        eLength, eLengthLength = decodeVarint(self.data[readPosition:readPosition+9])
        if eLength < 1:
            return
        readPosition += eLengthLength
        eString = self.data[readPosition:readPosition+eLength]
        #We are now ready to hash the public key and verify that its hash matches the hash claimed in the message
        readPosition += eLength
        sha = hashlib.new('sha512')
        sha.update(nString+eString)
        ripe = hashlib.new('ripemd160')
        ripe.update(sha.digest())
        if ripe.digest() != sendersHash:
            #The sender of this message lied.
            return

        readPositionAtBeginningOfMessageEncodingType = readPosition
        messageEncodingType, messageEncodingTypeLength = decodeVarint(self.data[readPosition:readPosition+9])
        if messageEncodingType == 0:
            return
        readPosition += messageEncodingTypeLength
        messageLength, messageLengthLength = decodeVarint(self.data[readPosition:readPosition+9])
        readPosition += messageLengthLength
        message = self.data[readPosition:readPosition+messageLength]
        readPosition += messageLength
        signature = self.data[readPosition:readPosition+nLength]
        print 'signature', repr(signature)
        sendersPubkey = rsa.PublicKey(convertStringToInt(nString),convertStringToInt(eString))
        #print 'senders Pubkey', sendersPubkey
        try:
            #You may notice that this signature doesn't cover any information that identifies the RECEIVER of the message. This makes it vulnerable to a malicious receiver Bob forwarding the message from Alice to Charlie, making it look like Alice sent the message to Charlie. This will be fixed in the next version.
                #See http://world.std.com/~dtd/sign_encrypt/sign_encrypt7.html
            rsa.verify(self.data[readPositionAtBeginningOfMessageEncodingType:readPositionAtBeginningOfMessageEncodingType+messageEncodingTypeLength+messageLengthLength+messageLength],signature,sendersPubkey)
            print 'verify passed'
        except Exception, err:
            print 'verify failed', err
            return
        #verify passed
        fromAddress = encodeAddress(sendersAddressVersion,sendersStream,ripe.digest())
        print 'fromAddress:', fromAddress

        if messageEncodingType == 2:
            bodyPositionIndex = string.find(message,'\nBody:')
            if bodyPositionIndex > 1:
                subject = message[8:bodyPositionIndex]
                body = message[bodyPositionIndex+6:]
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
        if messageEncodingType <> 0:
            sqlLock.acquire()
            t = (inventoryHash,toAddress,fromAddress,subject,int(time.time()),body,'inbox')
            sqlSubmitQueue.put('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?)''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            self.emit(SIGNAL("displayNewMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),inventoryHash,toAddress,fromAddress,subject,body)

    #We have received a msg message.
    def recmsg(self):
        #First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient():
            print 'Proof of work in msg message insufficient.'
            return
        initialDecryptionSuccessful = False
        readPosition = 32
        embeddedTime, = unpack('>I',self.data[readPosition:readPosition+4])
        if embeddedTime > int(time.time())+10800:
            print 'The time in the msg message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time())-maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in the msg message is too old. Ignoring it. Time:', embeddedTime
            return
        readPosition += 4
        inventoryHash = calculateInventoryHash(self.data[24:self.payloadLength+24])

        streamNumberAsClaimedByMsg, streamNumberAsClaimedByMsgLength = decodeVarint(self.data[readPosition:readPosition+9])
        if streamNumberAsClaimedByMsg != self.streamNumber:
            print 'The stream number encoded in this msg (' + streamNumberAsClaimedByMsg + ') message does not match the stream number on which it was received. Ignoring it.'
            return
        readPosition += streamNumberAsClaimedByMsgLength
        inventoryLock.acquire()
        if inventoryHash in inventory:
            print 'We have already received this msg message. Ignoring.'
            inventoryLock.release()
            return
        elif isInSqlInventory(inventoryHash):
            print 'We have already received this msg message (it is stored on disk in the SQL inventory). Ignoring it.'
            inventoryLock.release()
            return
        #This msg message is valid. Let's let our peers know about it.
        objectType = 'msg'
        inventory[inventoryHash] = (objectType, self.streamNumber, self.data[24:self.payloadLength+24], embeddedTime)
        inventoryLock.release()
        self.broadcastinv(inventoryHash)
        self.emit(SIGNAL("incrementNumberOfMessagesProcessed()"))

        #Let's check whether this is a message acknowledgement bound for us.
        if self.data[readPosition:24+self.payloadLength] in ackdataForWhichImWatching:
            printLock.acquire()
            print 'This msg IS an acknowledgement bound for me.'
            printLock.release()
            del ackdataForWhichImWatching[self.data[readPosition:24+self.payloadLength]]
            t = ('ackreceived',self.data[readPosition:24+self.payloadLength])
            sqlLock.acquire()
            sqlSubmitQueue.put('UPDATE sent SET status=? WHERE ackdata=?')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),self.data[readPosition:24+self.payloadLength],'Acknowledgement of the message received just now.')
            flushInventory() #so that we won't accidentially receive this message twice if the user restarts Bitmessage soon.
            return
        else:
            printLock.acquire()
            print 'This was NOT an acknowledgement bound for me.' #Msg potential ack data:', repr(self.data[readPosition:24+self.payloadLength])
            #print 'ackdataForWhichImWatching', ackdataForWhichImWatching
            printLock.release()

        #This is not an acknowledgement bound for me. See if it is a message bound for me by trying to decrypt it with my private keys.
        infile = cStringIO.StringIO(self.data[readPosition:self.payloadLength+24])
        outfile = cStringIO.StringIO()
        #print 'len(myAddressHashes.items()):', len(myAddressHashes.items())
        for key, value in myAddressHashes.items():
            try:
                decrypt_bigfile(infile, outfile, value)
                #The initial decryption passed though there is a small chance that the message isn't actually for me. We'll need to check that the 20 zeros are present.
                #print 'initial decryption successful using key', repr(key)
                initialDecryptionSuccessful = True
                printLock.acquire()
                print 'Initial decryption passed'
                printLock.release()
                break
            except Exception, err:
                infile.seek(0)
                #print 'Exception:', err
                #print 'outfile len is:', len(outfile.getvalue()),'data is:', repr(outfile.getvalue())
                #print 'Initial decryption failed using key', value
                #decryption failed for this key. The message is for someone else (or for a different key of mine).
        if initialDecryptionSuccessful and outfile.getvalue()[:20] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00': #this run of 0s allows the true message receiver to identify his message
            #This is clearly a message bound for me.
            flushInventory() #so that we won't accidentially receive this message twice if the user restarts Bitmessage soon.
            outfile.seek(0)
            data = outfile.getvalue()
            readPosition = 20 #To start reading past the 20 zero bytes
            messageVersion, messageVersionLength = decodeVarint(data[readPosition:readPosition+10])
            readPosition += messageVersionLength
            if messageVersion == 1:
                bitfieldBehavior = data[readPosition:readPosition+4]
                readPosition += 4
                sendersAddressVersionNumber, sendersAddressVersionNumberLength = decodeVarint(data[readPosition:readPosition+10])
                if sendersAddressVersionNumber == 1:
                    readPosition += sendersAddressVersionNumberLength
                    sendersStreamNumber, sendersStreamNumberLength = decodeVarint(data[readPosition:readPosition+10])
                    readPosition += sendersStreamNumberLength

                    sendersNLength, sendersNLengthLength = decodeVarint(data[readPosition:readPosition+10])
                    readPosition += sendersNLengthLength
                    sendersN = data[readPosition:readPosition+sendersNLength]
                    readPosition += sendersNLength
                    sendersELength, sendersELengthLength = decodeVarint(data[readPosition:readPosition+10])
                    readPosition += sendersELengthLength
                    sendersE = data[readPosition:readPosition+sendersELength]
                    readPosition += sendersELength
                    endOfThePublicKeyPosition = readPosition


                    messageEncodingType, messageEncodingTypeLength = decodeVarint(data[readPosition:readPosition+10])
                    readPosition += messageEncodingTypeLength
                    print 'Message Encoding Type:', messageEncodingType
                    messageLength, messageLengthLength = decodeVarint(data[readPosition:readPosition+10])
                    print 'message length:', messageLength
                    readPosition += messageLengthLength
                    message = data[readPosition:readPosition+messageLength]
                    #print 'First 150 characters of message:', repr(message[:150])
                    readPosition += messageLength
                    ackLength, ackLengthLength = decodeVarint(data[readPosition:readPosition+10])
                    #print 'ackLength:', ackLength
                    readPosition += ackLengthLength
                    ackData = data[readPosition:readPosition+ackLength]
                    readPosition += ackLength
                    payloadSigniture = data[readPosition:readPosition+sendersNLength] #We're using the length of the sender's n because it should match the signiture size.
                    sendersPubkey = rsa.PublicKey(convertStringToInt(sendersN),convertStringToInt(sendersE))
                    print 'sender\'s Pubkey', sendersPubkey
                    
                    #Check the cryptographic signiture
                    verifyPassed = False
                    try:
                        rsa.verify(data[:-len(payloadSigniture)],payloadSigniture, sendersPubkey)
                        print 'verify passed'
                        verifyPassed = True
                    except Exception, err:
                        print 'verify failed', err
                    if verifyPassed:
                        #Let's calculate the fromAddress.
                        sha = hashlib.new('sha512')
                        sha.update(sendersN+sendersE)
                        ripe = hashlib.new('ripemd160')
                        ripe.update(sha.digest())

                        #Let's store the public key in case we want to reply to this person.
                        #We don't have the correct nonce in order to send out a pubkey message so we'll just fill it with 1's. We won't be able to send this pubkey to others (without doing the proof of work ourselves, which this program is programmed to not do.)
                        t = (ripe.digest(),False,'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'+data[20+messageVersionLength:endOfThePublicKeyPosition],int(time.time())+2419200) #after one month we may remove this pub key from our database. (2419200 = a month)
                        sqlLock.acquire()
                        sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?)''')
                        sqlSubmitQueue.put(t)
                        sqlReturnQueue.get()
                        sqlLock.release()

                        blockMessage = False #Gets set to True if the user shouldn't see the message according to black or white lists.
                        fromAddress = encodeAddress(sendersAddressVersionNumber,sendersStreamNumber,ripe.digest())
                        if config.get('bitmessagesettings', 'blackwhitelist') == 'black': #If we are using a blacklist
                            t = (fromAddress,) 
                            sqlLock.acquire()
                            sqlSubmitQueue.put('''SELECT label, enabled FROM blacklist where address=?''')
                            sqlSubmitQueue.put(t)
                            queryreturn = sqlReturnQueue.get()
                            sqlLock.release()           
                            for row in queryreturn:
                                label, enabled = row
                                if enabled:
                                    print 'Message ignored because address is in blacklist.'
                                    blockMessage = True
                        else: #We're using a whitelist
                            t = (fromAddress,) 
                            sqlLock.acquire()
                            sqlSubmitQueue.put('''SELECT label, enabled FROM whitelist where address=?''')
                            sqlSubmitQueue.put(t)
                            queryreturn = sqlReturnQueue.get()
                            sqlLock.release()           
                            if queryreturn == []:
                                print 'Message ignored because address not in whitelist.'
                                blockMessage = True
                            for row in queryreturn: #It could be in the whitelist but disabled. Let's check.
                                label, enabled = row
                                if not enabled:
                                    print 'Message ignored because address in whitelist but not enabled.'
                                    blockMessage = True

                        if not blockMessage:
                            print 'fromAddress:', fromAddress
                            print 'First 150 characters of message:', repr(message[:150])

                            #Look up the destination address (my address) based on the destination ripe hash.
                            #I realize that I could have a data structure devoted to this task, or maintain an indexed table
                            #in the sql database, but I would prefer to minimize the number of data structures this program
                            #uses. Searching linearly through the user's short list of addresses doesn't take very long anyway.
                            configSections = config.sections()
                            for addressInKeysFile in configSections:
                                if addressInKeysFile <> 'bitmessagesettings':
                                    status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
                                    if hash == key:
                                        toAddress = addressInKeysFile
                                        toLabel = config.get(addressInKeysFile, 'label')
                                        if toLabel == '':
                                            toLabel = addressInKeysFile

                            if messageEncodingType == 2:
                                bodyPositionIndex = string.find(message,'\nBody:')
                                if bodyPositionIndex > 1:
                                    subject = message[8:bodyPositionIndex]
                                    body = message[bodyPositionIndex+6:]
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
                            print 'within recmsg, inventoryHash is', repr(inventoryHash)
                            if messageEncodingType <> 0:
                                sqlLock.acquire()
                                t = (inventoryHash,toAddress,fromAddress,subject,int(time.time()),body,'inbox')
                                sqlSubmitQueue.put('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?)''')
                                sqlSubmitQueue.put(t)
                                sqlReturnQueue.get()
                                sqlLock.release()
                                self.emit(SIGNAL("displayNewMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),inventoryHash,toAddress,fromAddress,subject,body)
                        #Now let's send the acknowledgement
                        #POW, = unpack('>Q',hashlib.sha512(hashlib.sha512(ackData[24:]).digest()).digest()[4:12])
                        #if POW <= 2**64 / ((len(ackData[24:])+payloadLengthExtraBytes) * averageProofOfWorkNonceTrialsPerByte):
                            #print 'The POW is strong enough that this ackdataPayload will be accepted by the Bitmessage network.'
                            #Currently PyBitmessage only supports sending a message with the acknowledgement in the form of a msg message. But future versions, and other clients, could send any object and this software will relay them. This can be used to relay identifying information, like your public key, through another Bitmessage host in case you believe that your Internet connection is being individually watched. You may pick a random address, hope its owner is online, and send a message with encoding type 0 so that they ignore the message but send your acknowledgement data over the network. If you send and receive many messages, it would also be clever to take someone else's acknowledgement data and use it for your own. Assuming that your message is delivered successfully, both will be acknowledged simultaneously (though if it is not delivered successfully, you will be in a pickle.)
                            #print 'self.data before:', repr(self.data)
                        #We'll need to make sure that our client will properly process the ackData; if the packet is malformed, we could clear out self.data and an attacker could use that behavior to determine that we were capable of decoding this message.
                        ackDataValidThusFar = True
                        if len(ackData) < 24:
                            print 'The length of ackData is unreasonably short. Not sending ackData.'
                            ackDataValidThusFar = False
                        if ackData[0:4] != '\xe9\xbe\xb4\xd9':
                            print 'Ackdata magic bytes were wrong. Not sending ackData.'
                            ackDataValidThusFar = False
                        if ackDataValidThusFar:
                            ackDataPayloadLength, = unpack('>L',ackData[16:20])
                            if len(ackData)-24 != ackDataPayloadLength:
                                print 'ackData payload length doesn\'t match the payload length specified in the header. Not sending ackdata.'
                                ackDataValidThusFar = False
                        if ackDataValidThusFar:
                            print 'ackData is valid. Will process it.'
                            #self.data = self.data[:self.payloadLength+24] + ackData + self.data[self.payloadLength+24:]
                            self.ackDataThatWeHaveYetToSend.append(ackData) #When we have processed all data, the processData function will pop the ackData out and process it as if it is a message received from our peer.
                            #print 'self.data after:', repr(self.data)
                        '''if ackData[4:16] == 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                            inventoryHash = calculateInventoryHash(ackData[24:])
                            #objectType = 'msg'
                            #inventory[inventoryHash] = (objectType, self.streamNumber, ackData[24:], embeddedTime) #We should probably be storing the embeddedTime of the ackData, not the embeddedTime of the original incoming msg message, but this is probably close enough.
                            #print 'sending the inv for the msg which is actually an acknowledgement (within sendmsg function)'
                            #self.broadcastinv(inventoryHash)
                            self.data[:payloadLength+24] + ackData + self.data[payloadLength+24:]
                        elif ackData[4:16] == 'getpubkey\x00\x00\x00':
                            #objectType = 'getpubkey'
                            #inventory[inventoryHash] = (objectType, self.streamNumber, ackData[24:], embeddedTime) #We should probably be storing the embeddedTime of the ackData, not the embeddedTime of the original incoming msg message, but this is probably close enough.
                            #print 'sending the inv for the getpubkey which is actually an acknowledgement (within sendmsg function)'
                            self.data[:payloadLength+24] + ackData + self.data[payloadLength+24:]
                        elif ackData[4:16] == 'pubkey\x00\x00\x00\x00\x00\x00':
                            #objectType = 'pubkey'
                            #inventory[inventoryHash] = (objectType, self.streamNumber, ackData[24:], embeddedTime) #We should probably be storing the embeddedTime of the ackData, not the embeddedTime of the original incoming msg message, but this is probably close enough.
                            #print 'sending the inv for a pubkey which is actually an acknowledgement (within sendmsg function)'
                            self.data[:payloadLength+24] + ackData + self.data[payloadLength+24:]
                        elif ackData[4:16] == 'broadcast\x00\x00\x00':
                            #objectType = 'broadcast'
                            #inventory[inventoryHash] = (objectType, self.streamNumber, ackData[24:], embeddedTime) #We should probably be storing the embeddedTime of the ackData, not the embeddedTime of the original incoming msg message, but this is probably close enough.
                            #print 'sending the inv for a broadcast which is actually an acknowledgement (within sendmsg function)'
                            self.data[:payloadLength+24] + ackData + self.data[payloadLength+24:]'''
                        #else:
                            #print 'ACK POW not strong enough to be accepted by the Bitmessage network.'

                else:
                    print 'This program cannot decode messages from addresses with versions higher than 1. Ignoring.'
                    statusbar = 'This program cannot decode messages from addresses with versions higher than 1. Ignoring it.'
                    self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
            else:
                print 'Error: Cannot decode incoming msg versions higher than 1. Assuming the sender isn\' being silly, you should upgrade Bitmessage because this message shall be ignored.'
                statusbar = 'Error: Cannot decode incoming msg versions higher than 1. Assuming the sender isn\' being silly, you should upgrade Bitmessage because this message shall be ignored.'
                self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
        else:
            printLock.acquire()
            print 'Decryption unsuccessful.'
            printLock.release()
        infile.close()
        outfile.close()

    #We have received a pubkey
    def recpubkey(self):
        #We must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient():
            print 'Proof of work in pubkey message insufficient.'
            return

        inventoryHash = calculateInventoryHash(self.data[24:self.payloadLength+24])
        inventoryLock.acquire()
        if inventoryHash in inventory:
            print 'We have already received this pubkey. Ignoring it.'
            inventoryLock.release()
            return
        elif isInSqlInventory(inventoryHash):
            print 'We have already received this pubkey (it is stored on disk in the SQL inventory). Ignoring it.'
            inventoryLock.release()
            return

        objectType = 'pubkey'
        inventory[inventoryHash] = (objectType, self.streamNumber, self.data[24:self.payloadLength+24], int(time.time()))
        inventoryLock.release()
        self.broadcastinv(inventoryHash)
        self.emit(SIGNAL("incrementNumberOfPubkeysProcessed()"))

        readPosition = 24 #for the message header
        readPosition += 8 #for the nonce
        bitfieldBehaviors = self.data[readPosition:readPosition+4]
        readPosition += 4 #for the bitfield of behaviors and features
        addressVersion, varintLength = decodeVarint(self.data[readPosition:readPosition+10])
        if addressVersion >= 2:
            print 'This version of Bitmessgae cannot handle version', addressVersion,'addresses.'
            return
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(self.data[readPosition:readPosition+10])
        readPosition += varintLength
        #ripe = self.data[readPosition:readPosition+20]
        #readPosition += 20 #for the ripe hash
        nLength, varintLength = decodeVarint(self.data[readPosition:readPosition+10])
        readPosition += varintLength
        nString = self.data[readPosition:readPosition+nLength]
        readPosition += nLength
        eLength, varintLength = decodeVarint(self.data[readPosition:readPosition+10])
        readPosition += varintLength
        eString = self.data[readPosition:readPosition+eLength]
        readPosition += eLength

        sha = hashlib.new('sha512')
        sha.update(nString+eString)
        ripeHasher = hashlib.new('ripemd160')
        ripeHasher.update(sha.digest())
        ripe = ripeHasher.digest()

        print 'within recpubkey, addressVersion', addressVersion
        print 'streamNumber', streamNumber
        print 'ripe', repr(ripe)
        print 'n=', convertStringToInt(nString)
        print 'e=', convertStringToInt(eString)

        t = (ripe,True,self.data[24:24+self.payloadLength],int(time.time())+604800) #after one week we may remove this pub key from our database.
        sqlLock.acquire()
        sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?)''')
        sqlSubmitQueue.put(t)
        sqlReturnQueue.get()
        sqlLock.release()
        print 'added foreign pubkey into our database'
        workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))

    #We have received a getpubkey message
    def recgetpubkey(self):
        if not self.isProofOfWorkSufficient():
            print 'Proof of work in getpubkey message insufficient.'
            return
        embeddedTime, = unpack('>I',self.data[32:36])
        if embeddedTime > int(time.time())+10800:
            print 'The time in this getpubkey message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time())-maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in this getpubkey message is too old. Ignoring it. Time:', embeddedTime
            return
        inventoryLock.acquire()
        inventoryHash = calculateInventoryHash(self.data[24:self.payloadLength+24])
        if inventoryHash in inventory:
            print 'We have already received this getpubkey request. Ignoring it.'
            inventoryLock.release()
            return
        elif isInSqlInventory(inventoryHash):
            print 'We have already received this getpubkey request (it is stored on disk in the SQL inventory). Ignoring it.'
            inventoryLock.release()
            return

        objectType = 'pubkeyrequest'
        inventory[inventoryHash] = (objectType, self.streamNumber, self.data[24:self.payloadLength+24], embeddedTime)
        inventoryLock.release()

        #Now let us make sure that the getpubkey request isn't too old or with a fake (future) time.

        addressVersionNumber, addressVersionLength = decodeVarint(self.data[36:42])
        streamNumber, streamNumberLength = decodeVarint(self.data[36+addressVersionLength:42+addressVersionLength])
        if streamNumber <> self.streamNumber:
            print 'The streamNumber', streamNumber, 'doesn\'t match our stream number:', self.streamNumber
            return

        #This getpubkey request is valid so far. Forward to peers.
        broadcastToSendDataQueues((self.streamNumber,'send',self.data[:self.payloadLength+24]))

        if addressVersionNumber > 1:
            print 'The addressVersionNumber of the pubkey is too high. Can\'t understand. Ignoring it.'
            return
        if self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength] in myAddressHashes:
            print 'Found getpubkey requested hash in my list of hashes.'
            #check to see whether we have already calculated the nonce and transmitted this key before
            sqlLock.acquire()#released at the bottom of this payload generation section
            t = (self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength],) #this prevents SQL injection
            sqlSubmitQueue.put('SELECT * FROM pubkeys WHERE hash=?')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            #print 'queryreturn', queryreturn

            if queryreturn == []:
                print 'pubkey request is for me but the pubkey is not in our database of pubkeys. Making it.'
                payload = '\x00\x00\x00\x01' #bitfield of features supported by me (see the wiki).
                payload += self.data[36:36+addressVersionLength+streamNumberLength]
                #print int(config.get(encodeAddress(addressVersionNumber,streamNumber,self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength]), 'n'))
                nString = convertIntToString(int(config.get(encodeAddress(addressVersionNumber,streamNumber,self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength]), 'n')))
                eString = convertIntToString(config.getint(encodeAddress(addressVersionNumber,streamNumber,self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength]), 'e'))
                payload += encodeVarint(len(nString))
                payload += nString
                payload += encodeVarint(len(eString))
                payload += eString

                nonce = 0
                trialValue = 99999999999999999999
                target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
                print '(For pubkey message) Doing proof of work...'
                initialHash = hashlib.sha512(payload).digest()
                while trialValue > target:
                    nonce += 1
                    trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
                    #trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + payload).digest()).digest()[4:12])
                print '(For pubkey message) Found proof of work', trialValue, 'Nonce:', nonce

                payload = pack('>Q',nonce) + payload
                t = (self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength],True,payload,int(time.time())+1209600) #after two weeks (1,209,600 seconds), we may remove our own pub key from our database. It will be regenerated and put back in the database if it is requested.
                sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?)''')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()

            #Now that we have the full pubkey message ready either from making it just now or making it earlier, we can send it out.
            t = (self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength],) #this prevents SQL injection
            sqlSubmitQueue.put('''SELECT * FROM pubkeys WHERE hash=? AND havecorrectnonce=1''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            if queryreturn == []:
                sys.stderr.write('Error: pubkey which we just put in our pubkey database suddenly is not there. Is the database malfunctioning?')
                sqlLock.release()
                return
            for row in queryreturn:
                hash, havecorrectnonce, payload, timeLastRequested = row
                if timeLastRequested < int(time.time())+604800: #if the last time anyone asked about this hash was this week, extend the time.
                    t = (int(time.time())+604800,hash)
                    sqlSubmitQueue.put('''UPDATE pubkeys set time=? WHERE hash=?''')
                    sqlSubmitQueue.put(t)
                    queryreturn = sqlReturnQueue.get()

            sqlLock.release()

            inventoryHash = calculateInventoryHash(payload)
            objectType = 'pubkey'
            inventory[inventoryHash] = (objectType, self.streamNumber, payload, int(time.time()))
            self.broadcastinv(inventoryHash)

        else:
            print 'Hash in getpubkey request is not for any of my keys.'
            #..but lets see if we have it stored from when it came in from someone else.
            t = (self.data[36+addressVersionLength+streamNumberLength:56+addressVersionLength+streamNumberLength],) #this prevents SQL injection
            sqlLock.acquire()
            sqlSubmitQueue.put('''SELECT hash, transmitdata, time FROM pubkeys WHERE hash=? AND havecorrectnonce=1''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()
            print 'queryreturn', queryreturn
            if queryreturn <> []:
                print 'we have the public key. sending it.'
                #We have it. Let's send it.
                for row in queryreturn:
                    hash, transmitdata, timeLastRequested = row
                    if timeLastRequested < int(time.time())+604800: #if the last time anyone asked about this hash was this week, extend the time.
                        t = (int(time.time())+604800,hash)
                        sqlSubmitQueue.put('''UPDATE pubkeys set time=? WHERE hash=? ''')
                        sqlSubmitQueue.put(t)
                        queryreturn = sqlReturnQueue.get()
                inventoryHash = calculateInventoryHash(transmitdata)
                objectType = 'pubkey'
                inventory[inventoryHash] = (objectType, self.streamNumber, transmitdata, int(time.time()))
                self.broadcastinv(inventoryHash)


    #We have received an inv message
    def recinv(self):
        numberOfItemsInInv, lengthOfVarint = decodeVarint(self.data[24:34])
        if numberOfItemsInInv == 1: #we'll just request this data from the person who advertised the object.
            for i in range(numberOfItemsInInv):
                if self.data[24+lengthOfVarint+(32*i):56+lengthOfVarint+(32*i)] in inventory:
                    print 'Inventory (in memory) has inventory item already.'
                elif isInSqlInventory(self.data[24+lengthOfVarint+(32*i):56+lengthOfVarint+(32*i)]):
                    print 'Inventory (SQL on disk) has inventory item already.'
                else:
                    self.sendgetdata(self.data[24+lengthOfVarint+(32*i):56+lengthOfVarint+(32*i)])
        else:
            print 'inv message lists', numberOfItemsInInv, 'objects.'
            for i in range(numberOfItemsInInv): #upon finishing dealing with an incoming message, the receiveDataThread will request a random object from the peer. This way if we get multiple inv messages from multiple peers which list mostly the same objects, we will make getdata requests for different random objects from the various peers.
                #print 'Adding object to self.objectsThatWeHaveYetToGet.'
                self.objectsThatWeHaveYetToGet[self.data[24+lengthOfVarint+(32*i):56+lengthOfVarint+(32*i)]] = 0
            print 'length of objectsThatWeHaveYetToGet', len(self.objectsThatWeHaveYetToGet)

    #Send a getdata message to our peer to request the object with the given hash
    def sendgetdata(self,hash):
        print 'sending getdata with hash', repr(hash)
        payload = '\x01' + hash
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData = headerData + 'getdata\x00\x00\x00\x00\x00'
        headerData = headerData + pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
        headerData = headerData + hashlib.sha512(payload).digest()[:4]
        self.sock.send(headerData + payload)

    #We have received a getdata request from our peer
    def recgetdata(self):
        value, lengthOfVarint = decodeVarint(self.data[24:34])
        #print 'Number of items in getdata request:', value
        try:
            for i in range(value):
                hash = self.data[24+lengthOfVarint+(i*32):56+lengthOfVarint+(i*32)]
                print 'getdata request for item:', repr(hash), 'length', len(hash)
                #print 'inventory is', inventory
                if hash in inventory:
                    objectType, streamNumber, payload, receivedTime = inventory[hash]
                    self.sendData(objectType,payload)
                else:
                    t = (hash,)
                    sqlLock.acquire()
                    sqlSubmitQueue.put('''select objecttype, payload from inventory where hash=?''')
                    sqlSubmitQueue.put(t)
                    queryreturn = sqlReturnQueue.get()
                    sqlLock.release()
                    if queryreturn <> []:
                        for row in queryreturn:
                            objectType, payload = row
                        self.sendData(objectType,payload)
                    else:
                        print 'Someone asked for an object with a getdata which is not in either our memory inventory or our SQL inventory. That shouldn\'t have happened.'
  
        except:
            pass   #someone is probably trying to cause a program error by, for example, making a request for 10 items but only including the hashes for 5.

    #Our peer has requested (in a getdata message) that we send an object.
    def sendData(self,objectType,payload):
        if objectType == 'pubkey':
            print 'sending pubkey'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData = headerData + 'pubkey\x00\x00\x00\x00\x00\x00'
            headerData = headerData + pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData = headerData + hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'pubkeyrequest':
            print 'sending pubkeyrequest'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData = headerData + 'getpubkey\x00\x00\x00'
            headerData = headerData + pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData = headerData + hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'msg':
            print 'sending msg'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData = headerData + 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            headerData = headerData + pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData = headerData + hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'broadcast':
            print 'sending broadcast'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData = headerData + 'broadcast\x00\x00\x00'
            headerData = headerData + pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData = headerData + hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'getpubkey':
            print 'sending getpubkey'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData = headerData + 'getpubkey\x00\x00\x00' #version command
            headerData = headerData + pack('>L',len(payload)) #payload length
            headerData = headerData + hashlib.sha512(payload).digest()[0:4]
            self.sock.send(headerData + payload)
        else:
            sys.stderr.write('Error: sendData has been asked to send a strange objectType: %s\n' % str(objectType))

    #Send an inv message with just one hash to all of our peers
    def broadcastinv(self,hash):
        print 'sending inv'
        #payload = '\x01' + pack('>H',objectType) + hash
        payload = '\x01' + hash
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData = headerData + 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData = headerData + pack('>L',len(payload)) 
        headerData = headerData + hashlib.sha512(payload).digest()[:4]
        printLock.acquire()
        print 'broadcasting inv with hash:', repr(hash)
        printLock.release()
        broadcastToSendDataQueues((self.streamNumber, 'send', headerData + payload))


    #We have received an addr message.
    def recaddr(self):
        listOfAddressDetailsToBroadcastToPeers = []
        numberOfAddressesIncluded = 0
        numberOfAddressesIncluded, lengthOfNumberOfAddresses = decodeVarint(self.data[24:29])

        if verbose >= 1:
            print 'addr message contains', numberOfAddressesIncluded, 'IP addresses.'
            #print 'lengthOfNumberOfAddresses', lengthOfNumberOfAddresses

        if numberOfAddressesIncluded > 1000:
            return
        needToWriteKnownNodesToDisk = False
        for i in range(0,numberOfAddressesIncluded):
            try:
                if self.data[40+lengthOfNumberOfAddresses+(34*i):52+lengthOfNumberOfAddresses+(34*i)] != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                    printLock.acquire()
                    print 'Skipping IPv6 address.', repr(self.data[40+lengthOfNumberOfAddresses+(34*i):56+lengthOfNumberOfAddresses+(34*i)])
                    printLock.release()
                    continue
                #print repr(self.data[6+lengthOfNumberOfAddresses+(34*i):18+lengthOfNumberOfAddresses+(34*i)])
            except Exception, err:
                if verbose >= 2:
                    printLock.acquire()
                    sys.stderr.write('ERROR TRYING TO UNPACK recaddr (to test for an IPv6 address). Message: %s\n' % str(err))
                    printLock.release()
                break #giving up on unpacking any more. We should still be connected however.

            try:
                recaddrStream, = unpack('>I',self.data[28+lengthOfNumberOfAddresses+(34*i):32+lengthOfNumberOfAddresses+(34*i)])
            except Exception, err:
                if verbose >= 2:
                    printLock.acquire()
                    sys.stderr.write('ERROR TRYING TO UNPACK recaddr (recaddrStream). Message: %s\n' % str(err))
                    printLock.release()
                break #giving up on unpacking any more. We should still be connected however.

            try:
                recaddrServices, = unpack('>Q',self.data[32+lengthOfNumberOfAddresses+(34*i):40+lengthOfNumberOfAddresses+(34*i)])
            except Exception, err:
                if verbose >= 2:
                    printLock.acquire()
                    sys.stderr.write('ERROR TRYING TO UNPACK recaddr (recaddrServices). Message: %s\n' % str(err))
                    printLock.release()
                break #giving up on unpacking any more. We should still be connected however.

            try:
                recaddrPort, = unpack('>H',self.data[56+lengthOfNumberOfAddresses+(34*i):58+lengthOfNumberOfAddresses+(34*i)])
            except Exception, err:
                if verbose >= 2:
                    printLock.acquire()
                    sys.stderr.write('ERROR TRYING TO UNPACK recaddr (recaddrPort). Message: %s\n' % str(err))
                    printLock.release()
                break #giving up on unpacking any more. We should still be connected however.
            #print 'Within recaddr(): IP', recaddrIP, ', Port', recaddrPort, ', i', i
            hostFromAddrMessage = socket.inet_ntoa(self.data[52+lengthOfNumberOfAddresses+(34*i):56+lengthOfNumberOfAddresses+(34*i)])
            #print 'hostFromAddrMessage', hostFromAddrMessage
            if hostFromAddrMessage == '127.0.0.1':
                continue
            timeSomeoneElseReceivedMessageFromThisNode, = unpack('>I',self.data[24+lengthOfNumberOfAddresses+(34*i):28+lengthOfNumberOfAddresses+(34*i)]) #This is the 'time' value in the received addr message.
            if hostFromAddrMessage not in knownNodes[recaddrStream]:
                if len(knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time())-10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800): #If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                    knownNodes[recaddrStream][hostFromAddrMessage] = (recaddrPort, timeSomeoneElseReceivedMessageFromThisNode)
                    print 'added new node', hostFromAddrMessage, 'to knownNodes.'
                    needToWriteKnownNodesToDisk = True
                    hostDetails = (timeSomeoneElseReceivedMessageFromThisNode, recaddrStream, recaddrServices, hostFromAddrMessage, recaddrPort)
                    listOfAddressDetailsToBroadcastToPeers.append(hostDetails)
            else:
                PORT, timeLastReceivedMessageFromThisNode = knownNodes[recaddrStream][hostFromAddrMessage]#PORT in this case is either the port we used to connect to the remote node, or the port that was specified by someone else in a past addr message.
                if (timeLastReceivedMessageFromThisNode < timeSomeoneElseReceivedMessageFromThisNode) and (timeSomeoneElseReceivedMessageFromThisNode < int(time.time())):
                    knownNodes[recaddrStream][hostFromAddrMessage] = (PORT, timeSomeoneElseReceivedMessageFromThisNode)
                    if PORT != recaddrPort:
                        print 'Strange occurance: The port specified in an addr message', str(recaddrPort),'does not match the port',str(PORT),'that this program (or some other peer) used to connect to it',str(hostFromAddrMessage),'. Perhaps they changed their port or are using a strange NAT configuration.'
        if needToWriteKnownNodesToDisk: #Runs if any nodes were new to us. Also, share those nodes with our peers.
            output = open(appdata + 'knownnodes.dat', 'wb')
            pickle.dump(knownNodes, output)
            output.close()
            self.broadcastaddr(listOfAddressDetailsToBroadcastToPeers)
        print 'knownNodes currently has', len(knownNodes[recaddrStream]), 'nodes for this stream.'

    #Function runs when we want to broadcast an addr message to all of our peers. Runs when we learn of nodes that we didn't previously know about and want to share them with our peers.
    def broadcastaddr(self,listOfAddressDetailsToBroadcastToPeers):
        numberOfAddressesInAddrMessage = len(listOfAddressDetailsToBroadcastToPeers)
        payload = ''
        for hostDetails in listOfAddressDetailsToBroadcastToPeers:
            timeLastReceivedMessageFromThisNode, streamNumber, services, host, port = hostDetails
            payload += pack('>I',timeLastReceivedMessageFromThisNode)
            payload += pack('>I',streamNumber)
            payload += pack('>q',services) #service bit flags offered by this node
            payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + socket.inet_aton(host)
            payload += pack('>H',port)#remote port

        payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
        datatosend = '\xE9\xBE\xB4\xD9addr\x00\x00\x00\x00\x00\x00\x00\x00'
        datatosend = datatosend + pack('>L',len(payload)) #payload length
        datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
        datatosend = datatosend + payload

        if verbose >= 2:
            printLock.acquire()
            print 'Broadcasting addr with # of entries:', numberOfAddressesInAddrMessage
            printLock.release()
        broadcastToSendDataQueues((self.streamNumber, 'send', datatosend))

    #Send a big addr message to our peer
    def sendaddr(self):
        addrsInMyStream = {}
        addrsInChildStreamLeft = {}
        addrsInChildStreamRight = {}
        #print 'knownNodes', knownNodes

        #We are going to share a maximum number of 1000 addrs with our peer. 500 from this stream, 250 from the left child stream, and 250 from the right child stream.

        if len(knownNodes[self.streamNumber]) > 0:
            for i in range(500):
                random.seed()
                HOST, = random.sample(knownNodes[self.streamNumber],  1)
                addrsInMyStream[HOST] = knownNodes[self.streamNumber][HOST]
        if len(knownNodes[self.streamNumber*2]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(knownNodes[self.streamNumber*2],  1)
                addrsInChildStreamLeft[HOST] = knownNodes[self.streamNumber*2][HOST]
        if len(knownNodes[(self.streamNumber*2)+1]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(knownNodes[(self.streamNumber*2)+1],  1)
                addrsInChildStreamRight[HOST] = knownNodes[(self.streamNumber*2)+1][HOST]

        numberOfAddressesInAddrMessage = 0
        payload = ''
        print 'addrsInMyStream.items()', addrsInMyStream.items()
        for HOST, value in addrsInMyStream.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time())- maximumAgeOfNodesThatIAdvertiseToOthers): #If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload +=  pack('>I',timeLastReceivedMessageFromThisNode)
                payload += pack('>I',self.streamNumber)
                payload += pack('>q',1) #service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + socket.inet_aton(HOST)
                payload += pack('>H',PORT)#remote port
        for HOST, value in addrsInChildStreamLeft.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time())- maximumAgeOfNodesThatIAdvertiseToOthers): #If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload += pack('>I',timeLastReceivedMessageFromThisNode)
                payload += pack('>I',self.streamNumber*2)
                payload += pack('>q',1) #service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + socket.inet_aton(HOST)
                payload += pack('>H',PORT)#remote port
        for HOST, value in addrsInChildStreamRight.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time())- maximumAgeOfNodesThatIAdvertiseToOthers): #If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload += pack('>I',timeLastReceivedMessageFromThisNode)
                payload += pack('>I',(self.streamNumber*2)+1)
                payload += pack('>q',1) #service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + socket.inet_aton(HOST)
                payload += pack('>H',PORT)#remote port

        payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
        datatosend = '\xE9\xBE\xB4\xD9addr\x00\x00\x00\x00\x00\x00\x00\x00'
        datatosend = datatosend + pack('>L',len(payload)) #payload length
        datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
        datatosend = datatosend + payload

        if verbose >= 2:
            printLock.acquire()
            print 'Sending addr with # of entries:', numberOfAddressesInAddrMessage
            printLock.release()
        self.sock.send(datatosend)

    #We have received a version message
    def recversion(self):
        if self.payloadLength < 83:
            #This version message is unreasonably short. Forget it.
            return
        elif not self.verackSent: #There is a potential exploit if we don't check to make sure that we have not already received and accepted a version message: An attacker could connect directly to us, send a msg message with the ackdata set to an invalid version message which would cause us to close the connection to the attacker thus proving that we were able to decode the message. Checking the connectionIsOrWasFullyEstablished variable would also suffice.
            self.remoteProtocolVersion, = unpack('>L',self.data[24:28])
            #print 'remoteProtocolVersion', self.remoteProtocolVersion
            self.myExternalIP = socket.inet_ntoa(self.data[64:68])
            #print 'myExternalIP', self.myExternalIP
            self.remoteNodeIncomingPort, = unpack('>H',self.data[94:96])
            #print 'remoteNodeIncomingPort', self.remoteNodeIncomingPort
            #print 'self.data[96:104]', repr(self.data[96:104])
            #print 'eightBytesOfRandomDataUsedToDetectConnectionsToSelf', repr(eightBytesOfRandomDataUsedToDetectConnectionsToSelf)
            useragentLength, lengthOfUseragentVarint = decodeVarint(self.data[104:108])
            readPosition = 104 + lengthOfUseragentVarint + useragentLength
            #Note that PyBitmessage curreutnly currentl supports a single stream per connection.
            numberOfStreamsInVersionMessage, lengthOfNumberOfStreamsInVersionMessage = decodeVarint(self.data[readPosition:])
            readPosition += lengthOfNumberOfStreamsInVersionMessage
            self.streamNumber, lengthOfRemoteStreamNumber = decodeVarint(self.data[readPosition:])
            print 'Remote node stream number:', self.streamNumber
            #If this was an incoming connection, then the sendData thread doesn't know the stream. We have to set it.
            if not self.initiatedConnection:
                broadcastToSendDataQueues((0,'setStreamNumber',(self.HOST,self.streamNumber)))
            if self.streamNumber != 1:
                self.sock.close()
                printLock.acquire()
                print 'Closed connection to', self.HOST, 'because they are interested in stream', self.steamNumber,'.'
                printLock.release()
                self.data = ''
                return
            if self.data[96:104] == eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
                self.sock.close()
                printLock.acquire()
                print 'Closing connection to myself: ', self.HOST
                printLock.release()
                self.data = ''
                return

            knownNodes[self.streamNumber][self.HOST] = (self.remoteNodeIncomingPort, int(time.time()))
            output = open(appdata + 'knownnodes.dat', 'wb')
            pickle.dump(knownNodes, output)
            output.close()



            #I've commented out this code because it should be up to the newer node to decide whether their protocol version is incompatiable with the remote node's version.
            '''if self.remoteProtocolVersion > 1:
                print 'The remote node''s protocol version is too new for this program to understand. Disconnecting. It is:', self.remoteProtocolVersion
                self.sock.close()
                self.selfInitiatedConnectionList.remove(self)
            else:'''
            self.sendverack()
            if self.initiatedConnection == False:
                self.sendversion()

    #Sends a version message
    def sendversion(self):
        global softwareVersion
        payload = ''
        payload += pack('>L',1) #protocol version.
        payload += pack('>q',1) #bitflags of the services I offer.
        payload += pack('>q',int(time.time()))

        payload += pack('>q',1) #boolservices of remote connection. How can I even know this for sure? This is probably ignored by the remote host.
        payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + socket.inet_aton(self.HOST)
        payload += pack('>H',self.PORT)#remote IPv6 and port

        payload += pack('>q',1) #bitflags of the services I offer.
        payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + pack('>L',2130706433) # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
        payload += pack('>H',config.getint('bitmessagesettings', 'port'))#my external IPv6 and port

        random.seed()
        payload += eightBytesOfRandomDataUsedToDetectConnectionsToSelf
        userAgent = '/PyBitmessage:' + softwareVersion + '/' #Length of userAgent must be less than 253.
        payload += pack('>B',len(userAgent)) #user agent string length. If the user agent is more than 252 bytes long, this code isn't going to work.
        payload += userAgent
        payload += encodeVarint(1) #The number of streams about which I care. PyBitmessage currently only supports 1.
        payload += encodeVarint(self.streamNumber)

        datatosend = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        datatosend = datatosend + 'version\x00\x00\x00\x00\x00' #version command
        datatosend = datatosend + pack('>L',len(payload)) #payload length
        datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
        datatosend = datatosend + payload

        printLock.acquire()
        print 'Sending version packet: ', repr(datatosend)
        printLock.release()
        self.sock.send(datatosend)
        #self.versionSent = 1

    #Sends a verack message
    def sendverack(self):
        print 'Sending verack'
        self.sock.sendall('\xE9\xBE\xB4\xD9\x76\x65\x72\x61\x63\x6B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
                                                                                                             #cf  83  e1  35
        self.verackSent = True
        if self.verackReceived == True:
            self.connectionFullyEstablished()

#Every connection to a peer has a sendDataThread (and also a receiveDataThread).
class sendDataThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.mailbox = Queue.Queue()
        sendDataQueues.append(self.mailbox)
        self.data = ''

    def setup(self,sock,HOST,PORT,streamNumber):
        self.sock = sock
        self.HOST = HOST
        self.PORT = PORT
        self.streamNumber = streamNumber
        self.lastTimeISentData = int(time.time()) #If this value increases beyond five minutes ago, we'll send a pong message to keep the connection alive.
        printLock.acquire()
        print 'The streamNumber of this sendDataThread at setup() is', self.streamNumber, self
        printLock.release()

    def sendVersionMessage(self):

        #Note that there is another copy of this version-sending code in the receiveData class which would need to be changed if you make changes here.
        global softwareVersion
        payload = ''
        payload += pack('>L',1) #protocol version.
        payload += pack('>q',1) #bitflags of the services I offer.
        payload += pack('>q',int(time.time()))

        payload += pack('>q',1) #boolservices of remote connection. How can I even know this for sure? This is probably ignored by the remote host.
        payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + socket.inet_aton(self.HOST)
        payload += pack('>H',self.PORT)#remote IPv6 and port

        payload += pack('>q',1) #bitflags of the services I offer.
        payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + pack('>L',2130706433) # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
        payload += pack('>H',config.getint('bitmessagesettings', 'port'))#my external IPv6 and port

        random.seed()
        payload += eightBytesOfRandomDataUsedToDetectConnectionsToSelf
        userAgent = '/PyBitmessage:' + softwareVersion + '/' #Length of userAgent must be less than 253.
        payload += pack('>B',len(userAgent)) #user agent string length. If the user agent is more than 252 bytes long, this code isn't going to work.
        payload += userAgent
        payload += encodeVarint(1) #The number of streams about which I care. PyBitmessage currently only supports 1 per connection.
        payload += encodeVarint(self.streamNumber)

        datatosend = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        datatosend = datatosend + 'version\x00\x00\x00\x00\x00' #version command
        datatosend = datatosend + pack('>L',len(payload)) #payload length
        datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
        datatosend = datatosend + payload

        printLock.acquire()
        print 'Sending version packet: ', repr(datatosend)
        printLock.release()
        self.sock.send(datatosend)
        self.versionSent = 1
        

    def run(self):
        message = ''
        while True:
            deststream,command,data = self.mailbox.get()
            #printLock.acquire()
            #print 'sendDataThread, destream:', deststream, ', Command:', command, ', ID:',id(self), ', HOST:', self.HOST
            #printLock.release()

            if deststream == self.streamNumber or deststream == 0:
                if command == 'shutdown':
                    if data == self.HOST or data == 'all':
                        printLock.acquire()
                        print 'sendDataThread thread (associated with', self.HOST,') ID:',id(self), 'shutting down now.'
                        self.sock.close()
                        sendDataQueues.remove(self.mailbox)
                        print 'len of sendDataQueues', len(sendDataQueues)
                        printLock.release()
                        break
                #When you receive an incoming connection, a sendDataThread is created even though you don't yet know what stream number the remote peer is interested in. They will tell you in a version message and if you too are interested in that stream then you will continue on with the connection and will set the streamNumber of this send data thread here:
                elif command == 'setStreamNumber':
                    hostInMessage, specifiedStreamNumber = data
                    if hostInMessage == self.HOST:
                        printLock.acquire()
                        print 'setting the stream number in the sendData thread (ID:',id(self), ') to', specifiedStreamNumber
                        printLock.release()
                        self.streamNumber = specifiedStreamNumber
                elif command == 'send':
                    try:
                        #To prevent some network analysis, 'leak' the data out to our peer after waiting a random amount of time.
                        random.seed()
                        time.sleep(random.randrange(0, 5)) 
                        self.sock.sendall(data)
                        self.lastTimeISentData = int(time.time())
                    except:
                        print 'self.sock.sendall failed'
                        self.sock.close()
                        sendDataQueues.remove(self.mailbox)
                        print 'sendDataThread thread', self, 'ending now'
                        break
                elif command == 'pong':
                    if self.lastTimeISentData < (int(time.time()) - 298):
                        #Send out a pong message to keep the connection alive.
                        printLock.acquire()
                        print 'Sending pong to', self.HOST, 'to keep connection alive.'
                        printLock.release()
                        try:
                            self.sock.sendall('\xE9\xBE\xB4\xD9\x70\x6F\x6E\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
                            self.lastTimeISentData = int(time.time())
                        except:
                            print 'self.sock.send pong failed'
                            self.sock.close()
                            sendDataQueues.remove(self.mailbox)
                            print 'sendDataThread thread', self, 'ending now'
                            break
            else:
                printLock.acquire()
                print 'sendDataThread ID:',id(self),'ignoring command', command,'because it is not in stream',deststream
                printLock.release()


#Wen you want to command a sendDataThread to do something, like shutdown or send some data, this function puts your data into the queues for each of the sendDataThreads. The sendDataThreads are responsible for putting their queue into (and out of) the sendDataQueues list.
def broadcastToSendDataQueues(data):
    #print 'running broadcastToSendDataQueues'
    for q in sendDataQueues:
        q.put((data))

def flushInventory():
    #Note that the singleCleanerThread clears out the inventory dictionary from time to time, although it only clears things that have been in the dictionary for a long time. This clears the inventory dictionary Now.
    sqlLock.acquire()
    for hash, storedValue in inventory.items():
        objectType, streamNumber, payload, receivedTime = storedValue
        t = (hash,objectType,streamNumber,payload,receivedTime)
        sqlSubmitQueue.put('''INSERT INTO inventory VALUES (?,?,?,?,?)''')
        sqlSubmitQueue.put(t)
        sqlReturnQueue.get()
        del inventory[hash]
    sqlLock.release()

def isInSqlInventory(hash):
    t = (hash,)
    sqlLock.acquire()
    sqlSubmitQueue.put('''select hash from inventory where hash=?''')
    sqlSubmitQueue.put(t)
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()
    if queryreturn == []:
        return False
    else:
        return True

def convertIntToString(n):
    a = __builtins__.hex(n)
    if a[-1:] == 'L':
        a = a[:-1]
    if (len(a) % 2) == 0:
        return a[2:].decode('hex')
    else:
        return ('0'+a[2:]).decode('hex')

def convertStringToInt(s):
    return int(s.encode('hex'), 16)

#This thread exists because SQLITE3 is so un-threadsafe that we must submit queries to it and it puts results back in a different queue. They won't let us just use locks.
class sqlThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        self.conn = sqlite3.connect(appdata + 'messages.dat' )
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        try:
            self.cur.execute( '''CREATE TABLE inbox (msgid blob, toaddress text, fromaddress text, subject text, received text, message text, folder text, UNIQUE(msgid) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''CREATE TABLE sent (msgid blob, toaddress text, toripe blob, fromaddress text, subject text, message text, ackdata blob, lastactiontime integer, status text, pubkeyretrynumber integer, msgretrynumber integer, folder text)''' )
            self.cur.execute( '''CREATE TABLE subscriptions (label text, address text, enabled bool)''' )
            self.cur.execute( '''CREATE TABLE addressbook (label text, address text)''' )
            self.cur.execute( '''CREATE TABLE blacklist (label text, address text, enabled bool)''' )
            self.cur.execute( '''CREATE TABLE whitelist (label text, address text, enabled bool)''' )
            self.cur.execute( '''CREATE TABLE pubkeys (hash blob, havecorrectnonce bool, transmitdata blob, time blob, UNIQUE(hash, havecorrectnonce, transmitdata) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''CREATE TABLE inventory (hash blob, objecttype text, streamnumber int, payload blob, receivedtime integer, UNIQUE(hash) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''CREATE TABLE knownnodes (timelastseen int, stream int, services blob, host blob, port blob, UNIQUE(host, stream, port) ON CONFLICT REPLACE)''' ) #This table isn't used in the program yet but I have a feeling that we'll need it.

            self.conn.commit()
            print 'Created messages database file'
        except Exception, err:
            if str(err) == 'table inbox already exists':
                print 'Database file already exists.'
            else:
                sys.stderr.write('ERROR trying to create database file (message.dat). Error message: %s\n' % str(err))
                sys.exit()
        
        try:
            testpayload = '\x00\x00'
            t = ('1234','True',testpayload,'12345678')
            self.cur.execute( '''INSERT INTO pubkeys VALUES(?,?,?,?)''',t)
            self.conn.commit()
            self.cur.execute('''SELECT transmitdata FROM pubkeys WHERE hash='1234' ''')
            queryreturn = self.cur.fetchall()
            for row in queryreturn:
                transmitdata, = row
            self.cur.execute('''DELETE FROM pubkeys WHERE hash='1234' ''')
            self.conn.commit()
            if transmitdata == '':
                sys.stderr.write('Problem: The version of SQLite you have cannot store Null values. Please download and install the latest revision of your version of Python (for example, the latest Python 2.7 revision) and try again.\n')
                sys.stderr.write('PyBitmessage will now exist very abruptly. You may now see threading errors related to this abrupt exit but the problem you need to solve is related to SQLite.\n\n')
                sys.exit()
        except Exception, err:
            print err

        while True:
            item = sqlSubmitQueue.get()
            parameters = sqlSubmitQueue.get()
            #print 'item', item
            #print 'parameters', parameters
            self.cur.execute(item, parameters)
            sqlReturnQueue.put(self.cur.fetchall())
            sqlSubmitQueue.task_done()
            self.conn.commit()
       

'''The singleCleaner class is a timer-driven thread that cleans data structures to free memory, resends messages when a remote node doesn't respond, and sends pong messages to keep connections alive if the network isn't busy.
It cleans these data structures in memory:
    inventory (moves data to the on-disk sql database)

It cleans these tables on the disk:
    inventory (clears data more than 2 days and 12 hours old)
    pubkeys (clears data older than the date specified in the table. This is because we won't want to hold pubkeys that show up randomly as long as those that we have actually have used.)

It resends messages when there has been no response:
    resends getpubkey messages in two days (then 4 days, then 8 days, etc...)
    resends msg messages in two days (then 4 days, then 8 days, etc...)


'''
class singleCleaner(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        timeWeLastClearedInventoryAndPubkeysTables = 0

        while True:
            time.sleep(300)
            sqlLock.acquire()
            for hash, storedValue in inventory.items():
                objectType, streamNumber, payload, receivedTime = storedValue
                if int(time.time())- 3600 > receivedTime:
                    t = (hash,objectType,streamNumber,payload,receivedTime)
                    sqlSubmitQueue.put('''INSERT INTO inventory VALUES (?,?,?,?,?)''')
                    sqlSubmitQueue.put(t)
                    sqlReturnQueue.get()
                    del inventory[hash]
            sqlLock.release()
            broadcastToSendDataQueues((0, 'pong', 'no data')) #commands the sendData threads to send out a pong message if they haven't sent anything else in the last five minutes. The socket timeout-time is 10 minutes.
            if timeWeLastClearedInventoryAndPubkeysTables < int(time.time()) - 7380:
                timeWeLastClearedInventoryAndPubkeysTables = int(time.time())
                #inventory (moves data from the inventory data structure to the on-disk sql database)
                sqlLock.acquire()
                #inventory (clears data more than 2 days and 12 hours old)
                t = (int(time.time())-lengthOfTimeToLeaveObjectsInInventory,)
                sqlSubmitQueue.put('''DELETE FROM inventory WHERE receivedtime<?''')
                sqlSubmitQueue.put(t)
                sqlReturnQueue.get()

                #pubkeys (clears data older than the date specified in the table. This is because we won't want to hold pubkeys that show up randomly as long as those that we have actually have used (unless someone can come up with a decent attack based on this behavior.))
                t = (int(time.time()),)
                sqlSubmitQueue.put('''DELETE FROM pubkeys WHERE time<?''')
                sqlSubmitQueue.put(t)
                sqlReturnQueue.get()

                t = ()
                sqlSubmitQueue.put('''select toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, pubkeyretrynumber, msgretrynumber FROM sent WHERE (status='findingpubkey' OR status='sentmessage') ''')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                for row in queryreturn:
                    toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, pubkeyretrynumber, msgretrynumber = row
                    if status == 'findingpubkey':
                        if int(time.time()) - lastactiontime > (maximumAgeOfAnObjectThatIAmWillingToAccept * (2 ** (pubkeyretrynumber))):
                            print 'It has been a long time and we haven\'t heard a response to our getpubkey request. Sending again.'
                            try:
                                del neededPubkeys[toripe]
                            except:
                                pass
                            workerQueue.put(('sendmessage',toaddress))
                            t = (int(time.time()),pubkeyretrynumber+1,toripe)
                            sqlSubmitQueue.put('''UPDATE sent SET lastactiontime=?, pubkeyretrynumber=? WHERE toripe=?''')
                            sqlSubmitQueue.put(t)
                            sqlReturnQueue.get()
                            #self.emit(SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"),toripe,'Public key requested again. ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
                    else:# status == sentmessage
                        if int(time.time()) - lastactiontime > (maximumAgeOfAnObjectThatIAmWillingToAccept * (2 ** (msgretrynumber))):
                            print 'It has been a long time and we haven\'t heard an acknowledgement to our msg. Sending again.'
                            t = (int(time.time()),msgretrynumber+1,'findingpubkey',ackdata)
                            sqlSubmitQueue.put('''UPDATE sent SET lastactiontime=?, msgretrynumber=?, status=? WHERE ackdata=?''')
                            sqlSubmitQueue.put(t)
                            sqlReturnQueue.get()
                            #self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Message sent again because the acknowledgement was never received. ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
                            workerQueue.put(('sendmessage',toaddress))
                sqlLock.release()

#This thread, of which there is only one, does the heavy lifting: calculating POWs.
class singleWorker(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        sqlLock.acquire()
        sqlSubmitQueue.put('SELECT toripe FROM sent WHERE status=?')
        sqlSubmitQueue.put(('findingpubkey',))
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        for row in queryreturn:
            toripe, = row
            neededPubkeys[toripe] = 0

        self.sendBroadcast() #just in case there are any proof of work tasks for Broadcasts that have yet to be sent.

        #Now let us see if there are any proofs of work for msg messages that we have yet to complete..
        sqlLock.acquire()
        t = ('doingpow',)
        sqlSubmitQueue.put('SELECT toripe FROM sent WHERE status=?')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        for row in queryreturn:
            toripe, = row
            self.sendMsg(toripe)

        while True:
            command, data = workerQueue.get()
            #statusbar = 'The singleWorker thread is working on work.'
            #self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
            if command == 'sendmessage':
                toAddress = data
                toStatus,toAddressVersionNumber,toStreamNumber,toRipe = decodeAddress(toAddress)
                #print 'message type', type(message)
                #print repr(message.toUtf8())
                #print str(message.toUtf8())
                sqlLock.acquire()
                sqlSubmitQueue.put('SELECT * FROM pubkeys WHERE hash=?')
                sqlSubmitQueue.put((toRipe,))
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()
                #print 'queryreturn', queryreturn
                if queryreturn == []:
                    #We'll need to request the pub key because we don't have it.
                    if not toRipe in neededPubkeys:
                        neededPubkeys[toRipe] = 0
                        print 'requesting pubkey:', repr(toRipe)
                        self.requestPubKey(toAddressVersionNumber,toStreamNumber,toRipe)
                    else:
                        print 'We have already requested this pubkey (the ripe hash is in neededPubkeys). We will re-request again soon.'
                        self.emit(SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"),toRipe,'Public key was requested earlier. Receiver must be offline. Will retry.')
                else:
                    print 'We already have the necessary public key.'
                    self.sendMsg(toRipe)
            elif command == 'sendbroadcast':
                print 'Within WorkerThread, processing sendbroadcast command.'
                fromAddress,subject,message = data
                self.sendBroadcast()

            elif command == 'newpubkey':
                toAddressVersion,toStreamNumber,toRipe = data
                if toRipe in neededPubkeys:
                    print 'We have been awaiting the arrival of this pubkey.'
                    del neededPubkeys[toRipe]
                    self.sendMsg(toRipe)
                else:
                    print 'We don\'t need this pub key. We didn\'t ask for it. Pubkey hash:', repr(toRipe)

            workerQueue.task_done()

    def sendBroadcast(self):
        sqlLock.acquire()
        t = ('broadcastpending',)
        sqlSubmitQueue.put('SELECT fromaddress, subject, message, ackdata FROM sent WHERE status=?')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        for row in queryreturn:
            #print 'within sendMsg, row is:', row
            #msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status = row
            fromaddress, subject, body, ackdata = row
            messageToTransmit = '\x02'
            messageToTransmit += encodeVarint(len('Subject:' + subject + '\n' + 'Body:' + body))  #Type 2 is simple UTF-8 message encoding.
            messageToTransmit += 'Subject:' + subject + '\n' + 'Body:' + body

            #We need the all the integers for our private key in order to sign our message, and we need our public key to send with the message.
            n = config.getint(fromaddress, 'n')
            e = config.getint(fromaddress, 'e')
            d = config.getint(fromaddress, 'd')
            p = config.getint(fromaddress, 'p')
            q = config.getint(fromaddress, 'q')
            nString = convertIntToString(n)
            eString = convertIntToString(e)
            myPubkey = rsa.PublicKey(n,e)
            myPrivatekey = rsa.PrivateKey(n,e,d,p,q)
            status,addressVersionNumber,streamNumber,ripe = decodeAddress(fromaddress)
            
            #The payload of the broadcast message starts with a POW, but that will be added later.
            payload = pack('>I',(int(time.time())))
            payload += encodeVarint(1) #broadcast version
            payload += encodeVarint(addressVersionNumber)
            payload += encodeVarint(streamNumber)
            payload += ripe
            payload += encodeVarint(len(nString))
            payload += nString
            payload += encodeVarint(len(eString))
            payload += eString
            payload += messageToTransmit
            signature = rsa.sign(messageToTransmit,myPrivatekey,'SHA-512')
            print 'signature', repr(signature)
            payload += signature

            print 'nString', repr(nString)
            print 'eString', repr(eString)

            nonce = 0
            trialValue = 99999999999999999999
            target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
            print '(For broadcast message) Doing proof of work...'
            initialHash = hashlib.sha512(payload).digest()
            while trialValue > target:
                nonce += 1
                trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
            print '(For broadcast message) Found proof of work', trialValue, 'Nonce:', nonce

            payload = pack('>Q',nonce) + payload

            inventoryHash = calculateInventoryHash(payload)
            objectType = 'broadcast'
            inventory[inventoryHash] = (objectType, streamNumber, payload, int(time.time()))
            print 'sending inv (within sendBroadcast function)'
            payload = '\x01' + inventoryHash
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData = headerData + 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            headerData = headerData + pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData = headerData + hashlib.sha512(payload).digest()[:4]
            broadcastToSendDataQueues((streamNumber, 'send', headerData + payload))

            self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Broadcast sent at '+strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))

            #Update the status of the message in the 'sent' table to have a 'broadcastsent' status
            sqlLock.acquire()
            t = ('broadcastsent',int(time.time()),fromaddress, subject, body,'broadcastpending')
            sqlSubmitQueue.put('UPDATE sent SET status=?, lastactiontime=? WHERE fromaddress=? AND subject=? AND message=? AND status=?')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()

    def sendMsg(self,toRipe):
        sqlLock.acquire()
        t = ('doingpow','findingpubkey',toRipe)       
        sqlSubmitQueue.put('UPDATE sent SET status=? WHERE status=? AND toripe=?')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()

        t = ('doingpow',toRipe)
        sqlSubmitQueue.put('SELECT toaddress, fromaddress, subject, message, ackdata FROM sent WHERE status=? AND toripe=?')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        for row in queryreturn:
            toaddress, fromaddress, subject, message, ackdata = row
            ackdataForWhichImWatching[ackdata] = 0
            status,addressVersionNumber,toStreamNumber,hash = decodeAddress(toaddress)
            #if hash == toRipe:
            self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Doing work necessary to send the message.')
            printLock.acquire()
            print 'Found the necessary message that needs to be sent with this pubkey.'
            print 'First 150 characters of message:', message[:150]
            printLock.release()
            payload = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' #this run of nulls allows the true message receiver to identify his message
            payload += '\x01' #Message version.
            payload += '\x00\x00\x00\x01'
            fromStatus,fromAddressVersionNumber,fromStreamNumber,fromHash = decodeAddress(fromaddress)
            payload += encodeVarint(fromAddressVersionNumber)
            payload += encodeVarint(fromStreamNumber)

            sendersN = convertIntToString(config.getint(fromaddress, 'n'))
            payload += encodeVarint(len(sendersN))
            payload += sendersN

            sendersE = convertIntToString(config.getint(fromaddress, 'e'))
            payload += encodeVarint(len(sendersE))
            payload += sendersE

            payload += '\x02' #Type 2 is simple UTF-8 message encoding.
            messageToTransmit = 'Subject:' + subject + '\n' + 'Body:' + message
            payload += encodeVarint(len(messageToTransmit))
            payload += messageToTransmit

            #Later, if anyone impliments clients that don't send the ack_data, then we should probably check here to make sure that the receiver will make use of this ack_data and not attach it if not.
            fullAckPayload = self.generateFullAckMessage(ackdata,toStreamNumber)
            payload += encodeVarint(len(fullAckPayload))
            payload += fullAckPayload
            sendersPrivKey = rsa.PrivateKey(config.getint(fromaddress, 'n'),config.getint(fromaddress, 'e'),config.getint(fromaddress, 'd'),config.getint(fromaddress, 'p'),config.getint(fromaddress, 'q'))

            payload += rsa.sign(payload,sendersPrivKey,'SHA-512')

            sqlLock.acquire()
            sqlSubmitQueue.put('SELECT * FROM pubkeys WHERE hash=?')
            sqlSubmitQueue.put((toRipe,))
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()

            for row in queryreturn:
                hash, havecorrectnonce, pubkeyPayload, timeLastRequested = row

            readPosition = 8 #to bypass the nonce
            bitfieldBehaviors = pubkeyPayload[8:12]
            readPosition += 4 #to bypass the bitfield of behaviors
            addressVersion, addressVersionLength = decodeVarint(pubkeyPayload[readPosition:readPosition+10])
            readPosition += addressVersionLength
            streamNumber, streamNumberLength = decodeVarint(pubkeyPayload[readPosition:readPosition+10])
            readPosition += streamNumberLength
            nLength, nLengthLength = decodeVarint(pubkeyPayload[readPosition:readPosition+10])
            readPosition += nLengthLength
            n = convertStringToInt(pubkeyPayload[readPosition:readPosition+nLength])
            readPosition += nLength
            eLength, eLengthLength = decodeVarint(pubkeyPayload[readPosition:readPosition+10])
            readPosition += eLengthLength
            e = convertStringToInt(pubkeyPayload[readPosition:readPosition+eLength])
            receiversPubkey = rsa.PublicKey(n,e)

            infile = cStringIO.StringIO(payload)
            outfile = cStringIO.StringIO()
            #print 'Encrypting using public key:', receiversPubkey
            encrypt_bigfile(infile,outfile,receiversPubkey)

            encrypted = outfile.getvalue()
            infile.close()
            outfile.close()

            nonce = 0
            trialValue = 99999999999999999999
            embeddedTime = pack('>I',(int(time.time())))
            encodedStreamNumber = encodeVarint(toStreamNumber)
            #We are now dropping the unencrypted data in payload since it has already been encrypted and replacing it with the encrypted payload that we will send out.
            payload = embeddedTime + encodedStreamNumber + encrypted
            target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
            print '(For msg message) Doing proof of work. Target:', target
            powStartTime = time.time()
            initialHash = hashlib.sha512(payload).digest()
            while trialValue > target:
                nonce += 1
                trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
            print '(For msg message) Found proof of work', trialValue, 'Nonce:', nonce
            print 'POW took', int(time.time()-powStartTime), 'seconds.', nonce/(time.time()-powStartTime), 'nonce trials per second.'
            payload = pack('>Q',nonce) + payload

            inventoryHash = calculateInventoryHash(payload)
            objectType = 'msg'
            inventory[inventoryHash] = (objectType, toStreamNumber, payload, int(time.time()))
            self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Message sent. Waiting on acknowledgement. Sent on ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
            print 'sending inv (within sendmsg function)'
            payload = '\x01' + inventoryHash
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData = headerData + 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            headerData = headerData + pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData = headerData + hashlib.sha512(payload).digest()[:4]
            broadcastToSendDataQueues((toStreamNumber, 'send', headerData + payload))

            #Update the status of the message in the 'sent' table to have a 'sent' status
            sqlLock.acquire()
            t = ('sentmessage',toaddress, fromaddress, subject, message,'doingpow')
            sqlSubmitQueue.put('UPDATE sent SET status=? WHERE toaddress=? AND fromaddress=? AND subject=? AND message=? AND status=?')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()

            #Update the time in the pubkey sql database so that we'll hold the foreign pubkey for quite a while longer
            t = (int(time.time())+31449600,toRipe) #Hold the pubkey for an entire year from today
            sqlSubmitQueue.put('UPDATE pubkeys SET time=? WHERE hash=?')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()

            sqlLock.release()


    def requestPubKey(self,addressVersionNumber,streamNumber,ripe):
        payload = pack('>I',int(time.time()))
        payload += encodeVarint(addressVersionNumber)
        payload += encodeVarint(streamNumber)
        payload += ripe
        nonce = 0
        trialValue = 99999999999999999999
        #print 'trial value', trialValue
        statusbar = 'Doing the computations necessary to request the recipient''s public key. (Doing the proof-of-work.)'
        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
        self.emit(SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"),ripe,'Doing work necessary to request public key.')
        print 'Doing proof-of-work necessary to send getpubkey message.'
        target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
        initialHash = hashlib.sha512(payload).digest()
        while trialValue > target:
            nonce += 1
            trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
        print 'Found proof of work', trialValue, 'Nonce:', nonce

        payload = pack('>Q',nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 'getpubkey'
        inventory[inventoryHash] = (objectType, streamNumber, payload, int(time.time()))
        print 'sending inv (for the getpubkey message)'
        #payload = '\x01' + pack('>H',objectType) + hash
        payload = '\x01' + inventoryHash
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData = headerData + 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData = headerData + pack('>L',len(payload))
        headerData = headerData + hashlib.sha512(payload).digest()[:4]
        broadcastToSendDataQueues((streamNumber, 'send', headerData + payload))

        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Broacasting the public key request. The recipient''s software must be on. This program will auto-retry if they are offline.')
        self.emit(SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"),ripe,'Sending public key request. Waiting for reply. Requested at ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
        broadcastToSendDataQueues((streamNumber, 'send', headerData + payload))

    def generateFullAckMessage(self,ackdata,toStreamNumber):
        nonce = 0
        trialValue = 99999999999999999999
        embeddedTime = pack('>I',(int(time.time())))
        encodedStreamNumber = encodeVarint(toStreamNumber)
        payload = embeddedTime + encodedStreamNumber + ackdata
        target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
        printLock.acquire()
        print '(For ack message) Doing proof of work...'
        printLock.release()
        powStartTime = time.time()
        initialHash = hashlib.sha512(payload).digest()
        while trialValue > target:
            nonce += 1
            trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
        printLock.acquire()
        print '(For ack message) Found proof of work', trialValue, 'Nonce:', nonce
        print 'POW took', int(time.time()-powStartTime), 'seconds.', nonce/(time.time()-powStartTime), 'nonce trials per second.'
        printLock.release()
        payload = pack('>Q',nonce) + payload
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData = headerData + 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData = headerData + pack('>L',len(payload))
        headerData = headerData + hashlib.sha512(payload).digest()[:4]
        return headerData + payload

class addressGenerator(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def setup(self,streamNumber,label):
        self.streamNumber = streamNumber
        self.label = label

    def run(self):
        statusbar = 'Generating new ' + str(config.getint('bitmessagesettings', 'bitstrength')) + ' bit RSA key. This takes a minute on average. If you want to generate multiple addresses now, you can; they will queue.'
        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
        (pubkey, privkey) = rsa.newkeys(config.getint('bitmessagesettings', 'bitstrength'))
        print privkey['n']
        print privkey['e']
        print privkey['d']
        print privkey['p']
        print privkey['q']

        sha = hashlib.new('sha512')
        #sha.update(str(pubkey.n)+str(pubkey.e))
        sha.update(convertIntToString(pubkey.n)+convertIntToString(pubkey.e))
        ripe = hashlib.new('ripemd160')
        ripe.update(sha.digest())
        address = encodeAddress(1,self.streamNumber,ripe.digest())

        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Finished generating address. Writing to keys.dat')
        config.add_section(address)
        config.set(address,'label',self.label)
        config.set(address,'enabled','true')
        config.set(address,'decoy','false')
        config.set(address,'n',str(privkey['n']))
        config.set(address,'e',str(privkey['e']))
        config.set(address,'d',str(privkey['d']))
        config.set(address,'p',str(privkey['p']))
        config.set(address,'q',str(privkey['q']))
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)

        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Done generating address')
        self.emit(SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),self.label,address,str(self.streamNumber))


class iconGlossaryDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_iconGlossaryDialog()
        self.ui.setupUi(self) 
        self.parent = parent
        self.ui.labelPortNumber.setText('You are using TCP port ' + str(config.getint('bitmessagesettings', 'port')) + '. (This can be changed in the settings).')
        QtGui.QWidget.resize(self,QtGui.QWidget.sizeHint(self))

class helpDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_helpDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.labelHelpURI.setOpenExternalLinks(True)
        QtGui.QWidget.resize(self,QtGui.QWidget.sizeHint(self))

class aboutDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.labelVersion.setText('version ' + softwareVersion)

class settingsDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_settingsDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.checkBoxStartOnLogon.setChecked(config.getboolean('bitmessagesettings', 'startonlogon'))
        self.ui.checkBoxMinimizeToTray.setChecked(config.getboolean('bitmessagesettings', 'minimizetotray'))
        self.ui.checkBoxShowTrayNotifications.setChecked(config.getboolean('bitmessagesettings', 'showtraynotifications'))
        self.ui.checkBoxStartInTray.setChecked(config.getboolean('bitmessagesettings', 'startintray'))
        if 'darwin' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.checkBoxMinimizeToTray.setDisabled(True)
            self.ui.checkBoxShowTrayNotifications.setDisabled(True)
            self.ui.checkBoxStartInTray.setDisabled(True)
            self.ui.labelSettingsNote.setText('Options have been disabled because they either arn\'t applicable or because they haven\'t yet been implimented for your operating system.')
        elif 'linux' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.labelSettingsNote.setText('Options have been disabled because they either arn\'t applicable or because they haven\'t yet been implimented for your operating system.')
        #On the Network settings tab:
        self.ui.lineEditTCPPort.setText(str(config.get('bitmessagesettings', 'port')))
        self.ui.checkBoxAuthentication.setChecked(config.getboolean('bitmessagesettings', 'socksauthentication'))
        if str(config.get('bitmessagesettings', 'socksproxytype')) == 'none':
            self.ui.comboBoxProxyType.setCurrentIndex(0)
            self.ui.lineEditSocksHostname.setEnabled(False)
            self.ui.lineEditSocksPort.setEnabled(False)
            self.ui.lineEditSocksUsername.setEnabled(False)
            self.ui.lineEditSocksPassword.setEnabled(False)
            self.ui.checkBoxAuthentication.setEnabled(False)
        elif str(config.get('bitmessagesettings', 'socksproxytype')) == 'SOCKS4a':
            self.ui.comboBoxProxyType.setCurrentIndex(1)
            self.ui.lineEditTCPPort.setEnabled(False)
        elif str(config.get('bitmessagesettings', 'socksproxytype')) == 'SOCKS5':
            self.ui.comboBoxProxyType.setCurrentIndex(2)
            self.ui.lineEditTCPPort.setEnabled(False)
        
        self.ui.lineEditSocksHostname.setText(str(config.get('bitmessagesettings', 'sockshostname')))
        self.ui.lineEditSocksPort.setText(str(config.get('bitmessagesettings', 'socksport')))
        self.ui.lineEditSocksUsername.setText(str(config.get('bitmessagesettings', 'socksusername')))
        self.ui.lineEditSocksPassword.setText(str(config.get('bitmessagesettings', 'sockspassword')))
        QtCore.QObject.connect(self.ui.comboBoxProxyType, QtCore.SIGNAL("currentIndexChanged(int)"), self.comboBoxProxyTypeChanged)

    def comboBoxProxyTypeChanged(self,comboBoxIndex):
        if comboBoxIndex == 0:
            self.ui.lineEditSocksHostname.setEnabled(False)
            self.ui.lineEditSocksPort.setEnabled(False)
            self.ui.lineEditSocksUsername.setEnabled(False)
            self.ui.lineEditSocksPassword.setEnabled(False)
            self.ui.checkBoxAuthentication.setEnabled(False)
            self.ui.lineEditTCPPort.setEnabled(True)
        elif comboBoxIndex == 1 or comboBoxIndex == 2:
            self.ui.lineEditSocksHostname.setEnabled(True)
            self.ui.lineEditSocksPort.setEnabled(True)
            self.ui.checkBoxAuthentication.setEnabled(True)
            if self.ui.checkBoxAuthentication.isChecked():
                self.ui.lineEditSocksUsername.setEnabled(True)
                self.ui.lineEditSocksPassword.setEnabled(True)
            self.ui.lineEditTCPPort.setEnabled(False)

class NewSubscriptionDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewSubscriptionDialog() #Jonathan changed this line
        self.ui.setupUi(self) #Jonathan left this line alone
        self.parent = parent
        QtCore.QObject.connect(self.ui.lineEditSubscriptionAddress, QtCore.SIGNAL("textChanged(QString)"), self.subscriptionAddressChanged)

    def subscriptionAddressChanged(self,QString):
        status,a,b,c = decodeAddress(str(QString))
        if status == 'missingbm':
            self.ui.labelSubscriptionAddressCheck.setText('The address should start with ''BM-''')
        elif status == 'checksumfailed':
            self.ui.labelSubscriptionAddressCheck.setText('The address is not typed or copied correctly (the checksum failed).')
        elif status == 'versiontoohigh':
            self.ui.labelSubscriptionAddressCheck.setText('The version number of this address is higher than this software can support. Please upgrade Bitmessage.')
        elif status == 'invalidcharacters':
            self.ui.labelSubscriptionAddressCheck.setText('The address contains invalid characters.')
        elif status == 'success':
            self.ui.labelSubscriptionAddressCheck.setText('Address is valid.')

class NewAddressDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewAddressDialog() #Jonathan changed this line
        self.ui.setupUi(self) #Jonathan left this line alone
        self.parent = parent
        row = 1
        while self.parent.ui.tableWidgetYourIdentities.item(row-1,1):
            self.ui.radioButtonExisting.click()
            #print self.parent.ui.tableWidgetYourIdentities.item(row-1,1).text()
            self.ui.comboBoxExisting.addItem(self.parent.ui.tableWidgetYourIdentities.item(row-1,1).text())
            row += 1
        #QtGui.QWidget.resize(self,QtGui.QWidget.sizeHint(self))
        


class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow() #Jonathan changed this line
        self.ui.setupUi(self) #Jonathan left this line alone

        if 'win32' in sys.platform or 'win64' in sys.platform:
            #Auto-startup for Windows
            RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            self.settings = QSettings(RUN_PATH, QSettings.NativeFormat)
            self.settings.remove("PyBitmessage") #In case the user moves the program and the registry entry is no longer valid, this will delete the old registry entry.
            if config.getboolean('bitmessagesettings', 'startonlogon'):
                self.settings.setValue("PyBitmessage",sys.argv[0])
        elif 'darwin' in sys.platform:
            #startup for mac
            pass
        elif 'linux' in sys.platform:
            #startup for linux
            pass

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setIcon( QtGui.QIcon(':/newPrefix/images/can-icon-16px.png') )
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"
        QtCore.QObject.connect(self.trayIcon, QtCore.SIGNAL(traySignal), self.__icon_activated)
        menu = QtGui.QMenu()
        self.exitAction = menu.addAction("Exit", self.close)
        self.trayIcon.setContextMenu(menu)
        #I'm currently under the impression that Mac users have different expectations for the tray icon. They don't necessairly expect it to open the main window when clicked and they still expect a program showing a tray icon to also be in the dock.
        if 'darwin' in sys.platform:
            self.trayIcon.show()

        #FILE MENU and other buttons
        QtCore.QObject.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"), self.close)
        QtCore.QObject.connect(self.ui.actionManageKeys, QtCore.SIGNAL("triggered()"), self.click_actionManageKeys)
        QtCore.QObject.connect(self.ui.pushButtonNewAddress, QtCore.SIGNAL("clicked()"), self.click_NewAddressDialog)
        QtCore.QObject.connect(self.ui.comboBoxSendFrom, QtCore.SIGNAL("activated(int)"),self.redrawLabelFrom)
        QtCore.QObject.connect(self.ui.pushButtonAddAddressBook, QtCore.SIGNAL("clicked()"), self.click_pushButtonAddAddressBook)
        QtCore.QObject.connect(self.ui.pushButtonAddSubscription, QtCore.SIGNAL("clicked()"), self.click_pushButtonAddSubscription)
        QtCore.QObject.connect(self.ui.pushButtonAddBlacklist, QtCore.SIGNAL("clicked()"), self.click_pushButtonAddBlacklist)
        QtCore.QObject.connect(self.ui.pushButtonSend, QtCore.SIGNAL("clicked()"), self.click_pushButtonSend)
        QtCore.QObject.connect(self.ui.pushButtonLoadFromAddressBook, QtCore.SIGNAL("clicked()"), self.click_pushButtonLoadFromAddressBook)
        QtCore.QObject.connect(self.ui.radioButtonBlacklist, QtCore.SIGNAL("clicked()"), self.click_radioButtonBlacklist)
        QtCore.QObject.connect(self.ui.radioButtonWhitelist, QtCore.SIGNAL("clicked()"), self.click_radioButtonWhitelist)
        QtCore.QObject.connect(self.ui.pushButtonStatusIcon, QtCore.SIGNAL("clicked()"), self.click_pushButtonStatusIcon)
        QtCore.QObject.connect(self.ui.actionSettings, QtCore.SIGNAL("triggered()"), self.click_actionSettings)
        QtCore.QObject.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"), self.click_actionAbout)
        QtCore.QObject.connect(self.ui.actionHelp, QtCore.SIGNAL("triggered()"), self.click_actionHelp)

        #Popup menu for the Inbox tab
        self.ui.inboxContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionReply = self.ui.inboxContextMenuToolbar.addAction("Reply", self.on_action_InboxReply)
        self.actionAddSenderToAddressBook = self.ui.inboxContextMenuToolbar.addAction("Add sender to your Address Book", self.on_action_InboxAddSenderToAddressBook)
        self.actionTrashInboxMessage = self.ui.inboxContextMenuToolbar.addAction("Move to Trash", self.on_action_InboxTrash)
        #self.actionDisable = self.ui.inboxContextMenuToolbar.addAction("Disable", self.on_action_YourIdentitiesDisable)
        #self.actionClipboard = self.ui.inboxContextMenuToolbar.addAction("Copy address to clipboard", self.on_action_YourIdentitiesClipboard)
        self.ui.tableWidgetInbox.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetInbox, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuInbox)
        self.popMenuInbox = QtGui.QMenu( self )
        self.popMenuInbox.addAction( self.actionReply )
        self.popMenuInbox.addAction( self.actionAddSenderToAddressBook )
        self.popMenuInbox.addSeparator()
        self.popMenuInbox.addAction( self.actionTrashInboxMessage )


        #Popup menu for the Your Identities tab
        self.ui.addressContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionNew = self.ui.addressContextMenuToolbar.addAction("New", self.on_action_YourIdentitiesNew)
        self.actionEnable = self.ui.addressContextMenuToolbar.addAction("Enable", self.on_action_YourIdentitiesEnable)
        self.actionDisable = self.ui.addressContextMenuToolbar.addAction("Disable", self.on_action_YourIdentitiesDisable)
        self.actionClipboard = self.ui.addressContextMenuToolbar.addAction("Copy address to clipboard", self.on_action_YourIdentitiesClipboard)
        self.ui.tableWidgetYourIdentities.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetYourIdentities, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuYourIdentities)
        self.popMenu = QtGui.QMenu( self )
        self.popMenu.addAction( self.actionNew )
        self.popMenu.addSeparator()
        self.popMenu.addAction( self.actionClipboard )
        self.popMenu.addSeparator()
        self.popMenu.addAction( self.actionEnable )
        self.popMenu.addAction( self.actionDisable )

        #Popup menu for the Address Book page
        self.ui.addressBookContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionAddressBookNew = self.ui.addressBookContextMenuToolbar.addAction("New", self.on_action_AddressBookNew)
        self.actionAddressBookDelete = self.ui.addressBookContextMenuToolbar.addAction("Delete", self.on_action_AddressBookDelete)
        self.actionAddressBookClipboard = self.ui.addressBookContextMenuToolbar.addAction("Copy address to clipboard", self.on_action_AddressBookClipboard)
        self.actionAddressBookSend = self.ui.addressBookContextMenuToolbar.addAction("Send message to this address", self.on_action_AddressBookSend)
        self.ui.tableWidgetAddressBook.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuAddressBook)
        self.popMenuAddressBook = QtGui.QMenu( self )
        self.popMenuAddressBook.addAction( self.actionAddressBookNew )
        self.popMenuAddressBook.addAction( self.actionAddressBookDelete )
        self.popMenuAddressBook.addSeparator()
        self.popMenuAddressBook.addAction( self.actionAddressBookSend )
        self.popMenuAddressBook.addAction( self.actionAddressBookClipboard )


        #Popup menu for the Subscriptions page
        self.ui.subscriptionsContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionsubscriptionsNew = self.ui.subscriptionsContextMenuToolbar.addAction("New", self.on_action_SubscriptionsNew)
        self.actionsubscriptionsDelete = self.ui.subscriptionsContextMenuToolbar.addAction("Delete", self.on_action_SubscriptionsDelete)
        self.actionsubscriptionsClipboard = self.ui.subscriptionsContextMenuToolbar.addAction("Copy address to clipboard", self.on_action_SubscriptionsClipboard)
        self.ui.tableWidgetSubscriptions.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetSubscriptions, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuSubscriptions)
        self.popMenuSubscriptions = QtGui.QMenu( self )
        self.popMenuSubscriptions.addAction( self.actionsubscriptionsNew )
        self.popMenuSubscriptions.addAction( self.actionsubscriptionsDelete )
        self.popMenuSubscriptions.addSeparator()
        self.popMenuSubscriptions.addAction( self.actionsubscriptionsClipboard )


        #Initialize the user's list of addresses on the 'Your Identities' tab.
        configSections = config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile <> 'bitmessagesettings':
                isEnabled = config.getboolean(addressInKeysFile, 'enabled')
                newItem = QtGui.QTableWidgetItem(unicode(config.get(addressInKeysFile, 'label'),'utf-8)'))
                if not isEnabled:
                    newItem.setTextColor(QtGui.QColor(128,128,128))
                self.ui.tableWidgetYourIdentities.insertRow(0)
                self.ui.tableWidgetYourIdentities.setItem(0, 0, newItem)
                newItem = QtGui.QTableWidgetItem(addressInKeysFile)
                newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                if not isEnabled:
                    newItem.setTextColor(QtGui.QColor(128,128,128))
                self.ui.tableWidgetYourIdentities.setItem(0, 1, newItem)
                newItem = QtGui.QTableWidgetItem(str(addressStream(addressInKeysFile)))
                newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                if not isEnabled:
                    newItem.setTextColor(QtGui.QColor(128,128,128))
                self.ui.tableWidgetYourIdentities.setItem(0, 2, newItem)
                if isEnabled:
                    status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
        
        self.sqlLookup = sqlThread()
        self.sqlLookup.start()

        self.reloadMyAddressHashes()
        self.reloadBroadcastSendersForWhichImWatching()


        #Load inbox from messages database file
        sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message FROM inbox where folder='inbox' ORDER BY received''')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        for row in queryreturn:
            msgid, toAddress, fromAddress, subject, received, message, = row


            try:
                if toAddress == '[Broadcast subscribers]':
                    toLabel = '[Broadcast subscribers]'
                else:
                    toLabel = config.get(toAddress, 'label')
            except:
                toLabel = ''
            if toLabel == '':
                toLabel = toAddress

            fromLabel = ''
            t = (fromAddress,)
            sqlSubmitQueue.put('''select label from addressbook where address=?''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()

            if queryreturn <> []:
                for row in queryreturn:
                    fromLabel, = row

            self.ui.tableWidgetInbox.insertRow(0)
            newItem =  QtGui.QTableWidgetItem(unicode(toLabel,'utf-8'))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            newItem.setData(Qt.UserRole,str(toAddress))
            self.ui.tableWidgetInbox.setItem(0,0,newItem)
            if fromLabel == '':
                newItem =  QtGui.QTableWidgetItem(unicode(fromAddress,'utf-8'))
            else:
                newItem =  QtGui.QTableWidgetItem(unicode(fromLabel,'utf-8'))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            newItem.setData(Qt.UserRole,str(fromAddress))
            self.ui.tableWidgetInbox.setItem(0,1,newItem)
            newItem =  QtGui.QTableWidgetItem(unicode(subject,'utf-8'))
            newItem.setData(Qt.UserRole,unicode(message,'utf-8)'))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetInbox.setItem(0,2,newItem)
            newItem =  myTableWidgetItem(strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(received))))
            newItem.setData(Qt.UserRole,QByteArray(msgid))
            newItem.setData(33,int(received))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetInbox.setItem(0,3,newItem)
            #self.ui.textEditInboxMessage.setText(self.ui.tableWidgetInbox.item(0,2).data(Qt.UserRole).toPyObject())

        #Load Sent items from database
        sqlSubmitQueue.put('SELECT toaddress, fromaddress, subject, message, status, ackdata, lastactiontime FROM sent ORDER BY lastactiontime')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        for row in queryreturn:
            toAddress, fromAddress, subject, message, status, ackdata, lastactiontime = row
            try:
                fromLabel = config.get(fromAddress, 'label')
            except:
                fromLabel = ''
            if fromLabel == '':
                fromLabel = fromAddress

            toLabel = ''
            t = (toAddress,)
            sqlSubmitQueue.put('''select label from addressbook where address=?''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()

            if queryreturn <> []:
                for row in queryreturn:
                    toLabel, = row

            self.ui.tableWidgetSent.insertRow(0)
            if toLabel == '':
                newItem =  QtGui.QTableWidgetItem(unicode(toAddress,'utf-8'))
            else:
                newItem =  QtGui.QTableWidgetItem(unicode(toLabel,'utf-8'))
            newItem.setData(Qt.UserRole,str(toAddress))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetSent.setItem(0,0,newItem)
            if fromLabel == '':
                newItem =  QtGui.QTableWidgetItem(unicode(fromAddress,'utf-8'))
            else:
                newItem =  QtGui.QTableWidgetItem(unicode(fromLabel,'utf-8'))
            newItem.setData(Qt.UserRole,str(fromAddress))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetSent.setItem(0,1,newItem)
            newItem =  QtGui.QTableWidgetItem(unicode(subject,'utf-8'))
            newItem.setData(Qt.UserRole,unicode(message,'utf-8)'))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetSent.setItem(0,2,newItem)
            if status == 'findingpubkey':
                newItem =  myTableWidgetItem('Waiting on their public key. Will request it again soon.')
            elif status == 'sentmessage':
                newItem =  myTableWidgetItem('Message sent. Waiting on acknowledgement. Sent at ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(lastactiontime)))
            elif status == 'doingpow':
                newItem =  myTableWidgetItem('Need to do work to send message. Work is queued.')
            elif status == 'ackreceived':
                newItem =  myTableWidgetItem('Acknowledgement of the message received ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(lastactiontime))))
            elif status == 'broadcastpending':
                newItem =  myTableWidgetItem('Doing the work necessary to send broadcast...')
            elif status == 'broadcastsent':
                newItem =  myTableWidgetItem('Broadcast on ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(lastactiontime))))
            else:
                newItem =  myTableWidgetItem('Unknown status.  ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(lastactiontime))))
            newItem.setData(Qt.UserRole,ackdata)
            newItem.setData(33,int(lastactiontime))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetSent.setItem(0,3,newItem)
       
        #Initialize the address book
        sqlSubmitQueue.put('SELECT * FROM addressbook')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        for row in queryreturn:
            label, address = row
            self.ui.tableWidgetAddressBook.insertRow(0)
            newItem =  QtGui.QTableWidgetItem(unicode(label,'utf-8'))
            self.ui.tableWidgetAddressBook.setItem(0,0,newItem)
            newItem =  QtGui.QTableWidgetItem(address)
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetAddressBook.setItem(0,1,newItem)

        #Initialize the Subscriptions
        sqlSubmitQueue.put('SELECT label, address FROM subscriptions')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        for row in queryreturn:
            label, address = row
            self.ui.tableWidgetSubscriptions.insertRow(0)
            newItem =  QtGui.QTableWidgetItem(unicode(label,'utf-8'))
            self.ui.tableWidgetSubscriptions.setItem(0,0,newItem)
            newItem =  QtGui.QTableWidgetItem(address)
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetSubscriptions.setItem(0,1,newItem)

        #Initialize the Blacklist or Whitelist
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            self.loadBlackWhiteList()
        else:
            self.ui.tabWidget.setTabText(6,'Whitelist')
            self.ui.radioButtonWhitelist.click()
            self.loadBlackWhiteList()


        #Initialize the ackdataForWhichImWatching data structure using data from the sql database.
        sqlSubmitQueue.put('''SELECT ackdata FROM sent where (status='sentmessage' OR status='doingpow')''')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        for row in queryreturn:
            ackdata,  = row
            print 'Watching for ackdata', repr(ackdata)
            ackdataForWhichImWatching[ackdata] = 0

        QtCore.QObject.connect(self.ui.tableWidgetYourIdentities, QtCore.SIGNAL("itemChanged(QTableWidgetItem *)"), self.tableWidgetYourIdentitiesItemChanged)
        QtCore.QObject.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL("itemChanged(QTableWidgetItem *)"), self.tableWidgetAddressBookItemChanged)
        QtCore.QObject.connect(self.ui.tableWidgetSubscriptions, QtCore.SIGNAL("itemChanged(QTableWidgetItem *)"), self.tableWidgetSubscriptionsItemChanged)
        QtCore.QObject.connect(self.ui.tableWidgetInbox, QtCore.SIGNAL("itemSelectionChanged ()"), self.tableWidgetInboxItemClicked)
        QtCore.QObject.connect(self.ui.tableWidgetSent, QtCore.SIGNAL("itemSelectionChanged ()"), self.tableWidgetSentItemClicked)

        #Put the colored icon on the status bar
        #self.ui.pushButtonStatusIcon.setIcon(QIcon(":/newPrefix/images/yellowicon.png"))
        self.statusbar = self.statusBar()
        self.statusbar.insertPermanentWidget(0,self.ui.pushButtonStatusIcon)
        self.ui.labelStartupTime.setText('Since startup on ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
        self.numberOfMessagesProcessed = 0
        self.numberOfBroadcastsProcessed = 0
        self.numberOfPubkeysProcessed = 0

#Below this point, it would be good if all of the necessary global data structures were initialized.

        self.rerenderComboBoxSendFrom()

        self.listOfOutgoingSynSenderThreads = [] #if we don't maintain this list, the threads will get garbage-collected.

        self.connectToStream(1)

        self.singleListenerThread = singleListener()
        self.singleListenerThread.start()
        QtCore.QObject.connect(self.singleListenerThread, QtCore.SIGNAL("passObjectThrough(PyQt_PyObject)"), self.connectObjectToSignals)
        

        self.singleCleanerThread = singleCleaner()
        self.singleCleanerThread.start()
        QtCore.QObject.connect(self.singleCleanerThread, QtCore.SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByHash)

        self.workerThread = singleWorker()
        
        #self.workerThread.setup(workerQueue)
        self.workerThread.start()
        QtCore.QObject.connect(self.workerThread, QtCore.SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByHash)
        QtCore.QObject.connect(self.workerThread, QtCore.SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByAckdata)

    def click_actionManageKeys(self):
        if 'darwin' in sys.platform or 'linux' in sys.platform:
            reply = QtGui.QMessageBox.information(self, 'keys.dat?','You may manage your keys by editing the keys.dat file stored in\n' + appdata + '\nIt is important that you back up this file.', QMessageBox.Ok)
        elif sys.platform == 'win32' or sys.platform == 'win64':
            reply = QtGui.QMessageBox.question(self, 'Open keys.dat?','You may manage your keys by editing the keys.dat file stored in\n' + appdata + '\nIt is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.openKeysFile()
            else:
                pass

    def openKeysFile(self):
        if 'linux' in sys.platform:
            subprocess.call(["xdg-open", file])
        else:
            os.startfile(appdata + '\\keys.dat')

    def changeEvent(self, event):
        if config.getboolean('bitmessagesettings', 'minimizetotray') and not 'darwin' in sys.platform:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.windowState() & QtCore.Qt.WindowMinimized:
                    self.hide()
                    self.trayIcon.show()
                    #self.hidden = True
                    if 'win32' in sys.platform or 'win64' in sys.platform:
                        self.setWindowFlags(Qt.ToolTip)
                elif event.oldState() & QtCore.Qt.WindowMinimized:
                    #The window state has just been changed to Normal/Maximised/FullScreen
                    pass
            #QtGui.QWidget.changeEvent(self, event)

    def __icon_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            if 'linux' in sys.platform:
                self.trayIcon.hide()
                self.setWindowFlags(Qt.Window)
                self.show()
            elif 'win32' in sys.platform or 'win64' in sys.platform:
                self.trayIcon.hide()
                self.setWindowFlags(Qt.Window)
                self.show()
                self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                self.activateWindow()
            elif 'darwin' in sys.platform:
                #self.trayIcon.hide() #this line causes a segmentation fault
                #self.setWindowFlags(Qt.Window)
                #self.show()
                self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                self.activateWindow()
            
    def incrementNumberOfMessagesProcessed(self):
        self.numberOfMessagesProcessed += 1
        self.ui.labelMessageCount.setText('Processed ' + str(self.numberOfMessagesProcessed) + ' person-to-person messages.')

    def incrementNumberOfBroadcastsProcessed(self):
        self.numberOfBroadcastsProcessed += 1
        self.ui.labelBroadcastCount.setText('Processed ' + str(self.numberOfBroadcastsProcessed) + ' broadcast messages.')
      
    def incrementNumberOfPubkeysProcessed(self):
        self.numberOfPubkeysProcessed += 1
        self.ui.labelPubkeyCount.setText('Processed ' + str(self.numberOfPubkeysProcessed) + ' public keys.')

    def updateNetworkStatusTab(self,streamNumber,connectionCount):
        global statusIconColor
        #print 'updating network status tab'
        totalNumberOfConnectionsFromAllStreams = 0 #One would think we could use len(sendDataQueues) for this, but sendData threads don't remove themselves from sendDataQueues fast enough for len(sendDataQueues) to be accurate here.
        for currentRow in range(self.ui.tableWidgetConnectionCount.rowCount()):
            rowStreamNumber = int(self.ui.tableWidgetConnectionCount.item(currentRow,0).text())
            if streamNumber == rowStreamNumber:
                self.ui.tableWidgetConnectionCount.item(currentRow,1).setText(str(connectionCount))
                totalNumberOfConnectionsFromAllStreams += connectionCount
        self.ui.labelTotalConnections.setText('Total Connections: ' + str(totalNumberOfConnectionsFromAllStreams))
        if totalNumberOfConnectionsFromAllStreams > 0 and statusIconColor == 'red': #FYI: The 'singlelistener' thread sets the icon color to green when it receives an incoming connection, meaning that the user's firewall is configured correctly.
            self.setStatusIcon('yellow')
        elif totalNumberOfConnectionsFromAllStreams == 0:
            self.setStatusIcon('red')

    def setStatusIcon(self,color):
        global statusIconColor
        #print 'setting status icon color'
        if color == 'red':
            self.ui.pushButtonStatusIcon.setIcon(QIcon(":/newPrefix/images/redicon.png"))
            statusIconColor = 'red'
        if color == 'yellow':
            if self.statusBar().currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusBar().showMessage('')
            self.ui.pushButtonStatusIcon.setIcon(QIcon(":/newPrefix/images/yellowicon.png"))
            statusIconColor = 'yellow'
        if color == 'green':
            if self.statusBar().currentMessage() == 'Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.':
                self.statusBar().showMessage('')
            self.ui.pushButtonStatusIcon.setIcon(QIcon(":/newPrefix/images/greenicon.png"))
            statusIconColor = 'green'

    def updateSentItemStatusByHash(self,toRipe,textToDisplay):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            toAddress = str(self.ui.tableWidgetSent.item(i,0).data(Qt.UserRole).toPyObject())
#            messageState = str(self.ui.tableWidgetSent.item(i,3).data(Qt.UserRole).toPyObject())
            status,addressVersionNumber,streamNumber,ripe = decodeAddress(toAddress)
            if ripe == toRipe:
                self.ui.tableWidgetSent.item(i,3).setText(unicode(textToDisplay,'utf-8'))
                #if textToDisplay == 'Sent':
                #    self.ui.tableWidgetSent.item(i,3).setData(Qt.UserRole,'sent')

    def updateSentItemStatusByAckdata(self,ackdata,textToDisplay):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            toAddress = str(self.ui.tableWidgetSent.item(i,0).data(Qt.UserRole).toPyObject())
            tableAckdata = self.ui.tableWidgetSent.item(i,3).data(Qt.UserRole).toPyObject()
            status,addressVersionNumber,streamNumber,ripe = decodeAddress(toAddress)
            if ackdata == tableAckdata:
                self.ui.tableWidgetSent.item(i,3).setText(unicode(textToDisplay,'utf-8'))
                #if textToDisplay == 'Sent':
                #    self.ui.tableWidgetSent.item(i,3).setData(Qt.UserRole,'sent')

    def rerenderInboxFromLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            addressToLookup = str(self.ui.tableWidgetInbox.item(i,1).data(Qt.UserRole).toPyObject())
            fromLabel = ''
            t = (addressToLookup,)
            sqlLock.acquire()
            sqlSubmitQueue.put('''select label from addressbook where address=?''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()

            if queryreturn <> []:
                for row in queryreturn:
                    fromLabel, = row
                    self.ui.tableWidgetInbox.item(i,1).setText(unicode(fromLabel,'utf-8'))
            else:
                #It might be a broadcast message. We should check for that label.
                sqlLock.acquire()
                sqlSubmitQueue.put('''select label from subscriptions where address=?''')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()

                if queryreturn <> []:
                    for row in queryreturn:
                        fromLabel, = row
                        self.ui.tableWidgetInbox.item(i,1).setText(unicode(fromLabel,'utf-8'))


    def rerenderInboxToLabels(self):
        for i in range(self.ui.tableWidgetInbox.rowCount()):
            toAddress = str(self.ui.tableWidgetInbox.item(i,0).data(Qt.UserRole).toPyObject())
            try:
                toLabel = config.get(toAddress, 'label')
            except:
                toLabel = ''
            if toLabel == '':
                toLabel = toAddress
            self.ui.tableWidgetInbox.item(i,0).setText(unicode(toLabel,'utf-8'))
            
    def rerenderSentFromLabels(self):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            fromAddress = str(self.ui.tableWidgetSent.item(i,1).data(Qt.UserRole).toPyObject())
            try:
                fromLabel = config.get(fromAddress, 'label')
            except:
                fromLabel = ''
            if fromLabel == '':
                fromLabel = fromAddress
            self.ui.tableWidgetSent.item(i,1).setText(unicode(fromLabel,'utf-8'))

    def rerenderSentToLabels(self):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            addressToLookup = str(self.ui.tableWidgetSent.item(i,0).data(Qt.UserRole).toPyObject())
            toLabel = ''
            t = (addressToLookup,)
            sqlSubmitQueue.put('''select label from addressbook where address=?''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()

            if queryreturn <> []:
                for row in queryreturn:
                    toLabel, = row
                    self.ui.tableWidgetSent.item(i,0).setText(unicode(toLabel,'utf-8'))
     
    def click_pushButtonSend(self):
        self.statusBar().showMessage('')
        toAddresses = str(self.ui.lineEditTo.text())
        fromAddress = str(self.ui.labelFrom.text())
        subject = str(self.ui.lineEditSubject.text().toUtf8())
        message = str(self.ui.textEditMessage.document().toPlainText().toUtf8())
        if self.ui.radioButtonSpecific.isChecked(): #To send a message to specific people (rather than broadcast)
            toAddressesList = [s.strip() for s in toAddresses.replace(',', ';').split(';')]
            toAddressesList = list(set(toAddressesList)) #remove duplicate addresses. If the user has one address with a BM- and the same address without the BM-, this will not catch it. They'll send the message to the person twice.
            for toAddress in toAddressesList:
                if toAddress <> '':
                    status,addressVersionNumber,streamNumber,ripe = decodeAddress(toAddress)
                    if status <> 'success':
                        print 'Status bar!', 'Error: Could not decode', toAddress, ':', status
                        if status == 'missingbm':
                            self.statusBar().showMessage('Error: Bitmessage addresses start with BM-   Please check ' + toAddress)
                        if status == 'checksumfailed':
                            self.statusBar().showMessage('Error: The address ' + toAddress+' is not typed or copied correctly. Please check it.')
                        if status == 'invalidcharacters':
                            self.statusBar().showMessage('Error: The address '+ toAddress+ ' contains invalid characters. Please check it.')
                        if status == 'versiontoohigh':
                            self.statusBar().showMessage('Error: The address version in '+ toAddress+ ' is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.')
                    elif fromAddress == '':
                        print 'Status bar!', 'Error: you must specify a From address.'
                        self.statusBar().showMessage('Error: You must specify a From address. If you don''t have one, go to the ''Your Identities'' tab.')
                    else:
                        toAddress = addBMIfNotPresent(toAddress)
                        self.statusBar().showMessage('')
                        if connectionsCount[streamNumber] == 0:
                            self.statusBar().showMessage('Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.')
                        ackdata = ''
                        for i in range(4): #This will make 32 bytes of random data.
                            random.seed()
                            ackdata += pack('>Q',random.randrange(1, 18446744073709551615))
                        sqlLock.acquire()
                        t = ('',toAddress,ripe,fromAddress,subject,message,ackdata,int(time.time()),'findingpubkey',1,1,'sent')
                        sqlSubmitQueue.put('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''')
                        sqlSubmitQueue.put(t)
                        sqlReturnQueue.get()
                        sqlLock.release()
                        workerQueue.put(('sendmessage',toAddress))

                        try:
                            fromLabel = config.get(fromAddress, 'label')
                        except:
                            fromLabel = ''
                        if fromLabel == '':
                            fromLabel = fromAddress

                        toLabel = ''

                        t = (toAddress,)
                        sqlLock.acquire()
                        sqlSubmitQueue.put('''select label from addressbook where address=?''')
                        sqlSubmitQueue.put(t)
                        queryreturn = sqlReturnQueue.get()
                        sqlLock.release()
                        if queryreturn <> []:
                            for row in queryreturn:
                                toLabel, = row

                        self.ui.tableWidgetSent.insertRow(0)
                        if toLabel == '':
                            newItem =  QtGui.QTableWidgetItem(unicode(toAddress,'utf-8'))
                        else:
                            newItem =  QtGui.QTableWidgetItem(unicode(toLabel,'utf-8'))
                        newItem.setData(Qt.UserRole,str(toAddress))
                        self.ui.tableWidgetSent.setItem(0,0,newItem)

                        if fromLabel == '':
                            newItem =  QtGui.QTableWidgetItem(unicode(fromAddress,'utf-8'))
                        else:
                            newItem =  QtGui.QTableWidgetItem(unicode(fromLabel,'utf-8'))
                        newItem.setData(Qt.UserRole,str(fromAddress))
                        self.ui.tableWidgetSent.setItem(0,1,newItem)
                        newItem =  QtGui.QTableWidgetItem(unicode(subject,'utf-8)'))
                        newItem.setData(Qt.UserRole,unicode(message,'utf-8)'))
                        self.ui.tableWidgetSent.setItem(0,2,newItem)
                        newItem =  myTableWidgetItem('Just pressed ''send'' '+strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
                        newItem.setData(Qt.UserRole,ackdata)
                        newItem.setData(33,int(time.time()))
                        self.ui.tableWidgetSent.setItem(0,3,newItem)

                        self.ui.textEditSentMessage.setText(self.ui.tableWidgetSent.item(0,2).data(Qt.UserRole).toPyObject())

                        self.ui.labelFrom.setText('')
                        self.ui.tabWidget.setCurrentIndex(2)
                else:
                    self.statusBar().showMessage('Your \'To\' field is empty.')
        else: #User selected 'Broadcast'
            if fromAddress == '':
                print 'Status bar!', 'Error: you must specify a From address.'
                self.statusBar().showMessage('Error: You must specify a From address. If you don\'t have one, go to the \'Your Identities\' tab.')
            else:
                self.statusBar().showMessage('')
                ackdata = ''
                #We don't actually need the ackdata for acknowledgement since this is a broadcast message, but we can use it to update the user interface when the POW is done generating.
                for i in range(4): #This will make 32 bytes of random data.
                    random.seed()
                    ackdata += pack('>Q',random.randrange(1, 18446744073709551615))
                toAddress = '[Broadcast subscribers]'
                ripe = ''
                sqlLock.acquire()
                t = ('',toAddress,ripe,fromAddress,subject,message,ackdata,int(time.time()),'broadcastpending',1,1,'sent')
                sqlSubmitQueue.put('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''')
                sqlSubmitQueue.put(t)
                sqlReturnQueue.get()
                sqlLock.release()

                workerQueue.put(('sendbroadcast',(fromAddress,subject,message)))

                try:
                    fromLabel = config.get(fromAddress, 'label')
                except:
                    fromLabel = ''
                if fromLabel == '':
                    fromLabel = fromAddress

                toLabel = '[Broadcast subscribers]'

                self.ui.tableWidgetSent.insertRow(0)
                newItem =  QtGui.QTableWidgetItem(unicode(toLabel,'utf-8'))
                newItem.setData(Qt.UserRole,str(toAddress))
                self.ui.tableWidgetSent.setItem(0,0,newItem)

                if fromLabel == '':
                    newItem =  QtGui.QTableWidgetItem(unicode(fromAddress,'utf-8'))
                else:
                    newItem =  QtGui.QTableWidgetItem(unicode(fromLabel,'utf-8'))
                newItem.setData(Qt.UserRole,str(fromAddress))
                self.ui.tableWidgetSent.setItem(0,1,newItem)
                newItem =  QtGui.QTableWidgetItem(unicode(subject,'utf-8)'))
                newItem.setData(Qt.UserRole,unicode(message,'utf-8)'))
                self.ui.tableWidgetSent.setItem(0,2,newItem)
                #newItem =  QtGui.QTableWidgetItem('Doing work necessary to send broadcast...'+strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
                newItem =  QtGui.QTableWidgetItem('Doing work necessary to send broadcast...')
                newItem.setData(Qt.UserRole,ackdata)
                self.ui.tableWidgetSent.setItem(0,3,newItem)

                self.ui.textEditSentMessage.setText(self.ui.tableWidgetSent.item(0,2).data(Qt.UserRole).toPyObject())

                self.ui.labelFrom.setText('')
                self.ui.tabWidget.setCurrentIndex(2)



    def click_pushButtonLoadFromAddressBook(self):
        self.ui.tabWidget.setCurrentIndex(5)
        for i in range(4):
            time.sleep(0.1)
            self.statusBar().showMessage('')
            time.sleep(0.1)
            self.statusBar().showMessage('Right click an entry in your address book and select \'Send message to this address\'.')
        
    def redrawLabelFrom(self,index):
        self.ui.labelFrom.setText(self.ui.comboBoxSendFrom.itemData(index).toPyObject())
        
    def rerenderComboBoxSendFrom(self):
        self.ui.comboBoxSendFrom.clear()
        self.ui.labelFrom.setText('')
        configSections = config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile <> 'bitmessagesettings':
                isEnabled = config.getboolean(addressInKeysFile, 'enabled') #I realize that this is poor programming practice but I don't care. It's easier for others to read.
                if isEnabled:
                    self.ui.comboBoxSendFrom.insertItem(0,unicode(config.get(addressInKeysFile, 'label'),'utf-8'),addressInKeysFile)
        self.ui.comboBoxSendFrom.insertItem(0,'','')
        if(self.ui.comboBoxSendFrom.count() == 2):
            self.ui.comboBoxSendFrom.setCurrentIndex(1)
            self.redrawLabelFrom(self.ui.comboBoxSendFrom.currentIndex())
        else:
            self.ui.comboBoxSendFrom.setCurrentIndex(0)

    def connectToStream(self,streamNumber):
        connectionsCount[streamNumber] = 0

        #Add a line to the Connection Count table on the Network Status tab with a 'zero' connection count. This will be updated as necessary by another function.
        self.ui.tableWidgetConnectionCount.insertRow(0)
        newItem =  QtGui.QTableWidgetItem(str(streamNumber))
        newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.ui.tableWidgetConnectionCount.setItem(0,0,newItem)
        newItem =  QtGui.QTableWidgetItem('0')
        newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.ui.tableWidgetConnectionCount.setItem(0,1,newItem)

        a = outgoingSynSender()
        self.listOfOutgoingSynSenderThreads.append(a)
        QtCore.QObject.connect(a, QtCore.SIGNAL("passObjectThrough(PyQt_PyObject)"), self.connectObjectToSignals)
        QtCore.QObject.connect(a, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
        a.setup(streamNumber)
        a.start()

    def connectObjectToSignals(self,object):
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
        QtCore.QObject.connect(object, QtCore.SIGNAL("displayNewMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewMessage)
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByHash)
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByAckdata)
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateNetworkStatusTab(PyQt_PyObject,PyQt_PyObject)"), self.updateNetworkStatusTab)
        QtCore.QObject.connect(object, QtCore.SIGNAL("incrementNumberOfMessagesProcessed()"), self.incrementNumberOfMessagesProcessed)
        QtCore.QObject.connect(object, QtCore.SIGNAL("incrementNumberOfPubkeysProcessed()"), self.incrementNumberOfPubkeysProcessed)
        QtCore.QObject.connect(object, QtCore.SIGNAL("incrementNumberOfBroadcastsProcessed()"), self.incrementNumberOfBroadcastsProcessed)
        QtCore.QObject.connect(object, QtCore.SIGNAL("setStatusIcon(PyQt_PyObject)"), self.setStatusIcon)

    def displayNewMessage(self,inventoryHash,toAddress,fromAddress,subject,message):
        '''print 'test signals displayNewMessage'
        print 'toAddress', toAddress
        print 'fromAddress', fromAddress
        print 'message', message'''

        fromLabel = ''
        sqlLock.acquire()
        t = (fromAddress,)
        sqlSubmitQueue.put('''select label from addressbook where address=?''')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        if queryreturn <> []:
            for row in queryreturn:
                fromLabel, = row
        else:
            #There might be a label in the subscriptions table
            sqlLock.acquire()
            t = (fromAddress,)
            sqlSubmitQueue.put('''select label from subscriptions where address=?''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()
            if queryreturn <> []:
                for row in queryreturn:
                    fromLabel, = row

        try:
            if toAddress == '[Broadcast subscribers]':
                toLabel = '[Broadcast subscribers]'
            else:
                toLabel = config.get(toAddress, 'label')
        except:
            toLabel = ''
        if toLabel == '':
            toLabel = toAddress

        #msgid, toaddress, fromaddress, subject, received, message = row
        newItem =  QtGui.QTableWidgetItem(unicode(toLabel,'utf-8'))
        newItem.setData(Qt.UserRole,str(toAddress))
        self.ui.tableWidgetInbox.insertRow(0)
        self.ui.tableWidgetInbox.setItem(0,0,newItem)

        if fromLabel == '':
            newItem =  QtGui.QTableWidgetItem(unicode(fromAddress,'utf-8'))
            if config.getboolean('bitmessagesettings', 'showtraynotifications'):
                self.trayIcon.showMessage('New Message', 'New message from '+ fromAddress, 1, 2000)
        else:
            newItem =  QtGui.QTableWidgetItem(unicode(fromLabel,'utf-8'))
            if config.getboolean('bitmessagesettings', 'showtraynotifications'):
                self.trayIcon.showMessage('New Message', 'New message from '+fromLabel, 1, 2000)
        newItem.setData(Qt.UserRole,str(fromAddress))
        self.ui.tableWidgetInbox.setItem(0,1,newItem)
        newItem =  QtGui.QTableWidgetItem(unicode(subject,'utf-8)'))
        newItem.setData(Qt.UserRole,unicode(message,'utf-8)'))
        self.ui.tableWidgetInbox.setItem(0,2,newItem)
        newItem =  myTableWidgetItem(strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
        newItem.setData(Qt.UserRole,QByteArray(inventoryHash))
        newItem.setData(33,int(time.time()))
        self.ui.tableWidgetInbox.setItem(0,3,newItem)

        self.ui.textEditInboxMessage.setText(self.ui.tableWidgetInbox.item(0,2).data(Qt.UserRole).toPyObject())


    def click_pushButtonAddAddressBook(self):
        self.NewSubscriptionDialogInstance = NewSubscriptionDialog(self)

        if self.NewSubscriptionDialogInstance.exec_():
            if self.NewSubscriptionDialogInstance.ui.labelSubscriptionAddressCheck.text() == 'Address is valid.':
                #First we must check to see if the address is already in the address book. The user cannot add it again or else it will cause problems when updating and deleting the entry.
                sqlLock.acquire()
                t = (addBMIfNotPresent(str(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text())),)
                sqlSubmitQueue.put('''select * from addressbook where address=?''')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()
                if queryreturn == []:
                    self.ui.tableWidgetAddressBook.insertRow(0)
                    newItem =  QtGui.QTableWidgetItem(unicode(self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8(),'utf-8'))
                    self.ui.tableWidgetAddressBook.setItem(0,0,newItem)
                    newItem =  QtGui.QTableWidgetItem(addBMIfNotPresent(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text()))
                    newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.ui.tableWidgetAddressBook.setItem(0,1,newItem)
                    t = (str(self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8()),addBMIfNotPresent(str(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text())))
                    sqlLock.acquire()
                    sqlSubmitQueue.put('''INSERT INTO addressbook VALUES (?,?)''')
                    sqlSubmitQueue.put(t)
                    queryreturn = sqlReturnQueue.get()
                    sqlLock.release()
                    self.rerenderInboxFromLabels()
                else:
                    self.statusBar().showMessage('Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.')
            else:
                self.statusBar().showMessage('The address you entered was invalid. Ignoring it.')

    def click_pushButtonAddSubscription(self):
        self.NewSubscriptionDialogInstance = NewSubscriptionDialog(self)

        if self.NewSubscriptionDialogInstance.exec_():
            if self.NewSubscriptionDialogInstance.ui.labelSubscriptionAddressCheck.text() == 'Address is valid.':
                #First we must check to see if the address is already in the address book. The user cannot add it again or else it will cause problems when updating and deleting the entry.
                sqlLock.acquire()
                t = (addBMIfNotPresent(str(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text())),)
                sqlSubmitQueue.put('''select * from subscriptions where address=?''')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()
                if queryreturn == []:
                    self.ui.tableWidgetSubscriptions.insertRow(0)
                    newItem =  QtGui.QTableWidgetItem(unicode(self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8(),'utf-8'))
                    self.ui.tableWidgetSubscriptions.setItem(0,0,newItem)
                    newItem =  QtGui.QTableWidgetItem(addBMIfNotPresent(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text()))
                    newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.ui.tableWidgetSubscriptions.setItem(0,1,newItem)
                    t = (str(self.NewSubscriptionDialogInstance.ui.newsubscriptionlabel.text().toUtf8()),addBMIfNotPresent(str(self.NewSubscriptionDialogInstance.ui.lineEditSubscriptionAddress.text())),True)
                    sqlLock.acquire()
                    sqlSubmitQueue.put('''INSERT INTO subscriptions VALUES (?,?,?)''')
                    sqlSubmitQueue.put(t)
                    queryreturn = sqlReturnQueue.get()
                    sqlLock.release()
                    self.rerenderInboxFromLabels()
                    self.reloadBroadcastSendersForWhichImWatching()
                else:
                    self.statusBar().showMessage('Error: You cannot add the same address to your subsciptions twice. Perhaps rename the existing one if you want.')
            else:
                self.statusBar().showMessage('The address you entered was invalid. Ignoring it.')

    def loadBlackWhiteList(self):
        #Initialize the Blacklist or Whitelist table
        listType = config.get('bitmessagesettings', 'blackwhitelist')
        if listType == 'black':
            sqlSubmitQueue.put('''SELECT label, address FROM blacklist''')
        else:
            sqlSubmitQueue.put('''SELECT label, address FROM whitelist''')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        for row in queryreturn:
            label, address = row
            self.ui.tableWidgetBlacklist.insertRow(0)
            newItem =  QtGui.QTableWidgetItem(unicode(label,'utf-8'))
            self.ui.tableWidgetBlacklist.setItem(0,0,newItem)
            newItem =  QtGui.QTableWidgetItem(address)
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetBlacklist.setItem(0,1,newItem)
    
    def click_pushButtonStatusIcon(self):
        print 'click_pushButtonStatusIcon'
        self.iconGlossaryInstance = iconGlossaryDialog(self)
        if self.iconGlossaryInstance.exec_():
            pass
    
    def click_actionHelp(self):
        self.helpDialogInstance = helpDialog(self)
        self.helpDialogInstance.exec_()

    def click_actionAbout(self):
        self.aboutDialogInstance = aboutDialog(self)
        self.aboutDialogInstance.exec_()

    def click_actionSettings(self):
        global statusIconColor
        self.settingsDialogInstance = settingsDialog(self)
        if self.settingsDialogInstance.exec_():
            config.set('bitmessagesettings', 'startonlogon', str(self.settingsDialogInstance.ui.checkBoxStartOnLogon.isChecked()))
            config.set('bitmessagesettings', 'minimizetotray', str(self.settingsDialogInstance.ui.checkBoxMinimizeToTray.isChecked()))
            config.set('bitmessagesettings', 'showtraynotifications', str(self.settingsDialogInstance.ui.checkBoxShowTrayNotifications.isChecked()))
            config.set('bitmessagesettings', 'startintray', str(self.settingsDialogInstance.ui.checkBoxStartInTray.isChecked()))
            if int(config.get('bitmessagesettings','port')) != int(self.settingsDialogInstance.ui.lineEditTCPPort.text()):
                QMessageBox.about(self, "Restart", "You must restart Bitmessage for the port number change to take effect.")
                config.set('bitmessagesettings', 'port', str(self.settingsDialogInstance.ui.lineEditTCPPort.text()))
            if config.get('bitmessagesettings', 'socksproxytype') == 'none' and str(self.settingsDialogInstance.ui.comboBoxProxyType.currentText())[0:5] == 'SOCKS':
                if statusIconColor != 'red':
                    QMessageBox.about(self, "Restart", "Bitmessage will use your proxy from now on now but you may want to manually restart Bitmessage now to close existing connections.")
            if config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and str(self.settingsDialogInstance.ui.comboBoxProxyType.currentText()) == 'none':
                self.statusBar().showMessage('')
            config.set('bitmessagesettings', 'socksproxytype', str(self.settingsDialogInstance.ui.comboBoxProxyType.currentText()))
            config.set('bitmessagesettings', 'socksauthentication', str(self.settingsDialogInstance.ui.checkBoxAuthentication.isChecked()))
            config.set('bitmessagesettings', 'sockshostname', str(self.settingsDialogInstance.ui.lineEditSocksHostname.text()))
            config.set('bitmessagesettings', 'socksport', str(self.settingsDialogInstance.ui.lineEditSocksPort.text()))
            config.set('bitmessagesettings', 'socksusername', str(self.settingsDialogInstance.ui.lineEditSocksUsername.text()))
            config.set('bitmessagesettings', 'sockspassword', str(self.settingsDialogInstance.ui.lineEditSocksPassword.text()))
            
            with open(appdata + 'keys.dat', 'wb') as configfile:
                config.write(configfile)

            if 'win32' in sys.platform or 'win64' in sys.platform:
            #Auto-startup for Windows
                RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                self.settings = QSettings(RUN_PATH, QSettings.NativeFormat)
                if config.getboolean('bitmessagesettings', 'startonlogon'):
                    self.settings.setValue("PyBitmessage",sys.argv[0])
                else:
                    self.settings.remove("PyBitmessage")
            elif 'darwin' in sys.platform:
                #startup for mac
                pass
            elif 'linux' in sys.platform:
                #startup for linux
                pass

    def click_radioButtonBlacklist(self):
        if config.get('bitmessagesettings', 'blackwhitelist') == 'white':
            config.set('bitmessagesettings','blackwhitelist','black')
            with open(appdata + 'keys.dat', 'wb') as configfile:
                config.write(configfile)
            #self.ui.tableWidgetBlacklist.clearContents()
            self.ui.tableWidgetBlacklist.setRowCount(0)
            self.loadBlackWhiteList()
            self.ui.tabWidget.setTabText(6,'Blacklist')


    def click_radioButtonWhitelist(self):
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            config.set('bitmessagesettings','blackwhitelist','white')
            with open(appdata + 'keys.dat', 'wb') as configfile:
                config.write(configfile)
            #self.ui.tableWidgetBlacklist.clearContents()
            self.ui.tableWidgetBlacklist.setRowCount(0)
            self.loadBlackWhiteList()
            self.ui.tabWidget.setTabText(6,'Whitelist')

    def click_pushButtonAddBlacklist(self):
        print 'click_pushButtonAddBlacklist'
        self.NewBlacklistDialogInstance = NewSubscriptionDialog(self)

        if self.NewBlacklistDialogInstance.exec_():
            if self.NewBlacklistDialogInstance.ui.labelSubscriptionAddressCheck.text() == 'Address is valid.':
                #First we must check to see if the address is already in the address book. The user cannot add it again or else it will cause problems when updating and deleting the entry.
                sqlLock.acquire()
                t = (addBMIfNotPresent(str(self.NewBlacklistDialogInstance.ui.lineEditSubscriptionAddress.text())),)
                if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                    sqlSubmitQueue.put('''select * from blacklist where address=?''')
                else:
                    sqlSubmitQueue.put('''select * from whitelist where address=?''')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()
                if queryreturn == []:
                    self.ui.tableWidgetBlacklist.insertRow(0)
                    newItem =  QtGui.QTableWidgetItem(unicode(self.NewBlacklistDialogInstance.ui.newsubscriptionlabel.text().toUtf8(),'utf-8'))
                    self.ui.tableWidgetBlacklist.setItem(0,0,newItem)
                    newItem =  QtGui.QTableWidgetItem(addBMIfNotPresent(self.NewBlacklistDialogInstance.ui.lineEditSubscriptionAddress.text()))
                    newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    self.ui.tableWidgetBlacklist.setItem(0,1,newItem)
                    t = (str(self.NewBlacklistDialogInstance.ui.newsubscriptionlabel.text().toUtf8()),addBMIfNotPresent(str(self.NewBlacklistDialogInstance.ui.lineEditSubscriptionAddress.text())),True)
                    sqlLock.acquire()
                    if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
                        sqlSubmitQueue.put('''INSERT INTO blacklist VALUES (?,?,?)''')
                    else:
                        sqlSubmitQueue.put('''INSERT INTO whitelist VALUES (?,?,?)''')
                    sqlSubmitQueue.put(t)
                    queryreturn = sqlReturnQueue.get()
                    sqlLock.release()
                else:
                    self.statusBar().showMessage('Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.')
            else:
                self.statusBar().showMessage('The address you entered was invalid. Ignoring it.')


    def click_NewAddressDialog(self):
        print 'click_buttondialog'
        self.dialog = NewAddressDialog(self)

        # For Modal dialogs
        if self.dialog.exec_():
            self.dialog.ui.buttonBox.enabled = False
            if self.dialog.ui.radioButtonMostAvailable.isChecked():
                #self.generateAndStoreAnAddress(1)
                streamNumberForAddress = 1


            else:
                #User selected 'Use the same stream as an existing address.'
                streamNumberForAddress = addressStream(self.dialog.ui.comboBoxExisting.currentText())

            self.addressGenerator = addressGenerator()
            self.addressGenerator.setup(streamNumberForAddress,str(self.dialog.ui.newaddresslabel.text().toUtf8()))

            QtCore.QObject.connect(self.addressGenerator, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
            QtCore.QObject.connect(self.addressGenerator, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)


            self.addressGenerator.start()
        else:
            print 'rejected'

    def closeEvent(self, event):
        broadcastToSendDataQueues((0, 'shutdown', 'all'))
        
        print 'Closing. Flushing inventory in memory out to disk...'
        self.statusBar().showMessage('Flushing inventory in memory out to disk.')
        flushInventory()
      
        '''quit_msg = "Are you sure you want to exit Bitmessage?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()'''

        #This one last useless query will guarantee that the previous query committed before we close the program.
        sqlLock.acquire()
        sqlSubmitQueue.put('SELECT address FROM subscriptions')
        sqlSubmitQueue.put('')
        sqlReturnQueue.get()
        sqlLock.release()

        self.statusBar().showMessage('Saving the knownNodes list of peers to disk...')
        output = open(appdata + 'knownnodes.dat', 'wb')
        pickle.dump(knownNodes, output)
        output.close()

        self.trayIcon.hide()
        print 'Done.'
        self.statusBar().showMessage('All done. Closing user interface...')
        event.accept()
        raise SystemExit
        

    def on_action_InboxReply(self):
        currentInboxRow = self.ui.tableWidgetInbox.currentRow()
        toAddressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(currentInboxRow,0).data(Qt.UserRole).toPyObject())
        fromAddressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(currentInboxRow,1).data(Qt.UserRole).toPyObject())
        if not config.get(toAddressAtCurrentInboxRow,'enabled'):
            self.statusBar().showMessage('Error: The address from which you are trying to send is disabled. Enable it from the \'Your Identities\' tab first.')
            return
        self.ui.lineEditTo.setText(str(fromAddressAtCurrentInboxRow))
        self.ui.labelFrom.setText(toAddressAtCurrentInboxRow)
        self.ui.comboBoxSendFrom.setCurrentIndex(0)
        #self.ui.comboBoxSendFrom.setEditText(str(self.ui.tableWidgetInbox.item(currentInboxRow,0).text))
        self.ui.textEditMessage.setText('\n\n------------------------------------------------------\n'+self.ui.tableWidgetInbox.item(currentInboxRow,2).data(Qt.UserRole).toPyObject())
        if self.ui.tableWidgetInbox.item(currentInboxRow,2).text()[0:3] == 'Re:':
            self.ui.lineEditSubject.setText(str(self.ui.tableWidgetInbox.item(currentInboxRow,2).text()))
        else:
            self.ui.lineEditSubject.setText('Re: '+self.ui.tableWidgetInbox.item(currentInboxRow,2).text())
        self.ui.radioButtonSpecific.setChecked(True)
        self.ui.tabWidget.setCurrentIndex(1)

    def on_action_InboxAddSenderToAddressBook(self):
        currentInboxRow = self.ui.tableWidgetInbox.currentRow()
        #self.ui.tableWidgetInbox.item(currentRow,1).data(Qt.UserRole).toPyObject()
        addressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(currentInboxRow,1).data(Qt.UserRole).toPyObject())
        #Let's make sure that it isn't already in the address book
        sqlLock.acquire()
        t = (addressAtCurrentInboxRow,)
        sqlSubmitQueue.put('''select * from addressbook where address=?''')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        if queryreturn == []:
            self.ui.tableWidgetAddressBook.insertRow(0)
            newItem =  QtGui.QTableWidgetItem('--New entry. Change label in Address Book.--')
            self.ui.tableWidgetAddressBook.setItem(0,0,newItem)
            newItem =  QtGui.QTableWidgetItem(addressAtCurrentInboxRow)
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.ui.tableWidgetAddressBook.setItem(0,1,newItem)
            t = ('--New entry. Change label in Address Book.--',addressAtCurrentInboxRow)
            sqlLock.acquire()
            sqlSubmitQueue.put('''INSERT INTO addressbook VALUES (?,?)''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()
            self.ui.tabWidget.setCurrentIndex(5)
            self.ui.tableWidgetAddressBook.setCurrentCell(0,0)
            self.statusBar().showMessage('Entry added to the Address Book. Edit the label to your liking.')
        else:
            self.statusBar().showMessage('Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.')

    def on_action_InboxTrash(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        inventoryHashToTrash = str(self.ui.tableWidgetInbox.item(currentRow,3).data(Qt.UserRole).toPyObject())
        t = (inventoryHashToTrash,)
        sqlLock.acquire()
        #sqlSubmitQueue.put('''delete from inbox where msgid=?''')
        sqlSubmitQueue.put('''UPDATE inbox SET folder='trash' WHERE msgid=?''')
        sqlSubmitQueue.put(t)
        sqlReturnQueue.get()
        sqlLock.release()
        self.ui.tableWidgetInbox.removeRow(currentRow)
        self.statusBar().showMessage('Moved item to trash. There is no user interface to view your trash, but it is still on disk if you are desperate to get it back.')

    #Group of functions for the Address Book dialog box
    def on_action_AddressBookNew(self):
        self.click_pushButtonAddAddressBook()
    def on_action_AddressBookDelete(self):
        currentRow = self.ui.tableWidgetAddressBook.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetAddressBook.item(currentRow,0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(currentRow,1).text()
        t = (str(labelAtCurrentRow),str(addressAtCurrentRow))
        sqlLock.acquire()
        sqlSubmitQueue.put('''DELETE FROM addressbook WHERE label=? AND address=?''')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        self.ui.tableWidgetAddressBook.removeRow(currentRow)
        self.rerenderInboxFromLabels()
        self.rerenderSentToLabels()
        self.reloadBroadcastSendersForWhichImWatching()
    def on_action_AddressBookClipboard(self):
        currentRow = self.ui.tableWidgetAddressBook.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(currentRow,1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))
    def on_action_AddressBookSend(self):
        currentRow = self.ui.tableWidgetAddressBook.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(currentRow,1).text()
        if self.ui.lineEditTo.text() == '':
            self.ui.lineEditTo.setText(str(addressAtCurrentRow))
        else:
            self.ui.lineEditTo.setText(str(self.ui.lineEditTo.text()) + '; '+ str(addressAtCurrentRow))
        self.statusBar().showMessage('You have added the address to the \'To\' field on the \'Send\' tab. You may add more recipients if you want. When you are done, go to the \'Send\' tab.')
    def on_context_menuAddressBook(self, point):
        self.popMenuAddressBook.exec_( self.ui.tableWidgetAddressBook.mapToGlobal(point) )


    #Group of functions for the Subscriptions dialog box
    def on_action_SubscriptionsNew(self):
        self.click_pushButtonAddSubscription()
    def on_action_SubscriptionsDelete(self):
        print 'clicked Delete'
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetSubscriptions.item(currentRow,0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(currentRow,1).text()
        t = (str(labelAtCurrentRow),str(addressAtCurrentRow))
        sqlLock.acquire()
        sqlSubmitQueue.put('''DELETE FROM subscriptions WHERE label=? AND address=?''')
        sqlSubmitQueue.put(t)
        sqlReturnQueue.get()
        sqlLock.release()
        self.ui.tableWidgetSubscriptions.removeRow(currentRow)
        self.rerenderInboxFromLabels()
    def on_action_SubscriptionsClipboard(self):
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(currentRow,1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))
    def on_context_menuSubscriptions(self, point):
        self.popMenuSubscriptions.exec_( self.ui.tableWidgetSubscriptions.mapToGlobal(point) )


    #Group of functions for the Your Identities dialog box
    def on_action_YourIdentitiesNew(self):
        self.click_NewAddressDialog()
    def on_action_YourIdentitiesEnable(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetYourIdentities.item(currentRow,1).text()
        config.set(str(addressAtCurrentRow),'enabled','true')
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)
        self.ui.tableWidgetYourIdentities.item(currentRow,0).setTextColor(QtGui.QColor(0,0,0))
        self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(0,0,0))
        self.ui.tableWidgetYourIdentities.item(currentRow,2).setTextColor(QtGui.QColor(0,0,0))
        self.reloadMyAddressHashes()
    def on_action_YourIdentitiesDisable(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetYourIdentities.item(currentRow,1).text()
        config.set(str(addressAtCurrentRow),'enabled','false')
        self.ui.tableWidgetYourIdentities.item(currentRow,0).setTextColor(QtGui.QColor(128,128,128))
        self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(128,128,128))
        self.ui.tableWidgetYourIdentities.item(currentRow,2).setTextColor(QtGui.QColor(128,128,128))
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)
        self.reloadMyAddressHashes()
    def on_action_YourIdentitiesClipboard(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetYourIdentities.item(currentRow,1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))
    def on_context_menuYourIdentities(self, point):
        self.popMenu.exec_( self.ui.tableWidgetYourIdentities.mapToGlobal(point) )
    def on_context_menuInbox(self, point):
        self.popMenuInbox.exec_( self.ui.tableWidgetInbox.mapToGlobal(point) )

    def tableWidgetInboxItemClicked(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        self.ui.textEditInboxMessage.setText(self.ui.tableWidgetInbox.item(currentRow,2).data(Qt.UserRole).toPyObject())

    def tableWidgetSentItemClicked(self):
            currentRow = self.ui.tableWidgetSent.currentRow()
            self.ui.textEditSentMessage.setText(self.ui.tableWidgetSent.item(currentRow,2).data(Qt.UserRole).toPyObject())

    def tableWidgetYourIdentitiesItemChanged(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        if currentRow >= 0:
            addressAtCurrentRow = self.ui.tableWidgetYourIdentities.item(currentRow,1).text()
            config.set(str(addressAtCurrentRow),'label',str(self.ui.tableWidgetYourIdentities.item(currentRow,0).text().toUtf8()))
            with open(appdata + 'keys.dat', 'wb') as configfile:
                config.write(configfile)
            self.rerenderComboBoxSendFrom()
            #self.rerenderInboxFromLabels()
            self.rerenderInboxToLabels()
            self.rerenderSentFromLabels()
            #self.rerenderSentToLabels()

    def tableWidgetAddressBookItemChanged(self):
        currentRow = self.ui.tableWidgetAddressBook.currentRow()
        sqlLock.acquire()
        if currentRow >= 0:
            addressAtCurrentRow = self.ui.tableWidgetAddressBook.item(currentRow,1).text()
            t = (str(self.ui.tableWidgetAddressBook.item(currentRow,0).text().toUtf8()),str(addressAtCurrentRow))
            sqlSubmitQueue.put('''UPDATE addressbook set label=? WHERE address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        #except Exception, err:
        #    print 'Program Exception in tableWidgetAddressBookItemChanged:', err
        sqlLock.release()
        self.rerenderInboxFromLabels()
        self.rerenderSentToLabels()

    def tableWidgetSubscriptionsItemChanged(self):
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        sqlLock.acquire()
        if currentRow >= 0:
            addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(currentRow,1).text()
            t = (str(self.ui.tableWidgetSubscriptions.item(currentRow,0).text().toUtf8()),str(addressAtCurrentRow))
            sqlSubmitQueue.put('''UPDATE subscriptions set label=? WHERE address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        #except Exception, err:
        #    print 'Program Exception in tableWidgetSubscriptionsItemChanged:', err
        sqlLock.release()
        self.rerenderInboxFromLabels()
        self.rerenderSentToLabels()   

    def writeNewAddressToTable(self,label,address,streamNumber):
        self.ui.tableWidgetYourIdentities.insertRow(0)
        self.ui.tableWidgetYourIdentities.setItem(0, 0, QtGui.QTableWidgetItem(unicode(label,'utf-8')))
        newItem = QtGui.QTableWidgetItem(address)
        newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.ui.tableWidgetYourIdentities.setItem(0, 1, newItem)
        newItem = QtGui.QTableWidgetItem(streamNumber)
        newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.ui.tableWidgetYourIdentities.setItem(0, 2, newItem)
        self.rerenderComboBoxSendFrom()
        self.reloadMyAddressHashes()

    def updateStatusBar(self,data):
        print 'Status bar!', data
        self.statusBar().showMessage(data)

    def reloadMyAddressHashes(self):
        print 'reloading my address hashes'
        myAddressHashes.clear()
        #myPrivateKeys.clear()
        configSections = config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile <> 'bitmessagesettings':
                isEnabled = config.getboolean(addressInKeysFile, 'enabled')
                if isEnabled:
                    status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
                    n = config.getint(addressInKeysFile, 'n')
                    e = config.getint(addressInKeysFile, 'e')
                    d = config.getint(addressInKeysFile, 'd')
                    p = config.getint(addressInKeysFile, 'p')
                    q = config.getint(addressInKeysFile, 'q')
                    myAddressHashes[hash] = rsa.PrivateKey(n,e,d,p,q)

    def reloadBroadcastSendersForWhichImWatching(self):
        broadcastSendersForWhichImWatching.clear()
        sqlLock.acquire()
        sqlSubmitQueue.put('SELECT address FROM subscriptions')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        for row in queryreturn:
            address, = row
            status,addressVersionNumber,streamNumber,hash = decodeAddress(address)
            broadcastSendersForWhichImWatching[hash] = 0

#In order for the time columns on the Inbox and Sent tabs to be sorted correctly (rather than alphabetically), we need to overload the < operator and use this class instead of QTableWidgetItem.
class myTableWidgetItem(QTableWidgetItem):
    def __lt__(self,other):
        return int(self.data(33).toPyObject()) < int(other.data(33).toPyObject())


sendDataQueues = [] #each sendData thread puts its queue in this list.
myAddressHashes = {}
#myPrivateKeys = {}
inventory = {} #of objects (like msg payloads and pubkey payloads) Does not include protocol headers (the first 24 bytes of each packet).
workerQueue = Queue.Queue()
sqlSubmitQueue = Queue.Queue() #SQLITE3 is so thread-unsafe that they won't even let you call it from different threads using your own locks. SQL objects can only be called from one thread.
sqlReturnQueue = Queue.Queue()
sqlLock = threading.Lock()
printLock = threading.Lock()
ackdataForWhichImWatching = {}
broadcastSendersForWhichImWatching = {}
statusIconColor = 'red'
connectionsCount = {} #Used for the 'network status' tab.
connectionsCountLock = threading.Lock()
inventoryLock = threading.Lock() #Guarantees that two receiveDataThreads don't receive and process the same message concurrently (probably sent by a malicious individual)
eightBytesOfRandomDataUsedToDetectConnectionsToSelf = pack('>Q',random.randrange(1, 18446744073709551615))
connectedHostsList = {} #List of hosts to which we are connected. Used to guarantee that the outgoingSynSender thread won't connect to the same remote node twice.
neededPubkeys = {}

#These constants are not at the top because if changed they will cause particularly unexpected behavior: You won't be able to either send or receive messages because the proof of work you do (or demand) won't match that done or demanded by others. Don't change them!
averageProofOfWorkNonceTrialsPerByte = 320 #The amount of work that should be performed (and demanded) per byte of the payload. Double this number to double the work.
payloadLengthExtraBytes = 14000 #To make sending short messages a little more difficult, this value is added to the payload length for use in calculating the proof of work target.

if __name__ == "__main__":
    #sqlite_version = sqlite3.sqlite_version_info
    # Check the Major version, the first element in the array
    if sqlite3.sqlite_version_info[0] < 3:
        print 'This program requires sqlite version 3 or higher because 2 and lower cannot store NULL values. I see version:', sqlite3.sqlite_version_info
        sys.exit()

    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            appdata = path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            print 'Could not find home folder, please report this message and your OS X version to the BitMessage Github.'
            sys.exit()

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        appdata = path.join(environ['APPDATA'], APPNAME) + '\\'
    else:
        appdata = path.expanduser(path.join("~", "." + APPNAME + "/"))

    if not os.path.exists(appdata):
        os.makedirs(appdata)

    config = ConfigParser.SafeConfigParser()
    config.read(appdata + 'keys.dat')
    try:
        config.get('bitmessagesettings', 'settingsversion')
        print 'Loading config files from', appdata
    except:
        #This appears to be the first time running the program; there is no config file (or it cannot be accessed). Create config file.
        config.add_section('bitmessagesettings')
        config.set('bitmessagesettings','settingsversion','1')
        config.set('bitmessagesettings','bitstrength','2048')
        config.set('bitmessagesettings','port','8444')
        config.set('bitmessagesettings','timeformat','%%a, %%d %%b %%Y  %%I:%%M %%p')
        config.set('bitmessagesettings','blackwhitelist','black')
        config.set('bitmessagesettings','startonlogon','false')
        config.set('bitmessagesettings','minimizetotray','true')
        config.set('bitmessagesettings','showtraynotifications','true')
        config.set('bitmessagesettings','startintray','false')



        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)
        print 'Storing config files in', appdata

    if config.getint('bitmessagesettings','settingsversion') == 1:
        config.set('bitmessagesettings','settingsversion','2')
        config.set('bitmessagesettings','socksproxytype','none')
        config.set('bitmessagesettings','sockshostname','localhost')
        config.set('bitmessagesettings','socksport','9050')
        config.set('bitmessagesettings','socksauthentication','false')
        config.set('bitmessagesettings','socksusername','')
        config.set('bitmessagesettings','sockspassword','')
        config.set('bitmessagesettings','keysencrypted','false')
        config.set('bitmessagesettings','messagesencrypted','false')
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)


    try:
        pickleFile = open(appdata + 'knownnodes.dat', 'rb')
        knownNodes = pickle.load(pickleFile)
        pickleFile.close()
    except:
        createDefaultKnownNodes(appdata)
        pickleFile = open(appdata + 'knownnodes.dat', 'rb')
        knownNodes = pickle.load(pickleFile)
        pickleFile.close()

    if config.getint('bitmessagesettings', 'settingsversion') > 2:
        print 'Bitmessage cannot read future versions of the keys file (keys.dat). Run the newer version of Bitmessage.'
        raise SystemExit

    
    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet("QStatusBar::item { border: 0px solid black }")
    myapp = MyForm()
    myapp.show()

    if config.getboolean('bitmessagesettings', 'startintray'):
        myapp.hide()
        myapp.trayIcon.show()
        #self.hidden = True
        #self.setWindowState(self.windowState() & QtCore.Qt.WindowMinimized)
        #self.hide()
        if 'win32' in sys.platform or 'win64' in sys.platform:
            myapp.setWindowFlags(Qt.ToolTip)
    
    sys.exit(app.exec_())

# So far, the Bitmessage protocol, this client, the Wiki, and the forums
# are all a one-man operation. Bitcoin tips are quite appreciated!
# 1H5XaDA6fYENLbknwZyjiYXYPQaFjjLX2u
