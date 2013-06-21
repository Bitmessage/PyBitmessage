import threading
import time
import random
import shared
import socks
import socket
import sys

import bitmessagemain
from class_sendDataThread import *
from class_receiveDataThread import *

# For each stream to which we connect, several outgoingSynSender threads
# will exist and will collectively create 8 connections with peers.

class outgoingSynSender(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def setup(self, streamNumber, selfInitiatedConnections):
        self.streamNumber = streamNumber
        self.selfInitiatedConnections = selfInitiatedConnections

    def run(self):
        time.sleep(1)
        while True:
            while len(self.selfInitiatedConnections[self.streamNumber]) >= 8:  # maximum number of outgoing connections = 8
                time.sleep(10)
            if shared.shutdown:
                break
            random.seed()
            shared.knownNodesLock.acquire()
            HOST, = random.sample(shared.knownNodes[self.streamNumber], 1)
            shared.knownNodesLock.release()
            bitmessagemain.alreadyAttemptedConnectionsListLock.acquire()
            while HOST in bitmessagemain.alreadyAttemptedConnectionsList or HOST in shared.connectedHostsList:
                bitmessagemain.alreadyAttemptedConnectionsListLock.release()
                # print 'choosing new sample'
                random.seed()
                shared.knownNodesLock.acquire()
                HOST, = random.sample(shared.knownNodes[self.streamNumber], 1)
                shared.knownNodesLock.release()
                time.sleep(1)
                # Clear out the bitmessagemain.alreadyAttemptedConnectionsList every half
                # hour so that this program will again attempt a connection
                # to any nodes, even ones it has already tried.
                if (time.time() - bitmessagemain.alreadyAttemptedConnectionsListResetTime) > 1800:
                    bitmessagemain.alreadyAttemptedConnectionsList.clear()
                    bitmessagemain.alreadyAttemptedConnectionsListResetTime = int(
                        time.time())
                bitmessagemain.alreadyAttemptedConnectionsListLock.acquire()
            bitmessagemain.alreadyAttemptedConnectionsList[HOST] = 0
            bitmessagemain.alreadyAttemptedConnectionsListLock.release()
            PORT, timeNodeLastSeen = shared.knownNodes[
                self.streamNumber][HOST]
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            # This option apparently avoids the TIME_WAIT state so that we
            # can rebind faster
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(20)
            if shared.config.get('bitmessagesettings', 'socksproxytype') == 'none' and bitmessagemain.verbose >= 2:
                shared.printLock.acquire()
                print 'Trying an outgoing connection to', HOST, ':', PORT
                shared.printLock.release()
                # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif shared.config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS4a':
                if bitmessagemain.verbose >= 2:
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
                if bitmessagemain.verbose >= 2:
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
                         objectsOfWhichThisRemoteNodeIsAlreadyAware, self.selfInitiatedConnections)
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
                if bitmessagemain.verbose >= 2:
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
                    if bitmessagemain.verbose >= 1:
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
                    'An exception has occurred in the outgoingSynSender thread that was not caught by other exception types: ')
                import traceback
                traceback.print_exc()
            time.sleep(0.1)
