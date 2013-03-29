#!/usr/bin/env python2.7
# Copyright (c) 2012 Jonathan Warren
# Copyright (c) 2012 The Bitmessage developers
# Distributed under the MIT/X11 software license. See the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

#Right now, PyBitmessage only support connecting to stream 1. It doesn't yet contain logic to expand into further streams.

softwareVersion = '0.2.7'
verbose = 1
maximumAgeOfAnObjectThatIAmWillingToAccept = 216000 #Equals two days and 12 hours.
lengthOfTimeToLeaveObjectsInInventory = 237600 #Equals two days and 18 hours. This should be longer than maximumAgeOfAnObjectThatIAmWillingToAccept so that we don't process messages twice.
lengthOfTimeToHoldOnToAllPubkeys = 2419200 #Equals 4 weeks. You could make this longer if you want but making it shorter would not be advisable because there is a very small possibility that it could keep you from obtaining a needed pubkey for a period of time.
maximumAgeOfObjectsThatIAdvertiseToOthers = 216000 #Equals two days and 12 hours
maximumAgeOfNodesThatIAdvertiseToOthers = 10800 #Equals three hours
storeConfigFilesInSameDirectoryAsProgramByDefault = False #The user may de-select Portable Mode in the settings if they want the config files to stay in the application data folder.
useVeryEasyProofOfWorkForTesting = False #If you set this to True while on the normal network, you won't be able to send or sometimes receive messages.

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
from regenerateaddresses import *
from specialaddressbehavior import *
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
import hashlib
from struct import *
import pickle
import random
import sqlite3
import threading #used for the locks, not for the threads
from time import strftime, localtime
import os
import shutil #used for moving the messages.dat file
import string
import socks
import highlevelcrypto
from pyelliptic.openssl import OpenSSL
import ctypes
from pyelliptic import arithmetic
#The next 3 are used for the API
from SimpleXMLRPCServer import *
import json
from subprocess import call #used when the API must execute an outside program

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
            #time.sleep(999999)#I sometimes use this to prevent connections for testing.
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
                    objectsOfWhichThisRemoteNodeIsAlreadyAware = {}
                    rd.setup(sock,HOST,PORT,self.streamNumber,self.selfInitiatedConnectionList,objectsOfWhichThisRemoteNodeIsAlreadyAware)
                    rd.start()
                    printLock.acquire()
                    print self, 'connected to', HOST, 'during an outgoing attempt.'
                    printLock.release()

                    sd = sendDataThread()
                    sd.setup(sock,HOST,PORT,self.streamNumber,objectsOfWhichThisRemoteNodeIsAlreadyAware)
                    sd.start()
                    sd.sendVersionMessage()

                except socks.GeneralProxyError, err:
                    printLock.acquire()
                    print 'Could NOT connect to', HOST, 'during outgoing attempt.', err
                    printLock.release()
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
                        printLock.acquire()
                        print 'Could NOT connect to', HOST, 'during outgoing attempt.', err
                        printLock.release()
                        PORT, timeLastSeen = knownNodes[self.streamNumber][HOST]
                        if (int(time.time())-timeLastSeen) > 172800 and len(knownNodes[self.streamNumber]) > 1000: # for nodes older than 48 hours old if we have more than 1000 hosts in our list, delete from the knownNodes data-structure.
                            del knownNodes[self.streamNumber][HOST]
                            print 'deleting ', HOST, 'from knownNodes because it is more than 48 hours old and we could not connect to it.'
                except Exception, err:
                    print 'An exception has occurred in the outgoingSynSender thread that was not caught by other exception types:', err
            time.sleep(0.1)

#Only one singleListener thread will ever exist. It creates the receiveDataThread and sendDataThread for each incoming connection. Note that it cannot set the stream number because it is not known yet- the other node will have to tell us its stream number in a version message. If we don't care about their stream, we will close the connection (within the recversion function of the recieveData thread)
class singleListener(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)


    def run(self):
        #We don't want to accept incoming connections if the user is using a SOCKS proxy. If they eventually select proxy 'none' then this will start listening for connections.
        while config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
            time.sleep(300)

        print 'Listening for incoming connections.'
        HOST = '' # Symbolic name meaning all available interfaces
        PORT = config.getint('bitmessagesettings', 'port')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #This option apparently avoids the TIME_WAIT state so that we can rebind faster
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(2)
        self.incomingConnectionList = [] #This list isn't used for anything. The reason it exists is because receiveData threads expect that a list be passed to them. They expect this because the outgoingSynSender thread DOES use a similar list to keep track of the number of outgoing connections it has created.


        while True:
            #We don't want to accept incoming connections if the user is using a SOCKS proxy. If the user eventually select proxy 'none' then this will start listening for connections.
            while config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
                time.sleep(10)
            a,(HOST,PORT) = sock.accept()
            #Users are finding that if they run more than one node in the same network (thus with the same public IP), they can not connect with the second node. This is because this section of code won't accept the connection from the same IP. This problem will go away when the Bitmessage network grows beyond being tiny but in the mean time I'll comment out this code section.
            """while HOST in connectedHostsList:
                print 'incoming connection is from a host in connectedHostsList (we are already connected to it). Ignoring it.'
                a.close()
                a,(HOST,PORT) = sock.accept()"""
            rd = receiveDataThread()
            self.emit(SIGNAL("passObjectThrough(PyQt_PyObject)"),rd)
            objectsOfWhichThisRemoteNodeIsAlreadyAware = {}
            rd.setup(a,HOST,PORT,-1,self.incomingConnectionList,objectsOfWhichThisRemoteNodeIsAlreadyAware)
            printLock.acquire()
            print self, 'connected to', HOST,'during INCOMING request.'
            printLock.release()
            rd.start()

            sd = sendDataThread()
            sd.setup(a,HOST,PORT,-1,objectsOfWhichThisRemoteNodeIsAlreadyAware)
            sd.start()


#This thread is created either by the synSenderThread(for outgoing connections) or the singleListenerThread(for incoming connectiosn).
class receiveDataThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.data = ''
        self.verackSent = False
        self.verackReceived = False

    def setup(self,sock,HOST,port,streamNumber,selfInitiatedConnectionList,objectsOfWhichThisRemoteNodeIsAlreadyAware):
        self.sock = sock
        self.HOST = HOST
        self.PORT = port
        self.sock.settimeout(600) #We'll send out a pong every 5 minutes to make sure the connection stays alive if there has been no other traffic to send lately.
        self.streamNumber = streamNumber
        self.selfInitiatedConnectionList = selfInitiatedConnectionList
        self.selfInitiatedConnectionList.append(self)
        self.payloadLength = 0 #This is the protocol payload length thus it doesn't include the 24 byte message header
        self.receivedgetbiginv = False #Gets set to true once we receive a getbiginv message from our peer. An abusive peer might request it too much so we use this variable to check whether they have already asked for a big inv message.
        self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave = {}
        connectedHostsList[self.HOST] = 0 #The very fact that this receiveData thread exists shows that we are connected to the remote host. Let's add it to this list so that the outgoingSynSender thread doesn't try to connect to it.
        self.connectionIsOrWasFullyEstablished = False #set to true after the remote node and I accept each other's version messages. This is needed to allow the user interface to accurately reflect the current number of connections.
        if self.streamNumber == -1: #This was an incoming connection. Send out a version message if we accept the other node's version message.
            self.initiatedConnection = False
        else:
            self.initiatedConnection = True
        self.ackDataThatWeHaveYetToSend = [] #When we receive a message bound for us, we store the acknowledgement that we need to send (the ackdata) here until we are done processing all other data received from this peer.
        self.objectsOfWhichThisRemoteNodeIsAlreadyAware = objectsOfWhichThisRemoteNodeIsAlreadyAware

    def run(self):

        while True:
            try:
                self.data += self.sock.recv(65536)
            except socket.timeout:
                printLock.acquire()
                print 'Timeout occurred waiting for data. Closing receiveData thread.'
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
                print 'Connection closed. Closing receiveData thread.'
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
            printLock.acquire()
            print 'removed self (a receiveDataThread) from ConnectionList'
            printLock.release()
        except:
            pass
        broadcastToSendDataQueues((0, 'shutdown', self.HOST))
        if self.connectionIsOrWasFullyEstablished: #We don't want to decrement the number of connections and show the result if we never incremented it in the first place (which we only do if the connection is fully established- meaning that both nodes accepted each other's version packets.)
            connectionsCountLock.acquire()
            connectionsCount[self.streamNumber] -= 1
            self.emit(SIGNAL("updateNetworkStatusTab(PyQt_PyObject,PyQt_PyObject)"),self.streamNumber,connectionsCount[self.streamNumber])
            printLock.acquire()
            print 'Updating network status tab with current connections count:', connectionsCount[self.streamNumber]
            printLock.release()
            connectionsCountLock.release()
        try:
            del connectedHostsList[self.HOST]
        except Exception, err:
            print 'Could not delete', self.HOST, 'from connectedHostsList.', err

    def processData(self):
        global verbose
        #if verbose >= 3:
            #printLock.acquire()
            #print 'self.data is currently ', repr(self.data)
            #printLock.release()
        if len(self.data) < 20: #if so little of the data has arrived that we can't even unpack the payload length
            pass
        elif self.data[0:4] != '\xe9\xbe\xb4\xd9':
            if verbose >= 1:
                printLock.acquire()
                sys.stderr.write('The magic bytes were not correct. First 40 bytes of data: %s\n' % repr(self.data[0:40]))
                print 'self.data:', self.data.encode('hex')
                printLock.release()
            self.data = ""
        else:
            self.payloadLength, = unpack('>L',self.data[16:20])
            if len(self.data) >= self.payloadLength+24: #check if the whole message has arrived yet. If it has,...
                if self.data[20:24] == hashlib.sha512(self.data[24:self.payloadLength+24]).digest()[0:4]:#test the checksum in the message. If it is correct...
                    #print 'message checksum is correct'
                    #The time we've last seen this node is obviously right now since we just received valid data from it. So update the knownNodes list so that other peers can be made aware of its existance.
                    if self.initiatedConnection: #The remote port is only something we should share with others if it is the remote node's incoming port (rather than some random operating-system-assigned outgoing port).
                        knownNodes[self.streamNumber][self.HOST] = (self.PORT,int(time.time()))
                    if self.payloadLength <= 180000000: #If the size of the message is greater than 180MB, ignore it. (I get memory errors when processing messages much larger than this though it is concievable that this value will have to be lowered if some systems are less tolarant of large messages.)
                        remoteCommand = self.data[4:16]
                        printLock.acquire()
                        print 'remoteCommand', repr(remoteCommand.replace('\x00','')), ' from', self.HOST
                        printLock.release()
                        if remoteCommand == 'version\x00\x00\x00\x00\x00':
                            self.recversion(self.data[24:self.payloadLength+24])
                        elif remoteCommand == 'verack\x00\x00\x00\x00\x00\x00':
                            self.recverack()
                        elif remoteCommand == 'addr\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.recaddr(self.data[24:self.payloadLength+24])
                        elif remoteCommand == 'getpubkey\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.recgetpubkey(self.data[24:self.payloadLength+24])
                        elif remoteCommand == 'pubkey\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.recpubkey(self.data[24:self.payloadLength+24])
                        elif remoteCommand == 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.recinv(self.data[24:self.payloadLength+24])
                        elif remoteCommand == 'getdata\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.recgetdata(self.data[24:self.payloadLength+24])
                        elif remoteCommand == 'getbiginv\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.sendBigInv()
                        elif remoteCommand == 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.recmsg(self.data[24:self.payloadLength+24])
                        elif remoteCommand == 'broadcast\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                            self.recbroadcast(self.data[24:self.payloadLength+24])
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
                        while len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 0:
                            random.seed()
                            objectHash, = random.sample(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave,  1)
                            if objectHash in inventory:
                                printLock.acquire()
                                print 'Inventory (in memory) already has object listed in inv message.'
                                printLock.release()
                                del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[objectHash]
                            elif isInSqlInventory(objectHash):
                                if verbose >= 2:
                                    printLock.acquire()
                                    print 'Inventory (SQL on disk) already has object listed in inv message.'
                                    printLock.release()
                                del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[objectHash]
                            else:
                                #print 'processData function making request for object:', objectHash.encode('hex')
                                self.sendgetdata(objectHash)
                                del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[objectHash] #It is possible that the remote node doesn't respond with the object. In that case, we'll very likely get it from someone else anyway.
                                break
                        if len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 0:
                            printLock.acquire()
                            print 'within processData, number of objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave is now', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)
                            printLock.release()
                        if len(self.ackDataThatWeHaveYetToSend) > 0:
                            self.data = self.ackDataThatWeHaveYetToSend.pop()
                    self.processData()
                else:
                    print 'Checksum incorrect. Clearing this message.'
                    self.data = self.data[self.payloadLength+24:]

    def isProofOfWorkSufficient(self,data):
        POW, = unpack('>Q',hashlib.sha512(hashlib.sha512(data[:8]+ hashlib.sha512(data[8:]).digest()).digest()).digest()[0:8])
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
        self.sendaddr() #This is one large addr message to this one peer.
        if connectionsCount[self.streamNumber] > 150:
            printLock.acquire()
            print 'We are connected to too many people. Closing connection.'
            printLock.release()
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
            bigInvList = {}
            for row in queryreturn:
                hash, = row
                if hash not in self.objectsOfWhichThisRemoteNodeIsAlreadyAware:
                    bigInvList[hash] = 0
                else:
                    printLock.acquire()
                    print 'Not including an object hash in a big inv message because the remote node is already aware of it.'#This line is here to check that this feature is working.
                    printLock.release()
            #We also have messages in our inventory in memory (which is a python dictionary). Let's fetch those too.
            for hash, storedValue in inventory.items():
                if hash not in self.objectsOfWhichThisRemoteNodeIsAlreadyAware:
                    objectType, streamNumber, payload, receivedTime = storedValue
                    if streamNumber == self.streamNumber and receivedTime > int(time.time())-maximumAgeOfObjectsThatIAdvertiseToOthers:
                        bigInvList[hash] = 0
                else:
                    printLock.acquire()
                    print 'Not including an object hash in a big inv message because the remote node is already aware of it.'#This line is here to check that this feature is working.
                    printLock.release()
            numberOfObjectsInInvMessage = 0
            payload = ''
            #Now let us start appending all of these hashes together. They will be sent out in a big inv message to our new peer.
            for hash, storedValue in bigInvList.items():
                payload += hash
                numberOfObjectsInInvMessage += 1
                if numberOfObjectsInInvMessage >= 50000: #We can only send a max of 50000 items per inv message but we may have more objects to advertise. They must be split up into multiple inv messages.
                    self.sendinvMessageToJustThisOnePeer(numberOfObjectsInInvMessage,payload)
                    payload = ''
                    numberOfObjectsInInvMessage = 0
            if numberOfObjectsInInvMessage > 0:
                self.sendinvMessageToJustThisOnePeer(numberOfObjectsInInvMessage,payload)

    #Self explanatory. Notice that there is also a broadcastinv function for broadcasting invs to everyone in our stream.
    def sendinvMessageToJustThisOnePeer(self,numberOfObjects,payload):
        payload = encodeVarint(numberOfObjects) + payload
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData += pack('>L',len(payload))
        headerData += hashlib.sha512(payload).digest()[:4]
        printLock.acquire()
        print 'Sending huge inv message with', numberOfObjects, 'objects to just this one peer'
        printLock.release()
        self.sock.send(headerData + payload)

    #We have received a broadcast message
    def recbroadcast(self,data):
        self.messageProcessingStartTime = time.time()
        #First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in broadcast message insufficient.'
            return
        embeddedTime, = unpack('>I',data[8:12])
        if embeddedTime > (int(time.time())+10800): #prevent funny business
            print 'The embedded time in this broadcast message is more than three hours in the future. That doesn\'t make sense. Ignoring message.'
            return
        if embeddedTime < (int(time.time())-maximumAgeOfAnObjectThatIAmWillingToAccept):
            print 'The embedded time in this broadcast message is too old. Ignoring message.'
            return
        if self.payloadLength < 66: #todo: When version 1 addresses are completely abandoned, this should be changed to 180
            print 'The payload length of this broadcast packet is unreasonably low. Someone is probably trying funny business. Ignoring message.'
            return
        inventoryLock.acquire()
        self.inventoryHash = calculateInventoryHash(data)
        if self.inventoryHash in inventory:
            print 'We have already received this broadcast object. Ignoring.'
            inventoryLock.release()
            return
        elif isInSqlInventory(self.inventoryHash):
            print 'We have already received this broadcast object (it is stored on disk in the SQL inventory). Ignoring it.'
            inventoryLock.release()
            return
        #It is valid so far. Let's let our peers know about it.
        objectType = 'broadcast'
        inventory[self.inventoryHash] = (objectType, self.streamNumber, data, embeddedTime)
        inventoryLock.release()
        self.broadcastinv(self.inventoryHash)
        self.emit(SIGNAL("incrementNumberOfBroadcastsProcessed()"))


        self.processbroadcast(data)#When this function returns, we will have either successfully processed this broadcast because we are interested in it, ignored it because we aren't interested in it, or found problem with the broadcast that warranted ignoring it.

        # Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. If we haven't used the specified amount of time, we shall sleep. These values are mostly the same values used for msg messages although broadcast messages are processed faster.
        if self.payloadLength > 100000000: #Size is greater than 100 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 100 #seconds.
        elif self.payloadLength > 10000000: #Between 100 and 10 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 20 #seconds.
        elif self.payloadLength > 1000000: #Between 10 and 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = 3 #seconds.
        else: #Less than 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = .1 #seconds.


        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - (time.time()- self.messageProcessingStartTime)
        if sleepTime > 0:
            printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime ,'seconds.'
            printLock.release()
            time.sleep(sleepTime)
        printLock.acquire()
        print 'Total message processing time:', time.time()- self.messageProcessingStartTime, 'seconds.'
        printLock.release()

    #A broadcast message has a valid time and POW and requires processing. The recbroadcast function calls this one.
    def processbroadcast(self,data):
        readPosition = 12
        broadcastVersion, broadcastVersionLength = decodeVarint(data[readPosition:readPosition+9])
        if broadcastVersion <> 1:
            #Cannot decode incoming broadcast versions higher than 1. Assuming the sender isn\' being silly, you should upgrade Bitmessage because this message shall be ignored.
            return
        readPosition += broadcastVersionLength
        beginningOfPubkeyPosition = readPosition #used when we add the pubkey to our pubkey table
        sendersAddressVersion, sendersAddressVersionLength = decodeVarint(data[readPosition:readPosition+9])
        if sendersAddressVersion <= 1 or sendersAddressVersion >=3:
            #Cannot decode senderAddressVersion higher than 2. Assuming the sender isn\' being silly, you should upgrade Bitmessage because this message shall be ignored.
            return
        readPosition += sendersAddressVersionLength
        if sendersAddressVersion == 2:
            sendersStream, sendersStreamLength = decodeVarint(data[readPosition:readPosition+9])
            if sendersStream <= 0 or sendersStream <> self.streamNumber:
                return
            readPosition += sendersStreamLength
            behaviorBitfield = data[readPosition:readPosition+4]
            readPosition += 4
            sendersPubSigningKey = '\x04' + data[readPosition:readPosition+64]
            readPosition += 64
            sendersPubEncryptionKey = '\x04' + data[readPosition:readPosition+64]
            readPosition += 64
            endOfPubkeyPosition = readPosition
            sendersHash = data[readPosition:readPosition+20]
            if sendersHash not in broadcastSendersForWhichImWatching:
                #Display timing data
                printLock.acquire()
                print 'Time spent deciding that we are not interested in this broadcast:', time.time()- self.messageProcessingStartTime
                printLock.release()
                return
            #At this point, this message claims to be from sendersHash and we are interested in it. We still have to hash the public key to make sure it is truly the key that matches the hash, and also check the signiture.
            readPosition += 20

            sha = hashlib.new('sha512')
            sha.update(sendersPubSigningKey+sendersPubEncryptionKey)
            ripe = hashlib.new('ripemd160')
            ripe.update(sha.digest())
            if ripe.digest() != sendersHash:
                #The sender of this message lied.
                return
            messageEncodingType, messageEncodingTypeLength = decodeVarint(data[readPosition:readPosition+9])
            if messageEncodingType == 0:
                return
            readPosition += messageEncodingTypeLength
            messageLength, messageLengthLength = decodeVarint(data[readPosition:readPosition+9])
            readPosition += messageLengthLength
            message = data[readPosition:readPosition+messageLength]
            readPosition += messageLength
            readPositionAtBottomOfMessage = readPosition
            signatureLength, signatureLengthLength = decodeVarint(data[readPosition:readPosition+9])
            readPosition += signatureLengthLength
            signature = data[readPosition:readPosition+signatureLength]
            try:
                highlevelcrypto.verify(data[12:readPositionAtBottomOfMessage],signature,sendersPubSigningKey.encode('hex'))
                print 'ECDSA verify passed'
            except Exception, err:
                print 'ECDSA verify failed', err
                return
            #verify passed

            #Let's store the public key in case we want to reply to this person.
            #We don't have the correct nonce or time (which would let us send out a pubkey message) so we'll just fill it with 1's. We won't be able to send this pubkey to others (without doing the proof of work ourselves, which this program is programmed to not do.)
            t = (ripe.digest(),False,'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'+'\xFF\xFF\xFF\xFF'+data[beginningOfPubkeyPosition:endOfPubkeyPosition],int(time.time()),'yes')
            sqlLock.acquire()
            sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            workerQueue.put(('newpubkey',(sendersAddressVersion,sendersStream,ripe.digest()))) #This will check to see whether we happen to be awaiting this pubkey in order to send a message. If we are, it will do the POW and send it.
            
            fromAddress = encodeAddress(sendersAddressVersion,sendersStream,ripe.digest())
            printLock.acquire()
            print 'fromAddress:', fromAddress
            printLock.release()
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
                t = (self.inventoryHash,toAddress,fromAddress,subject,int(time.time()),body,'inbox')
                sqlSubmitQueue.put('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?)''')
                sqlSubmitQueue.put(t)
                sqlReturnQueue.get()
                sqlLock.release()
                self.emit(SIGNAL("displayNewInboxMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),self.inventoryHash,toAddress,fromAddress,subject,body)

                #If we are behaving as an API then we might need to run an outside command to let some program know that a new message has arrived.
                if safeConfigGetBoolean('bitmessagesettings','apienabled'):
                    try:
                        apiNotifyPath = config.get('bitmessagesettings','apinotifypath')
                    except:
                        apiNotifyPath = ''
                    if apiNotifyPath != '':
                        call([apiNotifyPath, "newBroadcast"])

            #Display timing data
            printLock.acquire()
            print 'Time spent processing this interesting broadcast:', time.time()- self.messageProcessingStartTime
            printLock.release()


    #We have received a msg message.
    def recmsg(self,data):
        self.messageProcessingStartTime = time.time()
        #First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in msg message insufficient.'
            return

        readPosition = 8
        embeddedTime, = unpack('>I',data[readPosition:readPosition+4])
        if embeddedTime > int(time.time())+10800:
            print 'The time in the msg message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time())-maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in the msg message is too old. Ignoring it. Time:', embeddedTime
            return
        readPosition += 4
        streamNumberAsClaimedByMsg, streamNumberAsClaimedByMsgLength = decodeVarint(data[readPosition:readPosition+9])
        if streamNumberAsClaimedByMsg != self.streamNumber:
            print 'The stream number encoded in this msg (' + str(streamNumberAsClaimedByMsg) + ') message does not match the stream number on which it was received. Ignoring it.'
            return
        readPosition += streamNumberAsClaimedByMsgLength
        self.inventoryHash = calculateInventoryHash(data)
        inventoryLock.acquire()
        if self.inventoryHash in inventory:
            print 'We have already received this msg message. Ignoring.'
            inventoryLock.release()
            return
        elif isInSqlInventory(self.inventoryHash):
            print 'We have already received this msg message (it is stored on disk in the SQL inventory). Ignoring it.'
            inventoryLock.release()
            return
        #This msg message is valid. Let's let our peers know about it.
        objectType = 'msg'
        inventory[self.inventoryHash] = (objectType, self.streamNumber, data, embeddedTime)
        inventoryLock.release()
        self.broadcastinv(self.inventoryHash)
        self.emit(SIGNAL("incrementNumberOfMessagesProcessed()"))

        self.processmsg(readPosition,data) #When this function returns, we will have either successfully processed the message bound for us, ignored it because it isn't bound for us, or found problem with the message that warranted ignoring it.

        # Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. If we haven't used the specified amount of time, we shall sleep. These values are based on test timings and you may change them at-will.
        if self.payloadLength > 100000000: #Size is greater than 100 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 100 #seconds. Actual length of time it took my computer to decrypt and verify the signature of a 100 MB message: 3.7 seconds.
        elif self.payloadLength > 10000000: #Between 100 and 10 megabytes
            lengthOfTimeWeShouldUseToProcessThisMessage = 20 #seconds. Actual length of time it took my computer to decrypt and verify the signature of a 10 MB message: 0.53 seconds. Actual length of time it takes in practice when processing a real message: 1.44 seconds.
        elif self.payloadLength > 1000000: #Between 10 and 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = 3 #seconds. Actual length of time it took my computer to decrypt and verify the signature of a 1 MB message: 0.18 seconds. Actual length of time it takes in practice when processing a real message: 0.30 seconds.
        else: #Less than 1 megabyte
            lengthOfTimeWeShouldUseToProcessThisMessage = .6 #seconds. Actual length of time it took my computer to decrypt and verify the signature of a 100 KB message: 0.15 seconds. Actual length of time it takes in practice when processing a real message: 0.25 seconds.


        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - (time.time()- self.messageProcessingStartTime)
        if sleepTime > 0:
            printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime ,'seconds.'
            printLock.release()
            time.sleep(sleepTime)
        printLock.acquire()
        print 'Total message processing time:', time.time()- self.messageProcessingStartTime, 'seconds.'
        printLock.release()
        

    #A msg message has a valid time and POW and requires processing. The recmsg function calls this one.
    def processmsg(self,readPosition, encryptedData):
        initialDecryptionSuccessful = False
        #Let's check whether this is a message acknowledgement bound for us.
        if encryptedData[readPosition:] in ackdataForWhichImWatching:
            printLock.acquire()
            print 'This msg IS an acknowledgement bound for me.'
            printLock.release()
            del ackdataForWhichImWatching[encryptedData[readPosition:]]
            t = ('ackreceived',encryptedData[readPosition:])
            sqlLock.acquire()
            sqlSubmitQueue.put('UPDATE sent SET status=? WHERE ackdata=?')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),encryptedData[readPosition:],'Acknowledgement of the message received just now.')
            return
        else:
            printLock.acquire()
            print 'This was NOT an acknowledgement bound for me.' 
            #print 'ackdataForWhichImWatching', ackdataForWhichImWatching
            printLock.release()

        #This is not an acknowledgement bound for me. See if it is a message bound for me by trying to decrypt it with my private keys.
        for key, cryptorObject in myECAddressHashes.items():
            try:
                unencryptedData = cryptorObject.decrypt(encryptedData[readPosition:])
                toRipe = key #This is the RIPE hash of my pubkeys. We need this below to compare to the destination_ripe included in the encrypted data.
                initialDecryptionSuccessful = True
                print 'EC decryption successful using key associated with ripe hash:', key.encode('hex')
                break
            except Exception, err:
                pass
                #print 'cryptorObject.decrypt Exception:', err
        if not initialDecryptionSuccessful:
            #This is not a message bound for me.
            printLock.acquire()
            print 'Length of time program spent failing to decrypt this message:', time.time()- self.messageProcessingStartTime, 'seconds.'
            printLock.release()
        else:
            #This is a message bound for me.
            readPosition = 0
            messageVersion, messageVersionLength = decodeVarint(unencryptedData[readPosition:readPosition+10])
            readPosition += messageVersionLength
            if messageVersion != 1:
                print 'Cannot understand message versions other than one. Ignoring message.'
                return
            sendersAddressVersionNumber, sendersAddressVersionNumberLength = decodeVarint(unencryptedData[readPosition:readPosition+10])
            readPosition += sendersAddressVersionNumberLength
            if sendersAddressVersionNumber == 0:
                print 'Cannot understand sendersAddressVersionNumber = 0. Ignoring message.'
                return
            if sendersAddressVersionNumber >= 3:
                print 'Sender\'s address version number', sendersAddressVersionNumber, ' not yet supported. Ignoring message.'
                return
            if len(unencryptedData) < 170:
                print 'Length of the unencrypted data is unreasonably short. Sanity check failed. Ignoring message.'
                return
            sendersStreamNumber, sendersStreamNumberLength = decodeVarint(unencryptedData[readPosition:readPosition+10])
            if sendersStreamNumber == 0:
                print 'sender\'s stream number is 0. Ignoring message.'
                return
            readPosition += sendersStreamNumberLength
            behaviorBitfield = unencryptedData[readPosition:readPosition+4]
            readPosition += 4
            pubSigningKey = '\x04' + unencryptedData[readPosition:readPosition+64]
            readPosition += 64
            pubEncryptionKey = '\x04' + unencryptedData[readPosition:readPosition+64]
            readPosition += 64
            endOfThePublicKeyPosition = readPosition #needed for when we store the pubkey in our database of pubkeys for later use.
            if toRipe != unencryptedData[readPosition:readPosition+20]:
                printLock.acquire()
                print 'The original sender of this message did not send it to you. Someone is attempting a Surreptitious Forwarding Attack.'
                print 'See: http://world.std.com/~dtd/sign_encrypt/sign_encrypt7.html'
                print 'your toRipe:', toRipe.encode('hex')
                print 'embedded destination toRipe:', unencryptedData[readPosition:readPosition+20].encode('hex')
                printLock.release()
                return
            readPosition += 20
            messageEncodingType, messageEncodingTypeLength = decodeVarint(unencryptedData[readPosition:readPosition+10])
            readPosition += messageEncodingTypeLength
            messageLength, messageLengthLength = decodeVarint(unencryptedData[readPosition:readPosition+10])
            readPosition += messageLengthLength
            message = unencryptedData[readPosition:readPosition+messageLength]
            #print 'First 150 characters of message:', repr(message[:150])
            readPosition += messageLength
            ackLength, ackLengthLength = decodeVarint(unencryptedData[readPosition:readPosition+10])
            readPosition += ackLengthLength
            ackData = unencryptedData[readPosition:readPosition+ackLength]
            readPosition += ackLength
            positionOfBottomOfAckData = readPosition #needed to mark the end of what is covered by the signature
            signatureLength, signatureLengthLength = decodeVarint(unencryptedData[readPosition:readPosition+10])
            readPosition += signatureLengthLength
            signature = unencryptedData[readPosition:readPosition+signatureLength]
            try:
                highlevelcrypto.verify(unencryptedData[:positionOfBottomOfAckData],signature,pubSigningKey.encode('hex'))
                print 'ECDSA verify passed'
            except Exception, err:
                print 'ECDSA verify failed', err
                return
            printLock.acquire()
            print 'As a matter of intellectual curiosity, here is the Bitcoin address associated with the keys owned by the other person:', calculateBitcoinAddressFromPubkey(pubSigningKey), '  ..and here is the testnet address:',calculateTestnetAddressFromPubkey(pubSigningKey),'. The other person must take their private signing key from Bitmessage and import it into Bitcoin (or a service like Blockchain.info) for it to be of any use. Do not use this unless you know what you are doing.'
            printLock.release()
            #calculate the fromRipe.
            sha = hashlib.new('sha512')
            sha.update(pubSigningKey+pubEncryptionKey)
            ripe = hashlib.new('ripemd160')
            ripe.update(sha.digest())
            #Let's store the public key in case we want to reply to this person.
            #We don't have the correct nonce or time (which would let us send out a pubkey message) so we'll just fill it with 1's. We won't be able to send this pubkey to others (without doing the proof of work ourselves, which this program is programmed to not do.)
            t = (ripe.digest(),False,'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'+'\xFF\xFF\xFF\xFF'+unencryptedData[messageVersionLength:endOfThePublicKeyPosition],int(time.time()),'yes')
            sqlLock.acquire()
            sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            workerQueue.put(('newpubkey',(sendersAddressVersionNumber,sendersStreamNumber,ripe.digest()))) #This will check to see whether we happen to be awaiting this pubkey in order to send a message. If we are, it will do the POW and send it.
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
                        printLock.acquire()
                        print 'Message ignored because address is in blacklist.'
                        printLock.release()
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
                if messageEncodingType <> 0:
                    sqlLock.acquire()
                    t = (self.inventoryHash,toAddress,fromAddress,subject,int(time.time()),body,'inbox')
                    sqlSubmitQueue.put('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?)''')
                    sqlSubmitQueue.put(t)
                    sqlReturnQueue.get()
                    sqlLock.release()
                    self.emit(SIGNAL("displayNewInboxMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),self.inventoryHash,toAddress,fromAddress,subject,body)

                #If we are behaving as an API then we might need to run an outside command to let some program know that a new message has arrived.
                if safeConfigGetBoolean('bitmessagesettings','apienabled'):
                    try:
                        apiNotifyPath = config.get('bitmessagesettings','apinotifypath')
                    except:
                        apiNotifyPath = ''
                    if apiNotifyPath != '':
                        call([apiNotifyPath, "newMessage"])

                #Let us now check and see whether our receiving address is behaving as a mailing list
                if safeConfigGetBoolean(toAddress,'mailinglist'):
                    try:
                        mailingListName = config.get(toAddress, 'mailinglistname')
                    except:
                        mailingListName = ''
                    #Let us send out this message as a broadcast
                    subject = self.addMailingListNameToSubject(subject,mailingListName)
                    #Let us now send this message out as a broadcast
                    message = 'Message ostensibly from ' + fromAddress + ':\n\n' + body
                    fromAddress = toAddress #The fromAddress for the broadcast is the toAddress (my address) for the msg message we are currently processing.
                    ackdata = OpenSSL.rand(32) #We don't actually need the ackdata for acknowledgement since this is a broadcast message but we can use it to update the user interface when the POW is done generating.
                    toAddress = '[Broadcast subscribers]'
                    ripe = ''
                    sqlLock.acquire()
                    t = ('',toAddress,ripe,fromAddress,subject,message,ackdata,int(time.time()),'broadcastpending',1,1,'sent')
                    sqlSubmitQueue.put('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''')
                    sqlSubmitQueue.put(t)
                    sqlReturnQueue.get()
                    sqlLock.release()

                    self.emit(SIGNAL("displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),toAddress,'[Broadcast subscribers]',fromAddress,subject,message,ackdata)
                    workerQueue.put(('sendbroadcast',(fromAddress,subject,message)))

            #Now let's consider sending the acknowledgement. We'll need to make sure that our client will properly process the ackData; if the packet is malformed, we could clear out self.data and an attacker could use that behavior to determine that we were capable of decoding this message.
            ackDataValidThusFar = True
            if len(ackData) < 24:
                print 'The length of ackData is unreasonably short. Not sending ackData.'
                ackDataValidThusFar = False
            elif ackData[0:4] != '\xe9\xbe\xb4\xd9':
                print 'Ackdata magic bytes were wrong. Not sending ackData.'
                ackDataValidThusFar = False
            if ackDataValidThusFar:
                ackDataPayloadLength, = unpack('>L',ackData[16:20])
                if len(ackData)-24 != ackDataPayloadLength:
                    print 'ackData payload length doesn\'t match the payload length specified in the header. Not sending ackdata.'
                    ackDataValidThusFar = False
            if ackDataValidThusFar:
                print 'ackData is valid. Will process it.'
                self.ackDataThatWeHaveYetToSend.append(ackData) #When we have processed all data, the processData function will pop the ackData out and process it as if it is a message received from our peer.
            #Display timing data
            timeRequiredToAttemptToDecryptMessage = time.time()- self.messageProcessingStartTime
            successfullyDecryptMessageTimings.append(timeRequiredToAttemptToDecryptMessage)
            sum = 0
            for item in successfullyDecryptMessageTimings:
                sum += item
            printLock.acquire()
            print 'Time to decrypt this message successfully:', timeRequiredToAttemptToDecryptMessage
            print 'Average time for all message decryption successes since startup:', sum / len(successfullyDecryptMessageTimings)
            printLock.release()

    def addMailingListNameToSubject(self,subject,mailingListName):
        subject = subject.strip()
        if subject[:3] == 'Re:' or subject[:3] == 'RE:':
            subject = subject[3:].strip()
        if '['+mailingListName+']' in subject:
            return subject
        else:
            return '['+mailingListName+'] ' + subject

    #We have received a pubkey
    def recpubkey(self,data):
        self.pubkeyProcessingStartTime = time.time()
        if len(data) < 146 or len(data) >600: #sanity check
            return
        #We must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in pubkey message insufficient.'
            return

        readPosition = 8 #for the nonce
        embeddedTime, = unpack('>I',data[readPosition:readPosition+4])
        if embeddedTime < int(time.time())-lengthOfTimeToHoldOnToAllPubkeys-86400: #If the pubkey is more than a month old then reject it. (the 86400 is included to give an extra day of wiggle-room. If the wiggle-room is actually of any use, everyone on the network will delete this pubkey from their database the next time the cleanerThread cleans anyway- except for the node that actually wants the pubkey.)
            printLock.acquire()
            print 'The embedded time in this pubkey message is too old. Ignoring. Embedded time is:', embeddedTime
            printLock.release()
            return
        if embeddedTime > int(time.time()) + 10800:
            printLock.acquire()
            print 'The embedded time in this pubkey message more than several hours in the future. This is irrational. Ignoring message.'
            printLock.release()
            return
        readPosition += 4 #for the time
        addressVersion, varintLength = decodeVarint(data[readPosition:readPosition+10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(data[readPosition:readPosition+10])
        readPosition += varintLength
        if self.streamNumber != streamNumber:
            print 'stream number embedded in this pubkey doesn\'t match our stream number. Ignoring.'
            return

        inventoryHash = calculateInventoryHash(data)
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
        inventory[inventoryHash] = (objectType, self.streamNumber, data, int(time.time()))
        inventoryLock.release()
        self.broadcastinv(inventoryHash)
        self.emit(SIGNAL("incrementNumberOfPubkeysProcessed()"))

        self.processpubkey(data)

        lengthOfTimeWeShouldUseToProcessThisMessage = .2
        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - (time.time()- self.pubkeyProcessingStartTime)
        if sleepTime > 0:
            #printLock.acquire()
            #print 'Timing attack mitigation: Sleeping for', sleepTime ,'seconds.'
            #printLock.release()
            time.sleep(sleepTime)
        #printLock.acquire()
        #print 'Total pubkey processing time:', time.time()- self.pubkeyProcessingStartTime, 'seconds.'
        #printLock.release()

    def processpubkey(self,data):
        readPosition = 8 #for the nonce
        embeddedTime, = unpack('>I',data[readPosition:readPosition+4])
        readPosition += 4 #for the time
        addressVersion, varintLength = decodeVarint(data[readPosition:readPosition+10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(data[readPosition:readPosition+10])
        readPosition += varintLength
        if addressVersion == 0:
            print '(Within processpubkey) addressVersion of 0 doesn\'t make sense.'
            return
        if addressVersion >= 3 or addressVersion == 1:
            printLock.acquire()
            print 'This version of Bitmessage cannot handle version', addressVersion,'addresses.'
            printLock.release()
            return
        if addressVersion == 2:
            if self.payloadLength < 146: #sanity check. This is the minimum possible length.
                print 'payloadLength less than 146. Sanity check failed.'
                return
            bitfieldBehaviors = data[readPosition:readPosition+4]
            readPosition += 4
            publicSigningKey = data[readPosition:readPosition+64]
            #Is it possible for a public key to be invalid such that trying to encrypt or sign with it will cause an error? If it is, we should probably test these keys here.
            readPosition += 64
            publicEncryptionKey = data[readPosition:readPosition+64]
            if len(publicEncryptionKey) < 64:
                print 'publicEncryptionKey length less than 64. Sanity check failed.'
                return
            sha = hashlib.new('sha512')
            sha.update('\x04'+publicSigningKey+'\x04'+publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()

            printLock.acquire()
            print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
            print 'ripe', ripe.encode('hex')
            print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
            print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')
            printLock.release()

            t = (ripe,)
            sqlLock.acquire()
            sqlSubmitQueue.put('''SELECT usedpersonally FROM pubkeys WHERE hash=? AND usedpersonally='yes' ''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()
            if queryreturn != []: #if this pubkey is already in our database and if we have used it personally:
                print 'We HAVE used this pubkey personally. Updating time.'
                t = (ripe,True,data,embeddedTime,'yes')
                sqlLock.acquire()
                sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''')
                sqlSubmitQueue.put(t)
                sqlReturnQueue.get()
                sqlLock.release()
                printLock.acquire()
                printLock.release()
                workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))
            else:
                print 'We have NOT used this pubkey personally. Inserting in database.'
                t = (ripe,True,data,embeddedTime,'no')  #This will also update the embeddedTime.
                sqlLock.acquire()
                sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''')
                sqlSubmitQueue.put(t)
                sqlReturnQueue.get()
                sqlLock.release()
                printLock.acquire()
                printLock.release()
                workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))


    #We have received a getpubkey message
    def recgetpubkey(self,data):
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in getpubkey message insufficient.'
            return
        if len(data) < 34:
            print 'getpubkey message doesn\'t contain enough data. Ignoring.'
            return
        embeddedTime, = unpack('>I',data[8:12])
        if embeddedTime > int(time.time())+10800:
            print 'The time in this getpubkey message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time())-maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in this getpubkey message is too old. Ignoring it. Time:', embeddedTime
            return

        addressVersionNumber, addressVersionLength = decodeVarint(data[12:22])
        streamNumber, streamNumberLength = decodeVarint(data[12+addressVersionLength:22+addressVersionLength])
        if streamNumber <> self.streamNumber:
            print 'The streamNumber', streamNumber, 'doesn\'t match our stream number:', self.streamNumber
            return

        inventoryHash = calculateInventoryHash(data)
        inventoryLock.acquire()
        if inventoryHash in inventory:
            print 'We have already received this getpubkey request. Ignoring it.'
            inventoryLock.release()
            return
        elif isInSqlInventory(inventoryHash):
            print 'We have already received this getpubkey request (it is stored on disk in the SQL inventory). Ignoring it.'
            inventoryLock.release()
            return
        self.objectsOfWhichThisRemoteNodeIsAlreadyAware[inventoryHash] = 0
        objectType = 'getpubkey'
        inventory[inventoryHash] = (objectType, self.streamNumber, data, embeddedTime)
        inventoryLock.release()
        #This getpubkey request is valid so far. Forward to peers.
        self.broadcastinv(inventoryHash)

        if addressVersionNumber == 0:
            print 'The addressVersionNumber of the pubkey request is zero. That doesn\'t make any sense. Ignoring it.'
            return
        elif addressVersionNumber == 1:
            print 'The addressVersionNumber of the pubkey request is 1 which isn\'t supported anymore. Ignoring it.'
            return
        elif addressVersionNumber > 2:
            print 'The addressVersionNumber of the pubkey request is too high. Can\'t understand. Ignoring it.'
            return

        requestedHash = data[12+addressVersionLength+streamNumberLength:32+addressVersionLength+streamNumberLength]
        if len(requestedHash) != 20:
            print 'The length of the requested hash is not 20 bytes. Something is wrong. Ignoring.'
            return
        print 'the hash requested in this getpubkey request is:', requestedHash.encode('hex')

        sqlLock.acquire()
        t = (requestedHash,int(time.time())-lengthOfTimeToHoldOnToAllPubkeys) #this prevents SQL injection
        sqlSubmitQueue.put('''SELECT hash, transmitdata, time FROM pubkeys WHERE hash=? AND havecorrectnonce=1 AND time>?''')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        if queryreturn != []:
            for row in queryreturn:
                hash, payload, timeEncodedInPubkey = row
            printLock.acquire()
            print 'We have the requested pubkey stored in our database of pubkeys. Sending it.'
            printLock.release()
            inventoryHash = calculateInventoryHash(payload)
            objectType = 'pubkey'
            inventory[inventoryHash] = (objectType, self.streamNumber, payload, timeEncodedInPubkey)#If the time embedded in this pubkey is more than 3 days old then this object isn't going to last very long in the inventory- the cleanerThread is going to come along and move it from the inventory in memory to the SQL inventory and then delete it from the SQL inventory. It should still find its way back to the original requestor if he is online however.
            self.broadcastinv(inventoryHash)
        else: #the pubkey is not in our database of pubkeys. Let's check if the requested key is ours (which would mean we should do the POW, put it in the pubkey table, and broadcast out the pubkey.)
            if requestedHash in myECAddressHashes: #if this address hash is one of mine
                printLock.acquire()
                print 'Found getpubkey-requested-hash in my list of EC hashes. Telling Worker thread to do the POW for a pubkey message and send it out.'
                printLock.release()
                workerQueue.put(('doPOWForMyV2Pubkey',requestedHash))
            else:
                printLock.acquire()
                print 'This getpubkey request is not for any of my keys.'
                printLock.release()


    #We have received an inv message
    def recinv(self,data):
        numberOfItemsInInv, lengthOfVarint = decodeVarint(data[:10])
        if len(data) < lengthOfVarint + (numberOfItemsInInv * 32):
            print 'inv message doesn\'t contain enough data. Ignoring.'
            return
        if numberOfItemsInInv == 1: #we'll just request this data from the person who advertised the object.
            if data[lengthOfVarint:32+lengthOfVarint] in inventory:
                printLock.acquire()
                print 'Inventory (in memory) has inventory item already.'
                printLock.release()
            elif isInSqlInventory(data[lengthOfVarint:32+lengthOfVarint]):
                print 'Inventory (SQL on disk) has inventory item already.'
            else:
                self.sendgetdata(data[lengthOfVarint:32+lengthOfVarint])
        else:
            print 'inv message lists', numberOfItemsInInv, 'objects.'
            for i in range(numberOfItemsInInv): #upon finishing dealing with an incoming message, the receiveDataThread will request a random object from the peer. This way if we get multiple inv messages from multiple peers which list mostly the same objects, we will make getdata requests for different random objects from the various peers.
                if len(data[lengthOfVarint+(32*i):32+lengthOfVarint+(32*i)]) == 32: #The length of an inventory hash should be 32. If it isn't 32 then the remote node is either badly programmed or behaving nefariously.
                    self.objectsOfWhichThisRemoteNodeIsAlreadyAware[data[lengthOfVarint+(32*i):32+lengthOfVarint+(32*i)]] = 0
                    self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[data[lengthOfVarint+(32*i):32+lengthOfVarint+(32*i)]] = 0


    #Send a getdata message to our peer to request the object with the given hash
    def sendgetdata(self,hash):
        print 'sending getdata to retrieve object with hash:', hash.encode('hex')
        payload = '\x01' + hash
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'getdata\x00\x00\x00\x00\x00'
        headerData += pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
        headerData += hashlib.sha512(payload).digest()[:4]
        try:
            self.sock.send(headerData + payload)
        except Exception, err:
            if not 'Bad file descriptor' in err:
                printLock.acquire()
                sys.stderr.write('sock.send error: %s\n' % err)
                printLock.release()

    #We have received a getdata request from our peer
    def recgetdata(self, data):
        value, lengthOfVarint = decodeVarint(data[:10])
        #print 'Number of items in getdata request:', value
        try:
            for i in xrange(value):
                hash = data[lengthOfVarint+(i*32):32+lengthOfVarint+(i*32)]
                printLock.acquire()
                print 'received getdata request for item:', hash.encode('hex')
                printLock.release()
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
            headerData += 'pubkey\x00\x00\x00\x00\x00\x00'
            headerData += pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData += hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'getpubkey':
            print 'sending getpubkey'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData += 'getpubkey\x00\x00\x00'
            headerData += pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData += hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'msg':
            print 'sending msg'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData += 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            headerData += pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData += hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'broadcast':
            print 'sending broadcast'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData += 'broadcast\x00\x00\x00'
            headerData += pack('>L',len(payload)) #payload length. Note that we add an extra 8 for the nonce.
            headerData += hashlib.sha512(payload).digest()[:4]
            self.sock.send(headerData + payload)
        elif objectType == 'getpubkey' or objectType == 'pubkeyrequest':
            print 'sending getpubkey'
            headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
            headerData += 'getpubkey\x00\x00\x00' #version command
            headerData += pack('>L',len(payload)) #payload length
            headerData += hashlib.sha512(payload).digest()[0:4]
            self.sock.send(headerData + payload)
        else:
            sys.stderr.write('Error: sendData has been asked to send a strange objectType: %s\n' % str(objectType))

    #Send an inv message with just one hash to all of our peers
    def broadcastinv(self,hash):
        printLock.acquire()
        print 'broadcasting inv with hash:', hash.encode('hex')
        printLock.release()
        broadcastToSendDataQueues((self.streamNumber, 'sendinv', hash))


    #We have received an addr message.
    def recaddr(self,data):
        listOfAddressDetailsToBroadcastToPeers = []
        numberOfAddressesIncluded = 0
        numberOfAddressesIncluded, lengthOfNumberOfAddresses = decodeVarint(data[:10])

        if verbose >= 1:
            printLock.acquire()
            print 'addr message contains', numberOfAddressesIncluded, 'IP addresses.'
            printLock.release()
            #print 'lengthOfNumberOfAddresses', lengthOfNumberOfAddresses

        if numberOfAddressesIncluded > 1000 or numberOfAddressesIncluded == 0:
            return
        if self.payloadLength < lengthOfNumberOfAddresses + (34 * numberOfAddressesIncluded):
            print 'addr message does not contain enough data. Ignoring.'
            return

        needToWriteKnownNodesToDisk = False
        for i in range(0,numberOfAddressesIncluded):
            try:
                if data[16+lengthOfNumberOfAddresses+(34*i):28+lengthOfNumberOfAddresses+(34*i)] != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                    printLock.acquire()
                    print 'Skipping IPv6 address.', repr(data[16+lengthOfNumberOfAddresses+(34*i):28+lengthOfNumberOfAddresses+(34*i)])
                    printLock.release()
                    continue
            except Exception, err:
                printLock.acquire()
                sys.stderr.write('ERROR TRYING TO UNPACK recaddr (to test for an IPv6 address). Message: %s\n' % str(err))
                printLock.release()
                break #giving up on unpacking any more. We should still be connected however.

            try:
                recaddrStream, = unpack('>I',data[4+lengthOfNumberOfAddresses+(34*i):8+lengthOfNumberOfAddresses+(34*i)])
            except Exception, err:
                printLock.acquire()
                sys.stderr.write('ERROR TRYING TO UNPACK recaddr (recaddrStream). Message: %s\n' % str(err))
                printLock.release()
                break #giving up on unpacking any more. We should still be connected however.
            if recaddrStream == 0:
                continue
            if recaddrStream != self.streamNumber and recaddrStream != (self.streamNumber * 2) and recaddrStream != ((self.streamNumber * 2) + 1): #if the embedded stream number is not in my stream or either of my child streams then ignore it. Someone might be trying funny business.
                continue
            try:
                recaddrServices, = unpack('>Q',data[8+lengthOfNumberOfAddresses+(34*i):16+lengthOfNumberOfAddresses+(34*i)])
            except Exception, err:
                printLock.acquire()
                sys.stderr.write('ERROR TRYING TO UNPACK recaddr (recaddrServices). Message: %s\n' % str(err))
                printLock.release()
                break #giving up on unpacking any more. We should still be connected however.

            try:
                recaddrPort, = unpack('>H',data[32+lengthOfNumberOfAddresses+(34*i):34+lengthOfNumberOfAddresses+(34*i)])
            except Exception, err:
                printLock.acquire()
                sys.stderr.write('ERROR TRYING TO UNPACK recaddr (recaddrPort). Message: %s\n' % str(err))
                printLock.release()
                break #giving up on unpacking any more. We should still be connected however.
            #print 'Within recaddr(): IP', recaddrIP, ', Port', recaddrPort, ', i', i
            hostFromAddrMessage = socket.inet_ntoa(data[28+lengthOfNumberOfAddresses+(34*i):32+lengthOfNumberOfAddresses+(34*i)])
            #print 'hostFromAddrMessage', hostFromAddrMessage
            if data[28+lengthOfNumberOfAddresses+(34*i)] == '\x7F':
                print 'Ignoring IP address in loopback range:', hostFromAddrMessage
                continue
            if data[28+lengthOfNumberOfAddresses+(34*i)] == '\x0A':
                print 'Ignoring IP address in private range:', hostFromAddrMessage
                continue
            if data[28+lengthOfNumberOfAddresses+(34*i):30+lengthOfNumberOfAddresses+(34*i)] == '\xC0A8':
                print 'Ignoring IP address in private range:', hostFromAddrMessage
                continue
            timeSomeoneElseReceivedMessageFromThisNode, = unpack('>I',data[lengthOfNumberOfAddresses+(34*i):4+lengthOfNumberOfAddresses+(34*i)]) #This is the 'time' value in the received addr message.
            if recaddrStream not in knownNodes: #knownNodes is a dictionary of dictionaries with one outer dictionary for each stream. If the outer stream dictionary doesn't exist yet then we must make it.
                knownNodes[recaddrStream] = {}
            if hostFromAddrMessage not in knownNodes[recaddrStream]:
                if len(knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time())-10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800): #If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                    knownNodes[recaddrStream][hostFromAddrMessage] = (recaddrPort, timeSomeoneElseReceivedMessageFromThisNode)
                    print 'added new node', hostFromAddrMessage, 'to knownNodes in stream', recaddrStream
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
        printLock.acquire()
        print 'knownNodes currently has', len(knownNodes[self.streamNumber]), 'nodes for this stream.'
        printLock.release()

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

        if verbose >= 1:
            printLock.acquire()
            print 'Broadcasting addr with', numberOfAddressesInAddrMessage, 'entries.'
            printLock.release()
        broadcastToSendDataQueues((self.streamNumber, 'sendaddr', datatosend))

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
                if self.isHostInPrivateIPRange(HOST):
                    continue
                addrsInMyStream[HOST] = knownNodes[self.streamNumber][HOST]
        if len(knownNodes[self.streamNumber*2]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(knownNodes[self.streamNumber*2],  1)
                if self.isHostInPrivateIPRange(HOST):
                    continue
                addrsInChildStreamLeft[HOST] = knownNodes[self.streamNumber*2][HOST]
        if len(knownNodes[(self.streamNumber*2)+1]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(knownNodes[(self.streamNumber*2)+1],  1)
                if self.isHostInPrivateIPRange(HOST):
                    continue
                addrsInChildStreamRight[HOST] = knownNodes[(self.streamNumber*2)+1][HOST]

        numberOfAddressesInAddrMessage = 0
        payload = ''
        #print 'addrsInMyStream.items()', addrsInMyStream.items()
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

        if verbose >= 1:
            printLock.acquire()
            print 'Sending addr with', numberOfAddressesInAddrMessage, 'entries.'
            printLock.release()
        self.sock.send(datatosend)

    #We have received a version message
    def recversion(self,data):
        if self.payloadLength < 83:
            #This version message is unreasonably short. Forget it.
            return
        elif not self.verackSent: 
            self.remoteProtocolVersion, = unpack('>L',data[:4])
            #print 'remoteProtocolVersion', self.remoteProtocolVersion
            self.myExternalIP = socket.inet_ntoa(data[40:44])
            #print 'myExternalIP', self.myExternalIP
            self.remoteNodeIncomingPort, = unpack('>H',data[70:72])
            #print 'remoteNodeIncomingPort', self.remoteNodeIncomingPort
            useragentLength, lengthOfUseragentVarint = decodeVarint(data[80:84])
            readPosition = 80 + lengthOfUseragentVarint
            useragent = data[readPosition:readPosition+useragentLength]
            readPosition += useragentLength
            numberOfStreamsInVersionMessage, lengthOfNumberOfStreamsInVersionMessage = decodeVarint(data[readPosition:])
            readPosition += lengthOfNumberOfStreamsInVersionMessage
            self.streamNumber, lengthOfRemoteStreamNumber = decodeVarint(data[readPosition:])
            printLock.acquire()
            print 'Remote node useragent:', useragent, '  stream number:', self.streamNumber
            printLock.release()
            if self.streamNumber != 1:
                self.sock.close()
                printLock.acquire()
                print 'Closed connection to', self.HOST, 'because they are interested in stream', self.streamNumber,'.'
                printLock.release()
                return
            #If this was an incoming connection, then the sendData thread doesn't know the stream. We have to set it.
            if not self.initiatedConnection:
                broadcastToSendDataQueues((0,'setStreamNumber',(self.HOST,self.streamNumber)))
            if data[72:80] == eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
                self.sock.close()
                printLock.acquire()
                print 'Closing connection to myself: ', self.HOST
                printLock.release()
                return

            knownNodes[self.streamNumber][self.HOST] = (self.remoteNodeIncomingPort, int(time.time()))
            output = open(appdata + 'knownnodes.dat', 'wb')
            pickle.dump(knownNodes, output)
            output.close()

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

        payload += pack('>q',1) #boolservices offered by the remote node. This data is ignored by the remote host because how could We know what Their services are without them telling us?
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
        print 'Sending version message'
        printLock.release()
        self.sock.send(datatosend)
        #self.versionSent = 1

    #Sends a verack message
    def sendverack(self):
        printLock.acquire()
        print 'Sending verack'
        printLock.release()
        self.sock.sendall('\xE9\xBE\xB4\xD9\x76\x65\x72\x61\x63\x6B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
                                                                                                             #cf  83  e1  35
        self.verackSent = True
        if self.verackReceived == True:
            self.connectionFullyEstablished()

    def isHostInPrivateIPRange(self,host):
        if host[:3] == '10.':
            return True
        if host[:4] == '172.':
            if host[6] == '.':
                if int(host[4:6]) >= 16 and int(host[4:6]) <= 31:
                    return True
        if host[:8] == '192.168.':
            return True
        return False

#Every connection to a peer has a sendDataThread (and also a receiveDataThread).
class sendDataThread(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.mailbox = Queue.Queue()
        sendDataQueues.append(self.mailbox)
        self.data = ''

    def setup(self,sock,HOST,PORT,streamNumber,objectsOfWhichThisRemoteNodeIsAlreadyAware):
        self.sock = sock
        self.HOST = HOST
        self.PORT = PORT
        self.streamNumber = streamNumber
        self.lastTimeISentData = int(time.time()) #If this value increases beyond five minutes ago, we'll send a pong message to keep the connection alive.
        self.objectsOfWhichThisRemoteNodeIsAlreadyAware = objectsOfWhichThisRemoteNodeIsAlreadyAware
        printLock.acquire()
        print 'The streamNumber of this sendDataThread (ID:', id(self),') at setup() is', self.streamNumber
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
                elif command == 'sendaddr':
                    try:
                        #To prevent some network analysis, 'leak' the data out to our peer after waiting a random amount of time unless we have a long list of messages in our queue to send.
                        random.seed()
                        time.sleep(random.randrange(0, 10))
                        self.sock.sendall(data)
                        self.lastTimeISentData = int(time.time())
                    except:
                        print 'self.sock.sendall failed'
                        self.sock.close()
                        sendDataQueues.remove(self.mailbox)
                        print 'sendDataThread thread', self, 'ending now'
                        break
                elif command == 'sendinv':
                    if data not in self.objectsOfWhichThisRemoteNodeIsAlreadyAware:
                        payload = '\x01' + data
                        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
                        headerData += 'inv\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        headerData += pack('>L',len(payload))
                        headerData += hashlib.sha512(payload).digest()[:4]
                        #To prevent some network analysis, 'leak' the data out to our peer after waiting a random amount of time
                        random.seed()
                        time.sleep(random.randrange(0, 10))
                        try:
                            self.sock.sendall(headerData + payload)
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

def decodeWalletImportFormat(WIFstring):
    fullString = arithmetic.changebase(WIFstring,58,256)
    privkey = fullString[:-4]
    if fullString[-4:] != hashlib.sha256(hashlib.sha256(privkey).digest()).digest()[:4]:
        sys.stderr.write('Major problem! When trying to decode one of your private keys, the checksum failed. Here is the PRIVATE key: %s\n' % str(WIFstring))
        return ""
    else:
        #checksum passed
        if privkey[0] == '\x80':
            return privkey[1:]
        else:
            sys.stderr.write('Major problem! When trying to decode one of your private keys, the checksum passed but the key doesn\'t begin with hex 80. Here is the PRIVATE key: %s\n' % str(WIFstring))
            return ""

def reloadMyAddressHashes():
    printLock.acquire()
    print 'reloading keys from keys.dat file'
    printLock.release()
    myRSAAddressHashes.clear()
    myECAddressHashes.clear()
    #myPrivateKeys.clear()
    configSections = config.sections()
    for addressInKeysFile in configSections:
        if addressInKeysFile <> 'bitmessagesettings':
            isEnabled = config.getboolean(addressInKeysFile, 'enabled')
            if isEnabled:
                status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
                if addressVersionNumber == 2:
                    privEncryptionKey = decodeWalletImportFormat(config.get(addressInKeysFile, 'privencryptionkey')).encode('hex') #returns a simple 32 bytes of information encoded in 64 Hex characters, or null if there was an error
                    if len(privEncryptionKey) == 64:#It is 32 bytes encoded as 64 hex characters
                        myECAddressHashes[hash] = highlevelcrypto.makeCryptor(privEncryptionKey)
                elif addressVersionNumber == 1:
                    n = config.getint(addressInKeysFile, 'n')
                    e = config.getint(addressInKeysFile, 'e')
                    d = config.getint(addressInKeysFile, 'd')
                    p = config.getint(addressInKeysFile, 'p')
                    q = config.getint(addressInKeysFile, 'q')
                    myRSAAddressHashes[hash] = rsa.PrivateKey(n,e,d,p,q)

#This function expects that pubkey begin with \x04
def calculateBitcoinAddressFromPubkey(pubkey):
    if len(pubkey)!= 65:
        print 'Could not calculate Bitcoin address from pubkey because function was passed a pubkey that was', len(pubkey),'bytes long rather than 65.'
        return "error"
    ripe = hashlib.new('ripemd160')
    sha = hashlib.new('sha256')
    sha.update(pubkey)
    ripe.update(sha.digest())
    ripeWithProdnetPrefix = '\x00' + ripe.digest()

    checksum = hashlib.sha256(hashlib.sha256(ripeWithProdnetPrefix).digest()).digest()[:4]
    binaryBitcoinAddress = ripeWithProdnetPrefix + checksum
    numberOfZeroBytesOnBinaryBitcoinAddress = 0
    while binaryBitcoinAddress[0] == '\x00':
        numberOfZeroBytesOnBinaryBitcoinAddress += 1
        binaryBitcoinAddress = binaryBitcoinAddress[1:]
    base58encoded = arithmetic.changebase(binaryBitcoinAddress,256,58)
    return "1"*numberOfZeroBytesOnBinaryBitcoinAddress + base58encoded

def calculateTestnetAddressFromPubkey(pubkey):
    if len(pubkey)!= 65:
        print 'Could not calculate Bitcoin address from pubkey because function was passed a pubkey that was', len(pubkey),'bytes long rather than 65.'
        return "error"
    ripe = hashlib.new('ripemd160')
    sha = hashlib.new('sha256')
    sha.update(pubkey)
    ripe.update(sha.digest())
    ripeWithProdnetPrefix = '\x6F' + ripe.digest()

    checksum = hashlib.sha256(hashlib.sha256(ripeWithProdnetPrefix).digest()).digest()[:4]
    binaryBitcoinAddress = ripeWithProdnetPrefix + checksum
    numberOfZeroBytesOnBinaryBitcoinAddress = 0
    while binaryBitcoinAddress[0] == '\x00':
        numberOfZeroBytesOnBinaryBitcoinAddress += 1
        binaryBitcoinAddress = binaryBitcoinAddress[1:]
    base58encoded = arithmetic.changebase(binaryBitcoinAddress,256,58)
    return "1"*numberOfZeroBytesOnBinaryBitcoinAddress + base58encoded

def safeConfigGetBoolean(section,field):
        try:
            if config.getboolean(section,field):
                return True
            else:
                return False
        except:
            return False

def lookupAppdataFolder():
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
    return appdata

def isAddressInMyAddressBook(address):
    t = (address,)
    sqlLock.acquire()
    sqlSubmitQueue.put('''select address from addressbook where address=?''')
    sqlSubmitQueue.put(t)
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()
    return queryreturn != []

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
            #Explanation of what is in the pubkeys table:
            #   The hash is the RIPEMD160 hash that is encoded in the Bitmessage address.
            #   If you or someone else did the POW for this pubkey, then havecorrectnonce will be true. If you received the pubkey in a msg message then havecorrectnonce will be false. You won't have the correct nonce and won't be able to send the message to peers if they request the pubkey.
            #   transmitdata is literally the data that was included in the Bitmessage pubkey message when it arrived, except for the 24 byte protocol header- ie, it starts with the POW nonce.
            #   time is the time that the pubkey was broadcast on the network same as with every other type of Bitmessage object.
            #   usedpersonally is set to "yes" if we have used the key personally. This keeps us from deleting it because we may want to reply to a message in the future. This field is not a bool because we may need more flexability in the future and it doesn't take up much more space anyway.
            self.cur.execute( '''CREATE TABLE pubkeys (hash blob, havecorrectnonce bool, transmitdata blob, time blob, usedpersonally text, UNIQUE(hash, havecorrectnonce) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''CREATE TABLE inventory (hash blob, objecttype text, streamnumber int, payload blob, receivedtime integer, UNIQUE(hash) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''CREATE TABLE knownnodes (timelastseen int, stream int, services blob, host blob, port blob, UNIQUE(host, stream, port) ON CONFLICT REPLACE)''' ) #This table isn't used in the program yet but I have a feeling that we'll need it.
            self.cur.execute( '''INSERT INTO subscriptions VALUES('Bitmessage new releases/announcements','BM-BbkPSZbzPwpVcYZpU4yHwf9ZPEapN5Zx',1)''')
            self.conn.commit()
            print 'Created messages database file'
        except Exception, err:
            if str(err) == 'table inbox already exists':
                print 'Database file already exists.'
            else:
                sys.stderr.write('ERROR trying to create database file (message.dat). Error message: %s\n' % str(err))
                sys.exit()

        #People running earlier versions of PyBitmessage do not have the usedpersonally field in their pubkeys table. Let's add it.
        if config.getint('bitmessagesettings','settingsversion') == 2:
            item = '''ALTER TABLE pubkeys ADD usedpersonally text DEFAULT 'no' '''
            parameters = ''
            self.cur.execute(item, parameters)
            self.conn.commit()

            config.set('bitmessagesettings','settingsversion','3')
            with open(appdata + 'keys.dat', 'wb') as configfile:
                config.write(configfile)

        try:
            testpayload = '\x00\x00'
            t = ('1234','True',testpayload,'12345678','no')
            self.cur.execute( '''INSERT INTO pubkeys VALUES(?,?,?,?,?)''',t)
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
    pubkeys (clears pubkeys older than 4 weeks old which we have not used personally)

It resends messages when there has been no response:
    resends getpubkey messages in 4 days (then 8 days, then 16 days, etc...)
    resends msg messages in 4 days (then 8 days, then 16 days, etc...)

'''
class singleCleaner(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        timeWeLastClearedInventoryAndPubkeysTables = 0

        while True:
            time.sleep(300)
            sqlLock.acquire()
            self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"Doing housekeeping (Flushing inventory in memory to disk...)")
            for hash, storedValue in inventory.items():
                objectType, streamNumber, payload, receivedTime = storedValue
                if int(time.time())- 600 > receivedTime:
                    t = (hash,objectType,streamNumber,payload,receivedTime)
                    sqlSubmitQueue.put('''INSERT INTO inventory VALUES (?,?,?,?,?)''')
                    sqlSubmitQueue.put(t)
                    sqlReturnQueue.get()
                    del inventory[hash]
            self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"")
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

                #pubkeys
                t = (int(time.time())-lengthOfTimeToHoldOnToAllPubkeys,)
                sqlSubmitQueue.put('''DELETE FROM pubkeys WHERE time<? AND usedpersonally='no' ''')
                sqlSubmitQueue.put(t)
                sqlReturnQueue.get()

                t = ()
                sqlSubmitQueue.put('''select toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, pubkeyretrynumber, msgretrynumber FROM sent WHERE ((status='findingpubkey' OR status='sentmessage') AND folder='sent') ''') #If the message's folder='trash' then we'll ignore it.
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                for row in queryreturn:
                    toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, pubkeyretrynumber, msgretrynumber = row
                    if status == 'findingpubkey':
                        if int(time.time()) - lastactiontime > (maximumAgeOfAnObjectThatIAmWillingToAccept * (2 ** (pubkeyretrynumber))):
                            print 'It has been a long time and we haven\'t heard a response to our getpubkey request. Sending again.'
                            try:
                                del neededPubkeys[toripe] #We need to take this entry out of the neededPubkeys structure because the workerQueue checks to see whether the entry is already present and will not do the POW and send the message because it assumes that it has already done it recently.
                            except:
                                pass
                            workerQueue.put(('sendmessage',toaddress))
                            self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"Doing work necessary to again attempt to request a public key...")
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
                            self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"Doing work necessary to again attempt to deliver a message...")
                sqlLock.release()
            

#This thread, of which there is only one, does the heavy lifting: calculating POWs.
class singleWorker(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        sqlLock.acquire()
        sqlSubmitQueue.put('''SELECT toripe FROM sent WHERE (status=? AND folder='sent')''')
        sqlSubmitQueue.put(('findingpubkey',))
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        for row in queryreturn:
            toripe, = row
            #It is possible for the status of a message in our sent folder (which is also our 'outbox' folder) to have a status of 'findingpubkey' even if we have the pubkey.  This can
            #happen if the worker thread is working on the POW for an earlier message and does not get to the message in question before the user closes Bitmessage. In this case, the
            #status will still be 'findingpubkey' but Bitmessage will never have checked to see whether it actually already has the pubkey. We should therefore check here.
            sqlLock.acquire()
            sqlSubmitQueue.put('''SELECT hash FROM pubkeys WHERE hash=? ''')
            sqlSubmitQueue.put((toripe,))
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()
            if queryreturn != '': #If we have the pubkey then send the message otherwise put the hash in the neededPubkeys data structure so that we will pay attention to it if it comes over the wire.
                self.sendMsg(toripe)
            else:
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
            #Evidentially there is a remote possibility that we may, for some reason, no longer have the recipient's pubkey. Let us make sure we still have it or else the sendMsg function will appear to freeze.
            sqlLock.acquire()
            sqlSubmitQueue.put('''SELECT hash FROM pubkeys WHERE hash=? ''')
            sqlSubmitQueue.put((toripe,))
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()
            if queryreturn != []:
                #We have the needed pubkey
                self.sendMsg(toripe)
            else:
                printLock.acquire()
                sys.stderr.write('For some reason, the status of a message in our outbox is \'doingpow\' even though we lack the pubkey. Here is the RIPE hash of the needed pubkey: %s\n' % toripe.encode('hex'))
                printLock.release()

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
                        print 'requesting pubkey:', toRipe.encode('hex')
                        self.requestPubKey(toAddressVersionNumber,toStreamNumber,toRipe)
                    else:
                        print 'We have already requested this pubkey (the ripe hash is in neededPubkeys). We will re-request again soon.'
                        self.emit(SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"),toRipe,'Public key was requested earlier. Receiver must be offline. Will retry.')
                else:
                    print 'We already have the necessary public key.'
                    self.sendMsg(toRipe) #by calling this function, we are asserting that we already have the pubkey for toRipe
            elif command == 'sendbroadcast':
                print 'Within WorkerThread, processing sendbroadcast command.'
                fromAddress,subject,message = data
                self.sendBroadcast()
            elif command == 'doPOWForMyV2Pubkey':
                self.doPOWForMyV2Pubkey(data)
            elif command == 'newpubkey':
                toAddressVersion,toStreamNumber,toRipe = data
                if toRipe in neededPubkeys:
                    print 'We have been awaiting the arrival of this pubkey.'
                    del neededPubkeys[toRipe]
                    self.sendMsg(toRipe)
                else:
                    printLock.acquire()
                    print 'We don\'t need this pub key. We didn\'t ask for it. Pubkey hash:', toRipe.encode('hex')
                    printLock.release()
            else:
                printLock.acquire()
                sys.stderr.write('Probable programming error: The command sent to the workerThread is weird. It is: %s\n' % command)
                printLock.release()

            workerQueue.task_done()

    def doPOWForMyV2Pubkey(self,hash): #This function also broadcasts out the pubkey message once it is done with the POW
        #Look up my stream number based on my address hash
        configSections = config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile <> 'bitmessagesettings':
                status,addressVersionNumber,streamNumber,hashFromThisParticularAddress = decodeAddress(addressInKeysFile)
                if hash == hashFromThisParticularAddress:
                    myAddress = addressInKeysFile
                    break

        embeddedTime = int(time.time())+random.randrange(-300, 300) #the current time plus or minus five minutes
        payload = pack('>I',(embeddedTime))
        payload += encodeVarint(addressVersionNumber) #Address version number
        payload += encodeVarint(streamNumber)
        payload += '\x00\x00\x00\x01' #bitfield of features supported by me (see the wiki).

        try:
            privSigningKeyBase58 = config.get(myAddress, 'privsigningkey')
            privEncryptionKeyBase58 = config.get(myAddress, 'privencryptionkey')
        except Exception, err:
            printLock.acquire()
            sys.stderr.write('Error within doPOWForMyV2Pubkey. Could not read the keys from the keys.dat file for a requested address. %s\n' % err)
            printLock.release()
            return

        privSigningKeyHex = decodeWalletImportFormat(privSigningKeyBase58).encode('hex')
        privEncryptionKeyHex = decodeWalletImportFormat(privEncryptionKeyBase58).encode('hex')
        pubSigningKey = highlevelcrypto.privToPub(privSigningKeyHex).decode('hex')
        pubEncryptionKey = highlevelcrypto.privToPub(privEncryptionKeyHex).decode('hex')

        payload += pubSigningKey[1:]
        payload += pubEncryptionKey[1:]

        #Do the POW for this pubkey message
        nonce = 0
        trialValue = 99999999999999999999
        target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
        print '(For pubkey message) Doing proof of work...'
        initialHash = hashlib.sha512(payload).digest()
        while trialValue > target:
            nonce += 1
            trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
        print '(For pubkey message) Found proof of work', trialValue, 'Nonce:', nonce

        payload = pack('>Q',nonce) + payload
        t = (hash,True,payload,embeddedTime,'no')
        sqlLock.acquire()
        sqlSubmitQueue.put('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()

        inventoryHash = calculateInventoryHash(payload)
        objectType = 'pubkey'
        inventory[inventoryHash] = (objectType, streamNumber, payload, embeddedTime)

        printLock.acquire()
        print 'broadcasting inv with hash:', inventoryHash.encode('hex')
        printLock.release()
        broadcastToSendDataQueues((streamNumber, 'sendinv', inventoryHash))
        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),"")

    def sendBroadcast(self):
        sqlLock.acquire()
        t = ('broadcastpending',)
        sqlSubmitQueue.put('SELECT fromaddress, subject, message, ackdata FROM sent WHERE status=?')
        sqlSubmitQueue.put(t)
        queryreturn = sqlReturnQueue.get()
        sqlLock.release()
        for row in queryreturn:
            fromaddress, subject, body, ackdata = row
            status,addressVersionNumber,streamNumber,ripe = decodeAddress(fromaddress)
            if addressVersionNumber == 2:
                #We need to convert our private keys to public keys in order to include them.
                try:
                    privSigningKeyBase58 = config.get(fromaddress, 'privsigningkey')
                    privEncryptionKeyBase58 = config.get(fromaddress, 'privencryptionkey')
                except:
                    self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Error! Could not find sender address (your address) in the keys.dat file.')
                    continue

                privSigningKeyHex = decodeWalletImportFormat(privSigningKeyBase58).encode('hex')
                privEncryptionKeyHex = decodeWalletImportFormat(privEncryptionKeyBase58).encode('hex')

                pubSigningKey = highlevelcrypto.privToPub(privSigningKeyHex).decode('hex') #At this time these pubkeys are 65 bytes long because they include the encoding byte which we won't be sending in the broadcast message.
                pubEncryptionKey = highlevelcrypto.privToPub(privEncryptionKeyHex).decode('hex')

                payload = pack('>I',(int(time.time())+random.randrange(-300, 300)))#the current time plus or minus five minutes
                payload += encodeVarint(1) #broadcast version
                payload += encodeVarint(addressVersionNumber)
                payload += encodeVarint(streamNumber)
                payload += '\x00\x00\x00\x01' #behavior bitfield
                payload += pubSigningKey[1:]
                payload += pubEncryptionKey[1:]
                payload += ripe
                payload += '\x02' #message encoding type
                payload += encodeVarint(len('Subject:' + subject + '\n' + 'Body:' + body))  #Type 2 is simple UTF-8 message encoding.
                payload += 'Subject:' + subject + '\n' + 'Body:' + body

                signature = highlevelcrypto.sign(payload,privSigningKeyHex)
                payload += encodeVarint(len(signature))
                payload += signature

                nonce = 0
                trialValue = 99999999999999999999
                target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
                print '(For broadcast message) Doing proof of work...'
                self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Doing work necessary to send broadcast...')
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
                broadcastToSendDataQueues((streamNumber, 'sendinv', inventoryHash))

                self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Broadcast sent at '+strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))

                #Update the status of the message in the 'sent' table to have a 'broadcastsent' status
                sqlLock.acquire()
                t = ('broadcastsent',int(time.time()),fromaddress, subject, body,'broadcastpending')
                sqlSubmitQueue.put('UPDATE sent SET status=?, lastactiontime=? WHERE fromaddress=? AND subject=? AND message=? AND status=?')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()

                """elif addressVersionNumber == 1: #This whole section can be taken out soon because we aren't supporting v1 addresses for much longer.
                messageToTransmit = '\x02' #message encoding type
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
                #myPubkey = rsa.PublicKey(n,e)
                myPrivatekey = rsa.PrivateKey(n,e,d,p,q)

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
                #print 'signature', signature.encode('hex')
                payload += signature

                #print 'nString', repr(nString)
                #print 'eString', repr(eString)

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
                broadcastToSendDataQueues((streamNumber, 'sendinv', inventoryHash))

                self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Broadcast sent at '+strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))

                #Update the status of the message in the 'sent' table to have a 'broadcastsent' status
                sqlLock.acquire()
                t = ('broadcastsent',int(time.time()),fromaddress, subject, body,'broadcastpending')
                sqlSubmitQueue.put('UPDATE sent SET status=?, lastactiontime=? WHERE fromaddress=? AND subject=? AND message=? AND status=?')
                sqlSubmitQueue.put(t)
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()"""
            else:
                printLock.acquire()
                print 'In the singleWorker thread, the sendBroadcast function doesn\'t understand the address version'
                printLock.release()

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
            toStatus,toAddressVersionNumber,toStreamNumber,toHash = decodeAddress(toaddress)
            fromStatus,fromAddressVersionNumber,fromStreamNumber,fromHash = decodeAddress(fromaddress)
            self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Doing work necessary to send the message.')
            printLock.acquire()
            print 'Found a message in our database that needs to be sent with this pubkey.'
            print 'First 150 characters of message:', message[:150]
            printLock.release()
            embeddedTime = pack('>I',(int(time.time())+random.randrange(-300, 300)))#the current time plus or minus five minutes. We will use this time both for our message and for the ackdata packed within our message.
            if fromAddressVersionNumber == 2:
                payload = '\x01' #Message version.
                payload += encodeVarint(fromAddressVersionNumber)
                payload += encodeVarint(fromStreamNumber)
                payload += '\x00\x00\x00\x01' #Bitfield of features and behaviors that can be expected from me. (See https://bitmessage.org/wiki/Protocol_specification#Pubkey_bitfield_features  )

                #We need to convert our private keys to public keys in order to include them.
                try:
                    privSigningKeyBase58 = config.get(fromaddress, 'privsigningkey')
                    privEncryptionKeyBase58 = config.get(fromaddress, 'privencryptionkey')
                except:
                    self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Error! Could not find sender address (your address) in the keys.dat file.')
                    continue

                privSigningKeyHex = decodeWalletImportFormat(privSigningKeyBase58).encode('hex')
                privEncryptionKeyHex = decodeWalletImportFormat(privEncryptionKeyBase58).encode('hex')

                pubSigningKey = highlevelcrypto.privToPub(privSigningKeyHex).decode('hex')
                pubEncryptionKey = highlevelcrypto.privToPub(privEncryptionKeyHex).decode('hex')

                payload += pubSigningKey[1:] #The \x04 on the beginning of the public keys are not sent. This way there is only one acceptable way to encode and send a public key.
                payload += pubEncryptionKey[1:]

                payload += toHash #This hash will be checked by the receiver of the message to verify that toHash belongs to them. This prevents a Surreptitious Forwarding Attack.
                payload += '\x02' #Type 2 is simple UTF-8 message encoding as specified on the Protocol Specification on the Bitmessage Wiki.
                messageToTransmit = 'Subject:' + subject + '\n' + 'Body:' + message
                payload += encodeVarint(len(messageToTransmit))
                payload += messageToTransmit
                fullAckPayload = self.generateFullAckMessage(ackdata,toStreamNumber,embeddedTime)#The fullAckPayload is a normal msg protocol message with the proof of work already completed that the receiver of this message can easily send out.
                payload += encodeVarint(len(fullAckPayload))
                payload += fullAckPayload
                signature = highlevelcrypto.sign(payload,privSigningKeyHex)
                payload += encodeVarint(len(signature))
                payload += signature

            """elif fromAddressVersionNumber == 1: #This code is for old version 1 (RSA) addresses. It will soon be removed.
                payload = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' #this run of nulls allows the true message receiver to identify his message
                payload += '\x01' #Message version.
                payload += '\x00\x00\x00\x01'

                payload += encodeVarint(fromAddressVersionNumber)
                payload += encodeVarint(fromStreamNumber)

                try:
                    sendersN = convertIntToString(config.getint(fromaddress, 'n'))
                except:
                    printLock.acquire()
                    print 'Error: Could not find', fromaddress, 'in our keys.dat file. You must have deleted it. Aborting the send.'
                    printLock.release()
                    return
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
                fullAckPayload = self.generateFullAckMessage(ackdata,toStreamNumber,embeddedTime)
                payload += encodeVarint(len(fullAckPayload))
                payload += fullAckPayload
                sendersPrivKey = rsa.PrivateKey(config.getint(fromaddress, 'n'),config.getint(fromaddress, 'e'),config.getint(fromaddress, 'd'),config.getint(fromaddress, 'p'),config.getint(fromaddress, 'q'))

                payload += rsa.sign(payload,sendersPrivKey,'SHA-512')"""

            #We have assembled the data that will be encrypted. Now let us fetch the recipient's public key out of our database and do the encryption.

            if toAddressVersionNumber == 2:
                sqlLock.acquire()
                sqlSubmitQueue.put('SELECT transmitdata FROM pubkeys WHERE hash=?')
                sqlSubmitQueue.put((toRipe,))
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()

                for row in queryreturn:
                    pubkeyPayload, = row

                #The pubkey is stored the way we originally received it which means that we need to read beyond things like the nonce and time to get to the public keys.
                readPosition = 8 #to bypass the nonce
                readPosition += 4 #to bypass the embedded time
                readPosition += 1 #to bypass the address version whose length is definitely 1
                streamNumber, streamNumberLength = decodeVarint(pubkeyPayload[readPosition:readPosition+10])
                readPosition += streamNumberLength
                behaviorBitfield = pubkeyPayload[readPosition:readPosition+4]
                readPosition += 4 #to bypass the bitfield of behaviors
                #pubSigningKeyBase256 = pubkeyPayload[readPosition:readPosition+64] #We don't use this key for anything here.
                readPosition += 64
                pubEncryptionKeyBase256 = pubkeyPayload[readPosition:readPosition+64]
                readPosition += 64
                encrypted = highlevelcrypto.encrypt(payload,"04"+pubEncryptionKeyBase256.encode('hex'))

            """elif toAddressVersionNumber == 1:
                sqlLock.acquire()
                sqlSubmitQueue.put('SELECT transmitdata FROM pubkeys WHERE hash=?')
                sqlSubmitQueue.put((toRipe,))
                queryreturn = sqlReturnQueue.get()
                sqlLock.release()

                for row in queryreturn:
                    pubkeyPayload, = row

                readPosition = 8 #to bypass the nonce
                behaviorBitfield = pubkeyPayload[8:12]
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
                outfile.close()"""

            nonce = 0
            trialValue = 99999999999999999999

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
            try:
                print 'POW took', int(time.time()-powStartTime), 'seconds.', nonce/(time.time()-powStartTime), 'nonce trials per second.'
            except:
                pass
            payload = pack('>Q',nonce) + payload

            inventoryHash = calculateInventoryHash(payload)
            objectType = 'msg'
            inventory[inventoryHash] = (objectType, toStreamNumber, payload, int(time.time()))
            self.emit(SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"),ackdata,'Message sent. Waiting on acknowledgement. Sent on ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
            print 'sending inv (within sendmsg function)'
            broadcastToSendDataQueues((streamNumber, 'sendinv', inventoryHash))

            #Update the status of the message in the 'sent' table to have a 'sent' status
            sqlLock.acquire()
            t = ('sentmessage',toaddress, fromaddress, subject, message,'doingpow')
            sqlSubmitQueue.put('UPDATE sent SET status=? WHERE toaddress=? AND fromaddress=? AND subject=? AND message=? AND status=?')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()

            t = (toRipe,)
            sqlSubmitQueue.put('''UPDATE pubkeys SET usedpersonally='yes' WHERE hash=?''')
            sqlSubmitQueue.put(t)
            queryreturn = sqlReturnQueue.get()

            sqlLock.release()


    def requestPubKey(self,addressVersionNumber,streamNumber,ripe):
        payload = pack('>I',int(time.time()))
        payload += encodeVarint(addressVersionNumber)
        payload += encodeVarint(streamNumber)
        payload += ripe
        printLock.acquire()
        print 'making request for pubkey with ripe:', ripe.encode('hex')
        printLock.release()
        nonce = 0
        trialValue = 99999999999999999999
        #print 'trial value', trialValue
        statusbar = 'Doing the computations necessary to request the recipient\'s public key.'
        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
        self.emit(SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"),ripe,'Doing work necessary to request public key.')
        print 'Doing proof-of-work necessary to send getpubkey message.'
        target = 2**64 / ((len(payload)+payloadLengthExtraBytes+8) * averageProofOfWorkNonceTrialsPerByte)
        initialHash = hashlib.sha512(payload).digest()
        while trialValue > target:
            nonce += 1
            trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
        printLock.acquire()
        print 'Found proof of work', trialValue, 'Nonce:', nonce
        printLock.release()

        payload = pack('>Q',nonce) + payload
        inventoryHash = calculateInventoryHash(payload)
        objectType = 'getpubkey'
        inventory[inventoryHash] = (objectType, streamNumber, payload, int(time.time()))
        print 'sending inv (for the getpubkey message)'
        broadcastToSendDataQueues((streamNumber, 'sendinv', inventoryHash))

        self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Broacasting the public key request. This program will auto-retry if they are offline.')
        self.emit(SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"),ripe,'Sending public key request. Waiting for reply. Requested at ' + strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))

    def generateFullAckMessage(self,ackdata,toStreamNumber,embeddedTime):
        nonce = 0
        trialValue = 99999999999999999999
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
        try:
            print 'POW took', int(time.time()-powStartTime), 'seconds.', nonce/(time.time()-powStartTime), 'nonce trials per second.'
        except:
            pass
        printLock.release()
        payload = pack('>Q',nonce) + payload
        headerData = '\xe9\xbe\xb4\xd9' #magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        headerData += pack('>L',len(payload))
        headerData += hashlib.sha512(payload).digest()[:4]
        return headerData + payload

class addressGenerator(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def setup(self,addressVersionNumber,streamNumber,label="(no label)",numberOfAddressesToMake=1,deterministicPassphrase="",eighteenByteRipe=False):
        self.addressVersionNumber = addressVersionNumber
        self.streamNumber = streamNumber
        self.label = label
        self.numberOfAddressesToMake = numberOfAddressesToMake
        self.deterministicPassphrase = deterministicPassphrase
        self.eighteenByteRipe = eighteenByteRipe

    def run(self):
        if self.addressVersionNumber == 2:

            if self.deterministicPassphrase == "":
                statusbar = 'Generating one new address'
                self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
                #This next section is a little bit strange. We're going to generate keys over and over until we
                #find one that starts with either \x00 or \x00\x00. Then when we pack them into a Bitmessage address,
                #we won't store the \x00 or \x00\x00 bytes thus making the address shorter.
                startTime = time.time()
                numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix = 0
                potentialPrivSigningKey = OpenSSL.rand(32)
                potentialPubSigningKey = self.pointMult(potentialPrivSigningKey)
                while True:
                    numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix += 1
                    potentialPrivEncryptionKey = OpenSSL.rand(32)
                    potentialPubEncryptionKey = self.pointMult(potentialPrivEncryptionKey)
                    #print 'potentialPubSigningKey', potentialPubSigningKey.encode('hex')
                    #print 'potentialPubEncryptionKey', potentialPubEncryptionKey.encode('hex')
                    ripe = hashlib.new('ripemd160')
                    sha = hashlib.new('sha512')
                    sha.update(potentialPubSigningKey+potentialPubEncryptionKey)
                    ripe.update(sha.digest())
                    #print 'potential ripe.digest', ripe.digest().encode('hex')
                    if self.eighteenByteRipe:
                        if ripe.digest()[:2] == '\x00\x00':
                            break
                    else:
                        if ripe.digest()[:1] == '\x00':
                            break
                print 'Generated address with ripe digest:', ripe.digest().encode('hex')
                print 'Address generator calculated', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix, 'addresses at', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix/(time.time()-startTime),'addresses per second before finding one with the correct ripe-prefix.'
                if ripe.digest()[:2] == '\x00\x00':
                    address = encodeAddress(2,self.streamNumber,ripe.digest()[2:])
                elif ripe.digest()[:1] == '\x00':
                    address = encodeAddress(2,self.streamNumber,ripe.digest()[1:])
                #self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Finished generating address. Writing to keys.dat')

                #An excellent way for us to store our keys is in Wallet Import Format. Let us convert now.
                #https://en.bitcoin.it/wiki/Wallet_import_format
                privSigningKey = '\x80'+potentialPrivSigningKey
                checksum = hashlib.sha256(hashlib.sha256(privSigningKey).digest()).digest()[0:4]
                privSigningKeyWIF = arithmetic.changebase(privSigningKey + checksum,256,58)
                #print 'privSigningKeyWIF',privSigningKeyWIF

                privEncryptionKey = '\x80'+potentialPrivEncryptionKey
                checksum = hashlib.sha256(hashlib.sha256(privEncryptionKey).digest()).digest()[0:4]
                privEncryptionKeyWIF = arithmetic.changebase(privEncryptionKey + checksum,256,58)
                #print 'privEncryptionKeyWIF',privEncryptionKeyWIF

                config.add_section(address)
                config.set(address,'label',self.label)
                config.set(address,'enabled','true')
                config.set(address,'decoy','false')
                config.set(address,'privSigningKey',privSigningKeyWIF)
                config.set(address,'privEncryptionKey',privEncryptionKeyWIF)
                with open(appdata + 'keys.dat', 'wb') as configfile:
                    config.write(configfile)
                
                #It may be the case that this address is being generated as a result of a call to the API. Let us put the result in the necessary queue. 
                apiAddressGeneratorReturnQueue.put(address)

                self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Done generating address. Doing work necessary to broadcast it...')
                self.emit(SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),self.label,address,str(self.streamNumber))
                reloadMyAddressHashes()
                workerQueue.put(('doPOWForMyV2Pubkey',ripe.digest()))

            else: #There is something in the deterministicPassphrase variable thus we are going to do this deterministically.
                statusbar = 'Generating '+str(self.numberOfAddressesToMake) + ' new addresses.'
                self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),statusbar)
                signingKeyNonce = 0
                encryptionKeyNonce = 1
                listOfNewAddressesToSendOutThroughTheAPI = [] #We fill out this list no matter what although we only need it if we end up passing the info to the API.

                for i in range(self.numberOfAddressesToMake):
                    #This next section is a little bit strange. We're going to generate keys over and over until we
                    #find one that has a RIPEMD hash that starts with either \x00 or \x00\x00. Then when we pack them
                    #into a Bitmessage address, we won't store the \x00 or \x00\x00 bytes thus making the address shorter.
                    startTime = time.time()
                    numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix = 0
                    while True:
                        numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix += 1
                        potentialPrivSigningKey = hashlib.sha512(self.deterministicPassphrase + encodeVarint(signingKeyNonce)).digest()[:32]
                        potentialPrivEncryptionKey = hashlib.sha512(self.deterministicPassphrase + encodeVarint(encryptionKeyNonce)).digest()[:32]
                        potentialPubSigningKey = self.pointMult(potentialPrivSigningKey)
                        potentialPubEncryptionKey = self.pointMult(potentialPrivEncryptionKey)
                        #print 'potentialPubSigningKey', potentialPubSigningKey.encode('hex')
                        #print 'potentialPubEncryptionKey', potentialPubEncryptionKey.encode('hex')
                        signingKeyNonce += 2
                        encryptionKeyNonce += 2
                        ripe = hashlib.new('ripemd160')
                        sha = hashlib.new('sha512')
                        sha.update(potentialPubSigningKey+potentialPubEncryptionKey)
                        ripe.update(sha.digest())
                        #print 'potential ripe.digest', ripe.digest().encode('hex')
                        if self.eighteenByteRipe:
                            if ripe.digest()[:2] == '\x00\x00':
                                break
                        else:
                            if ripe.digest()[:1] == '\x00':
                                break

                    print 'ripe.digest', ripe.digest().encode('hex')
                    print 'Address generator calculated', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix, 'addresses at', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix/(time.time()-startTime),'keys per second.'
                    if ripe.digest()[:2] == '\x00\x00':
                        address = encodeAddress(2,self.streamNumber,ripe.digest()[2:])
                    elif ripe.digest()[:1] == '\x00':
                        address = encodeAddress(2,self.streamNumber,ripe.digest()[1:])
                    #self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Finished generating address. Writing to keys.dat')

                    #An excellent way for us to store our keys is in Wallet Import Format. Let us convert now.
                    #https://en.bitcoin.it/wiki/Wallet_import_format
                    privSigningKey = '\x80'+potentialPrivSigningKey
                    checksum = hashlib.sha256(hashlib.sha256(privSigningKey).digest()).digest()[0:4]
                    privSigningKeyWIF = arithmetic.changebase(privSigningKey + checksum,256,58)

                    privEncryptionKey = '\x80'+potentialPrivEncryptionKey
                    checksum = hashlib.sha256(hashlib.sha256(privEncryptionKey).digest()).digest()[0:4]
                    privEncryptionKeyWIF = arithmetic.changebase(privEncryptionKey + checksum,256,58)

                    try:
                        config.add_section(address)
                        print 'self.label', self.label
                        config.set(address,'label',self.label)
                        config.set(address,'enabled','true')
                        config.set(address,'decoy','false')
                        config.set(address,'privSigningKey',privSigningKeyWIF)
                        config.set(address,'privEncryptionKey',privEncryptionKeyWIF)
                        with open(appdata + 'keys.dat', 'wb') as configfile:
                            config.write(configfile)

                        self.emit(SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),self.label,address,str(self.streamNumber))
                        listOfNewAddressesToSendOutThroughTheAPI.append(address)
                    except:
                        print address,'already exists. Not adding it again.'
                #It may be the case that this address is being generated as a result of a call to the API. Let us put the result in the necessary queue. 
                apiAddressGeneratorReturnQueue.put(listOfNewAddressesToSendOutThroughTheAPI)
                self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),'Done generating address')
                reloadMyAddressHashes()

        #This code which deals with old RSA addresses will soon be removed.
        """elif self.addressVersionNumber == 1:
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
            reloadMyAddressHashes()"""

    #Does an EC point multiplication; turns a private key into a public key.
    def pointMult(self,secret):
        #ctx = OpenSSL.BN_CTX_new() #This value proved to cause Seg Faults on Linux. It turns out that it really didn't speed up EC_POINT_mul anyway.
        k = OpenSSL.EC_KEY_new_by_curve_name(OpenSSL.get_curve('secp256k1'))
        priv_key = OpenSSL.BN_bin2bn(secret, 32, 0)
        group = OpenSSL.EC_KEY_get0_group(k)
        pub_key = OpenSSL.EC_POINT_new(group)

        OpenSSL.EC_POINT_mul(group, pub_key, priv_key, None, None, None)
        OpenSSL.EC_KEY_set_private_key(k, priv_key)
        OpenSSL.EC_KEY_set_public_key(k, pub_key)
        #print 'priv_key',priv_key
        #print 'pub_key',pub_key

        size = OpenSSL.i2o_ECPublicKey(k, 0)
        mb = ctypes.create_string_buffer(size)
        OpenSSL.i2o_ECPublicKey(k, ctypes.byref(ctypes.pointer(mb)))
        #print 'mb.raw', mb.raw.encode('hex'), 'length:', len(mb.raw)
        #print 'mb.raw', mb.raw, 'length:', len(mb.raw)

        OpenSSL.EC_POINT_free(pub_key)
        #OpenSSL.BN_CTX_free(ctx)
        OpenSSL.BN_free(priv_key)
        OpenSSL.EC_KEY_free(k)
        return mb.raw

#This is one of several classes that constitute the API
#This class was written by Vaibhav Bhatia. Modified by Jonathan Warren (Atheros).
#http://code.activestate.com/recipes/501148-xmlrpc-serverclient-which-does-cookie-handling-and/
class MySimpleXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    def do_POST(self):
        #Handles the HTTP POST request.
        #Attempts to interpret all HTTP POST requests as XML-RPC calls,
        #which are forwarded to the server's _dispatch method for handling.

        #Note: this method is the same as in SimpleXMLRPCRequestHandler,
        #just hacked to handle cookies

        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))

            # HACK :start -> sends cookies here
            if self.cookies:
                for cookie in self.cookies:
                    self.send_header('Set-Cookie',cookie.output(header=''))
            # HACK :end

            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)


    def APIAuthenticateClient(self):
        if self.headers.has_key('Authorization'):
            # handle Basic authentication
            (enctype, encstr) =  self.headers.get('Authorization').split()
            (emailid, password) = encstr.decode('base64').split(':')
            if emailid == config.get('bitmessagesettings', 'apiusername') and password == config.get('bitmessagesettings', 'apipassword'):
                return True
            else:
                return False
        else:
            print 'Authentication failed because header lacks Authentication field'
            time.sleep(2)
            return False

        return False

    def _dispatch(self, method, params):
        self.cookies = []

        validuser = self.APIAuthenticateClient()
        if not validuser:
            time.sleep(2)
            return "RPC Username or password incorrect or HTTP header lacks authentication at all."
        # handle request
        if method == 'helloWorld':
            (a,b) = params
            return a+'-'+b
        elif method == 'add':
            (a,b) = params
            return a+b
        elif method == 'statusBar':
            message, = params
            apiSignalQueue.put(('updateStatusBar',message))
        elif method == 'listAddresses':
            data = '{"addresses":['
            configSections = config.sections()
            for addressInKeysFile in configSections:
                if addressInKeysFile <> 'bitmessagesettings':
                    status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
                    data
                    if len(data) > 20:
                        data += ','
                    data += json.dumps({'label':config.get(addressInKeysFile,'label'),'address':addressInKeysFile,'stream':streamNumber,'enabled':config.getboolean(addressInKeysFile,'enabled')},indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'createRandomAddress':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            elif len(params) == 1:
                label, = params
                eighteenByteRipe = False
            elif len(params) == 2:
                label, eighteenByteRipe = params
            label = label.decode('base64')
            apiAddressGeneratorReturnQueue.queue.clear()
            apiSignalQueue.put(('createRandomAddress',(label, eighteenByteRipe))) #params should be a twopul which equals (eighteenByteRipe, label)
            return apiAddressGeneratorReturnQueue.get()
        elif method == 'createDeterministicAddresses':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            elif len(params) == 1:
                passphrase, = params
                numberOfAddresses = 1
                addressVersionNumber = 0
                streamNumber = 0
                eighteenByteRipe = False
            elif len(params) == 2:
                passphrase, numberOfAddresses = params
                addressVersionNumber = 0
                streamNumber = 0
                eighteenByteRipe = False
            elif len(params) == 3:
                passphrase, numberOfAddresses, addressVersionNumber = params
                streamNumber = 0
                eighteenByteRipe = False
            elif len(params) == 4:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber = params
                eighteenByteRipe = False
            elif len(params) == 5:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe = params
            if len(passphrase) == 0:
                return 'API Error 0001: the specified passphrase is blank.'
            passphrase = passphrase.decode('base64')
            if addressVersionNumber == 0: #0 means "just use the proper addressVersionNumber"
                addressVersionNumber == 2
            if addressVersionNumber != 2:
                return 'API Error 0002: the address version number currently must be 2 (or 0 which means auto-select). Others aren\'t supported.'
            if streamNumber == 0: #0 means "just use the most available stream"
                streamNumber = 1
            if streamNumber != 1:
                return 'API Error 0003: the stream number must be 1 (or 0 which means auto-select). Others aren\'t supported.'
            if numberOfAddresses == 0:
                return 'API Error 0004: Why would you ask me to generate 0 addresses for you?'
            if numberOfAddresses > 9999:
                return 'API Error 0005: You have (accidentially?) specified too many addresses to make. Maximum 9999. This check only exists to prevent mischief; if you really want to create more addresses than this, contact the Bitmessage developers and we can modify the check or you can do it yourself by searching the source code for this message.'
            apiAddressGeneratorReturnQueue.queue.clear()
            print 'about to send numberOfAddresses', numberOfAddresses
            apiSignalQueue.put(('createDeterministicAddresses',(passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe)))
            data = '{"addresses":['
            queueReturn = apiAddressGeneratorReturnQueue.get()
            for item in queueReturn:
                if len(data) > 20:
                    data += ','
                data += "\""+item+ "\""
            data += ']}'
            return data
        elif method == 'getAllInboxMessages':
            sqlLock.acquire()
            sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message FROM inbox where folder='inbox' ORDER BY received''')
            sqlSubmitQueue.put('')
            queryreturn = sqlReturnQueue.get()
            sqlLock.release()
            data = '{"inboxMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, = row
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid':msgid.encode('hex'),'toAddress':toAddress,'fromAddress':fromAddress,'subject':subject.encode('base64'),'message':message.encode('base64'),'encodingType':2,'receivedTime':received},indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'trashMessage':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            t = (msgid,)
            sqlLock.acquire()
            sqlSubmitQueue.put('''UPDATE inbox SET folder='trash' WHERE msgid=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            apiSignalQueue.put(('updateStatusBar','Per API: Trashed message (assuming message existed). UI not updated.'))
            return 'Trashed message (assuming message existed). UI not updated. To double check, run getAllInboxMessages to see that the message disappeared, or restart Bitmessage and look in the normal Bitmessage GUI.'
        elif method == 'sendMessage':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            elif len(params) == 4:
                toAddress, fromAddress, subject, message = params
                encodingType = 2
            elif len(params) == 5:
                toAddress, fromAddress, subject, message, encodingType = params
            if encodingType != 2:
                return 'API Error 0006: The encoding type must be 2 because that is the only one this program currently supports.'
            subject = subject.decode('base64')
            message = message.decode('base64')
            status,addressVersionNumber,streamNumber,toRipe = decodeAddress(toAddress)
            if status <> 'success':
                printLock.acquire()
                print 'API Error 0007: Could not decode address:', toAddress, ':', status
                printLock.release()
                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + toAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: '+ toAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + toAddress
            if addressVersionNumber != 2:
                return 'API Error 0011: the address version number currently must be 2. Others aren\'t supported. Check the toAddress.'
            if streamNumber != 1:
                return 'API Error 0012: the stream number must be 1. Others aren\'t supported. Check the toAddress.'
            status,addressVersionNumber,streamNumber,fromRipe = decodeAddress(fromAddress)
            if status <> 'success':
                printLock.acquire()
                print 'API Error 0007: Could not decode address:', fromAddress, ':', status
                printLock.release()
                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + fromAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: '+ fromAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + fromAddress
            if addressVersionNumber != 2:
                return 'API Error 0011: the address version number currently must be 2. Others aren\'t supported. Check the fromAddress.'
            if streamNumber != 1:
                return 'API Error 0012: the stream number must be 1. Others aren\'t supported. Check the fromAddress.'
            toAddress = addBMIfNotPresent(toAddress)
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = config.getboolean(fromAddress,'enabled')
            except:
                return 'API Error 0013: could not find your fromAddress in the keys.dat file.'
            if not fromAddressEnabled:
                return 'API Error 0014: your fromAddress is disabled. Cannot send.'

            ackdata = OpenSSL.rand(32)
            sqlLock.acquire()
            t = ('',toAddress,toRipe,fromAddress,subject,message,ackdata,int(time.time()),'findingpubkey',1,1,'sent')
            sqlSubmitQueue.put('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            
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
            apiSignalQueue.put(('displayNewSentMessage',(toAddress,toLabel,fromAddress,subject,message,ackdata)))

            workerQueue.put(('sendmessage',toAddress))
            
            return ackdata.encode('hex')
        
        elif method == 'sendBroadcast':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            if len(params) == 3:
                fromAddress, subject, message = params
                encodingType = 2
            elif len(params) == 4:
                fromAddress, subject, message, encodingType = params
            if encodingType != 2:
                return 'API Error 0006: The encoding type must be 2 because that is the only one this program currently supports.'
            subject = subject.decode('base64')
            message = message.decode('base64')

            status,addressVersionNumber,streamNumber,fromRipe = decodeAddress(fromAddress)
            if status <> 'success':
                printLock.acquire()
                print 'API Error 0007: Could not decode address:', fromAddress, ':', status
                printLock.release()
                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + fromAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: '+ fromAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + fromAddress
            if addressVersionNumber != 2:
                return 'API Error 0011: the address version number currently must be 2. Others aren\'t supported. Check the fromAddress.'
            if streamNumber != 1:
                return 'API Error 0012: the stream number must be 1. Others aren\'t supported. Check the fromAddress.'
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = config.getboolean(fromAddress,'enabled')
            except:
                return 'API Error 0013: could not find your fromAddress in the keys.dat file.'
            ackdata = OpenSSL.rand(32)
            toAddress = '[Broadcast subscribers]'
            ripe = ''

            sqlLock.acquire()
            t = ('',toAddress,ripe,fromAddress,subject,message,ackdata,int(time.time()),'broadcastpending',1,1,'sent')
            sqlSubmitQueue.put('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()

            toLabel = '[Broadcast subscribers]'
            apiSignalQueue.put(('displayNewSentMessage',(toAddress,toLabel,fromAddress,subject,message,ackdata)))

            workerQueue.put(('sendbroadcast',(fromAddress,subject,message)))

            return ackdata.encode('hex')         

        else:
            return 'Invalid Method: %s'%method

#This thread, of which there is only one, runs the API.
class singleAPI(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        se = SimpleXMLRPCServer((config.get('bitmessagesettings', 'apiinterface'),config.getint('bitmessagesettings', 'apiport')), MySimpleXMLRPCRequestHandler, True, True)
        se.register_introspection_functions()
        se.serve_forever()

#The MySimpleXMLRPCRequestHandler class cannot emit signals (or at least I don't know how) because it is not a QT thread. It therefore puts data in a queue which this thread monitors and emits the signals on its behalf.
class singleAPISignalHandler(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

    def run(self):
        while True:
            command, data = apiSignalQueue.get()
            if command == 'updateStatusBar':
                self.emit(SIGNAL("updateStatusBar(PyQt_PyObject)"),data)
            elif command == 'createRandomAddress':
                label, eighteenByteRipe = data
                streamNumberForAddress = 1
                self.addressGenerator = addressGenerator()
                self.addressGenerator.setup(2,streamNumberForAddress,label,1,"",eighteenByteRipe)
                self.emit(SIGNAL("passAddressGeneratorObjectThrough(PyQt_PyObject)"),self.addressGenerator)
                self.addressGenerator.start()
            elif command == 'createDeterministicAddresses':
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe = data
                self.addressGenerator = addressGenerator()
                self.addressGenerator.setup(addressVersionNumber,streamNumber,'unused API address',numberOfAddresses,passphrase,eighteenByteRipe)
                self.emit(SIGNAL("passAddressGeneratorObjectThrough(PyQt_PyObject)"),self.addressGenerator)
                self.addressGenerator.start()
            elif command == 'displayNewSentMessage':
                toAddress,toLabel,fromAddress,subject,message,ackdata = data
                self.emit(SIGNAL("displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),toAddress,toLabel,fromAddress,subject,message,ackdata)

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

class regenerateAddressesDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_regenerateAddressesDialog()
        self.ui.setupUi(self)
        self.parent = parent
        QtGui.QWidget.resize(self,QtGui.QWidget.sizeHint(self))

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
        if appdata == '':
            self.ui.checkBoxPortableMode.setChecked(True)
        if 'darwin' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.checkBoxMinimizeToTray.setDisabled(True)
            self.ui.checkBoxShowTrayNotifications.setDisabled(True)
            self.ui.checkBoxStartInTray.setDisabled(True)
            self.ui.labelSettingsNote.setText('Options have been disabled because they either arn\'t applicable or because they haven\'t yet been implimented for your operating system.')
        elif 'linux' in sys.platform:
            self.ui.checkBoxStartOnLogon.setDisabled(True)
            self.ui.checkBoxMinimizeToTray.setDisabled(True)
            self.ui.checkBoxStartInTray.setDisabled(True)
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
        QtGui.QWidget.resize(self,QtGui.QWidget.sizeHint(self))

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

class SpecialAddressBehaviorDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SpecialAddressBehaviorDialog()
        self.ui.setupUi(self)
        self.parent = parent
        currentRow = parent.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = str(parent.ui.tableWidgetYourIdentities.item(currentRow,1).text())
        if safeConfigGetBoolean(addressAtCurrentRow,'mailinglist'):
            self.ui.radioButtonBehaviorMailingList.click()
        else:
            self.ui.radioButtonBehaveNormalAddress.click()
        try:
            mailingListName = config.get(addressAtCurrentRow, 'mailinglistname')
        except:
            mailingListName = ''
        self.ui.lineEditMailingListName.setText(unicode(mailingListName,'utf-8'))
        QtGui.QWidget.resize(self,QtGui.QWidget.sizeHint(self))

class NewSubscriptionDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_NewSubscriptionDialog()
        self.ui.setupUi(self)
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
        self.ui = Ui_NewAddressDialog()
        self.ui.setupUi(self)
        self.parent = parent
        row = 1
        #Let's fill out the 'existing address' combo box with addresses from the 'Your Identities' tab.
        while self.parent.ui.tableWidgetYourIdentities.item(row-1,1):
            self.ui.radioButtonExisting.click()
            #print self.parent.ui.tableWidgetYourIdentities.item(row-1,1).text()
            self.ui.comboBoxExisting.addItem(self.parent.ui.tableWidgetYourIdentities.item(row-1,1).text())
            row += 1
        self.ui.groupBoxDeterministic.setHidden(True)
        QtGui.QWidget.resize(self,QtGui.QWidget.sizeHint(self))


class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Ask the user if we may delete their old version 1 addresses if they have any.
        configSections = config.sections()
        for addressInKeysFile in configSections:
            if addressInKeysFile <> 'bitmessagesettings':
                status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
                if addressVersionNumber == 1:
                    displayMsg = "One of your addresses, "+addressInKeysFile+", is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?"
                    reply = QtGui.QMessageBox.question(self, 'Message',displayMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        config.remove_section(addressInKeysFile)
                        with open(appdata + 'keys.dat', 'wb') as configfile:
                            config.write(configfile)

        #Configure Bitmessage to start on startup (or remove the configuration) based on the setting in the keys.dat file
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
        QtCore.QObject.connect(self.ui.actionRegenerateDeterministicAddresses, QtCore.SIGNAL("triggered()"), self.click_actionRegenerateDeterministicAddresses)
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
        self.actionSpecialAddressBehavior = self.ui.addressContextMenuToolbar.addAction("Special address behavior...", self.on_action_SpecialAddressBehaviorDialog)
        self.ui.tableWidgetYourIdentities.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetYourIdentities, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuYourIdentities)
        self.popMenu = QtGui.QMenu( self )
        self.popMenu.addAction( self.actionNew )
        self.popMenu.addSeparator()
        self.popMenu.addAction( self.actionClipboard )
        self.popMenu.addSeparator()
        self.popMenu.addAction( self.actionEnable )
        self.popMenu.addAction( self.actionDisable )
        self.popMenu.addAction( self.actionSpecialAddressBehavior )

        #Popup menu for the Address Book page
        self.ui.addressBookContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionAddressBookSend = self.ui.addressBookContextMenuToolbar.addAction("Send message to this address", self.on_action_AddressBookSend)
        self.actionAddressBookClipboard = self.ui.addressBookContextMenuToolbar.addAction("Copy address to clipboard", self.on_action_AddressBookClipboard)
        self.actionAddressBookNew = self.ui.addressBookContextMenuToolbar.addAction("Add New Address", self.on_action_AddressBookNew)
        self.actionAddressBookDelete = self.ui.addressBookContextMenuToolbar.addAction("Delete", self.on_action_AddressBookDelete)
        self.ui.tableWidgetAddressBook.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetAddressBook, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuAddressBook)
        self.popMenuAddressBook = QtGui.QMenu( self )
        self.popMenuAddressBook.addAction( self.actionAddressBookSend )
        self.popMenuAddressBook.addAction( self.actionAddressBookClipboard )
        self.popMenuAddressBook.addSeparator()
        self.popMenuAddressBook.addAction( self.actionAddressBookNew )
        self.popMenuAddressBook.addAction( self.actionAddressBookDelete )

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

        #Popup menu for the Sent page
        self.ui.sentContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionTrashSentMessage = self.ui.sentContextMenuToolbar.addAction("Move to Trash", self.on_action_SentTrash)
        self.actionSentClipboard = self.ui.sentContextMenuToolbar.addAction("Copy destination address to clipboard", self.on_action_SentClipboard)
        self.ui.tableWidgetSent.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetSent, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuSent)
        self.popMenuSent = QtGui.QMenu( self )
        self.popMenuSent.addAction( self.actionSentClipboard )
        self.popMenuSent.addAction( self.actionTrashSentMessage )


        #Popup menu for the Blacklist page
        self.ui.blacklistContextMenuToolbar = QtGui.QToolBar()
          # Actions
        self.actionBlacklistNew = self.ui.blacklistContextMenuToolbar.addAction("Add new entry", self.on_action_BlacklistNew)
        self.actionBlacklistDelete = self.ui.blacklistContextMenuToolbar.addAction("Delete", self.on_action_BlacklistDelete)
        self.actionBlacklistClipboard = self.ui.blacklistContextMenuToolbar.addAction("Copy address to clipboard", self.on_action_BlacklistClipboard)
        self.actionBlacklistEnable = self.ui.blacklistContextMenuToolbar.addAction("Enable", self.on_action_BlacklistEnable)
        self.actionBlacklistDisable = self.ui.blacklistContextMenuToolbar.addAction("Disable", self.on_action_BlacklistDisable)
        self.ui.tableWidgetBlacklist.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.connect(self.ui.tableWidgetBlacklist, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.on_context_menuBlacklist)
        self.popMenuBlacklist = QtGui.QMenu( self )
        #self.popMenuBlacklist.addAction( self.actionBlacklistNew )
        self.popMenuBlacklist.addAction( self.actionBlacklistDelete )
        self.popMenuBlacklist.addSeparator()
        self.popMenuBlacklist.addAction( self.actionBlacklistClipboard )
        self.popMenuBlacklist.addSeparator()
        self.popMenuBlacklist.addAction( self.actionBlacklistEnable )
        self.popMenuBlacklist.addAction( self.actionBlacklistDisable )

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
                if safeConfigGetBoolean(addressInKeysFile,'mailinglist'):
                    newItem.setTextColor(QtGui.QColor(137,04,177))#magenta
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

        reloadMyAddressHashes()
        self.reloadBroadcastSendersForWhichImWatching()

        self.ui.tableWidgetSent.keyPressEvent = self.tableWidgetSentKeyPressEvent
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
            if safeConfigGetBoolean(toAddress,'mailinglist'):
                newItem.setTextColor(QtGui.QColor(137,04,177))
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
            #self.ui.textEditInboxMessage.setPlainText(self.ui.tableWidgetInbox.item(0,2).data(Qt.UserRole).toPyObject())

        self.ui.tableWidgetInbox.keyPressEvent = self.tableWidgetInboxKeyPressEvent
        #Load Sent items from database
        sqlSubmitQueue.put('''SELECT toaddress, fromaddress, subject, message, status, ackdata, lastactiontime FROM sent where folder = 'sent' ORDER BY lastactiontime''')
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
            newItem.setData(Qt.UserRole,QByteArray(ackdata))
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
            print 'Watching for ackdata', ackdata.encode('hex')
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
        QtCore.QObject.connect(self.singleCleanerThread, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)

        self.workerThread = singleWorker()
        self.workerThread.start()
        QtCore.QObject.connect(self.workerThread, QtCore.SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByHash)
        QtCore.QObject.connect(self.workerThread, QtCore.SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByAckdata)
        QtCore.QObject.connect(self.workerThread, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)

        if safeConfigGetBoolean('bitmessagesettings','apienabled'):
            try:
                apiNotifyPath = config.get('bitmessagesettings','apinotifypath')
            except:
                apiNotifyPath = ''
            if apiNotifyPath != '':
                printLock.acquire()
                print 'Trying to call', apiNotifyPath
                printLock.release()
                call([apiNotifyPath, "startingUp"])
            self.singleAPIThread = singleAPI()
            self.singleAPIThread.start()
            self.singleAPISignalHandlerThread = singleAPISignalHandler()
            self.singleAPISignalHandlerThread.start()
            QtCore.QObject.connect(self.singleAPISignalHandlerThread, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
            QtCore.QObject.connect(self.singleAPISignalHandlerThread, QtCore.SIGNAL("passAddressGeneratorObjectThrough(PyQt_PyObject)"), self.connectObjectToAddressGeneratorSignals)
            QtCore.QObject.connect(self.singleAPISignalHandlerThread, QtCore.SIGNAL("displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewSentMessage)

    def tableWidgetInboxKeyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.on_action_InboxTrash()
        return QtGui.QTableWidget.keyPressEvent(self.ui.tableWidgetInbox, event)

    def tableWidgetSentKeyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.on_action_SentTrash()
        return QtGui.QTableWidget.keyPressEvent(self.ui.tableWidgetSent, event)

    def click_actionManageKeys(self):
        if 'darwin' in sys.platform or 'linux' in sys.platform:
            if appdata == '':
                reply = QtGui.QMessageBox.information(self, 'keys.dat?','You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.', QMessageBox.Ok)
            else:
                QtGui.QMessageBox.information(self, 'keys.dat?','You may manage your keys by editing the keys.dat file stored in\n' + appdata + '\nIt is important that you back up this file.', QMessageBox.Ok)
        elif sys.platform == 'win32' or sys.platform == 'win64':
            if appdata == '':
                reply = QtGui.QMessageBox.question(self, 'Open keys.dat?','You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            else:
                reply = QtGui.QMessageBox.question(self, 'Open keys.dat?','You may manage your keys by editing the keys.dat file stored in\n' + appdata + '\nIt is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.openKeysFile()

    def click_actionRegenerateDeterministicAddresses(self):
        self.regenerateAddressesDialogInstance = regenerateAddressesDialog(self)
        if self.regenerateAddressesDialogInstance.exec_():
            if self.regenerateAddressesDialogInstance.ui.lineEditPassphrase.text() == "":
                QMessageBox.about(self, "bad passphrase", "You must type your passphrase. If you don\'t have one then this is not the form for you.")
            else:
                streamNumberForAddress = int(self.regenerateAddressesDialogInstance.ui.lineEditStreamNumber.text())
                addressVersionNumber = int(self.regenerateAddressesDialogInstance.ui.lineEditAddressVersionNumber.text())
                self.addressGenerator = addressGenerator()
                self.addressGenerator.setup(addressVersionNumber,streamNumberForAddress,"unused address",self.regenerateAddressesDialogInstance.ui.spinBoxNumberOfAddressesToMake.value(),self.regenerateAddressesDialogInstance.ui.lineEditPassphrase.text().toUtf8(),self.regenerateAddressesDialogInstance.ui.checkBoxEighteenByteRipe.isChecked())
                QtCore.QObject.connect(self.addressGenerator, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
                QtCore.QObject.connect(self.addressGenerator, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
                self.addressGenerator.start()
                self.ui.tabWidget.setCurrentIndex(3)

    def openKeysFile(self):
        if 'linux' in sys.platform:
            subprocess.call(["xdg-open", appdata + 'keys.dat'])
        else:
            os.startfile(appdata + 'keys.dat')

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
            status,addressVersionNumber,streamNumber,ripe = decodeAddress(toAddress)
            if ripe == toRipe:
                self.ui.tableWidgetSent.item(i,3).setText(unicode(textToDisplay,'utf-8'))

    def updateSentItemStatusByAckdata(self,ackdata,textToDisplay):
        for i in range(self.ui.tableWidgetSent.rowCount()):
            toAddress = str(self.ui.tableWidgetSent.item(i,0).data(Qt.UserRole).toPyObject())
            tableAckdata = self.ui.tableWidgetSent.item(i,3).data(Qt.UserRole).toPyObject()
            status,addressVersionNumber,streamNumber,ripe = decodeAddress(toAddress)
            if ackdata == tableAckdata:
                self.ui.tableWidgetSent.item(i,3).setText(unicode(textToDisplay,'utf-8'))

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
            #Set the color according to whether it is the address of a mailing list or not.
            if safeConfigGetBoolean(toAddress,'mailinglist'):
                self.ui.tableWidgetInbox.item(i,0).setTextColor(QtGui.QColor(137,04,177))
            else:
                self.ui.tableWidgetInbox.item(i,0).setTextColor(QtGui.QColor(0,0,0))

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
                        printLock.acquire()
                        print 'Error: Could not decode', toAddress, ':', status
                        printLock.release()
                        if status == 'missingbm':
                            self.statusBar().showMessage('Error: Bitmessage addresses start with BM-   Please check ' + toAddress)
                        if status == 'checksumfailed':
                            self.statusBar().showMessage('Error: The address ' + toAddress+' is not typed or copied correctly. Please check it.')
                        if status == 'invalidcharacters':
                            self.statusBar().showMessage('Error: The address '+ toAddress+ ' contains invalid characters. Please check it.')
                        if status == 'versiontoohigh':
                            self.statusBar().showMessage('Error: The address version in '+ toAddress+ ' is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.')
                    elif fromAddress == '':
                        self.statusBar().showMessage('Error: You must specify a From address. If you don\'t have one, go to the \'Your Identities\' tab.')
                    else:
                        toAddress = addBMIfNotPresent(toAddress)
                        try:
                            config.get(toAddress, 'enabled')
                            #The toAddress is one owned by me. We cannot send messages to ourselves without significant changes to the codebase.
                            QMessageBox.about(self, "Sending to your address", "Error: One of the addresses to which you are sending a message, "+toAddress+", is yours. Unfortunately the Bitmessage client cannot process its own messages. Please try running a second client on a different computer or within a VM.")
                            continue
                        except:
                            pass
                        if addressVersionNumber > 2 or addressVersionNumber == 0:
                            QMessageBox.about(self, "Address version number", "Concerning the address "+toAddress+", Bitmessage cannot understand address version numbers of "+str(addressVersionNumber)+". Perhaps upgrade Bitmessage to the latest version.")
                            continue
                        if streamNumber > 1 or streamNumber == 0:
                            QMessageBox.about(self, "Stream number", "Concerning the address "+toAddress+", Bitmessage cannot handle stream numbers of "+str(streamNumber)+". Perhaps upgrade Bitmessage to the latest version.")
                            continue
                        self.statusBar().showMessage('')
                        try:
                            if connectionsCount[streamNumber] == 0:
                                self.statusBar().showMessage('Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won\'t send until you connect.')
                        except:
                            self.statusBar().showMessage('Warning: The address uses a stream number currently not supported by this Bitmessage version. Perhaps upgrade.')
                        ackdata = OpenSSL.rand(32)
                        sqlLock.acquire()
                        t = ('',toAddress,ripe,fromAddress,subject,message,ackdata,int(time.time()),'findingpubkey',1,1,'sent')
                        sqlSubmitQueue.put('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''')
                        sqlSubmitQueue.put(t)
                        sqlReturnQueue.get()
                        sqlLock.release()


                        

                        """try:
                            fromLabel = config.get(fromAddress, 'label')
                        except:
                            fromLabel = ''
                        if fromLabel == '':
                            fromLabel = fromAddress"""

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
                        
                        self.displayNewSentMessage(toAddress,toLabel,fromAddress, subject, message, ackdata)
                        workerQueue.put(('sendmessage',toAddress))

                        """self.ui.tableWidgetSent.insertRow(0)
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
                        newItem.setData(Qt.UserRole,QByteArray(ackdata))
                        newItem.setData(33,int(time.time()))
                        self.ui.tableWidgetSent.setItem(0,3,newItem)

                        self.ui.textEditSentMessage.setPlainText(self.ui.tableWidgetSent.item(0,2).data(Qt.UserRole).toPyObject())"""

                        self.ui.comboBoxSendFrom.setCurrentIndex(0)
                        self.ui.labelFrom.setText('')
                        self.ui.lineEditTo.setText('')
                        self.ui.lineEditSubject.setText('')
                        self.ui.textEditMessage.setText('')
                        self.ui.tabWidget.setCurrentIndex(2)
                        self.ui.tableWidgetSent.setCurrentCell(0,0)
                else:
                    self.statusBar().showMessage('Your \'To\' field is empty.')
        else: #User selected 'Broadcast'
            if fromAddress == '':
                self.statusBar().showMessage('Error: You must specify a From address. If you don\'t have one, go to the \'Your Identities\' tab.')
            else:
                self.statusBar().showMessage('')
                #We don't actually need the ackdata for acknowledgement since this is a broadcast message, but we can use it to update the user interface when the POW is done generating.
                ackdata = OpenSSL.rand(32)
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
                newItem =  myTableWidgetItem('Work is queued.')
                newItem.setData(Qt.UserRole,QByteArray(ackdata))
                newItem.setData(33,int(time.time()))
                self.ui.tableWidgetSent.setItem(0,3,newItem)

                self.ui.textEditSentMessage.setPlainText(self.ui.tableWidgetSent.item(0,2).data(Qt.UserRole).toPyObject())

                self.ui.comboBoxSendFrom.setCurrentIndex(0)
                self.ui.labelFrom.setText('')
                self.ui.lineEditTo.setText('')
                self.ui.lineEditSubject.setText('')
                self.ui.textEditMessage.setText('')
                self.ui.tabWidget.setCurrentIndex(2)
                self.ui.tableWidgetSent.setCurrentCell(0,0)


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
        QtCore.QObject.connect(object, QtCore.SIGNAL("displayNewInboxMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewInboxMessage)
        QtCore.QObject.connect(object, QtCore.SIGNAL("displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.displayNewSentMessage)
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateSentItemStatusByHash(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByHash)
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateSentItemStatusByAckdata(PyQt_PyObject,PyQt_PyObject)"), self.updateSentItemStatusByAckdata)
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateNetworkStatusTab(PyQt_PyObject,PyQt_PyObject)"), self.updateNetworkStatusTab)
        QtCore.QObject.connect(object, QtCore.SIGNAL("incrementNumberOfMessagesProcessed()"), self.incrementNumberOfMessagesProcessed)
        QtCore.QObject.connect(object, QtCore.SIGNAL("incrementNumberOfPubkeysProcessed()"), self.incrementNumberOfPubkeysProcessed)
        QtCore.QObject.connect(object, QtCore.SIGNAL("incrementNumberOfBroadcastsProcessed()"), self.incrementNumberOfBroadcastsProcessed)
        QtCore.QObject.connect(object, QtCore.SIGNAL("setStatusIcon(PyQt_PyObject)"), self.setStatusIcon)

    #This function exists because of the API. The API thread starts an address generator thread and must somehow connect the address generator's signals to the QApplication thread. This function is used to connect the slots and signals.
    def connectObjectToAddressGeneratorSignals(self,object):
        QtCore.QObject.connect(object, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
        QtCore.QObject.connect(object, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)

    #This function is called by the processmsg function when that function receives a message to an address that is acting as a pseudo-mailing-list. The message will be broadcast out. This function puts the message on the 'Sent' tab.
    def displayNewSentMessage(self,toAddress,toLabel,fromAddress,subject,message,ackdata):
        try:
            fromLabel = config.get(fromAddress, 'label')
        except:
            fromLabel = ''
        if fromLabel == '':
            fromLabel = fromAddress

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
        #newItem =  QtGui.QTableWidgetItem('Doing work necessary to send broadcast...'+strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
        newItem =  myTableWidgetItem('Work is queued. '+strftime(config.get('bitmessagesettings', 'timeformat'),localtime(int(time.time()))))
        newItem.setData(Qt.UserRole,QByteArray(ackdata))
        newItem.setData(33,int(time.time()))
        self.ui.tableWidgetSent.setItem(0,3,newItem)
        self.ui.textEditSentMessage.setPlainText(self.ui.tableWidgetSent.item(0,2).data(Qt.UserRole).toPyObject())

    def displayNewInboxMessage(self,inventoryHash,toAddress,fromAddress,subject,message):
        '''print 'test signals displayNewInboxMessage'
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
        if safeConfigGetBoolean(str(toAddress),'mailinglist'):
            newItem.setTextColor(QtGui.QColor(137,04,177))
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

        self.ui.tableWidgetInbox.setCurrentCell(0,0)

        #If we have received this message from either a broadcast address or from someone in our address book, display as HTML
        if decodeAddress(fromAddress)[3] in broadcastSendersForWhichImWatching or isAddressInMyAddressBook(fromAddress):
            self.ui.textEditInboxMessage.setText(self.ui.tableWidgetInbox.item(0,2).data(Qt.UserRole).toPyObject())
        else:
            self.ui.textEditInboxMessage.setPlainText(self.ui.tableWidgetInbox.item(0,2).data(Qt.UserRole).toPyObject())
        

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
            sqlSubmitQueue.put('''SELECT label, address, enabled FROM blacklist''')
        else:
            sqlSubmitQueue.put('''SELECT label, address, enabled FROM whitelist''')
        sqlSubmitQueue.put('')
        queryreturn = sqlReturnQueue.get()
        for row in queryreturn:
            label, address, enabled = row
            self.ui.tableWidgetBlacklist.insertRow(0)
            newItem =  QtGui.QTableWidgetItem(unicode(label,'utf-8'))
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128,128,128))
            self.ui.tableWidgetBlacklist.setItem(0,0,newItem)
            newItem =  QtGui.QTableWidgetItem(address)
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            if not enabled:
                newItem.setTextColor(QtGui.QColor(128,128,128))
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
        global appdata
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

            if appdata != '' and self.settingsDialogInstance.ui.checkBoxPortableMode.isChecked(): #If we are NOT using portable mode now but the user selected that we should...
                config.set('bitmessagesettings','movemessagstoprog','true') #Tells bitmessage to move the messages.dat file to the program directory the next time the program starts.
                #Write the keys.dat file to disk in the new location
                with open('keys.dat', 'wb') as configfile:
                    config.write(configfile)
                #Write the knownnodes.dat file to disk in the new location
                output = open('knownnodes.dat', 'wb')
                pickle.dump(knownNodes, output)
                output.close()
                os.remove(appdata + 'keys.dat')
                os.remove(appdata + 'knownnodes.dat')
                appdata = ''
                QMessageBox.about(self, "Restart", "Bitmessage has moved most of your config files to the program directory but you must restart Bitmessage to move the last file (the file which holds messages).")

            if appdata == '' and not self.settingsDialogInstance.ui.checkBoxPortableMode.isChecked(): #If we ARE using portable mode now but the user selected that we shouldn't...
                appdata = lookupAppdataFolder()
                if not os.path.exists(appdata):
                    os.makedirs(appdata)         
                config.set('bitmessagesettings','movemessagstoappdata','true') #Tells bitmessage to move the messages.dat file to the appdata directory the next time the program starts.
                #Write the keys.dat file to disk in the new location
                with open(appdata + 'keys.dat', 'wb') as configfile:
                    config.write(configfile)
                #Write the knownnodes.dat file to disk in the new location
                output = open(appdata + 'knownnodes.dat', 'wb')
                pickle.dump(knownNodes, output)
                output.close()
                os.remove('keys.dat')
                os.remove('knownnodes.dat')
                QMessageBox.about(self, "Restart", "Bitmessage has moved most of your config files to the application data directory but you must restart Bitmessage to move the last file (the file which holds messages).")


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

    def on_action_SpecialAddressBehaviorDialog(self):
        self.dialog = SpecialAddressBehaviorDialog(self)
        # For Modal dialogs
        if self.dialog.exec_():
            currentRow = self.ui.tableWidgetYourIdentities.currentRow()
            addressAtCurrentRow = str(self.ui.tableWidgetYourIdentities.item(currentRow,1).text())
            if self.dialog.ui.radioButtonBehaveNormalAddress.isChecked():
                config.set(str(addressAtCurrentRow),'mailinglist','false')
                #Set the color to either black or grey
                if config.getboolean(addressAtCurrentRow,'enabled'):
                    self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(0,0,0))
                else:
                    self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(128,128,128))
            else:
                config.set(str(addressAtCurrentRow),'mailinglist','true')
                config.set(str(addressAtCurrentRow),'mailinglistname',str(self.dialog.ui.lineEditMailingListName.text().toUtf8()))
                self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(137,04,177))
            with open(appdata + 'keys.dat', 'wb') as configfile:
                config.write(configfile)
            self.rerenderInboxToLabels()


    def click_NewAddressDialog(self):
        self.dialog = NewAddressDialog(self)
        # For Modal dialogs
        if self.dialog.exec_():
            #self.dialog.ui.buttonBox.enabled = False
            if self.dialog.ui.radioButtonRandomAddress.isChecked():
                if self.dialog.ui.radioButtonMostAvailable.isChecked():
                    streamNumberForAddress = 1
                else:
                    #User selected 'Use the same stream as an existing address.'
                    streamNumberForAddress = addressStream(self.dialog.ui.comboBoxExisting.currentText())

                self.addressGenerator = addressGenerator()
                self.addressGenerator.setup(2,streamNumberForAddress,str(self.dialog.ui.newaddresslabel.text().toUtf8()),1,"",self.dialog.ui.checkBoxEighteenByteRipe.isChecked())
                QtCore.QObject.connect(self.addressGenerator, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
                QtCore.QObject.connect(self.addressGenerator, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
                self.addressGenerator.start()
            else:
                if self.dialog.ui.lineEditPassphrase.text() != self.dialog.ui.lineEditPassphraseAgain.text():
                    QMessageBox.about(self, "Passphrase mismatch", "The passphrase you entered twice doesn\'t match. Try again.")
                elif self.dialog.ui.lineEditPassphrase.text() == "":
                    QMessageBox.about(self, "Choose a passphrase", "You really do need a passphrase.")
                else:
                    streamNumberForAddress = 1 #this will eventually have to be replaced by logic to determine the most available stream number.
                    self.addressGenerator = addressGenerator()
                    self.addressGenerator.setup(2,streamNumberForAddress,"unused address",self.dialog.ui.spinBoxNumberOfAddressesToMake.value(),self.dialog.ui.lineEditPassphrase.text().toUtf8(),self.dialog.ui.checkBoxEighteenByteRipe.isChecked())
                    QtCore.QObject.connect(self.addressGenerator, SIGNAL("writeNewAddressToTable(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.writeNewAddressToTable)
                    QtCore.QObject.connect(self.addressGenerator, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
                    self.addressGenerator.start()
        else:
            print 'new address dialog box rejected'

    def closeEvent(self, event):
        '''quit_msg = "Are you sure you want to exit Bitmessage?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()'''

        broadcastToSendDataQueues((0, 'shutdown', 'all'))

        printLock.acquire()
        print 'Closing. Flushing inventory in memory out to disk...'
        printLock.release()
        self.statusBar().showMessage('Flushing inventory in memory out to disk.')
        flushInventory()

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
        printLock.acquire()
        print 'Done.'
        printLock.release()
        self.statusBar().showMessage('All done. Closing user interface...')
        event.accept()
        raise SystemExit


    def on_action_InboxReply(self):
        currentInboxRow = self.ui.tableWidgetInbox.currentRow()
        toAddressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(currentInboxRow,0).data(Qt.UserRole).toPyObject())
        fromAddressAtCurrentInboxRow = str(self.ui.tableWidgetInbox.item(currentInboxRow,1).data(Qt.UserRole).toPyObject())


        if toAddressAtCurrentInboxRow == '[Broadcast subscribers]':
            self.ui.labelFrom.setText('')
        else:
            if not config.get(toAddressAtCurrentInboxRow,'enabled'):
                self.statusBar().showMessage('Error: The address from which you are trying to send is disabled. Enable it from the \'Your Identities\' tab first.')
                return
            self.ui.labelFrom.setText(toAddressAtCurrentInboxRow)
        self.ui.lineEditTo.setText(str(fromAddressAtCurrentInboxRow))
        self.ui.comboBoxSendFrom.setCurrentIndex(0)
        #self.ui.comboBoxSendFrom.setEditText(str(self.ui.tableWidgetInbox.item(currentInboxRow,0).text))
        self.ui.textEditMessage.setText('\n\n------------------------------------------------------\n'+self.ui.tableWidgetInbox.item(currentInboxRow,2).data(Qt.UserRole).toPyObject())
        if self.ui.tableWidgetInbox.item(currentInboxRow,2).text()[0:3] == 'Re:':
            self.ui.lineEditSubject.setText(self.ui.tableWidgetInbox.item(currentInboxRow,2).text())
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

    #Send item on the Inbox tab to trash
    def on_action_InboxTrash(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        if currentRow >= 0:
            inventoryHashToTrash = str(self.ui.tableWidgetInbox.item(currentRow,3).data(Qt.UserRole).toPyObject())
            t = (inventoryHashToTrash,)
            sqlLock.acquire()
            #sqlSubmitQueue.put('''delete from inbox where msgid=?''')
            sqlSubmitQueue.put('''UPDATE inbox SET folder='trash' WHERE msgid=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            self.ui.textEditInboxMessage.setText("")
            self.ui.tableWidgetInbox.removeRow(currentRow)
            self.statusBar().showMessage('Moved item to trash. There is no user interface to view your trash, but it is still on disk if you are desperate to get it back.')

    #Send item on the Sent tab to trash
    def on_action_SentTrash(self):
        currentRow = self.ui.tableWidgetSent.currentRow()
        if currentRow >= 0:
            ackdataToTrash = str(self.ui.tableWidgetSent.item(currentRow,3).data(Qt.UserRole).toPyObject())
            t = (ackdataToTrash,)
            sqlLock.acquire()
            sqlSubmitQueue.put('''UPDATE sent SET folder='trash' WHERE ackdata=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
            sqlLock.release()
            self.ui.textEditSentMessage.setPlainText("")
            self.ui.tableWidgetSent.removeRow(currentRow)
            self.statusBar().showMessage('Moved item to trash. There is no user interface to view your trash, but it is still on disk if you are desperate to get it back.')
    def on_action_SentClipboard(self):
        currentRow = self.ui.tableWidgetSent.currentRow()
        addressAtCurrentRow = str(self.ui.tableWidgetSent.item(currentRow,0).data(Qt.UserRole).toPyObject())
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))

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
        self.reloadBroadcastSendersForWhichImWatching()
    def on_action_SubscriptionsClipboard(self):
        currentRow = self.ui.tableWidgetSubscriptions.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetSubscriptions.item(currentRow,1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))
    def on_context_menuSubscriptions(self, point):
        self.popMenuSubscriptions.exec_( self.ui.tableWidgetSubscriptions.mapToGlobal(point) )

    #Group of functions for the Blacklist dialog box
    def on_action_BlacklistNew(self):
        self.click_pushButtonAddBlacklist()
    def on_action_BlacklistDelete(self):
        print 'clicked Delete'
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        labelAtCurrentRow = self.ui.tableWidgetBlacklist.item(currentRow,0).text().toUtf8()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(currentRow,1).text()
        t = (str(labelAtCurrentRow),str(addressAtCurrentRow))
        sqlLock.acquire()
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlSubmitQueue.put('''DELETE FROM blacklist WHERE label=? AND address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        else:
            sqlSubmitQueue.put('''DELETE FROM whitelist WHERE label=? AND address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        sqlLock.release()
        self.ui.tableWidgetBlacklist.removeRow(currentRow)
    def on_action_BlacklistClipboard(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(currentRow,1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))
    def on_context_menuBlacklist(self, point):
        self.popMenuBlacklist.exec_( self.ui.tableWidgetBlacklist.mapToGlobal(point) )
    def on_action_BlacklistEnable(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(currentRow,1).text()
        self.ui.tableWidgetBlacklist.item(currentRow,0).setTextColor(QtGui.QColor(0,0,0))
        self.ui.tableWidgetBlacklist.item(currentRow,1).setTextColor(QtGui.QColor(0,0,0))
        t = (str(addressAtCurrentRow),)
        sqlLock.acquire()
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlSubmitQueue.put('''UPDATE blacklist SET enabled=1 WHERE address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        else:
            sqlSubmitQueue.put('''UPDATE whitelist SET enabled=1 WHERE address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        sqlLock.release()
    def on_action_BlacklistDisable(self):
        currentRow = self.ui.tableWidgetBlacklist.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetBlacklist.item(currentRow,1).text()
        self.ui.tableWidgetBlacklist.item(currentRow,0).setTextColor(QtGui.QColor(128,128,128))
        self.ui.tableWidgetBlacklist.item(currentRow,1).setTextColor(QtGui.QColor(128,128,128))
        t = (str(addressAtCurrentRow),)
        sqlLock.acquire()
        if config.get('bitmessagesettings', 'blackwhitelist') == 'black':
            sqlSubmitQueue.put('''UPDATE blacklist SET enabled=0 WHERE address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        else:
            sqlSubmitQueue.put('''UPDATE whitelist SET enabled=0 WHERE address=?''')
            sqlSubmitQueue.put(t)
            sqlReturnQueue.get()
        sqlLock.release()

    #Group of functions for the Your Identities dialog box
    def on_action_YourIdentitiesNew(self):
        self.click_NewAddressDialog()
    def on_action_YourIdentitiesEnable(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = str(self.ui.tableWidgetYourIdentities.item(currentRow,1).text())
        config.set(addressAtCurrentRow,'enabled','true')
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)
        self.ui.tableWidgetYourIdentities.item(currentRow,0).setTextColor(QtGui.QColor(0,0,0))
        self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(0,0,0))
        self.ui.tableWidgetYourIdentities.item(currentRow,2).setTextColor(QtGui.QColor(0,0,0))
        if safeConfigGetBoolean(addressAtCurrentRow,'mailinglist'):
            self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(137,04,177))
        reloadMyAddressHashes()
    def on_action_YourIdentitiesDisable(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = str(self.ui.tableWidgetYourIdentities.item(currentRow,1).text())
        config.set(str(addressAtCurrentRow),'enabled','false')
        self.ui.tableWidgetYourIdentities.item(currentRow,0).setTextColor(QtGui.QColor(128,128,128))
        self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(128,128,128))
        self.ui.tableWidgetYourIdentities.item(currentRow,2).setTextColor(QtGui.QColor(128,128,128))
        if safeConfigGetBoolean(addressAtCurrentRow,'mailinglist'):
            self.ui.tableWidgetYourIdentities.item(currentRow,1).setTextColor(QtGui.QColor(137,04,177))
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)
        reloadMyAddressHashes()
    def on_action_YourIdentitiesClipboard(self):
        currentRow = self.ui.tableWidgetYourIdentities.currentRow()
        addressAtCurrentRow = self.ui.tableWidgetYourIdentities.item(currentRow,1).text()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(str(addressAtCurrentRow))
    def on_context_menuYourIdentities(self, point):
        self.popMenu.exec_( self.ui.tableWidgetYourIdentities.mapToGlobal(point) )
    def on_context_menuInbox(self, point):
        self.popMenuInbox.exec_( self.ui.tableWidgetInbox.mapToGlobal(point) )
    def on_context_menuSent(self, point):
        self.popMenuSent.exec_( self.ui.tableWidgetSent.mapToGlobal(point) )

    def tableWidgetInboxItemClicked(self):
        currentRow = self.ui.tableWidgetInbox.currentRow()
        if currentRow >= 0:
            fromAddress = str(self.ui.tableWidgetInbox.item(currentRow,1).data(Qt.UserRole).toPyObject())
            #If we have received this message from either a broadcast address or from someone in our address book, display as HTML
            if decodeAddress(fromAddress)[3] in broadcastSendersForWhichImWatching or isAddressInMyAddressBook(fromAddress):
                self.ui.textEditInboxMessage.setText(self.ui.tableWidgetInbox.item(currentRow,2).data(Qt.UserRole).toPyObject())
            else:
                self.ui.textEditInboxMessage.setPlainText(self.ui.tableWidgetInbox.item(currentRow,2).data(Qt.UserRole).toPyObject())

        
    def tableWidgetSentItemClicked(self):
        currentRow = self.ui.tableWidgetSent.currentRow()
        if currentRow >= 0:
            self.ui.textEditSentMessage.setPlainText(self.ui.tableWidgetSent.item(currentRow,2).data(Qt.UserRole).toPyObject())

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

    def updateStatusBar(self,data):
        if data != "":
            printLock.acquire()
            print 'Status bar:', data
            printLock.release()
        self.statusBar().showMessage(data)

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
myRSAAddressHashes = {}
myECAddressHashes = {}
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
successfullyDecryptMessageTimings = [] #A list of the amounts of time it took to successfully decrypt msg messages
apiSignalQueue = Queue.Queue() #The singleAPI thread uses this queue to pass messages to a QT thread which can emit signals to do things like display a message in the UI.
apiAddressGeneratorReturnQueue = Queue.Queue() #The address generator thread uses this queue to get information back to the API thread.

#These constants are not at the top because if changed they will cause particularly unexpected behavior: You won't be able to either send or receive messages because the proof of work you do (or demand) won't match that done or demanded by others. Don't change them!
averageProofOfWorkNonceTrialsPerByte = 320 #The amount of work that should be performed (and demanded) per byte of the payload. Double this number to double the work.
payloadLengthExtraBytes = 14000 #To make sending short messages a little more difficult, this value is added to the payload length for use in calculating the proof of work target.

if useVeryEasyProofOfWorkForTesting:
    averageProofOfWorkNonceTrialsPerByte = averageProofOfWorkNonceTrialsPerByte / 16
    payloadLengthExtraBytes = payloadLengthExtraBytes / 7000

if __name__ == "__main__":
    # Check the Major version, the first element in the array
    if sqlite3.sqlite_version_info[0] < 3:
        print 'This program requires sqlite version 3 or higher because 2 and lower cannot store NULL values. I see version:', sqlite3.sqlite_version_info
        sys.exit()

    #First try to load the config file (the keys.dat file) from the program directory
    config = ConfigParser.SafeConfigParser()
    config.read('keys.dat')
    try:
        config.get('bitmessagesettings', 'settingsversion')
        #settingsFileExistsInProgramDirectory = True
        print 'Loading config files from same directory as program'
        appdata = ''
    except:
        #Could not load the keys.dat file in the program directory. Perhaps it is in the appdata directory.
        appdata = lookupAppdataFolder()
        #if not os.path.exists(appdata):
        #    os.makedirs(appdata)

        config = ConfigParser.SafeConfigParser()
        config.read(appdata + 'keys.dat')
        try:
            config.get('bitmessagesettings', 'settingsversion')
            print 'Loading existing config files from', appdata
        except:
            #This appears to be the first time running the program; there is no config file (or it cannot be accessed). Create config file.
            config.add_section('bitmessagesettings')
            config.set('bitmessagesettings','settingsversion','1')
            config.set('bitmessagesettings','port','8444')
            config.set('bitmessagesettings','timeformat','%%a, %%d %%b %%Y  %%I:%%M %%p')
            config.set('bitmessagesettings','blackwhitelist','black')
            config.set('bitmessagesettings','startonlogon','false')
            if 'linux' in sys.platform:
                config.set('bitmessagesettings','minimizetotray','false')#This isn't implimented yet and when True on Ubuntu causes Bitmessage to disappear while running when minimized.
            else:
                config.set('bitmessagesettings','minimizetotray','true')
            config.set('bitmessagesettings','showtraynotifications','true')
            config.set('bitmessagesettings','startintray','false')

            if storeConfigFilesInSameDirectoryAsProgramByDefault:
                #Just use the same directory as the program and forget about the appdata folder
                appdata = ''
                print 'Creating new config files in same directory as program.'
            else:
                print 'Creating new config files in', appdata
                if not os.path.exists(appdata):
                    os.makedirs(appdata)
            with open(appdata + 'keys.dat', 'wb') as configfile:
                config.write(configfile)

    if config.getint('bitmessagesettings','settingsversion') == 1:
        config.set('bitmessagesettings','settingsversion','3') #If the settings version is equal to 2 then the sqlThread will modify the pubkeys table and change the settings version to 3.
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

    #Let us now see if we should move the messages.dat file. There is an option in the settings to switch 'Portable Mode' on or off. Most of the files are moved instantly, but the messages.dat file cannot be moved while it is open. Now that it is not open we can move it now!
    try:
        config.getboolean('bitmessagesettings', 'movemessagstoprog')
        #If we have reached this point then we must move the messages.dat file from the appdata folder to the program folder
        print 'Moving messages.dat from its old location in the application data folder to its new home along side the program.'
        shutil.move(lookupAppdataFolder()+'messages.dat','messages.dat')
        config.remove_option('bitmessagesettings', 'movemessagstoprog')
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)
    except:
        pass
    try:
        config.getboolean('bitmessagesettings', 'movemessagstoappdata')
        #If we have reached this point then we must move the messages.dat file from the appdata folder to the program folder
        print 'Moving messages.dat from its old location next to the program to its new home in the application data folder.'
        shutil.move('messages.dat',lookupAppdataFolder()+'messages.dat')
        config.remove_option('bitmessagesettings', 'movemessagstoappdata')
        with open(appdata + 'keys.dat', 'wb') as configfile:
            config.write(configfile)
    except:
        pass


    try:
        pickleFile = open(appdata + 'knownnodes.dat', 'rb')
        knownNodes = pickle.load(pickleFile)
        pickleFile.close()
    except:
        createDefaultKnownNodes(appdata)
        pickleFile = open(appdata + 'knownnodes.dat', 'rb')
        knownNodes = pickle.load(pickleFile)
        pickleFile.close()

    if config.getint('bitmessagesettings', 'settingsversion') > 3:
        print 'Bitmessage cannot read future versions of the keys file (keys.dat). Run the newer version of Bitmessage.'
        raise SystemExit

    #DNS bootstrap. This could be programmed to use the SOCKS proxy to do the DNS lookup some day but for now we will just rely on the entries in defaultKnownNodes.py. Hopefully either they are up to date or the user has run Bitmessage recently without SOCKS turned on and received good bootstrap nodes using that method.
    if config.get('bitmessagesettings', 'socksproxytype') == 'none':
        try:
            for item in socket.getaddrinfo('bootstrap8080.bitmessage.org',80):
                print 'Adding', item[4][0],'to knownNodes based on DNS boostrap method'
                knownNodes[1][item[4][0]] = (8080,int(time.time()))
        except:
            print 'bootstrap8080.bitmessage.org DNS bootstraping failed.'
        try:
            for item in socket.getaddrinfo('bootstrap8444.bitmessage.org',80):
                print 'Adding', item[4][0],'to knownNodes based on DNS boostrap method'
                knownNodes[1][item[4][0]] = (8444,int(time.time()))
        except:
            print 'bootstrap8444.bitmessage.org DNS bootstrapping failed.'
    else:
        print 'DNS bootstrap skipped because SOCKS is used.'

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
