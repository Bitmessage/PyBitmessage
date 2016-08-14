import threading
import time
import random
import shared
import select
import socks
import socket
import sys
import tr

from class_sendDataThread import *
from class_receiveDataThread import *
from helper_threading import *

# For each stream to which we connect, several outgoingSynSender threads
# will exist and will collectively create 8 connections with peers.

class outgoingSynSender(threading.Thread, StoppableThread):

    def __init__(self):
        threading.Thread.__init__(self, name="outgoingSynSender")
        self.initStop()

    def setup(self, streamNumber, selfInitiatedConnections):
        self.streamNumber = streamNumber
        self.selfInitiatedConnections = selfInitiatedConnections

    def _getPeer(self):
        # If the user has specified a trusted peer then we'll only
        # ever connect to that. Otherwise we'll pick a random one from
        # the known nodes
        if shared.trustedPeer:
            shared.knownNodesLock.acquire()
            peer = shared.trustedPeer
            shared.knownNodes[self.streamNumber][peer] = time.time()
            shared.knownNodesLock.release()
        else:
            while not shared.shutdown:
                shared.knownNodesLock.acquire()
                try:
                    peer, = random.sample(shared.knownNodes[self.streamNumber], 1)
                except ValueError: # no known nodes
                    shared.knownNodesLock.release()
                    time.sleep(1)
                    continue
                priority = (183600 - (time.time() - shared.knownNodes[self.streamNumber][peer])) / 183600 # 2 days and 3 hours
                shared.knownNodesLock.release()
                if shared.config.get('bitmessagesettings', 'socksproxytype') != 'none':
                    if peer.host.find(".onion") == -1:
                        priority /= 10 # hidden services have 10x priority over plain net
                elif peer.host.find(".onion") != -1: # onion address and so proxy
                    continue
                if priority <= 0.001: # everyone has at least this much priority
                    priority = 0.001
                if (random.random() <=  priority):
                    break
                time.sleep(0.01) # prevent CPU hogging if something is broken
        try:
            return peer
        except NameError:
            return shared.Peer('127.0.0.1', 8444)
        
    def stopThread(self):
        super(outgoingSynSender, self).stopThread()
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass

    def run(self):
        while shared.safeConfigGetBoolean('bitmessagesettings', 'dontconnect') and not self._stopped:
            self.stop.wait(2)
        while shared.safeConfigGetBoolean('bitmessagesettings', 'sendoutgoingconnections') and not self._stopped:
            self.name = "outgoingSynSender"
            maximumConnections = 1 if shared.trustedPeer else 8 # maximum number of outgoing connections = 8
            while len(self.selfInitiatedConnections[self.streamNumber]) >= maximumConnections:
                self.stop.wait(10)
            if shared.shutdown:
                break
            random.seed()
            peer = self._getPeer()
            shared.alreadyAttemptedConnectionsListLock.acquire()
            while peer in shared.alreadyAttemptedConnectionsList or peer.host in shared.connectedHostsList:
                shared.alreadyAttemptedConnectionsListLock.release()
                # print 'choosing new sample'
                random.seed()
                peer = self._getPeer()
                self.stop.wait(1)
                if shared.shutdown:
                    break
                # Clear out the shared.alreadyAttemptedConnectionsList every half
                # hour so that this program will again attempt a connection
                # to any nodes, even ones it has already tried.
                if (time.time() - shared.alreadyAttemptedConnectionsListResetTime) > 1800:
                    shared.alreadyAttemptedConnectionsList.clear()
                    shared.alreadyAttemptedConnectionsListResetTime = int(
                        time.time())
                shared.alreadyAttemptedConnectionsListLock.acquire()
            shared.alreadyAttemptedConnectionsList[peer] = 0
            try:
                shared.alreadyAttemptedConnectionsListLock.release()
            except threading.ThreadError as e:
                pass
            if shared.shutdown:
                break
            self.name = "outgoingSynSender-" + peer.host.replace(":", ".") # log parser field separator
            if peer.host.find(':') == -1:
                address_family = socket.AF_INET
            else:
                address_family = socket.AF_INET6
            try:
                self.sock = socks.socksocket(address_family, socket.SOCK_STREAM)
            except:
                """
                The line can fail on Windows systems which aren't
                64-bit compatiable:
                      File "C:\Python27\lib\socket.py", line 187, in __init__
                        _sock = _realsocket(family, type, proto)
                      error: [Errno 10047] An address incompatible with the requested protocol was used
                      
                So let us remove the offending address from our knownNodes file.
                """
                shared.knownNodesLock.acquire()
                try:
                    del shared.knownNodes[self.streamNumber][peer]
                except:
                    pass
                shared.knownNodesLock.release()
                logger.debug('deleting ' + str(peer) + ' from shared.knownNodes because it caused a socks.socksocket exception. We must not be 64-bit compatible.')
                continue
            # This option apparently avoids the TIME_WAIT state so that we
            # can rebind faster
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.settimeout(20)
            if shared.config.get('bitmessagesettings', 'socksproxytype') == 'none' and shared.verbose >= 2:
                logger.debug('Trying an outgoing connection to ' + str(peer))

                # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif shared.config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS4a':
                if shared.verbose >= 2:
                    logger.debug ('(Using SOCKS4a) Trying an outgoing connection to ' + str(peer))

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
                    self.sock.setproxy(
                        proxytype, sockshostname, socksport, rdns, socksusername, sockspassword)
                else:
                    self.sock.setproxy(
                        proxytype, sockshostname, socksport, rdns)
            elif shared.config.get('bitmessagesettings', 'socksproxytype') == 'SOCKS5':
                if shared.verbose >= 2:
                    logger.debug ('(Using SOCKS5) Trying an outgoing connection to ' + str(peer))

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
                    self.sock.setproxy(
                        proxytype, sockshostname, socksport, rdns, socksusername, sockspassword)
                else:
                    self.sock.setproxy(
                        proxytype, sockshostname, socksport, rdns)

            try:
                self.sock.connect((peer.host, peer.port))
                someObjectsOfWhichThisRemoteNodeIsAlreadyAware = {} # This is not necessairly a complete list; we clear it from time to time to save memory.
                sendDataThreadQueue = Queue.Queue() # Used to submit information to the send data thread for this connection. 

                sd = sendDataThread(sendDataThreadQueue)
                sd.setup(self.sock, peer.host, peer.port, self.streamNumber,
                         someObjectsOfWhichThisRemoteNodeIsAlreadyAware)
                sd.start()

                rd = receiveDataThread()
                rd.daemon = True  # close the main program even if there are threads left
                rd.setup(self.sock, 
                         peer.host, 
                         peer.port, 
                         self.streamNumber,
                         someObjectsOfWhichThisRemoteNodeIsAlreadyAware, 
                         self.selfInitiatedConnections, 
                         sendDataThreadQueue,
                         sd.objectHashHolderInstance)
                rd.start()

                sd.sendVersionMessage()

                logger.debug(str(self) + ' connected to ' + str(peer) + ' during an outgoing attempt.')
            except socks.GeneralProxyError as err:
                if shared.verbose >= 2:
                    logger.debug('Could NOT connect to ' + str(peer) + ' during outgoing attempt. ' + str(err))

                deletedPeer = None
                with shared.knownNodesLock:
                    """
                    It is remotely possible that peer is no longer in shared.knownNodes.
                    This could happen if two outgoingSynSender threads both try to 
                    connect to the same peer, both fail, and then both try to remove
                    it from shared.knownNodes. This is unlikely because of the
                    alreadyAttemptedConnectionsList but because we clear that list once
                    every half hour, it can happen.
                    """
                    if peer in shared.knownNodes[self.streamNumber]:
                        timeLastSeen = shared.knownNodes[self.streamNumber][peer]
                        if (int(time.time()) - timeLastSeen) > 172800 and len(shared.knownNodes[self.streamNumber]) > 1000:  # for nodes older than 48 hours old if we have more than 1000 hosts in our list, delete from the shared.knownNodes data-structure.
                            del shared.knownNodes[self.streamNumber][peer]
                            deletedPeer = peer
                if deletedPeer:
                    str ('deleting ' + str(peer) + ' from shared.knownNodes because it is more than 48 hours old and we could not connect to it.')

            except socks.Socks5AuthError as err:
                shared.UISignalQueue.put((
                    'updateStatusBar', tr._translate(
                    "MainWindow", "SOCKS5 Authentication problem: %1").arg(str(err))))
            except socks.Socks5Error as err:
                if err[0] in [3, 4, 5, 6]:
                    # this is a more bening "error": host unreachable, network unreachable, connection refused, TTL expired
                    logger.debug('SOCKS5 error. ' + str(err))
                else:
                    logger.error('SOCKS5 error. ' + str(err))
            except socks.Socks4Error as err:
                logger.error('Socks4Error: ' + str(err))
            except socket.error as err:
                if shared.config.get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS':
                    logger.error('Bitmessage MIGHT be having trouble connecting to the SOCKS server. ' + str(err))
                else:
                    if shared.verbose >= 1:
                        logger.debug('Could NOT connect to ' + str(peer) + 'during outgoing attempt. ' + str(err))

                deletedPeer = None
                with shared.knownNodesLock:
                    """
                    It is remotely possible that peer is no longer in shared.knownNodes.
                    This could happen if two outgoingSynSender threads both try to 
                    connect to the same peer, both fail, and then both try to remove
                    it from shared.knownNodes. This is unlikely because of the
                    alreadyAttemptedConnectionsList but because we clear that list once
                    every half hour, it can happen.
                    """
                    if peer in shared.knownNodes[self.streamNumber]:
                        timeLastSeen = shared.knownNodes[self.streamNumber][peer]
                        if (int(time.time()) - timeLastSeen) > 172800 and len(shared.knownNodes[self.streamNumber]) > 1000:  # for nodes older than 48 hours old if we have more than 1000 hosts in our list, delete from the shared.knownNodes data-structure.
                            del shared.knownNodes[self.streamNumber][peer]
                            deletedPeer = peer
                if deletedPeer:
                    logger.debug('deleting ' + str(peer) + ' from shared.knownNodes because it is more than 48 hours old and we could not connect to it.')

            except Exception as err:
                import traceback
                logger.exception('An exception has occurred in the outgoingSynSender thread that was not caught by other exception types:')
            self.stop.wait(0.1)
