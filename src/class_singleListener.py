import threading
import shared
import socket
from bmconfigparser import BMConfigParser
from class_sendDataThread import *
from class_receiveDataThread import *
import helper_bootstrap
from helper_threading import *
import protocol
import errno
import re

import state

# Only one singleListener thread will ever exist. It creates the
# receiveDataThread and sendDataThread for each incoming connection. Note
# that it cannot set the stream number because it is not known yet- the
# other node will have to tell us its stream number in a version message.
# If we don't care about their stream, we will close the connection
# (within the recversion function of the recieveData thread)


class singleListener(threading.Thread, StoppableThread):

    def __init__(self):
        threading.Thread.__init__(self, name="singleListener")
        self.initStop()

    def setup(self, selfInitiatedConnections):
        self.selfInitiatedConnections = selfInitiatedConnections

    def _createListenSocket(self, family):
        HOST = ''  # Symbolic name meaning all available interfaces
        # If not sockslisten, but onionhostname defined, only listen on localhost
        if not BMConfigParser().safeGetBoolean('bitmessagesettings', 'sockslisten') and ".onion" in BMConfigParser().get('bitmessagesettings', 'onionhostname'):
            if family == socket.AF_INET6 and "." in BMConfigParser().get('bitmessagesettings', 'onionbindip'):
                raise socket.error(errno.EINVAL, "Invalid mix of IPv4 and IPv6")
            elif family == socket.AF_INET and ":" in BMConfigParser().get('bitmessagesettings', 'onionbindip'):
                raise socket.error(errno.EINVAL, "Invalid mix of IPv4 and IPv6")
            HOST = BMConfigParser().get('bitmessagesettings', 'onionbindip')
        PORT = BMConfigParser().getint('bitmessagesettings', 'port')
        sock = socket.socket(family, socket.SOCK_STREAM)
        if family == socket.AF_INET6:
            # Make sure we can accept both IPv4 and IPv6 connections.
            # This is the default on everything apart from Windows
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        # This option apparently avoids the TIME_WAIT state so that we can
        # rebind faster
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(2)
        return sock
        
    def stopThread(self):
        super(singleListener, self).stopThread()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for ip in ('127.0.0.1', BMConfigParser().get('bitmessagesettings', 'onionbindip')):
            try:
                s.connect((ip, BMConfigParser().getint('bitmessagesettings', 'port')))
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                break
            except:
                pass

    def run(self):
        # If there is a trusted peer then we don't want to accept
        # incoming connections so we'll just abandon the thread
        if state.trustedPeer:
            return

        while BMConfigParser().safeGetBoolean('bitmessagesettings', 'dontconnect') and state.shutdown == 0:
            self.stop.wait(1)
        helper_bootstrap.dns()
        # We typically don't want to accept incoming connections if the user is using a
        # SOCKS proxy, unless they have configured otherwise. If they eventually select
        # proxy 'none' or configure SOCKS listening then this will start listening for
        # connections. But if on SOCKS and have an onionhostname, listen
        # (socket is then only opened for localhost)
        while BMConfigParser().get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and \
            (not BMConfigParser().getboolean('bitmessagesettings', 'sockslisten') and \
            ".onion" not in BMConfigParser().get('bitmessagesettings', 'onionhostname')) and \
            state.shutdown == 0:
            self.stop.wait(5)

        logger.info('Listening for incoming connections.')

        # First try listening on an IPv6 socket. This should also be
        # able to accept connections on IPv4. If that's not available
        # we'll fall back to IPv4-only.
        try:
            sock = self._createListenSocket(socket.AF_INET6)
        except socket.error as e:
            if (isinstance(e.args, tuple) and
                e.args[0] in (errno.EAFNOSUPPORT,
                              errno.EPFNOSUPPORT,
                              errno.EADDRNOTAVAIL,
                              errno.ENOPROTOOPT,
                              errno.EINVAL)):
                sock = self._createListenSocket(socket.AF_INET)
            else:
                raise

        # regexp to match an IPv4-mapped IPv6 address
        mappedAddressRegexp = re.compile(r'^::ffff:([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)$')

        while state.shutdown == 0:
            # We typically don't want to accept incoming connections if the user is using a
            # SOCKS proxy, unless they have configured otherwise. If they eventually select
            # proxy 'none' or configure SOCKS listening then this will start listening for
            # connections.
            while BMConfigParser().get('bitmessagesettings', 'socksproxytype')[0:5] == 'SOCKS' and not BMConfigParser().getboolean('bitmessagesettings', 'sockslisten') and ".onion" not in BMConfigParser().get('bitmessagesettings', 'onionhostname') and state.shutdown == 0:
                self.stop.wait(10)
            while len(shared.connectedHostsList) > \
                BMConfigParser().safeGetInt("bitmessagesettings", "maxtotalconnections", 200) + \
                BMConfigParser().safeGetInt("bitmessagesettings", "maxbootstrapconnections", 20) \
                and state.shutdown == 0:
                logger.info('We are connected to too many people. Not accepting further incoming connections for ten seconds.')

                self.stop.wait(10)

            while state.shutdown == 0:
                try:
                    socketObject, sockaddr = sock.accept()
                except socket.error as e:
                    if isinstance(e.args, tuple) and \
                        e.args[0] in (errno.EINTR,):
                        continue
                    time.wait(1)
                    continue

                (HOST, PORT) = sockaddr[0:2]

                # If the address is an IPv4-mapped IPv6 address then
                # convert it to just the IPv4 representation
                md = mappedAddressRegexp.match(HOST)
                if md != None:
                    HOST = md.group(1)

                # The following code will, unfortunately, block an
                # incoming connection if someone else on the same LAN
                # is already connected because the two computers will
                # share the same external IP. This is here to prevent
                # connection flooding.
                # permit repeated connections from Tor
                if HOST in shared.connectedHostsList and \
                    (".onion" not in BMConfigParser().get('bitmessagesettings', 'onionhostname') or not protocol.checkSocksIP(HOST)):
                    socketObject.close()
                    logger.info('We are already connected to ' + str(HOST) + '. Ignoring connection.')
                else:
                    break

            sendDataThreadQueue = Queue.Queue() # Used to submit information to the send data thread for this connection.
            socketObject.settimeout(20)

            sd = sendDataThread(sendDataThreadQueue)
            sd.setup(
                socketObject, HOST, PORT, -1)
            sd.start()

            rd = receiveDataThread()
            rd.daemon = True  # close the main program even if there are threads left
            rd.setup(
                socketObject, HOST, PORT, -1, self.selfInitiatedConnections, sendDataThreadQueue, sd.objectHashHolderInstance)
            rd.start()

            logger.info('connected to ' + HOST + ' during INCOMING request.')

