#!/usr/bin/env python2.7
# Copyright (c) 2012 Jonathan Warren
# Copyright (c) 2012 The Bitmessage developers
# Distributed under the MIT/X11 software license. See the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Right now, PyBitmessage only support connecting to stream 1. It doesn't
# yet contain logic to expand into further streams.

# The software version variable is now held in shared.py
verbose = 1
maximumAgeOfAnObjectThatIAmWillingToAccept = 216000  # Equals two days and 12 hours.
lengthOfTimeToLeaveObjectsInInventory = 237600  # Equals two days and 18 hours. This should be longer than maximumAgeOfAnObjectThatIAmWillingToAccept so that we don't process messages twice.
lengthOfTimeToHoldOnToAllPubkeys = 2419200  # Equals 4 weeks. You could make this longer if you want but making it shorter would not be advisable because there is a very small possibility that it could keep you from obtaining a needed pubkey for a period of time.
maximumAgeOfObjectsThatIAdvertiseToOthers = 216000  # Equals two days and 12 hours
maximumAgeOfNodesThatIAdvertiseToOthers = 10800  # Equals three hours
storeConfigFilesInSameDirectoryAsProgramByDefault = False  # The user may de-select Portable Mode in the settings if they want the config files to stay in the application data folder.
useVeryEasyProofOfWorkForTesting = False  # If you set this to True while on the normal network, you won't be able to send or sometimes receive messages.
encryptedBroadcastSwitchoverTime = 1369735200

import sys
import Queue
from addresses import *
import shared
from defaultKnownNodes import *
import time
import socket
import threading
import hashlib
from struct import *
import pickle
import random
import sqlite3
from time import strftime, localtime, gmtime
import string
import socks
import highlevelcrypto
from pyelliptic.openssl import OpenSSL
#import ctypes
import signal  # Used to capture a Ctrl-C keypress so that Bitmessage can shutdown gracefully.
# The next 3 are used for the API
from SimpleXMLRPCServer import *
import json
from subprocess import call  # used when the API must execute an outside program
import singleton
import proofofwork

# Classes
from class_sqlThread import *
from class_singleCleaner import *
from class_singleWorker import *
from class_addressGenerator import *

# Helper Functions
import helper_startup
import helper_bootstrap
import helper_inbox
import helper_sent
import helper_generic
import helper_bitcoin

# For each stream to which we connect, several outgoingSynSender threads
# will exist and will collectively create 8 connections with peers.

class outgoingSynSender(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def setup(self, streamNumber):
        self.streamNumber = streamNumber

    def run(self):
        time.sleep(1)
        global alreadyAttemptedConnectionsListResetTime
        while True:
            while len(selfInitiatedConnections[self.streamNumber]) >= 8:  # maximum number of outgoing connections = 8
                time.sleep(10)
            if shared.shutdown:
                break
            random.seed()
            shared.knownNodesLock.acquire()
            HOST, = random.sample(shared.knownNodes[self.streamNumber], 1)
            shared.knownNodesLock.release()
            alreadyAttemptedConnectionsListLock.acquire()
            while HOST in alreadyAttemptedConnectionsList or HOST in shared.connectedHostsList:
                alreadyAttemptedConnectionsListLock.release()
                # print 'choosing new sample'
                random.seed()
                shared.knownNodesLock.acquire()
                HOST, = random.sample(shared.knownNodes[self.streamNumber], 1)
                shared.knownNodesLock.release()
                time.sleep(1)
                # Clear out the alreadyAttemptedConnectionsList every half
                # hour so that this program will again attempt a connection
                # to any nodes, even ones it has already tried.
                if (time.time() - alreadyAttemptedConnectionsListResetTime) > 1800:
                    alreadyAttemptedConnectionsList.clear()
                    alreadyAttemptedConnectionsListResetTime = int(
                        time.time())
                alreadyAttemptedConnectionsListLock.acquire()
            alreadyAttemptedConnectionsList[HOST] = 0
            alreadyAttemptedConnectionsListLock.release()
            PORT, timeNodeLastSeen = shared.knownNodes[
                self.streamNumber][HOST]
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            # This option apparently avoids the TIME_WAIT state so that we
            # can rebind faster
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(20)
            if shared.config.get('bitmessagesettings', 'socksproxytype') == 'none' and verbose >= 2:
                shared.printLock.acquire()
                print 'Trying an outgoing connection to', HOST, ':', PORT
                shared.printLock.release()
                # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif shared.config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS4a':
                if verbose >= 2:
                    shared.printLock.acquire()
                    print '(Using SOCKS4a) Trying an outgoing connection to', HOST, ':', PORT
                    shared.printLock.release()
                proxytype = socks.PROXY_TYPE_SOCKS4
                sockshostname = shared.config.get(
                    'bitmessagesettings', 'sockshostname')
                socksport = shared.config.getint(
                    'bitmessagesettings', 'socksport')
                rdns = True  # Do domain name lookups through the proxy; though this setting doesn't really matter since we won't be doing any domain name lookups anyway.
                if shared.config.getboolean('bitmessagesettings', 'socksauthentication'):
                    socksusername = shared.config.get(
                        'bitmessagesettings', 'socksusername')
                    sockspassword = shared.config.get(
                        'bitmessagesettings', 'sockspassword')
                    sock.setproxy(
                        proxytype, sockshostname, socksport, rdns, socksusername, sockspassword)
                else:
                    sock.setproxy(
                        proxytype, sockshostname, socksport, rdns)
            elif shared.config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS5':
                if verbose >= 2:
                    shared.printLock.acquire()
                    print '(Using SOCKS5) Trying an outgoing connection to', HOST, ':', PORT
                    shared.printLock.release()
                proxytype = socks.PROXY_TYPE_SOCKS5
                sockshostname = shared.config.get(
                    'bitmessagesettings', 'sockshostname')
                socksport = shared.config.getint(
                    'bitmessagesettings', 'socksport')
                rdns = True  # Do domain name lookups through the proxy; though this setting doesn't really matter since we won't be doing any domain name lookups anyway.
                if shared.config.getboolean('bitmessagesettings', 'socksauthentication'):
                    socksusername = shared.config.get(
                        'bitmessagesettings', 'socksusername')
                    sockspassword = shared.config.get(
                        'bitmessagesettings', 'sockspassword')
                    sock.setproxy(
                        proxytype, sockshostname, socksport, rdns, socksusername, sockspassword)
                else:
                    sock.setproxy(
                        proxytype, sockshostname, socksport, rdns)

            try:
                sock.connect((HOST, PORT))
                rd = receiveDataThread()
                rd.daemon = True  # close the main program even if there are threads left
                objectsOfWhichThisRemoteNodeIsAlreadyAware = {}
                rd.setup(sock, HOST, PORT, self.streamNumber,
                         objectsOfWhichThisRemoteNodeIsAlreadyAware)
                rd.start()
                shared.printLock.acquire()
                print self, 'connected to', HOST, 'during an outgoing attempt.'
                shared.printLock.release()

                sd = sendDataThread()
                sd.setup(sock, HOST, PORT, self.streamNumber,
                         objectsOfWhichThisRemoteNodeIsAlreadyAware)
                sd.start()
                sd.sendVersionMessage()

            except socks.GeneralProxyError as err:
                if verbose >= 2:
                    shared.printLock.acquire()
                    print 'Could NOT connect to', HOST, 'during outgoing attempt.', err
                    shared.printLock.release()
                PORT, timeLastSeen = shared.knownNodes[
                    self.streamNumber][HOST]
                if (int(time.time()) - timeLastSeen) > 172800 and len(shared.knownNodes[self.streamNumber]) > 1000:  # for nodes older than 48 hours old if we have more than 1000 hosts in our list, delete from the shared.knownNodes data-structure.
                    shared.knownNodesLock.acquire()
                    del shared.knownNodes[self.streamNumber][HOST]
                    shared.knownNodesLock.release()
                    shared.printLock.acquire()
                    print 'deleting ', HOST, 'from shared.knownNodes because it is more than 48 hours old and we could not connect to it.'
                    shared.printLock.release()
            except socks.Socks5AuthError as err:
                shared.UISignalQueue.put((
                    'updateStatusBar', translateText(
                    "MainWindow", "SOCKS5 Authentication problem: %1").arg(str(err))))
            except socks.Socks5Error as err:
                pass
                print 'SOCKS5 error. (It is possible that the server wants authentication).)', str(err)
            except socks.Socks4Error as err:
                print 'Socks4Error:', err
            except socket.error as err:
                if shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
                    print 'Bitmessage MIGHT be having trouble connecting to the SOCKS server. ' + str(err)
                else:
                    if verbose >= 1:
                        shared.printLock.acquire()
                        print 'Could NOT connect to', HOST, 'during outgoing attempt.', err
                        shared.printLock.release()
                    PORT, timeLastSeen = shared.knownNodes[
                        self.streamNumber][HOST]
                    if (int(time.time()) - timeLastSeen) > 172800 and len(shared.knownNodes[self.streamNumber]) > 1000:  # for nodes older than 48 hours old if we have more than 1000 hosts in our list, delete from the knownNodes data-structure.
                        shared.knownNodesLock.acquire()
                        del shared.knownNodes[self.streamNumber][HOST]
                        shared.knownNodesLock.release()
                        shared.printLock.acquire()
                        print 'deleting ', HOST, 'from knownNodes because it is more than 48 hours old and we could not connect to it.'
                        shared.printLock.release()
            except Exception as err:
                sys.stderr.write(
                    'An exception has occurred in the outgoingSynSender thread that was not caught by other exception types: %s\n' % err)
            time.sleep(0.1)


# Only one singleListener thread will ever exist. It creates the
# receiveDataThread and sendDataThread for each incoming connection. Note
# that it cannot set the stream number because it is not known yet- the
# other node will have to tell us its stream number in a version message.
# If we don't care about their stream, we will close the connection
# (within the recversion function of the recieveData thread)

class singleListener(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # We don't want to accept incoming connections if the user is using a
        # SOCKS proxy. If they eventually select proxy 'none' then this will
        # start listening for connections.
        while shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
            time.sleep(300)

        shared.printLock.acquire()
        print 'Listening for incoming connections.'
        shared.printLock.release()
        HOST = ''  # Symbolic name meaning all available interfaces
        PORT = shared.config.getint('bitmessagesettings', 'port')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This option apparently avoids the TIME_WAIT state so that we can
        # rebind faster
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(2)

        while True:
            # We don't want to accept incoming connections if the user is using
            # a SOCKS proxy. If the user eventually select proxy 'none' then
            # this will start listening for connections.
            while shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
                time.sleep(10)
            while len(shared.connectedHostsList) > 220:
                shared.printLock.acquire()
                print 'We are connected to too many people. Not accepting further incoming connections for ten seconds.'
                shared.printLock.release()
                time.sleep(10)
            a, (HOST, PORT) = sock.accept()

            # The following code will, unfortunately, block an incoming
            # connection if someone else on the same LAN is already connected
            # because the two computers will share the same external IP. This
            # is here to prevent connection flooding.
            while HOST in shared.connectedHostsList:
                shared.printLock.acquire()
                print 'We are already connected to', HOST + '. Ignoring connection.'
                shared.printLock.release()
                a.close()
                a, (HOST, PORT) = sock.accept()
            objectsOfWhichThisRemoteNodeIsAlreadyAware = {}
            a.settimeout(20)

            sd = sendDataThread()
            sd.setup(
                a, HOST, PORT, -1, objectsOfWhichThisRemoteNodeIsAlreadyAware)
            sd.start()

            rd = receiveDataThread()
            rd.daemon = True  # close the main program even if there are threads left
            rd.setup(
                a, HOST, PORT, -1, objectsOfWhichThisRemoteNodeIsAlreadyAware)
            rd.start()

            shared.printLock.acquire()
            print self, 'connected to', HOST, 'during INCOMING request.'
            shared.printLock.release()

# This thread is created either by the synSenderThread(for outgoing
# connections) or the singleListenerThread(for incoming connectiosn).

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
            objectsOfWhichThisRemoteNodeIsAlreadyAware):
        self.sock = sock
        self.HOST = HOST
        self.PORT = port
        self.streamNumber = streamNumber
        self.payloadLength = 0  # This is the protocol payload length thus it doesn't include the 24 byte message header
        self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave = {}
        shared.connectedHostsList[
            self.HOST] = 0  # The very fact that this receiveData thread exists shows that we are connected to the remote host. Let's add it to this list so that an outgoingSynSender thread doesn't try to connect to it.
        self.connectionIsOrWasFullyEstablished = False  # set to true after the remote node and I accept each other's version messages. This is needed to allow the user interface to accurately reflect the current number of connections.
        if self.streamNumber == -1:  # This was an incoming connection. Send out a version message if we accept the other node's version message.
            self.initiatedConnection = False
        else:
            self.initiatedConnection = True
            selfInitiatedConnections[streamNumber][self] = 0
        self.ackDataThatWeHaveYetToSend = [
        ]  # When we receive a message bound for us, we store the acknowledgement that we need to send (the ackdata) here until we are done processing all other data received from this peer.
        self.objectsOfWhichThisRemoteNodeIsAlreadyAware = objectsOfWhichThisRemoteNodeIsAlreadyAware

    def run(self):
        shared.printLock.acquire()
        print 'ID of the receiveDataThread is', str(id(self)) + '. The size of the shared.connectedHostsList is now', len(shared.connectedHostsList)
        shared.printLock.release()
        while True:
            try:
                self.data += self.sock.recv(4096)
            except socket.timeout:
                shared.printLock.acquire()
                print 'Timeout occurred waiting for data from', self.HOST + '. Closing receiveData thread. (ID:', str(id(self)) + ')'
                shared.printLock.release()
                break
            except Exception as err:
                shared.printLock.acquire()
                print 'sock.recv error. Closing receiveData thread (HOST:', self.HOST, 'ID:', str(id(self)) + ').', err
                shared.printLock.release()
                break
            # print 'Received', repr(self.data)
            if self.data == "":
                shared.printLock.acquire()
                print 'Connection to', self.HOST, 'closed. Closing receiveData thread. (ID:', str(id(self)) + ')'
                shared.printLock.release()
                break
            else:
                self.processData()

        try:
            del selfInitiatedConnections[self.streamNumber][self]
            shared.printLock.acquire()
            print 'removed self (a receiveDataThread) from selfInitiatedConnections'
            shared.printLock.release()
        except:
            pass
        shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
        try:
            del shared.connectedHostsList[self.HOST]
        except Exception as err:
            shared.printLock.acquire()
            print 'Could not delete', self.HOST, 'from shared.connectedHostsList.', err
            shared.printLock.release()
        try:
            del numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                self.HOST]
        except:
            pass
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        shared.printLock.acquire()
        print 'The size of the connectedHostsList is now:', len(shared.connectedHostsList)
        shared.printLock.release()

    def processData(self):
        global verbose
        # if verbose >= 3:
            # shared.printLock.acquire()
            # print 'self.data is currently ', repr(self.data)
            # shared.printLock.release()
        if len(self.data) < 20:  # if so little of the data has arrived that we can't even unpack the payload length
            return
        if self.data[0:4] != '\xe9\xbe\xb4\xd9':
            if verbose >= 1:
                shared.printLock.acquire()
                print 'The magic bytes were not correct. First 40 bytes of data: ' + repr(self.data[0:40])
                shared.printLock.release()
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
            shared.knownNodes[self.streamNumber][
                self.HOST] = (self.PORT, int(time.time()))
            shared.knownNodesLock.release()
        if self.payloadLength <= 180000000:  # If the size of the message is greater than 180MB, ignore it. (I get memory errors when processing messages much larger than this though it is concievable that this value will have to be lowered if some systems are less tolarant of large messages.)
            remoteCommand = self.data[4:16]
            shared.printLock.acquire()
            print 'remoteCommand', repr(remoteCommand.replace('\x00', '')), ' from', self.HOST
            shared.printLock.release()
            if remoteCommand == 'version\x00\x00\x00\x00\x00':
                self.recversion(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'verack\x00\x00\x00\x00\x00\x00':
                self.recverack()
            elif remoteCommand == 'addr\x00\x00\x00\x00\x00\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recaddr(self.data[24:self.payloadLength + 24])
            elif remoteCommand == 'getpubkey\x00\x00\x00' and self.connectionIsOrWasFullyEstablished:
                self.recgetpubkey(self.data[24:self.payloadLength + 24])
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
            while len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 0:
                random.seed()
                objectHash, = random.sample(
                    self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave, 1)
                if objectHash in shared.inventory:
                    shared.printLock.acquire()
                    print 'Inventory (in memory) already has object listed in inv message.'
                    shared.printLock.release()
                    del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        objectHash]
                elif isInSqlInventory(objectHash):
                    if verbose >= 3:
                        shared.printLock.acquire()
                        print 'Inventory (SQL on disk) already has object listed in inv message.'
                        shared.printLock.release()
                    del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        objectHash]
                else:
                    self.sendgetdata(objectHash)
                    del self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        objectHash]  # It is possible that the remote node doesn't respond with the object. In that case, we'll very likely get it from someone else anyway.
                    if len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) == 0:
                        shared.printLock.acquire()
                        print '(concerning', self.HOST + ')', 'number of objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave is now', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)
                        shared.printLock.release()
                        try:
                            del numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                                self.HOST]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                        except:
                            pass
                    break
                if len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) == 0:
                    shared.printLock.acquire()
                    print '(concerning', self.HOST + ')', 'number of objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave is now', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)
                    shared.printLock.release()
                    try:
                        del numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                            self.HOST]  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
                    except:
                        pass
            if len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 0:
                shared.printLock.acquire()
                print '(concerning', self.HOST + ')', 'number of objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave is now', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)
                shared.printLock.release()
                numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[self.HOST] = len(
                    self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)  # this data structure is maintained so that we can keep track of how many total objects, across all connections, are currently outstanding. If it goes too high it can indicate that we are under attack by multiple nodes working together.
            if len(self.ackDataThatWeHaveYetToSend) > 0:
                self.data = self.ackDataThatWeHaveYetToSend.pop()
        self.processData()

    def isProofOfWorkSufficient(
        self,
        data,
        nonceTrialsPerByte=0,
            payloadLengthExtraBytes=0):
        if nonceTrialsPerByte < shared.networkDefaultProofOfWorkNonceTrialsPerByte:
            nonceTrialsPerByte = shared.networkDefaultProofOfWorkNonceTrialsPerByte
        if payloadLengthExtraBytes < shared.networkDefaultPayloadLengthExtraBytes:
            payloadLengthExtraBytes = shared.networkDefaultPayloadLengthExtraBytes
        POW, = unpack('>Q', hashlib.sha512(hashlib.sha512(data[
                      :8] + hashlib.sha512(data[8:]).digest()).digest()).digest()[0:8])
        # print 'POW:', POW
        return POW <= 2 ** 64 / ((len(data) + payloadLengthExtraBytes) * (nonceTrialsPerByte))

    def sendpong(self):
        print 'Sending pong'
        try:
            self.sock.sendall(
                '\xE9\xBE\xB4\xD9\x70\x6F\x6E\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()

    def recverack(self):
        print 'verack received'
        self.verackReceived = True
        if self.verackSent:
            # We have thus both sent and received a verack.
            self.connectionFullyEstablished()

    def connectionFullyEstablished(self):
        self.connectionIsOrWasFullyEstablished = True
        if not self.initiatedConnection:
            shared.UISignalQueue.put(('setStatusIcon', 'green'))
        self.sock.settimeout(
            600)  # We'll send out a pong every 5 minutes to make sure the connection stays alive if there has been no other traffic to send lately.
        shared.UISignalQueue.put(('updateNetworkStatusTab', 'no data'))
        remoteNodeIncomingPort, remoteNodeSeenTime = shared.knownNodes[
            self.streamNumber][self.HOST]
        shared.printLock.acquire()
        print 'Connection fully established with', self.HOST, remoteNodeIncomingPort
        print 'The size of the connectedHostsList is now', len(shared.connectedHostsList)
        print 'The length of sendDataQueues is now:', len(shared.sendDataQueues)
        print 'broadcasting addr from within connectionFullyEstablished function.'
        shared.printLock.release()
        self.broadcastaddr([(int(time.time()), self.streamNumber, 1, self.HOST,
                           remoteNodeIncomingPort)])  # This lets all of our peers know about this new node.
        self.sendaddr()  # This is one large addr message to this one peer.
        if not self.initiatedConnection and len(shared.connectedHostsList) > 200:
            shared.printLock.acquire()
            print 'We are connected to too many people. Closing connection.'
            shared.printLock.release()
            shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
            return
        self.sendBigInv()

    def sendBigInv(self):
        shared.sqlLock.acquire()
        # Select all hashes which are younger than two days old and in this
        # stream.
        t = (int(time.time()) - maximumAgeOfObjectsThatIAdvertiseToOthers, int(
            time.time()) - lengthOfTimeToHoldOnToAllPubkeys, self.streamNumber)
        shared.sqlSubmitQueue.put(
            '''SELECT hash FROM inventory WHERE ((receivedtime>? and objecttype<>'pubkey') or (receivedtime>? and objecttype='pubkey')) and streamnumber=?''')
        shared.sqlSubmitQueue.put(t)
        queryreturn = shared.sqlReturnQueue.get()
        shared.sqlLock.release()
        bigInvList = {}
        for row in queryreturn:
            hash, = row
            if hash not in self.objectsOfWhichThisRemoteNodeIsAlreadyAware:
                bigInvList[hash] = 0
        # We also have messages in our inventory in memory (which is a python
        # dictionary). Let's fetch those too.
        for hash, storedValue in shared.inventory.items():
            if hash not in self.objectsOfWhichThisRemoteNodeIsAlreadyAware:
                objectType, streamNumber, payload, receivedTime = storedValue
                if streamNumber == self.streamNumber and receivedTime > int(time.time()) - maximumAgeOfObjectsThatIAdvertiseToOthers:
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
        shared.printLock.acquire()
        print 'Sending huge inv message with', numberOfObjects, 'objects to just this one peer'
        shared.printLock.release()
        try:
            self.sock.sendall(headerData + payload)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()

    # We have received a broadcast message
    def recbroadcast(self, data):
        self.messageProcessingStartTime = time.time()
        # First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in broadcast message insufficient.'
            return
        readPosition = 8  # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime > (int(time.time()) + 10800):  # prevent funny business
            print 'The embedded time in this broadcast message is more than three hours in the future. That doesn\'t make sense. Ignoring message.'
            return
        if embeddedTime < (int(time.time()) - maximumAgeOfAnObjectThatIAmWillingToAccept):
            print 'The embedded time in this broadcast message is too old. Ignoring message.'
            return
        if len(data) < 180:
            print 'The payload length of this broadcast packet is unreasonably low. Someone is probably trying funny business. Ignoring message.'
            return
        # Let us check to make sure the stream number is correct (thus
        # preventing an individual from sending broadcasts out on the wrong
        # streams or all streams).
        broadcastVersion, broadcastVersionLength = decodeVarint(
            data[readPosition:readPosition + 10])
        if broadcastVersion >= 2:
            streamNumber, streamNumberLength = decodeVarint(data[
                                                            readPosition + broadcastVersionLength:readPosition + broadcastVersionLength + 10])
            if streamNumber != self.streamNumber:
                print 'The stream number encoded in this broadcast message (' + str(streamNumber) + ') does not match the stream number on which it was received. Ignoring it.'
                return

        shared.inventoryLock.acquire()
        self.inventoryHash = calculateInventoryHash(data)
        if self.inventoryHash in shared.inventory:
            print 'We have already received this broadcast object. Ignoring.'
            shared.inventoryLock.release()
            return
        elif isInSqlInventory(self.inventoryHash):
            print 'We have already received this broadcast object (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return
        # It is valid so far. Let's let our peers know about it.
        objectType = 'broadcast'
        shared.inventory[self.inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        self.broadcastinv(self.inventoryHash)
        shared.UISignalQueue.put((
            'incrementNumberOfBroadcastsProcessed', 'no data'))

        self.processbroadcast(
            readPosition, data)  # When this function returns, we will have either successfully processed this broadcast because we are interested in it, ignored it because we aren't interested in it, or found problem with the broadcast that warranted ignoring it.

        # Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. If we
        # haven't used the specified amount of time, we shall sleep. These
        # values are mostly the same values used for msg messages although
        # broadcast messages are processed faster.
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
        if sleepTime > 0:
            shared.printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            shared.printLock.release()
            time.sleep(sleepTime)
        shared.printLock.acquire()
        print 'Total message processing time:', time.time() - self.messageProcessingStartTime, 'seconds.'
        shared.printLock.release()

    # A broadcast message has a valid time and POW and requires processing.
    # The recbroadcast function calls this one.
    def processbroadcast(self, readPosition, data):
        broadcastVersion, broadcastVersionLength = decodeVarint(
            data[readPosition:readPosition + 9])
        readPosition += broadcastVersionLength
        if broadcastVersion < 1 or broadcastVersion > 2:
            print 'Cannot decode incoming broadcast versions higher than 2. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.'
            return
        if broadcastVersion == 1:
            beginningOfPubkeyPosition = readPosition  # used when we add the pubkey to our pubkey table
            sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
                data[readPosition:readPosition + 9])
            if sendersAddressVersion <= 1 or sendersAddressVersion >= 3:
                # Cannot decode senderAddressVersion higher than 2. Assuming
                # the sender isn\'t being silly, you should upgrade Bitmessage
                # because this message shall be ignored.
                return
            readPosition += sendersAddressVersionLength
            if sendersAddressVersion == 2:
                sendersStream, sendersStreamLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                readPosition += sendersStreamLength
                behaviorBitfield = data[readPosition:readPosition + 4]
                readPosition += 4
                sendersPubSigningKey = '\x04' + \
                    data[readPosition:readPosition + 64]
                readPosition += 64
                sendersPubEncryptionKey = '\x04' + \
                    data[readPosition:readPosition + 64]
                readPosition += 64
                endOfPubkeyPosition = readPosition
                sendersHash = data[readPosition:readPosition + 20]
                if sendersHash not in shared.broadcastSendersForWhichImWatching:
                    # Display timing data
                    shared.printLock.acquire()
                    print 'Time spent deciding that we are not interested in this v1 broadcast:', time.time() - self.messageProcessingStartTime
                    shared.printLock.release()
                    return
                # At this point, this message claims to be from sendersHash and
                # we are interested in it. We still have to hash the public key
                # to make sure it is truly the key that matches the hash, and
                # also check the signiture.
                readPosition += 20

                sha = hashlib.new('sha512')
                sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
                ripe = hashlib.new('ripemd160')
                ripe.update(sha.digest())
                if ripe.digest() != sendersHash:
                    # The sender of this message lied.
                    return
                messageEncodingType, messageEncodingTypeLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                if messageEncodingType == 0:
                    return
                readPosition += messageEncodingTypeLength
                messageLength, messageLengthLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                readPosition += messageLengthLength
                message = data[readPosition:readPosition + messageLength]
                readPosition += messageLength
                readPositionAtBottomOfMessage = readPosition
                signatureLength, signatureLengthLength = decodeVarint(
                    data[readPosition:readPosition + 9])
                readPosition += signatureLengthLength
                signature = data[readPosition:readPosition + signatureLength]
                try:
                    if not highlevelcrypto.verify(data[12:readPositionAtBottomOfMessage], signature, sendersPubSigningKey.encode('hex')):
                        print 'ECDSA verify failed'
                        return
                    print 'ECDSA verify passed'
                except Exception as err:
                    print 'ECDSA verify failed', err
                    return
                # verify passed

                # Let's store the public key in case we want to reply to this person.
                # We don't have the correct nonce or time (which would let us
                # send out a pubkey message) so we'll just fill it with 1's. We
                # won't be able to send this pubkey to others (without doing
                # the proof of work ourselves, which this program is programmed
                # to not do.)
                t = (ripe.digest(), '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + data[
                     beginningOfPubkeyPosition:endOfPubkeyPosition], int(time.time()), 'yes')
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
                shared.sqlSubmitQueue.put(t)
                shared.sqlReturnQueue.get()
                shared.sqlSubmitQueue.put('commit')
                shared.sqlLock.release()
                # shared.workerQueue.put(('newpubkey',(sendersAddressVersion,sendersStream,ripe.digest())))
                # This will check to see whether we happen to be awaiting this
                # pubkey in order to send a message. If we are, it will do the
                # POW and send it.
                self.possibleNewPubkey(ripe.digest())

                fromAddress = encodeAddress(
                    sendersAddressVersion, sendersStream, ripe.digest())
                shared.printLock.acquire()
                print 'fromAddress:', fromAddress
                shared.printLock.release()
                if messageEncodingType == 2:
                    bodyPositionIndex = string.find(message, '\nBody:')
                    if bodyPositionIndex > 1:
                        subject = message[8:bodyPositionIndex]
                        body = message[bodyPositionIndex + 6:]
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
                if messageEncodingType != 0:
                    
                    t = (self.inventoryHash, toAddress, fromAddress, subject, int(
                        time.time()), body, 'inbox', messageEncodingType, 0)
                    helper_inbox.insert(t)
                    
                    shared.UISignalQueue.put(('displayNewInboxMessage', (
                        self.inventoryHash, toAddress, fromAddress, subject, body)))

                    # If we are behaving as an API then we might need to run an
                    # outside command to let some program know that a new
                    # message has arrived.
                    if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
                        try:
                            apiNotifyPath = shared.config.get(
                                'bitmessagesettings', 'apinotifypath')
                        except:
                            apiNotifyPath = ''
                        if apiNotifyPath != '':
                            call([apiNotifyPath, "newBroadcast"])

                # Display timing data
                shared.printLock.acquire()
                print 'Time spent processing this interesting broadcast:', time.time() - self.messageProcessingStartTime
                shared.printLock.release()
        if broadcastVersion == 2:
            cleartextStreamNumber, cleartextStreamNumberLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += cleartextStreamNumberLength
            initialDecryptionSuccessful = False
            for key, cryptorObject in shared.MyECSubscriptionCryptorObjects.items():
                try:
                    decryptedData = cryptorObject.decrypt(data[readPosition:])
                    toRipe = key  # This is the RIPE hash of the sender's pubkey. We need this below to compare to the RIPE hash of the sender's address to verify that it was encrypted by with their key rather than some other key.
                    initialDecryptionSuccessful = True
                    print 'EC decryption successful using key associated with ripe hash:', key.encode('hex')
                    break
                except Exception as err:
                    pass
                    # print 'cryptorObject.decrypt Exception:', err
            if not initialDecryptionSuccessful:
                # This is not a broadcast I am interested in.
                shared.printLock.acquire()
                print 'Length of time program spent failing to decrypt this v2 broadcast:', time.time() - self.messageProcessingStartTime, 'seconds.'
                shared.printLock.release()
                return
            # At this point this is a broadcast I have decrypted and thus am
            # interested in.
            signedBroadcastVersion, readPosition = decodeVarint(
                decryptedData[:10])
            beginningOfPubkeyPosition = readPosition  # used when we add the pubkey to our pubkey table
            sendersAddressVersion, sendersAddressVersionLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersAddressVersion < 2 or sendersAddressVersion > 3:
                print 'Cannot decode senderAddressVersion other than 2 or 3. Assuming the sender isn\'t being silly, you should upgrade Bitmessage because this message shall be ignored.'
                return
            readPosition += sendersAddressVersionLength
            sendersStream, sendersStreamLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if sendersStream != cleartextStreamNumber:
                print 'The stream number outside of the encryption on which the POW was completed doesn\'t match the stream number inside the encryption. Ignoring broadcast.'
                return
            readPosition += sendersStreamLength
            behaviorBitfield = decryptedData[readPosition:readPosition + 4]
            readPosition += 4
            sendersPubSigningKey = '\x04' + \
                decryptedData[readPosition:readPosition + 64]
            readPosition += 64
            sendersPubEncryptionKey = '\x04' + \
                decryptedData[readPosition:readPosition + 64]
            readPosition += 64
            if sendersAddressVersion >= 3:
                requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                print 'sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is', requiredAverageProofOfWorkNonceTrialsPerByte
                requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                print 'sender\'s requiredPayloadLengthExtraBytes is', requiredPayloadLengthExtraBytes
            endOfPubkeyPosition = readPosition

            sha = hashlib.new('sha512')
            sha.update(sendersPubSigningKey + sendersPubEncryptionKey)
            ripe = hashlib.new('ripemd160')
            ripe.update(sha.digest())

            if toRipe != ripe.digest():
                print 'The encryption key used to encrypt this message doesn\'t match the keys inbedded in the message itself. Ignoring message.'
                return
            messageEncodingType, messageEncodingTypeLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            if messageEncodingType == 0:
                return
            readPosition += messageEncodingTypeLength
            messageLength, messageLengthLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            readPosition += messageLengthLength
            message = decryptedData[readPosition:readPosition + messageLength]
            readPosition += messageLength
            readPositionAtBottomOfMessage = readPosition
            signatureLength, signatureLengthLength = decodeVarint(
                decryptedData[readPosition:readPosition + 9])
            readPosition += signatureLengthLength
            signature = decryptedData[
                readPosition:readPosition + signatureLength]
            try:
                if not highlevelcrypto.verify(decryptedData[:readPositionAtBottomOfMessage], signature, sendersPubSigningKey.encode('hex')):
                    print 'ECDSA verify failed'
                    return
                print 'ECDSA verify passed'
            except Exception as err:
                print 'ECDSA verify failed', err
                return
            # verify passed

            # Let's store the public key in case we want to reply to this
            # person.
            t = (ripe.digest(), '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + decryptedData[
                 beginningOfPubkeyPosition:endOfPubkeyPosition], int(time.time()), 'yes')
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(sendersAddressVersion,sendersStream,ripe.digest())))
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(ripe.digest())

            fromAddress = encodeAddress(
                sendersAddressVersion, sendersStream, ripe.digest())
            shared.printLock.acquire()
            print 'fromAddress:', fromAddress
            shared.printLock.release()
            if messageEncodingType == 2:
                bodyPositionIndex = string.find(message, '\nBody:')
                if bodyPositionIndex > 1:
                    subject = message[8:bodyPositionIndex]
                    body = message[bodyPositionIndex + 6:]
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
            if messageEncodingType != 0:
                
                t = (self.inventoryHash, toAddress, fromAddress, subject, int(
                    time.time()), body, 'inbox', messageEncodingType, 0)
                helper_inbox.insert(t)
                
                shared.UISignalQueue.put(('displayNewInboxMessage', (
                    self.inventoryHash, toAddress, fromAddress, subject, body)))

                # If we are behaving as an API then we might need to run an
                # outside command to let some program know that a new message
                # has arrived.
                if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
                    try:
                        apiNotifyPath = shared.config.get(
                            'bitmessagesettings', 'apinotifypath')
                    except:
                        apiNotifyPath = ''
                    if apiNotifyPath != '':
                        call([apiNotifyPath, "newBroadcast"])

            # Display timing data
            shared.printLock.acquire()
            print 'Time spent processing this interesting broadcast:', time.time() - self.messageProcessingStartTime
            shared.printLock.release()

    # We have received a msg message.
    def recmsg(self, data):
        self.messageProcessingStartTime = time.time()
        # First we must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in msg message insufficient.'
            return

        readPosition = 8
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime > int(time.time()) + 10800:
            print 'The time in the msg message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time()) - maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in the msg message is too old. Ignoring it. Time:', embeddedTime
            return
        streamNumberAsClaimedByMsg, streamNumberAsClaimedByMsgLength = decodeVarint(
            data[readPosition:readPosition + 9])
        if streamNumberAsClaimedByMsg != self.streamNumber:
            print 'The stream number encoded in this msg (' + str(streamNumberAsClaimedByMsg) + ') message does not match the stream number on which it was received. Ignoring it.'
            return
        readPosition += streamNumberAsClaimedByMsgLength
        self.inventoryHash = calculateInventoryHash(data)
        shared.inventoryLock.acquire()
        if self.inventoryHash in shared.inventory:
            print 'We have already received this msg message. Ignoring.'
            shared.inventoryLock.release()
            return
        elif isInSqlInventory(self.inventoryHash):
            print 'We have already received this msg message (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return
        # This msg message is valid. Let's let our peers know about it.
        objectType = 'msg'
        shared.inventory[self.inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        self.broadcastinv(self.inventoryHash)
        shared.UISignalQueue.put((
            'incrementNumberOfMessagesProcessed', 'no data'))

        self.processmsg(
            readPosition, data)  # When this function returns, we will have either successfully processed the message bound for us, ignored it because it isn't bound for us, or found problem with the message that warranted ignoring it.

        # Let us now set lengthOfTimeWeShouldUseToProcessThisMessage. If we
        # haven't used the specified amount of time, we shall sleep. These
        # values are based on test timings and you may change them at-will.
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
        if sleepTime > 0:
            shared.printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            shared.printLock.release()
            time.sleep(sleepTime)
        shared.printLock.acquire()
        print 'Total message processing time:', time.time() - self.messageProcessingStartTime, 'seconds.'
        shared.printLock.release()

    # A msg message has a valid time and POW and requires processing. The
    # recmsg function calls this one.
    def processmsg(self, readPosition, encryptedData):
        initialDecryptionSuccessful = False
        # Let's check whether this is a message acknowledgement bound for us.
        if encryptedData[readPosition:] in ackdataForWhichImWatching:
            shared.printLock.acquire()
            print 'This msg IS an acknowledgement bound for me.'
            shared.printLock.release()
            del ackdataForWhichImWatching[encryptedData[readPosition:]]
            t = ('ackreceived', encryptedData[readPosition:])
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                'UPDATE sent SET status=? WHERE ackdata=?')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.UISignalQueue.put(('updateSentItemStatusByAckdata', (encryptedData[readPosition:], translateText("MainWindow",'Acknowledgement of the message received. %1').arg(unicode(
                strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(time.time()))), 'utf-8')))))
            return
        else:
            shared.printLock.acquire()
            print 'This was NOT an acknowledgement bound for me.'
            # print 'ackdataForWhichImWatching', ackdataForWhichImWatching
            shared.printLock.release()

        # This is not an acknowledgement bound for me. See if it is a message
        # bound for me by trying to decrypt it with my private keys.
        for key, cryptorObject in shared.myECCryptorObjects.items():
            try:
                decryptedData = cryptorObject.decrypt(
                    encryptedData[readPosition:])
                toRipe = key  # This is the RIPE hash of my pubkeys. We need this below to compare to the destination_ripe included in the encrypted data.
                initialDecryptionSuccessful = True
                print 'EC decryption successful using key associated with ripe hash:', key.encode('hex')
                break
            except Exception as err:
                pass
                # print 'cryptorObject.decrypt Exception:', err
        if not initialDecryptionSuccessful:
            # This is not a message bound for me.
            shared.printLock.acquire()
            print 'Length of time program spent failing to decrypt this message:', time.time() - self.messageProcessingStartTime, 'seconds.'
            shared.printLock.release()
        else:
            # This is a message bound for me.
            toAddress = shared.myAddressesByHash[
                toRipe]  # Look up my address based on the RIPE hash.
            readPosition = 0
            messageVersion, messageVersionLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += messageVersionLength
            if messageVersion != 1:
                print 'Cannot understand message versions other than one. Ignoring message.'
                return
            sendersAddressVersionNumber, sendersAddressVersionNumberLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += sendersAddressVersionNumberLength
            if sendersAddressVersionNumber == 0:
                print 'Cannot understand sendersAddressVersionNumber = 0. Ignoring message.'
                return
            if sendersAddressVersionNumber >= 4:
                print 'Sender\'s address version number', sendersAddressVersionNumber, 'not yet supported. Ignoring message.'
                return
            if len(decryptedData) < 170:
                print 'Length of the unencrypted data is unreasonably short. Sanity check failed. Ignoring message.'
                return
            sendersStreamNumber, sendersStreamNumberLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            if sendersStreamNumber == 0:
                print 'sender\'s stream number is 0. Ignoring message.'
                return
            readPosition += sendersStreamNumberLength
            behaviorBitfield = decryptedData[readPosition:readPosition + 4]
            readPosition += 4
            pubSigningKey = '\x04' + decryptedData[
                readPosition:readPosition + 64]
            readPosition += 64
            pubEncryptionKey = '\x04' + decryptedData[
                readPosition:readPosition + 64]
            readPosition += 64
            if sendersAddressVersionNumber >= 3:
                requiredAverageProofOfWorkNonceTrialsPerByte, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                print 'sender\'s requiredAverageProofOfWorkNonceTrialsPerByte is', requiredAverageProofOfWorkNonceTrialsPerByte
                requiredPayloadLengthExtraBytes, varintLength = decodeVarint(
                    decryptedData[readPosition:readPosition + 10])
                readPosition += varintLength
                print 'sender\'s requiredPayloadLengthExtraBytes is', requiredPayloadLengthExtraBytes
            endOfThePublicKeyPosition = readPosition  # needed for when we store the pubkey in our database of pubkeys for later use.
            if toRipe != decryptedData[readPosition:readPosition + 20]:
                shared.printLock.acquire()
                print 'The original sender of this message did not send it to you. Someone is attempting a Surreptitious Forwarding Attack.'
                print 'See: http://world.std.com/~dtd/sign_encrypt/sign_encrypt7.html'
                print 'your toRipe:', toRipe.encode('hex')
                print 'embedded destination toRipe:', decryptedData[readPosition:readPosition + 20].encode('hex')
                shared.printLock.release()
                return
            readPosition += 20
            messageEncodingType, messageEncodingTypeLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += messageEncodingTypeLength
            messageLength, messageLengthLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += messageLengthLength
            message = decryptedData[readPosition:readPosition + messageLength]
            # print 'First 150 characters of message:', repr(message[:150])
            readPosition += messageLength
            ackLength, ackLengthLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += ackLengthLength
            ackData = decryptedData[readPosition:readPosition + ackLength]
            readPosition += ackLength
            positionOfBottomOfAckData = readPosition  # needed to mark the end of what is covered by the signature
            signatureLength, signatureLengthLength = decodeVarint(
                decryptedData[readPosition:readPosition + 10])
            readPosition += signatureLengthLength
            signature = decryptedData[
                readPosition:readPosition + signatureLength]
            try:
                if not highlevelcrypto.verify(decryptedData[:positionOfBottomOfAckData], signature, pubSigningKey.encode('hex')):
                    print 'ECDSA verify failed'
                    return
                print 'ECDSA verify passed'
            except Exception as err:
                print 'ECDSA verify failed', err
                return
            shared.printLock.acquire()
            print 'As a matter of intellectual curiosity, here is the Bitcoin address associated with the keys owned by the other person:', helper_bitcoin.calculateBitcoinAddressFromPubkey(pubSigningKey), '  ..and here is the testnet address:', helper_bitcoin.calculateTestnetAddressFromPubkey(pubSigningKey), '. The other person must take their private signing key from Bitmessage and import it into Bitcoin (or a service like Blockchain.info) for it to be of any use. Do not use this unless you know what you are doing.'
            shared.printLock.release()
            # calculate the fromRipe.
            sha = hashlib.new('sha512')
            sha.update(pubSigningKey + pubEncryptionKey)
            ripe = hashlib.new('ripemd160')
            ripe.update(sha.digest())
            # Let's store the public key in case we want to reply to this
            # person.
            t = (ripe.digest(), '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + '\xFF\xFF\xFF\xFF' + decryptedData[
                 messageVersionLength:endOfThePublicKeyPosition], int(time.time()), 'yes')
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(sendersAddressVersionNumber,sendersStreamNumber,ripe.digest())))
            # This will check to see whether we happen to be awaiting this
            # pubkey in order to send a message. If we are, it will do the POW
            # and send it.
            self.possibleNewPubkey(ripe.digest())
            fromAddress = encodeAddress(
                sendersAddressVersionNumber, sendersStreamNumber, ripe.digest())
            # If this message is bound for one of my version 3 addresses (or
            # higher), then we must check to make sure it meets our demanded
            # proof of work requirement.
            if decodeAddress(toAddress)[1] >= 3:  # If the toAddress version number is 3 or higher:
                if not shared.isAddressInMyAddressBookSubscriptionsListOrWhitelist(fromAddress):  # If I'm not friendly with this person:
                    requiredNonceTrialsPerByte = shared.config.getint(
                        toAddress, 'noncetrialsperbyte')
                    requiredPayloadLengthExtraBytes = shared.config.getint(
                        toAddress, 'payloadlengthextrabytes')
                    if not self.isProofOfWorkSufficient(encryptedData, requiredNonceTrialsPerByte, requiredPayloadLengthExtraBytes):
                        print 'Proof of work in msg message insufficient only because it does not meet our higher requirement.'
                        return
            blockMessage = False  # Gets set to True if the user shouldn't see the message according to black or white lists.
            if shared.config.get('bitmessagesettings', 'blackwhitelist') == 'black':  # If we are using a blacklist
                t = (fromAddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''SELECT label FROM blacklist where address=? and enabled='1' ''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn != []:
                    shared.printLock.acquire()
                    print 'Message ignored because address is in blacklist.'
                    shared.printLock.release()
                    blockMessage = True
            else:  # We're using a whitelist
                t = (fromAddress,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''SELECT label FROM whitelist where address=? and enabled='1' ''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
                if queryreturn == []:
                    print 'Message ignored because address not in whitelist.'
                    blockMessage = True
            if not blockMessage:
                print 'fromAddress:', fromAddress
                print 'First 150 characters of message:', repr(message[:150])

                toLabel = shared.config.get(toAddress, 'label')
                if toLabel == '':
                    toLabel = toAddress

                if messageEncodingType == 2:
                    bodyPositionIndex = string.find(message, '\nBody:')
                    if bodyPositionIndex > 1:
                        subject = message[8:bodyPositionIndex]
                        subject = subject[
                            :500]  # Only save and show the first 500 characters of the subject. Any more is probably an attak.
                        body = message[bodyPositionIndex + 6:]
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
                if messageEncodingType != 0:
                    t = (self.inventoryHash, toAddress, fromAddress, subject, int(
                        time.time()), body, 'inbox', messageEncodingType, 0)
                    helper_inbox.insert(t)
                    
                    shared.UISignalQueue.put(('displayNewInboxMessage', (
                        self.inventoryHash, toAddress, fromAddress, subject, body)))

                # If we are behaving as an API then we might need to run an
                # outside command to let some program know that a new message
                # has arrived.
                if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
                    try:
                        apiNotifyPath = shared.config.get(
                            'bitmessagesettings', 'apinotifypath')
                    except:
                        apiNotifyPath = ''
                    if apiNotifyPath != '':
                        call([apiNotifyPath, "newMessage"])

                # Let us now check and see whether our receiving address is
                # behaving as a mailing list
                if shared.safeConfigGetBoolean(toAddress, 'mailinglist'):
                    try:
                        mailingListName = shared.config.get(
                            toAddress, 'mailinglistname')
                    except:
                        mailingListName = ''
                    # Let us send out this message as a broadcast
                    subject = self.addMailingListNameToSubject(
                        subject, mailingListName)
                    # Let us now send this message out as a broadcast
                    message = strftime("%a, %Y-%m-%d %H:%M:%S UTC", gmtime(
                    )) + '   Message ostensibly from ' + fromAddress + ':\n\n' + body
                    fromAddress = toAddress  # The fromAddress for the broadcast that we are about to send is the toAddress (my address) for the msg message we are currently processing.
                    ackdata = OpenSSL.rand(
                        32)  # We don't actually need the ackdata for acknowledgement since this is a broadcast message but we can use it to update the user interface when the POW is done generating.
                    toAddress = '[Broadcast subscribers]'
                    ripe = ''
                    
                    t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                        time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
                    helper_sent.insert(t)

                    shared.UISignalQueue.put(('displayNewSentMessage', (
                        toAddress, '[Broadcast subscribers]', fromAddress, subject, message, ackdata)))
                    shared.workerQueue.put(('sendbroadcast', ''))

            if self.isAckDataValid(ackData):
                print 'ackData is valid. Will process it.'
                self.ackDataThatWeHaveYetToSend.append(
                    ackData)  # When we have processed all data, the processData function will pop the ackData out and process it as if it is a message received from our peer.
            # Display timing data
            timeRequiredToAttemptToDecryptMessage = time.time(
            ) - self.messageProcessingStartTime
            successfullyDecryptMessageTimings.append(
                timeRequiredToAttemptToDecryptMessage)
            sum = 0
            for item in successfullyDecryptMessageTimings:
                sum += item
            shared.printLock.acquire()
            print 'Time to decrypt this message successfully:', timeRequiredToAttemptToDecryptMessage
            print 'Average time for all message decryption successes since startup:', sum / len(successfullyDecryptMessageTimings)
            shared.printLock.release()

    def isAckDataValid(self, ackData):
        if len(ackData) < 24:
            print 'The length of ackData is unreasonably short. Not sending ackData.'
            return False
        if ackData[0:4] != '\xe9\xbe\xb4\xd9':
            print 'Ackdata magic bytes were wrong. Not sending ackData.'
            return False
        ackDataPayloadLength, = unpack('>L', ackData[16:20])
        if len(ackData) - 24 != ackDataPayloadLength:
            print 'ackData payload length doesn\'t match the payload length specified in the header. Not sending ackdata.'
            return False
        if ackData[4:16] != 'getpubkey\x00\x00\x00' and ackData[4:16] != 'pubkey\x00\x00\x00\x00\x00\x00' and ackData[4:16] != 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00' and ackData[4:16] != 'broadcast\x00\x00\x00':
            return False
        return True

    def addMailingListNameToSubject(self, subject, mailingListName):
        subject = subject.strip()
        if subject[:3] == 'Re:' or subject[:3] == 'RE:':
            subject = subject[3:].strip()
        if '[' + mailingListName + ']' in subject:
            return subject
        else:
            return '[' + mailingListName + '] ' + subject

    def possibleNewPubkey(self, toRipe):
        if toRipe in neededPubkeys:
            print 'We have been awaiting the arrival of this pubkey.'
            del neededPubkeys[toRipe]
            t = (toRipe,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND status='awaitingpubkey' and folder='sent' ''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.workerQueue.put(('sendmessage', ''))
        else:
            shared.printLock.acquire()
            print 'We don\'t need this pub key. We didn\'t ask for it. Pubkey hash:', toRipe.encode('hex')
            shared.printLock.release()

    # We have received a pubkey
    def recpubkey(self, data):
        self.pubkeyProcessingStartTime = time.time()
        if len(data) < 146 or len(data) > 600:  # sanity check
            return
        # We must check to make sure the proof of work is sufficient.
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in pubkey message insufficient.'
            return

        readPosition = 8  # for the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime < int(time.time()) - lengthOfTimeToHoldOnToAllPubkeys:
            shared.printLock.acquire()
            print 'The embedded time in this pubkey message is too old. Ignoring. Embedded time is:', embeddedTime
            shared.printLock.release()
            return
        if embeddedTime > int(time.time()) + 10800:
            shared.printLock.acquire()
            print 'The embedded time in this pubkey message more than several hours in the future. This is irrational. Ignoring message.'
            shared.printLock.release()
            return
        addressVersion, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        if self.streamNumber != streamNumber:
            print 'stream number embedded in this pubkey doesn\'t match our stream number. Ignoring.'
            return

        inventoryHash = calculateInventoryHash(data)
        shared.inventoryLock.acquire()
        if inventoryHash in shared.inventory:
            print 'We have already received this pubkey. Ignoring it.'
            shared.inventoryLock.release()
            return
        elif isInSqlInventory(inventoryHash):
            print 'We have already received this pubkey (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return
        objectType = 'pubkey'
        shared.inventory[inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        self.broadcastinv(inventoryHash)
        shared.UISignalQueue.put((
            'incrementNumberOfPubkeysProcessed', 'no data'))

        self.processpubkey(data)

        lengthOfTimeWeShouldUseToProcessThisMessage = .2
        sleepTime = lengthOfTimeWeShouldUseToProcessThisMessage - \
            (time.time() - self.pubkeyProcessingStartTime)
        if sleepTime > 0:
            shared.printLock.acquire()
            print 'Timing attack mitigation: Sleeping for', sleepTime, 'seconds.'
            shared.printLock.release()
            time.sleep(sleepTime)
        shared.printLock.acquire()
        print 'Total pubkey processing time:', time.time() - self.pubkeyProcessingStartTime, 'seconds.'
        shared.printLock.release()

    def processpubkey(self, data):
        readPosition = 8  # for the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        addressVersion, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        streamNumber, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        if addressVersion == 0:
            print '(Within processpubkey) addressVersion of 0 doesn\'t make sense.'
            return
        if addressVersion >= 4 or addressVersion == 1:
            shared.printLock.acquire()
            print 'This version of Bitmessage cannot handle version', addressVersion, 'addresses.'
            shared.printLock.release()
            return
        if addressVersion == 2:
            if len(data) < 146:  # sanity check. This is the minimum possible length.
                print '(within processpubkey) payloadLength less than 146. Sanity check failed.'
                return
            bitfieldBehaviors = data[readPosition:readPosition + 4]
            readPosition += 4
            publicSigningKey = data[readPosition:readPosition + 64]
            # Is it possible for a public key to be invalid such that trying to
            # encrypt or sign with it will cause an error? If it is, we should
            # probably test these keys here.
            readPosition += 64
            publicEncryptionKey = data[readPosition:readPosition + 64]
            if len(publicEncryptionKey) < 64:
                print 'publicEncryptionKey length less than 64. Sanity check failed.'
                return
            sha = hashlib.new('sha512')
            sha.update(
                '\x04' + publicSigningKey + '\x04' + publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()

            shared.printLock.acquire()
            print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
            print 'ripe', ripe.encode('hex')
            print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
            print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')
            shared.printLock.release()

            t = (ripe,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT usedpersonally FROM pubkeys WHERE hash=? AND usedpersonally='yes' ''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                print 'We HAVE used this pubkey personally. Updating time.'
                t = (ripe, data, embeddedTime, 'yes')
            else:
                print 'We have NOT used this pubkey personally. Inserting in database.'
                t = (ripe, data, embeddedTime, 'no')
                     # This will also update the embeddedTime.
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))
            self.possibleNewPubkey(ripe)
        if addressVersion == 3:
            if len(data) < 170:  # sanity check.
                print '(within processpubkey) payloadLength less than 170. Sanity check failed.'
                return
            bitfieldBehaviors = data[readPosition:readPosition + 4]
            readPosition += 4
            publicSigningKey = '\x04' + data[readPosition:readPosition + 64]
            # Is it possible for a public key to be invalid such that trying to
            # encrypt or sign with it will cause an error? If it is, we should
            # probably test these keys here.
            readPosition += 64
            publicEncryptionKey = '\x04' + data[readPosition:readPosition + 64]
            readPosition += 64
            specifiedNonceTrialsPerByte, specifiedNonceTrialsPerByteLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += specifiedNonceTrialsPerByteLength
            specifiedPayloadLengthExtraBytes, specifiedPayloadLengthExtraBytesLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += specifiedPayloadLengthExtraBytesLength
            endOfSignedDataPosition = readPosition
            signatureLength, signatureLengthLength = decodeVarint(
                data[readPosition:readPosition + 10])
            readPosition += signatureLengthLength
            signature = data[readPosition:readPosition + signatureLength]
            try:
                if not highlevelcrypto.verify(data[8:endOfSignedDataPosition], signature, publicSigningKey.encode('hex')):
                    print 'ECDSA verify failed (within processpubkey)'
                    return
                print 'ECDSA verify passed (within processpubkey)'
            except Exception as err:
                print 'ECDSA verify failed (within processpubkey)', err
                return

            sha = hashlib.new('sha512')
            sha.update(publicSigningKey + publicEncryptionKey)
            ripeHasher = hashlib.new('ripemd160')
            ripeHasher.update(sha.digest())
            ripe = ripeHasher.digest()

            shared.printLock.acquire()
            print 'within recpubkey, addressVersion:', addressVersion, ', streamNumber:', streamNumber
            print 'ripe', ripe.encode('hex')
            print 'publicSigningKey in hex:', publicSigningKey.encode('hex')
            print 'publicEncryptionKey in hex:', publicEncryptionKey.encode('hex')
            shared.printLock.release()

            t = (ripe,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT usedpersonally FROM pubkeys WHERE hash=? AND usedpersonally='yes' ''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:  # if this pubkey is already in our database and if we have used it personally:
                print 'We HAVE used this pubkey personally. Updating time.'
                t = (ripe, data, embeddedTime, 'yes')
            else:
                print 'We have NOT used this pubkey personally. Inserting in database.'
                t = (ripe, data, embeddedTime, 'no')
                     # This will also update the embeddedTime.
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO pubkeys VALUES (?,?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            # shared.workerQueue.put(('newpubkey',(addressVersion,streamNumber,ripe)))
            self.possibleNewPubkey(ripe)

    # We have received a getpubkey message
    def recgetpubkey(self, data):
        if not self.isProofOfWorkSufficient(data):
            print 'Proof of work in getpubkey message insufficient.'
            return
        if len(data) < 34:
            print 'getpubkey message doesn\'t contain enough data. Ignoring.'
            return
        readPosition = 8  # bypass the nonce
        embeddedTime, = unpack('>I', data[readPosition:readPosition + 4])

        # This section is used for the transition from 32 bit time to 64 bit
        # time in the protocol.
        if embeddedTime == 0:
            embeddedTime, = unpack('>Q', data[readPosition:readPosition + 8])
            readPosition += 8
        else:
            readPosition += 4

        if embeddedTime > int(time.time()) + 10800:
            print 'The time in this getpubkey message is too new. Ignoring it. Time:', embeddedTime
            return
        if embeddedTime < int(time.time()) - maximumAgeOfAnObjectThatIAmWillingToAccept:
            print 'The time in this getpubkey message is too old. Ignoring it. Time:', embeddedTime
            return
        requestedAddressVersionNumber, addressVersionLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += addressVersionLength
        streamNumber, streamNumberLength = decodeVarint(
            data[readPosition:readPosition + 10])
        if streamNumber != self.streamNumber:
            print 'The streamNumber', streamNumber, 'doesn\'t match our stream number:', self.streamNumber
            return
        readPosition += streamNumberLength

        inventoryHash = calculateInventoryHash(data)
        shared.inventoryLock.acquire()
        if inventoryHash in shared.inventory:
            print 'We have already received this getpubkey request. Ignoring it.'
            shared.inventoryLock.release()
            return
        elif isInSqlInventory(inventoryHash):
            print 'We have already received this getpubkey request (it is stored on disk in the SQL inventory). Ignoring it.'
            shared.inventoryLock.release()
            return

        objectType = 'getpubkey'
        shared.inventory[inventoryHash] = (
            objectType, self.streamNumber, data, embeddedTime)
        shared.inventoryLock.release()
        # This getpubkey request is valid so far. Forward to peers.
        self.broadcastinv(inventoryHash)

        if requestedAddressVersionNumber == 0:
            print 'The requestedAddressVersionNumber of the pubkey request is zero. That doesn\'t make any sense. Ignoring it.'
            return
        elif requestedAddressVersionNumber == 1:
            print 'The requestedAddressVersionNumber of the pubkey request is 1 which isn\'t supported anymore. Ignoring it.'
            return
        elif requestedAddressVersionNumber > 3:
            print 'The requestedAddressVersionNumber of the pubkey request is too high. Can\'t understand. Ignoring it.'
            return

        requestedHash = data[readPosition:readPosition + 20]
        if len(requestedHash) != 20:
            print 'The length of the requested hash is not 20 bytes. Something is wrong. Ignoring.'
            return
        print 'the hash requested in this getpubkey request is:', requestedHash.encode('hex')

        if requestedHash in shared.myAddressesByHash:  # if this address hash is one of mine
            if decodeAddress(shared.myAddressesByHash[requestedHash])[1] != requestedAddressVersionNumber:
                shared.printLock.acquire()
                sys.stderr.write(
                    '(Within the recgetpubkey function) Someone requested one of my pubkeys but the requestedAddressVersionNumber doesn\'t match my actual address version number. That shouldn\'t have happened. Ignoring.\n')
                shared.printLock.release()
                return
            try:
                lastPubkeySendTime = int(shared.config.get(
                    shared.myAddressesByHash[requestedHash], 'lastpubkeysendtime'))
            except:
                lastPubkeySendTime = 0
            if lastPubkeySendTime < time.time() - lengthOfTimeToHoldOnToAllPubkeys:  # If the last time we sent our pubkey was 28 days ago
                shared.printLock.acquire()
                print 'Found getpubkey-requested-hash in my list of EC hashes. Telling Worker thread to do the POW for a pubkey message and send it out.'
                shared.printLock.release()
                if requestedAddressVersionNumber == 2:
                    shared.workerQueue.put((
                        'doPOWForMyV2Pubkey', requestedHash))
                elif requestedAddressVersionNumber == 3:
                    shared.workerQueue.put((
                        'doPOWForMyV3Pubkey', requestedHash))
            else:
                shared.printLock.acquire()
                print 'Found getpubkey-requested-hash in my list of EC hashes BUT we already sent it recently. Ignoring request. The lastPubkeySendTime is:', lastPubkeySendTime
                shared.printLock.release()
        else:
            shared.printLock.acquire()
            print 'This getpubkey request is not for any of my keys.'
            shared.printLock.release()

    # We have received an inv message
    def recinv(self, data):
        totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave = 0  # ..from all peers, counting duplicates seperately (because they take up memory)
        if len(numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer) > 0:
            for key, value in numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer.items():
                totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave += value
            shared.printLock.acquire()
            print 'number of keys(hosts) in numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer:', len(numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer)
            print 'totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave = ', totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave
            shared.printLock.release()
        numberOfItemsInInv, lengthOfVarint = decodeVarint(data[:10])
        if numberOfItemsInInv > 50000:
            sys.stderr.write('Too many items in inv message!')
            return
        if len(data) < lengthOfVarint + (numberOfItemsInInv * 32):
            print 'inv message doesn\'t contain enough data. Ignoring.'
            return
        if numberOfItemsInInv == 1:  # we'll just request this data from the person who advertised the object.
            if totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave > 200000 and len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 1000:  # inv flooding attack mitigation
                shared.printLock.acquire()
                print 'We already have', totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave, 'items yet to retrieve from peers and over 1000 from this node in particular. Ignoring this inv message.'
                shared.printLock.release()
                return
            self.objectsOfWhichThisRemoteNodeIsAlreadyAware[
                data[lengthOfVarint:32 + lengthOfVarint]] = 0
            if data[lengthOfVarint:32 + lengthOfVarint] in shared.inventory:
                shared.printLock.acquire()
                print 'Inventory (in memory) has inventory item already.'
                shared.printLock.release()
            elif isInSqlInventory(data[lengthOfVarint:32 + lengthOfVarint]):
                print 'Inventory (SQL on disk) has inventory item already.'
            else:
                self.sendgetdata(data[lengthOfVarint:32 + lengthOfVarint])
        else:
            print 'inv message lists', numberOfItemsInInv, 'objects.'
            for i in range(numberOfItemsInInv):  # upon finishing dealing with an incoming message, the receiveDataThread will request a random object from the peer. This way if we get multiple inv messages from multiple peers which list mostly the same objects, we will make getdata requests for different random objects from the various peers.
                if len(data[lengthOfVarint + (32 * i):32 + lengthOfVarint + (32 * i)]) == 32:  # The length of an inventory hash should be 32. If it isn't 32 then the remote node is either badly programmed or behaving nefariously.
                    if totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave > 200000 and len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave) > 1000:  # inv flooding attack mitigation
                        shared.printLock.acquire()
                        print 'We already have', totalNumberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave, 'items yet to retrieve from peers and over', len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave), 'from this node in particular. Ignoring the rest of this inv message.'
                        shared.printLock.release()
                        break
                    self.objectsOfWhichThisRemoteNodeIsAlreadyAware[data[
                        lengthOfVarint + (32 * i):32 + lengthOfVarint + (32 * i)]] = 0
                    self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave[
                        data[lengthOfVarint + (32 * i):32 + lengthOfVarint + (32 * i)]] = 0
            numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer[
                self.HOST] = len(self.objectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHave)

    # Send a getdata message to our peer to request the object with the given
    # hash
    def sendgetdata(self, hash):
        shared.printLock.acquire()
        print 'sending getdata to retrieve object with hash:', hash.encode('hex')
        shared.printLock.release()
        payload = '\x01' + hash
        headerData = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
        headerData += 'getdata\x00\x00\x00\x00\x00'
        headerData += pack('>L', len(
            payload))  # payload length. Note that we add an extra 8 for the nonce.
        headerData += hashlib.sha512(payload).digest()[:4]
        try:
            self.sock.sendall(headerData + payload)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()

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
            shared.printLock.acquire()
            print 'received getdata request for item:', hash.encode('hex')
            shared.printLock.release()
            # print 'inventory is', shared.inventory
            if hash in shared.inventory:
                objectType, streamNumber, payload, receivedTime = shared.inventory[
                    hash]
                self.sendData(objectType, payload)
            else:
                t = (hash,)
                shared.sqlLock.acquire()
                shared.sqlSubmitQueue.put(
                    '''select objecttype, payload from inventory where hash=?''')
                shared.sqlSubmitQueue.put(t)
                queryreturn = shared.sqlReturnQueue.get()
                shared.sqlLock.release()
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
            shared.printLock.acquire()
            print 'sending pubkey'
            shared.printLock.release()
            headerData += 'pubkey\x00\x00\x00\x00\x00\x00'
        elif objectType == 'getpubkey' or objectType == 'pubkeyrequest':
            shared.printLock.acquire()
            print 'sending getpubkey'
            shared.printLock.release()
            headerData += 'getpubkey\x00\x00\x00'
        elif objectType == 'msg':
            shared.printLock.acquire()
            print 'sending msg'
            shared.printLock.release()
            headerData += 'msg\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        elif objectType == 'broadcast':
            shared.printLock.acquire()
            print 'sending broadcast'
            shared.printLock.release()
            headerData += 'broadcast\x00\x00\x00'
        else:
            sys.stderr.write(
                'Error: sendData has been asked to send a strange objectType: %s\n' % str(objectType))
            return
        headerData += pack('>L', len(payload))  # payload length.
        headerData += hashlib.sha512(payload).digest()[:4]
        try:
            self.sock.sendall(headerData + payload)
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()

    # Send an inv message with just one hash to all of our peers
    def broadcastinv(self, hash):
        shared.printLock.acquire()
        print 'broadcasting inv with hash:', hash.encode('hex')
        shared.printLock.release()
        shared.broadcastToSendDataQueues((self.streamNumber, 'sendinv', hash))

    # We have received an addr message.
    def recaddr(self, data):
        listOfAddressDetailsToBroadcastToPeers = []
        numberOfAddressesIncluded = 0
        numberOfAddressesIncluded, lengthOfNumberOfAddresses = decodeVarint(
            data[:10])

        if verbose >= 1:
            shared.printLock.acquire()
            print 'addr message contains', numberOfAddressesIncluded, 'IP addresses.'
            shared.printLock.release()

        if self.remoteProtocolVersion == 1:
            if numberOfAddressesIncluded > 1000 or numberOfAddressesIncluded == 0:
                return
            if len(data) != lengthOfNumberOfAddresses + (34 * numberOfAddressesIncluded):
                print 'addr message does not contain the correct amount of data. Ignoring.'
                return

            needToWriteKnownNodesToDisk = False
            for i in range(0, numberOfAddressesIncluded):
                try:
                    if data[16 + lengthOfNumberOfAddresses + (34 * i):28 + lengthOfNumberOfAddresses + (34 * i)] != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                        shared.printLock.acquire()
                        print 'Skipping IPv6 address.', repr(data[16 + lengthOfNumberOfAddresses + (34 * i):28 + lengthOfNumberOfAddresses + (34 * i)])
                        shared.printLock.release()
                        continue
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (to test for an IPv6 address). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrStream, = unpack('>I', data[4 + lengthOfNumberOfAddresses + (
                        34 * i):8 + lengthOfNumberOfAddresses + (34 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrStream). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.
                if recaddrStream == 0:
                    continue
                if recaddrStream != self.streamNumber and recaddrStream != (self.streamNumber * 2) and recaddrStream != ((self.streamNumber * 2) + 1):  # if the embedded stream number is not in my stream or either of my child streams then ignore it. Someone might be trying funny business.
                    continue
                try:
                    recaddrServices, = unpack('>Q', data[8 + lengthOfNumberOfAddresses + (
                        34 * i):16 + lengthOfNumberOfAddresses + (34 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrServices). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrPort, = unpack('>H', data[32 + lengthOfNumberOfAddresses + (
                        34 * i):34 + lengthOfNumberOfAddresses + (34 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrPort). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.
                # print 'Within recaddr(): IP', recaddrIP, ', Port',
                # recaddrPort, ', i', i
                hostFromAddrMessage = socket.inet_ntoa(data[
                                                       28 + lengthOfNumberOfAddresses + (34 * i):32 + lengthOfNumberOfAddresses + (34 * i)])
                # print 'hostFromAddrMessage', hostFromAddrMessage
                if data[28 + lengthOfNumberOfAddresses + (34 * i)] == '\x7F':
                    print 'Ignoring IP address in loopback range:', hostFromAddrMessage
                    continue
                if helper_generic.isHostInPrivateIPRange(hostFromAddrMessage):
                    print 'Ignoring IP address in private range:', hostFromAddrMessage
                    continue
                timeSomeoneElseReceivedMessageFromThisNode, = unpack('>I', data[lengthOfNumberOfAddresses + (
                    34 * i):4 + lengthOfNumberOfAddresses + (34 * i)])  # This is the 'time' value in the received addr message.
                if recaddrStream not in shared.knownNodes:  # knownNodes is a dictionary of dictionaries with one outer dictionary for each stream. If the outer stream dictionary doesn't exist yet then we must make it.
                    shared.knownNodesLock.acquire()
                    shared.knownNodes[recaddrStream] = {}
                    shared.knownNodesLock.release()
                if hostFromAddrMessage not in shared.knownNodes[recaddrStream]:
                    if len(shared.knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time()) - 10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800):  # If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            recaddrPort, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        needToWriteKnownNodesToDisk = True
                        hostDetails = (
                            timeSomeoneElseReceivedMessageFromThisNode,
                            recaddrStream, recaddrServices, hostFromAddrMessage, recaddrPort)
                        listOfAddressDetailsToBroadcastToPeers.append(
                            hostDetails)
                else:
                    PORT, timeLastReceivedMessageFromThisNode = shared.knownNodes[recaddrStream][
                        hostFromAddrMessage]  # PORT in this case is either the port we used to connect to the remote node, or the port that was specified by someone else in a past addr message.
                    if (timeLastReceivedMessageFromThisNode < timeSomeoneElseReceivedMessageFromThisNode) and (timeSomeoneElseReceivedMessageFromThisNode < int(time.time())):
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            PORT, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        if PORT != recaddrPort:
                            print 'Strange occurance: The port specified in an addr message', str(recaddrPort), 'does not match the port', str(PORT), 'that this program (or some other peer) used to connect to it', str(hostFromAddrMessage), '. Perhaps they changed their port or are using a strange NAT configuration.'
            if needToWriteKnownNodesToDisk:  # Runs if any nodes were new to us. Also, share those nodes with our peers.
                shared.knownNodesLock.acquire()
                output = open(shared.appdata + 'knownnodes.dat', 'wb')
                pickle.dump(shared.knownNodes, output)
                output.close()
                shared.knownNodesLock.release()
                self.broadcastaddr(
                    listOfAddressDetailsToBroadcastToPeers)  # no longer broadcast
            shared.printLock.acquire()
            print 'knownNodes currently has', len(shared.knownNodes[self.streamNumber]), 'nodes for this stream.'
            shared.printLock.release()
        elif self.remoteProtocolVersion >= 2:  # The difference is that in protocol version 2, network addresses use 64 bit times rather than 32 bit times.
            if numberOfAddressesIncluded > 1000 or numberOfAddressesIncluded == 0:
                return
            if len(data) != lengthOfNumberOfAddresses + (38 * numberOfAddressesIncluded):
                print 'addr message does not contain the correct amount of data. Ignoring.'
                return

            needToWriteKnownNodesToDisk = False
            for i in range(0, numberOfAddressesIncluded):
                try:
                    if data[20 + lengthOfNumberOfAddresses + (38 * i):32 + lengthOfNumberOfAddresses + (38 * i)] != '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
                        shared.printLock.acquire()
                        print 'Skipping IPv6 address.', repr(data[20 + lengthOfNumberOfAddresses + (38 * i):32 + lengthOfNumberOfAddresses + (38 * i)])
                        shared.printLock.release()
                        continue
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (to test for an IPv6 address). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrStream, = unpack('>I', data[8 + lengthOfNumberOfAddresses + (
                        38 * i):12 + lengthOfNumberOfAddresses + (38 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrStream). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.
                if recaddrStream == 0:
                    continue
                if recaddrStream != self.streamNumber and recaddrStream != (self.streamNumber * 2) and recaddrStream != ((self.streamNumber * 2) + 1):  # if the embedded stream number is not in my stream or either of my child streams then ignore it. Someone might be trying funny business.
                    continue
                try:
                    recaddrServices, = unpack('>Q', data[12 + lengthOfNumberOfAddresses + (
                        38 * i):20 + lengthOfNumberOfAddresses + (38 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrServices). Message: %s\n' % str(err))
                    shared.printLock.release()
                    break  # giving up on unpacking any more. We should still be connected however.

                try:
                    recaddrPort, = unpack('>H', data[36 + lengthOfNumberOfAddresses + (
                        38 * i):38 + lengthOfNumberOfAddresses + (38 * i)])
                except Exception as err:
                    shared.printLock.acquire()
                    sys.stderr.write(
                        'ERROR TRYING TO UNPACK recaddr (recaddrPort). Message: %s\n' % str(err))
                    shared.printLock.release()
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
                if hostFromAddrMessage not in shared.knownNodes[recaddrStream]:
                    if len(shared.knownNodes[recaddrStream]) < 20000 and timeSomeoneElseReceivedMessageFromThisNode > (int(time.time()) - 10800) and timeSomeoneElseReceivedMessageFromThisNode < (int(time.time()) + 10800):  # If we have more than 20000 nodes in our list already then just forget about adding more. Also, make sure that the time that someone else received a message from this node is within three hours from now.
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            recaddrPort, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        shared.printLock.acquire()
                        print 'added new node', hostFromAddrMessage, 'to knownNodes in stream', recaddrStream
                        shared.printLock.release()
                        needToWriteKnownNodesToDisk = True
                        hostDetails = (
                            timeSomeoneElseReceivedMessageFromThisNode,
                            recaddrStream, recaddrServices, hostFromAddrMessage, recaddrPort)
                        listOfAddressDetailsToBroadcastToPeers.append(
                            hostDetails)
                else:
                    PORT, timeLastReceivedMessageFromThisNode = shared.knownNodes[recaddrStream][
                        hostFromAddrMessage]  # PORT in this case is either the port we used to connect to the remote node, or the port that was specified by someone else in a past addr message.
                    if (timeLastReceivedMessageFromThisNode < timeSomeoneElseReceivedMessageFromThisNode) and (timeSomeoneElseReceivedMessageFromThisNode < int(time.time())):
                        shared.knownNodesLock.acquire()
                        shared.knownNodes[recaddrStream][hostFromAddrMessage] = (
                            PORT, timeSomeoneElseReceivedMessageFromThisNode)
                        shared.knownNodesLock.release()
                        if PORT != recaddrPort:
                            print 'Strange occurance: The port specified in an addr message', str(recaddrPort), 'does not match the port', str(PORT), 'that this program (or some other peer) used to connect to it', str(hostFromAddrMessage), '. Perhaps they changed their port or are using a strange NAT configuration.'
            if needToWriteKnownNodesToDisk:  # Runs if any nodes were new to us. Also, share those nodes with our peers.
                shared.knownNodesLock.acquire()
                output = open(shared.appdata + 'knownnodes.dat', 'wb')
                pickle.dump(shared.knownNodes, output)
                output.close()
                shared.knownNodesLock.release()
                self.broadcastaddr(listOfAddressDetailsToBroadcastToPeers)
            shared.printLock.acquire()
            print 'knownNodes currently has', len(shared.knownNodes[self.streamNumber]), 'nodes for this stream.'
            shared.printLock.release()

    # Function runs when we want to broadcast an addr message to all of our
    # peers. Runs when we learn of nodes that we didn't previously know about
    # and want to share them with our peers.
    def broadcastaddr(self, listOfAddressDetailsToBroadcastToPeers):
        numberOfAddressesInAddrMessage = len(
            listOfAddressDetailsToBroadcastToPeers)
        payload = ''
        for hostDetails in listOfAddressDetailsToBroadcastToPeers:
            timeLastReceivedMessageFromThisNode, streamNumber, services, host, port = hostDetails
            payload += pack(
                '>Q', timeLastReceivedMessageFromThisNode)  # now uses 64-bit time
            payload += pack('>I', streamNumber)
            payload += pack(
                '>q', services)  # service bit flags offered by this node
            payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                socket.inet_aton(host)
            payload += pack('>H', port)  # remote port

        payload = encodeVarint(numberOfAddressesInAddrMessage) + payload
        datatosend = '\xE9\xBE\xB4\xD9addr\x00\x00\x00\x00\x00\x00\x00\x00'
        datatosend = datatosend + pack('>L', len(payload))  # payload length
        datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
        datatosend = datatosend + payload

        if verbose >= 1:
            shared.printLock.acquire()
            print 'Broadcasting addr with', numberOfAddressesInAddrMessage, 'entries.'
            shared.printLock.release()
        shared.broadcastToSendDataQueues((
            self.streamNumber, 'sendaddr', datatosend))

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
                random.seed()
                HOST, = random.sample(shared.knownNodes[self.streamNumber], 1)
                if helper_generic.isHostInPrivateIPRange(HOST):
                    continue
                addrsInMyStream[HOST] = shared.knownNodes[
                    self.streamNumber][HOST]
        if len(shared.knownNodes[self.streamNumber * 2]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(shared.knownNodes[
                                      self.streamNumber * 2], 1)
                if helper_generic.isHostInPrivateIPRange(HOST):
                    continue
                addrsInChildStreamLeft[HOST] = shared.knownNodes[
                    self.streamNumber * 2][HOST]
        if len(shared.knownNodes[(self.streamNumber * 2) + 1]) > 0:
            for i in range(250):
                random.seed()
                HOST, = random.sample(shared.knownNodes[
                                      (self.streamNumber * 2) + 1], 1)
                if helper_generic.isHostInPrivateIPRange(HOST):
                    continue
                addrsInChildStreamRight[HOST] = shared.knownNodes[
                    (self.streamNumber * 2) + 1][HOST]
        shared.knownNodesLock.release()
        numberOfAddressesInAddrMessage = 0
        payload = ''
        # print 'addrsInMyStream.items()', addrsInMyStream.items()
        for HOST, value in addrsInMyStream.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time()) - maximumAgeOfNodesThatIAdvertiseToOthers):  # If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', self.streamNumber)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                    socket.inet_aton(HOST)
                payload += pack('>H', PORT)  # remote port
        for HOST, value in addrsInChildStreamLeft.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time()) - maximumAgeOfNodesThatIAdvertiseToOthers):  # If it is younger than 3 hours old..
                numberOfAddressesInAddrMessage += 1
                payload += pack(
                    '>Q', timeLastReceivedMessageFromThisNode)  # 64-bit time
                payload += pack('>I', self.streamNumber * 2)
                payload += pack(
                    '>q', 1)  # service bit flags offered by this node
                payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
                    socket.inet_aton(HOST)
                payload += pack('>H', PORT)  # remote port
        for HOST, value in addrsInChildStreamRight.items():
            PORT, timeLastReceivedMessageFromThisNode = value
            if timeLastReceivedMessageFromThisNode > (int(time.time()) - maximumAgeOfNodesThatIAdvertiseToOthers):  # If it is younger than 3 hours old..
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
        try:
            self.sock.sendall(datatosend)
            if verbose >= 1:
                shared.printLock.acquire()
                print 'Sending addr with', numberOfAddressesInAddrMessage, 'entries.'
                shared.printLock.release()
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()

    # We have received a version message
    def recversion(self, data):
        if len(data) < 83:
            # This version message is unreasonably short. Forget it.
            return
        elif not self.verackSent:
            self.remoteProtocolVersion, = unpack('>L', data[:4])
            if self.remoteProtocolVersion <= 1:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
                shared.printLock.acquire()
                print 'Closing connection to old protocol version 1 node: ', self.HOST
                shared.printLock.release()
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
            shared.printLock.acquire()
            print 'Remote node useragent:', useragent, '  stream number:', self.streamNumber
            shared.printLock.release()
            if self.streamNumber != 1:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
                shared.printLock.acquire()
                print 'Closed connection to', self.HOST, 'because they are interested in stream', self.streamNumber, '.'
                shared.printLock.release()
                return
            shared.connectedHostsList[
                self.HOST] = 1  # We use this data structure to not only keep track of what hosts we are connected to so that we don't try to connect to them again, but also to list the connections count on the Network Status tab.
            # If this was an incoming connection, then the sendData thread
            # doesn't know the stream. We have to set it.
            if not self.initiatedConnection:
                shared.broadcastToSendDataQueues((
                    0, 'setStreamNumber', (self.HOST, self.streamNumber)))
            if data[72:80] == eightBytesOfRandomDataUsedToDetectConnectionsToSelf:
                shared.broadcastToSendDataQueues((0, 'shutdown', self.HOST))
                shared.printLock.acquire()
                print 'Closing connection to myself: ', self.HOST
                shared.printLock.release()
                return
            shared.broadcastToSendDataQueues((0, 'setRemoteProtocolVersion', (
                self.HOST, self.remoteProtocolVersion)))

            shared.knownNodesLock.acquire()
            shared.knownNodes[self.streamNumber][self.HOST] = (
                self.remoteNodeIncomingPort, int(time.time()))
            output = open(shared.appdata + 'knownnodes.dat', 'wb')
            pickle.dump(shared.knownNodes, output)
            output.close()
            shared.knownNodesLock.release()

            self.sendverack()
            if self.initiatedConnection == False:
                self.sendversion()

    # Sends a version message
    def sendversion(self):
        shared.printLock.acquire()
        print 'Sending version message'
        shared.printLock.release()
        try:
            self.sock.sendall(assembleVersionMessage(
                self.HOST, self.PORT, self.streamNumber))
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()

    # Sends a verack message
    def sendverack(self):
        shared.printLock.acquire()
        print 'Sending verack'
        shared.printLock.release()
        try:
            self.sock.sendall(
                '\xE9\xBE\xB4\xD9\x76\x65\x72\x61\x63\x6B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcf\x83\xe1\x35')
        except Exception as err:
            # if not 'Bad file descriptor' in err:
            shared.printLock.acquire()
            sys.stderr.write('sock.sendall error: %s\n' % err)
            shared.printLock.release()
                                                                                                             # cf
                                                                                                             # 83
                                                                                                             # e1
                                                                                                             # 35
        self.verackSent = True
        if self.verackReceived:
            self.connectionFullyEstablished()


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
        datatosend = assembleVersionMessage(
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


def isInSqlInventory(hash):
    t = (hash,)
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put('''select hash from inventory where hash=?''')
    shared.sqlSubmitQueue.put(t)
    queryreturn = shared.sqlReturnQueue.get()
    shared.sqlLock.release()
    if queryreturn == []:
        return False
    else:
        return True


def connectToStream(streamNumber):
    selfInitiatedConnections[streamNumber] = {}
    if sys.platform[0:3] == 'win':
        maximumNumberOfHalfOpenConnections = 9
    else:
        maximumNumberOfHalfOpenConnections = 32
    for i in range(maximumNumberOfHalfOpenConnections):
        a = outgoingSynSender()
        a.setup(streamNumber)
        a.start()



def assembleVersionMessage(remoteHost, remotePort, myStreamNumber):
    shared.softwareVersion
    payload = ''
    payload += pack('>L', 2)  # protocol version.
    payload += pack('>q', 1)  # bitflags of the services I offer.
    payload += pack('>q', int(time.time()))

    payload += pack(
        '>q', 1)  # boolservices of remote connection. How can I even know this for sure? This is probably ignored by the remote host.
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
        socket.inet_aton(remoteHost)
    payload += pack('>H', remotePort)  # remote IPv6 and port

    payload += pack('>q', 1)  # bitflags of the services I offer.
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + pack(
        '>L', 2130706433)  # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
    payload += pack('>H', shared.config.getint(
        'bitmessagesettings', 'port'))  # my external IPv6 and port

    random.seed()
    payload += eightBytesOfRandomDataUsedToDetectConnectionsToSelf
    userAgent = '/PyBitmessage:' + shared.softwareVersion + \
        '/'  # Length of userAgent must be less than 253.
    payload += pack('>B', len(
        userAgent))  # user agent string length. If the user agent is more than 252 bytes long, this code isn't going to work.
    payload += userAgent
    payload += encodeVarint(
        1)  # The number of streams about which I care. PyBitmessage currently only supports 1 per connection.
    payload += encodeVarint(myStreamNumber)

    datatosend = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
    datatosend = datatosend + 'version\x00\x00\x00\x00\x00'  # version command
    datatosend = datatosend + pack('>L', len(payload))  # payload length
    datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
    return datatosend + payload




# This is one of several classes that constitute the API
# This class was written by Vaibhav Bhatia. Modified by Jonathan Warren (Atheros).
# http://code.activestate.com/recipes/501148-xmlrpc-serverclient-which-does-cookie-handling-and/


class MySimpleXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):

    def do_POST(self):
        # Handles the HTTP POST request.
        # Attempts to interpret all HTTP POST requests as XML-RPC calls,
        # which are forwarded to the server's _dispatch method for handling.

        # Note: this method is the same as in SimpleXMLRPCRequestHandler,
        # just hacked to handle cookies

        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10 * 1024 * 1024
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
        except:  # This should only happen if the module is buggy
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
                    self.send_header('Set-Cookie', cookie.output(header=''))
            # HACK :end

            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)

    def APIAuthenticateClient(self):
        if 'Authorization' in self.headers:
            # handle Basic authentication
            (enctype, encstr) = self.headers.get('Authorization').split()
            (emailid, password) = encstr.decode('base64').split(':')
            if emailid == shared.config.get('bitmessagesettings', 'apiusername') and password == shared.config.get('bitmessagesettings', 'apipassword'):
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
            (a, b) = params
            return a + '-' + b
        elif method == 'add':
            (a, b) = params
            return a + b
        elif method == 'statusBar':
            message, = params
            shared.UISignalQueue.put(('updateStatusBar', message))
        elif method == 'listAddresses':
            data = '{"addresses":['
            configSections = shared.config.sections()
            for addressInKeysFile in configSections:
                if addressInKeysFile != 'bitmessagesettings':
                    status, addressVersionNumber, streamNumber, hash = decodeAddress(
                        addressInKeysFile)
                    data
                    if len(data) > 20:
                        data += ','
                    data += json.dumps({'label': shared.config.get(addressInKeysFile, 'label'), 'address': addressInKeysFile, 'stream':
                                       streamNumber, 'enabled': shared.config.getboolean(addressInKeysFile, 'enabled')}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'createRandomAddress':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            elif len(params) == 1:
                label, = params
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 2:
                label, eighteenByteRipe = params
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 3:
                label, eighteenByteRipe, totalDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 4:
                label, eighteenByteRipe, totalDifficulty, smallMessageDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = int(
                    shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
            else:
                return 'API Error 0000: Too many parameters!'
            label = label.decode('base64')
            try:
                unicode(label, 'utf-8')
            except:
                return 'API Error 0017: Label is not valid UTF-8 data.'
            apiAddressGeneratorReturnQueue.queue.clear()
            streamNumberForAddress = 1
            shared.addressGeneratorQueue.put((
                'createRandomAddress', 3, streamNumberForAddress, label, 1, "", eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
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
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 2:
                passphrase, numberOfAddresses = params
                addressVersionNumber = 0
                streamNumber = 0
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 3:
                passphrase, numberOfAddresses, addressVersionNumber = params
                streamNumber = 0
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 4:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber = params
                eighteenByteRipe = False
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 5:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe = params
                nonceTrialsPerByte = shared.config.get(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 6:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe, totalDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = shared.config.get(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            elif len(params) == 7:
                passphrase, numberOfAddresses, addressVersionNumber, streamNumber, eighteenByteRipe, totalDifficulty, smallMessageDifficulty = params
                nonceTrialsPerByte = int(
                    shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
                payloadLengthExtraBytes = int(
                    shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
            else:
                return 'API Error 0000: Too many parameters!'
            if len(passphrase) == 0:
                return 'API Error 0001: The specified passphrase is blank.'
            passphrase = passphrase.decode('base64')
            if addressVersionNumber == 0:  # 0 means "just use the proper addressVersionNumber"
                addressVersionNumber = 3
            if addressVersionNumber != 3:
                return 'API Error 0002: The address version number currently must be 3 (or 0 which means auto-select). ' + addressVersionNumber + ' isn\'t supported.'
            if streamNumber == 0:  # 0 means "just use the most available stream"
                streamNumber = 1
            if streamNumber != 1:
                return 'API Error 0003: The stream number must be 1 (or 0 which means auto-select). Others aren\'t supported.'
            if numberOfAddresses == 0:
                return 'API Error 0004: Why would you ask me to generate 0 addresses for you?'
            if numberOfAddresses > 999:
                return 'API Error 0005: You have (accidentally?) specified too many addresses to make. Maximum 999. This check only exists to prevent mischief; if you really want to create more addresses than this, contact the Bitmessage developers and we can modify the check or you can do it yourself by searching the source code for this message.'
            apiAddressGeneratorReturnQueue.queue.clear()
            print 'Requesting that the addressGenerator create', numberOfAddresses, 'addresses.'
            shared.addressGeneratorQueue.put(
                ('createDeterministicAddresses', addressVersionNumber, streamNumber,
                 'unused API address', numberOfAddresses, passphrase, eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
            data = '{"addresses":['
            queueReturn = apiAddressGeneratorReturnQueue.get()
            for item in queueReturn:
                if len(data) > 20:
                    data += ','
                data += "\"" + item + "\""
            data += ']}'
            return data
        elif method == 'getDeterministicAddress':
            if len(params) != 3:
                return 'API Error 0000: I need exactly 3 parameters.'
            passphrase, addressVersionNumber, streamNumber = params
            numberOfAddresses = 1
            eighteenByteRipe = False
            if len(passphrase) == 0:
                return 'API Error 0001: The specified passphrase is blank.'
            passphrase = passphrase.decode('base64')
            if addressVersionNumber != 3:
                return 'API Error 0002: The address version number currently must be 3. ' + addressVersionNumber + ' isn\'t supported.'
            if streamNumber != 1:
                return 'API Error 0003: The stream number must be 1. Others aren\'t supported.'
            apiAddressGeneratorReturnQueue.queue.clear()
            print 'Requesting that the addressGenerator create', numberOfAddresses, 'addresses.'
            shared.addressGeneratorQueue.put(
                ('getDeterministicAddress', addressVersionNumber,
                 streamNumber, 'unused API address', numberOfAddresses, passphrase, eighteenByteRipe))
            return apiAddressGeneratorReturnQueue.get()
        elif method == 'getAllInboxMessages':
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype FROM inbox where folder='inbox' ORDER BY received''')
            shared.sqlSubmitQueue.put('')
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"inboxMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid': msgid.encode('hex'), 'toAddress': toAddress, 'fromAddress': fromAddress, 'subject': subject.encode(
                    'base64'), 'message': message.encode('base64'), 'encodingType': encodingtype, 'receivedTime': received}, indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getInboxMessageById':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            v = (msgid,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype FROM inbox WHERE msgid=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"inboxMessage":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                data += json.dumps({'msgid':msgid.encode('hex'),'toAddress':toAddress,'fromAddress':fromAddress,'subject':subject.encode('base64'),'message':message.encode('base64'),'encodingType':encodingtype,'receivedTime':received},indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getAllSentMessages':
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent where folder='sent' ORDER BY lastactiontime''')
            shared.sqlSubmitQueue.put('')
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid':msgid.encode('hex'),'toAddress':toAddress,'fromAddress':fromAddress,'subject':subject.encode('base64'),'message':message.encode('base64'),'encodingType':encodingtype,'lastActionTime':lastactiontime,'status':status,'ackData':ackdata.encode('hex')},indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getInboxMessagesByAddress':
            toAddress = params[0]
            v = (toAddress,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype FROM inbox WHERE toAddress=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"inboxMessages":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype= row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                if len(data) > 25:
                    data += ','
                data += json.dumps({'msgid':msgid.encode('hex'),'toAddress':toAddress,'fromAddress':fromAddress,'subject':subject.encode('base64'),'message':message.encode('base64'),'encodingType':encodingtype,'received':received},indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getSentMessageById':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            v = (msgid,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE msgid=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessage":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                data += json.dumps({'msgid':msgid.encode('hex'),'toAddress':toAddress,'fromAddress':fromAddress,'subject':subject.encode('base64'),'message':message.encode('base64'),'encodingType':encodingtype,'lastActionTime':lastactiontime,'status':status,'ackData':ackdata.encode('hex')},indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif method == 'getSentMessageByAckData':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            ackData = params[0].decode('hex')
            v = (ackData,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE ackdata=?''')
            shared.sqlSubmitQueue.put(v)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            data = '{"sentMessage":['
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = shared.fixPotentiallyInvalidUTF8Data(subject)
                message = shared.fixPotentiallyInvalidUTF8Data(message)
                data += json.dumps({'msgid':msgid.encode('hex'),'toAddress':toAddress,'fromAddress':fromAddress,'subject':subject.encode('base64'),'message':message.encode('base64'),'encodingType':encodingtype,'lastActionTime':lastactiontime,'status':status,'ackData':ackdata.encode('hex')},indent=4, separators=(',', ': '))
            data += ']}'
            return data
        elif (method == 'trashMessage') or (method == 'trashInboxMessage'):
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            helper_inbox.trash(msgid)
            return 'Trashed inbox message (assuming message existed).'
        elif method == 'trashSentMessage':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            msgid = params[0].decode('hex')
            t = (msgid,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put('''UPDATE sent SET folder='trash' WHERE msgid=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            #shared.UISignalQueue.put(('removeSentRowByMsgid',msgid)) This function doesn't exist yet.
            return 'Trashed sent message (assuming message existed).'
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
            status, addressVersionNumber, streamNumber, toRipe = decodeAddress(
                toAddress)
            if status != 'success':
                shared.printLock.acquire()
                print 'API Error 0007: Could not decode address:', toAddress, ':', status
                shared.printLock.release()
                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + toAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + toAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + toAddress
                return 'API Error 0007: Could not decode address: ' + toAddress + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: The address version number currently must be 2 or 3. Others aren\'t supported. Check the toAddress.'
            if streamNumber != 1:
                return 'API Error 0012: The stream number must be 1. Others aren\'t supported. Check the toAddress.'
            status, addressVersionNumber, streamNumber, fromRipe = decodeAddress(
                fromAddress)
            if status != 'success':
                shared.printLock.acquire()
                print 'API Error 0007: Could not decode address:', fromAddress, ':', status
                shared.printLock.release()
                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + fromAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + fromAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + fromAddress
                return 'API Error 0007: Could not decode address: ' + fromAddress + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: The address version number currently must be 2 or 3. Others aren\'t supported. Check the fromAddress.'
            if streamNumber != 1:
                return 'API Error 0012: The stream number must be 1. Others aren\'t supported. Check the fromAddress.'
            toAddress = addBMIfNotPresent(toAddress)
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = shared.config.getboolean(
                    fromAddress, 'enabled')
            except:
                return 'API Error 0013: Could not find your fromAddress in the keys.dat file.'
            if not fromAddressEnabled:
                return 'API Error 0014: Your fromAddress is disabled. Cannot send.'

            ackdata = OpenSSL.rand(32)
            
            t = ('', toAddress, toRipe, fromAddress, subject, message, ackdata, int(
                time.time()), 'msgqueued', 1, 1, 'sent', 2)
            helper_sent.insert(t)

            toLabel = ''
            t = (toAddress,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''select label from addressbook where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:
                for row in queryreturn:
                    toLabel, = row
            # apiSignalQueue.put(('displayNewSentMessage',(toAddress,toLabel,fromAddress,subject,message,ackdata)))
            shared.UISignalQueue.put(('displayNewSentMessage', (
                toAddress, toLabel, fromAddress, subject, message, ackdata)))

            shared.workerQueue.put(('sendmessage', toAddress))

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

            status, addressVersionNumber, streamNumber, fromRipe = decodeAddress(
                fromAddress)
            if status != 'success':
                shared.printLock.acquire()
                print 'API Error 0007: Could not decode address:', fromAddress, ':', status
                shared.printLock.release()
                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + fromAddress
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + fromAddress
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + fromAddress
                return 'API Error 0007: Could not decode address: ' + fromAddress + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: the address version number currently must be 2 or 3. Others aren\'t supported. Check the fromAddress.'
            if streamNumber != 1:
                return 'API Error 0012: the stream number must be 1. Others aren\'t supported. Check the fromAddress.'
            fromAddress = addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = shared.config.getboolean(
                    fromAddress, 'enabled')
            except:
                return 'API Error 0013: could not find your fromAddress in the keys.dat file.'
            ackdata = OpenSSL.rand(32)
            toAddress = '[Broadcast subscribers]'
            ripe = ''

            
            t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
            helper_sent.insert(t)

            toLabel = '[Broadcast subscribers]'
            shared.UISignalQueue.put(('displayNewSentMessage', (
                toAddress, toLabel, fromAddress, subject, message, ackdata)))
            shared.workerQueue.put(('sendbroadcast', ''))

            return ackdata.encode('hex')
        elif method == 'getStatus':
            if len(params) != 1:
                return 'API Error 0000: I need one parameter!'
            ackdata, = params
            if len(ackdata) != 64:
                return 'API Error 0015: The length of ackData should be 32 bytes (encoded in hex thus 64 characters).'
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''SELECT status FROM sent where ackdata=?''')
            shared.sqlSubmitQueue.put((ackdata.decode('hex'),))
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn == []:
                return 'notfound'
            for row in queryreturn:
                status, = row
                return status
        elif method == 'addSubscription':
            if len(params) == 0:
                return 'API Error 0000: I need parameters!'
            if len(params) == 1:
                address, = params
                label == ''
            if len(params) == 2:
                address, label = params
                label = label.decode('base64')
                try:
                    unicode(label, 'utf-8')
                except:
                    return 'API Error 0017: Label is not valid UTF-8 data.'
            if len(params) > 2:
                return 'API Error 0000: I need either 1 or 2 parameters!'
            address = addBMIfNotPresent(address)
            status, addressVersionNumber, streamNumber, toRipe = decodeAddress(
                address)
            if status != 'success':
                shared.printLock.acquire()
                print 'API Error 0007: Could not decode address:', address, ':', status
                shared.printLock.release()
                if status == 'checksumfailed':
                    return 'API Error 0008: Checksum failed for address: ' + address
                if status == 'invalidcharacters':
                    return 'API Error 0009: Invalid characters in address: ' + address
                if status == 'versiontoohigh':
                    return 'API Error 0010: Address version number too high (or zero) in address: ' + address
                return 'API Error 0007: Could not decode address: ' + address + ' : ' + status
            if addressVersionNumber < 2 or addressVersionNumber > 3:
                return 'API Error 0011: The address version number currently must be 2 or 3. Others aren\'t supported.'
            if streamNumber != 1:
                return 'API Error 0012: The stream number must be 1. Others aren\'t supported.'
            # First we must check to see if the address is already in the
            # subscriptions list.
            shared.sqlLock.acquire()
            t = (address,)
            shared.sqlSubmitQueue.put(
                '''select * from subscriptions where address=?''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlLock.release()
            if queryreturn != []:
                return 'API Error 0016: You are already subscribed to that address.'
            t = (label, address, True)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''INSERT INTO subscriptions VALUES (?,?,?)''')
            shared.sqlSubmitQueue.put(t)
            queryreturn = shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.reloadBroadcastSendersForWhichImWatching()
            shared.UISignalQueue.put(('rerenderInboxFromLabels', ''))
            shared.UISignalQueue.put(('rerenderSubscriptions', ''))
            return 'Added subscription.'

        elif method == 'deleteSubscription':
            if len(params) != 1:
                return 'API Error 0000: I need 1 parameter!'
            address, = params
            address = addBMIfNotPresent(address)
            t = (address,)
            shared.sqlLock.acquire()
            shared.sqlSubmitQueue.put(
                '''DELETE FROM subscriptions WHERE address=?''')
            shared.sqlSubmitQueue.put(t)
            shared.sqlReturnQueue.get()
            shared.sqlSubmitQueue.put('commit')
            shared.sqlLock.release()
            shared.reloadBroadcastSendersForWhichImWatching()
            shared.UISignalQueue.put(('rerenderInboxFromLabels', ''))
            shared.UISignalQueue.put(('rerenderSubscriptions', ''))
            return 'Deleted subscription if it existed.'
        elif method == 'clientStatus':
            return '{ "networkConnections" : "%s" }' % str(len(shared.connectedHostsList))
        else:
            return 'Invalid Method: %s' % method

# This thread, of which there is only one, runs the API.


class singleAPI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        se = SimpleXMLRPCServer((shared.config.get('bitmessagesettings', 'apiinterface'), shared.config.getint(
            'bitmessagesettings', 'apiport')), MySimpleXMLRPCRequestHandler, True, True)
        se.register_introspection_functions()
        se.serve_forever()

# This is used so that the translateText function can be used when we are in daemon mode and not using any QT functions.
class translateClass:
    def __init__(self, context, text):
        self.context = context
        self.text = text
    def arg(self,argument):
        if '%' in self.text:
            return translateClass(self.context, self.text.replace('%','',1)) # This doesn't actually do anything with the arguments because we don't have a UI in which to display this information anyway.
        else:
            return self.text

def _translate(context, text):
    return translateText(context, text)

def translateText(context, text):
    if not shared.safeConfigGetBoolean('bitmessagesettings', 'daemon'):
        try:
            from PyQt4 import QtCore, QtGui
        except Exception as err:
            print 'PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API. You can download PyQt from http://www.riverbankcomputing.com/software/pyqt/download   or by searching Google for \'PyQt Download\'. If you want to run in daemon mode, see https://bitmessage.org/wiki/Daemon'
            print 'Error message:', err
            os._exit(0)
        return QtGui.QApplication.translate(context, text)
    else:
        if '%' in text:
            return translateClass(context, text.replace('%','',1))
        else:
            return text
            

selfInitiatedConnections = {}
    # This is a list of current connections (the thread pointers at least)
alreadyAttemptedConnectionsList = {
}  # This is a list of nodes to which we have already attempted a connection
ackdataForWhichImWatching = {}
alreadyAttemptedConnectionsListLock = threading.Lock()
eightBytesOfRandomDataUsedToDetectConnectionsToSelf = pack(
    '>Q', random.randrange(1, 18446744073709551615))
neededPubkeys = {}
successfullyDecryptMessageTimings = [
]  # A list of the amounts of time it took to successfully decrypt msg messages
apiAddressGeneratorReturnQueue = Queue.Queue(
)  # The address generator thread uses this queue to get information back to the API thread.
alreadyAttemptedConnectionsListResetTime = int(
    time.time())  # used to clear out the alreadyAttemptedConnectionsList periodically so that we will retry connecting to hosts to which we have already tried to connect.
numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer = {}

if useVeryEasyProofOfWorkForTesting:
    shared.networkDefaultProofOfWorkNonceTrialsPerByte = int(
        shared.networkDefaultProofOfWorkNonceTrialsPerByte / 16)
    shared.networkDefaultPayloadLengthExtraBytes = int(
        shared.networkDefaultPayloadLengthExtraBytes / 7000)

if __name__ == "__main__":
    # is the application already running?  If yes then exit.
    thisapp = singleton.singleinstance()

    signal.signal(signal.SIGINT, helper_generic.signal_handler)
    # signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Check the Major version, the first element in the array
    if sqlite3.sqlite_version_info[0] < 3:
        print 'This program requires sqlite version 3 or higher because 2 and lower cannot store NULL values. I see version:', sqlite3.sqlite_version_info
        os._exit(0)

    helper_startup.loadConfig()

    helper_bootstrap.knownNodes()
    helper_bootstrap.dns()
    
    # Start the address generation thread
    addressGeneratorThread = addressGenerator()
    addressGeneratorThread.daemon = True  # close the main program even if there are threads left
    addressGeneratorThread.start()

    # Start the thread that calculates POWs
    singleWorkerThread = singleWorker()
    singleWorkerThread.daemon = True  # close the main program even if there are threads left
    singleWorkerThread.start()

    # Start the SQL thread
    sqlLookup = sqlThread()
    sqlLookup.daemon = False  # DON'T close the main program even if there are threads left. The closeEvent should command this thread to exit gracefully.
    sqlLookup.start()

    # Start the cleanerThread
    singleCleanerThread = singleCleaner()
    singleCleanerThread.daemon = True  # close the main program even if there are threads left
    singleCleanerThread.start()

    shared.reloadMyAddressHashes()
    shared.reloadBroadcastSendersForWhichImWatching()

    if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
        try:
            apiNotifyPath = shared.config.get(
                'bitmessagesettings', 'apinotifypath')
        except:
            apiNotifyPath = ''
        if apiNotifyPath != '':
            shared.printLock.acquire()
            print 'Trying to call', apiNotifyPath
            shared.printLock.release()
            call([apiNotifyPath, "startingUp"])
        singleAPIThread = singleAPI()
        singleAPIThread.daemon = True  # close the main program even if there are threads left
        singleAPIThread.start()
        # self.singleAPISignalHandlerThread = singleAPISignalHandler()
        # self.singleAPISignalHandlerThread.start()
        # QtCore.QObject.connect(self.singleAPISignalHandlerThread, QtCore.SIGNAL("updateStatusBar(PyQt_PyObject)"), self.updateStatusBar)
        # QtCore.QObject.connect(self.singleAPISignalHandlerThread, QtCore.SIGNAL("passAddressGeneratorObjectThrough(PyQt_PyObject)"), self.connectObjectToAddressGeneratorSignals)
        # QtCore.QObject.connect(self.singleAPISignalHandlerThread,
        # QtCore.SIGNAL("displayNewSentMessage(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"),
        # self.displayNewSentMessage)

    connectToStream(1)

    singleListenerThread = singleListener()
    singleListenerThread.daemon = True  # close the main program even if there are threads left
    singleListenerThread.start()

    if not shared.safeConfigGetBoolean('bitmessagesettings', 'daemon'):
        try:
            from PyQt4 import QtCore, QtGui
        except Exception as err:
            print 'PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API. You can download PyQt from http://www.riverbankcomputing.com/software/pyqt/download   or by searching Google for \'PyQt Download\'. If you want to run in daemon mode, see https://bitmessage.org/wiki/Daemon'
            print 'Error message:', err
            os._exit(0)

        import bitmessageqt
        bitmessageqt.run()
    else:
        shared.printLock.acquire()
        print 'Running as a daemon. You can use Ctrl+C to exit.'
        shared.printLock.release()
        while True:
            time.sleep(20)

# So far, the creation of and management of the Bitmessage protocol and this
# client is a one-man operation. Bitcoin tips are quite appreciated.
# 1H5XaDA6fYENLbknwZyjiYXYPQaFjjLX2u
