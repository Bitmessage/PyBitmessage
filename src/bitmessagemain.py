#!/usr/bin/python2.7
# Copyright (c) 2012-2016 Jonathan Warren
# Copyright (c) 2012-2016 The Bitmessage developers
# Distributed under the MIT/X11 software license. See the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Right now, PyBitmessage only support connecting to stream 1. It doesn't
# yet contain logic to expand into further streams.

# The software version variable is now held in shared.py

import os
import sys

app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)
sys.path.insert(0, app_dir)

import depends
depends.check_dependencies()

import signal  # Used to capture a Ctrl-C keypress so that Bitmessage can shutdown gracefully.
# The next 3 are used for the API
from singleinstance import singleinstance
import errno
import socket
import ctypes
from struct import pack
from subprocess import call
from time import sleep
from random import randint
import getopt

from api import MySimpleXMLRPCRequestHandler, StoppableXMLRPCServer
from helper_startup import isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections

import defaults
import shared
import knownnodes
import state
import shutdown
import threading

# Classes
from class_sqlThread import sqlThread
from class_singleCleaner import singleCleaner
from class_objectProcessor import objectProcessor
from class_singleWorker import singleWorker
from class_addressGenerator import addressGenerator
from class_smtpDeliver import smtpDeliver
from class_smtpServer import smtpServer
from bmconfigparser import BMConfigParser

from inventory import Inventory

from network.connectionpool import BMConnectionPool
from network.dandelion import Dandelion
from network.networkthread import BMNetworkThread
from network.receivequeuethread import ReceiveQueueThread
from network.announcethread import AnnounceThread
from network.invthread import InvThread
from network.addrthread import AddrThread
from network.downloadthread import DownloadThread

# Helper Functions
import helper_bootstrap
import helper_generic
import helper_threading


def connectToStream(streamNumber):
    state.streamsInWhichIAmParticipating.append(streamNumber)
    selfInitiatedConnections[streamNumber] = {}

    if isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections():
        # Some XP and Vista systems can only have 10 outgoing connections at a time.
        state.maximumNumberOfHalfOpenConnections = 9
    else:
        state.maximumNumberOfHalfOpenConnections = 64
    try:
        # don't overload Tor
        if BMConfigParser().get('bitmessagesettings', 'socksproxytype') != 'none':
            state.maximumNumberOfHalfOpenConnections = 4
    except:
        pass
    
    with knownnodes.knownNodesLock:
        if streamNumber not in knownnodes.knownNodes:
            knownnodes.knownNodes[streamNumber] = {}
        if streamNumber*2 not in knownnodes.knownNodes:
            knownnodes.knownNodes[streamNumber*2] = {}
        if streamNumber*2+1 not in knownnodes.knownNodes:
            knownnodes.knownNodes[streamNumber*2+1] = {}

    BMConnectionPool().connectToStream(streamNumber)

def _fixSocket():
    if sys.platform.startswith('linux'):
        socket.SO_BINDTODEVICE = 25

    if not sys.platform.startswith('win'):
        return

    # Python 2 on Windows doesn't define a wrapper for
    # socket.inet_ntop but we can make one ourselves using ctypes
    if not hasattr(socket, 'inet_ntop'):
        addressToString = ctypes.windll.ws2_32.WSAAddressToStringA
        def inet_ntop(family, host):
            if family == socket.AF_INET:
                if len(host) != 4:
                    raise ValueError("invalid IPv4 host")
                host = pack("hH4s8s", socket.AF_INET, 0, host, "\0" * 8)
            elif family == socket.AF_INET6:
                if len(host) != 16:
                    raise ValueError("invalid IPv6 host")
                host = pack("hHL16sL", socket.AF_INET6, 0, 0, host, 0)
            else:
                raise ValueError("invalid address family")
            buf = "\0" * 64
            lengthBuf = pack("I", len(buf))
            addressToString(host, len(host), None, buf, lengthBuf)
            return buf[0:buf.index("\0")]
        socket.inet_ntop = inet_ntop

    # Same for inet_pton
    if not hasattr(socket, 'inet_pton'):
        stringToAddress = ctypes.windll.ws2_32.WSAStringToAddressA
        def inet_pton(family, host):
            buf = "\0" * 28
            lengthBuf = pack("I", len(buf))
            if stringToAddress(str(host),
                               int(family),
                               None,
                               buf,
                               lengthBuf) != 0:
                raise socket.error("illegal IP address passed to inet_pton")
            if family == socket.AF_INET:
                return buf[4:8]
            elif family == socket.AF_INET6:
                return buf[8:24]
            else:
                raise ValueError("invalid address family")
        socket.inet_pton = inet_pton

    # These sockopts are needed on for IPv6 support
    if not hasattr(socket, 'IPPROTO_IPV6'):
        socket.IPPROTO_IPV6 = 41
    if not hasattr(socket, 'IPV6_V6ONLY'):
        socket.IPV6_V6ONLY = 27

# This thread, of which there is only one, runs the API.
class singleAPI(threading.Thread, helper_threading.StoppableThread):
    def __init__(self):
        threading.Thread.__init__(self, name="singleAPI")
        self.initStop()
        
    def stopThread(self):
        super(singleAPI, self).stopThread()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((BMConfigParser().get('bitmessagesettings', 'apiinterface'), BMConfigParser().getint(
                'bitmessagesettings', 'apiport')))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except:
            pass

    def run(self):
        port = BMConfigParser().getint('bitmessagesettings', 'apiport')
        try:
            from errno import WSAEADDRINUSE
        except (ImportError, AttributeError):
            errno.WSAEADDRINUSE = errno.EADDRINUSE
        for attempt in range(50):
            try:
                if attempt > 0:
                    port = randint(32767, 65535)
                se = StoppableXMLRPCServer((BMConfigParser().get('bitmessagesettings', 'apiinterface'), port),
                    MySimpleXMLRPCRequestHandler, True, True)
            except socket.error as e:
                if e.errno in (errno.EADDRINUSE, errno.WSAEADDRINUSE):
                    continue
            else:
                if attempt > 0:
                    BMConfigParser().set("bitmessagesettings", "apiport", str(port))
                    BMConfigParser().save()
                break
        se.register_introspection_functions()
        se.serve_forever()

# This is a list of current connections (the thread pointers at least)
selfInitiatedConnections = {}

if shared.useVeryEasyProofOfWorkForTesting:
    defaults.networkDefaultProofOfWorkNonceTrialsPerByte = int(
        defaults.networkDefaultProofOfWorkNonceTrialsPerByte / 100)
    defaults.networkDefaultPayloadLengthExtraBytes = int(
        defaults.networkDefaultPayloadLengthExtraBytes / 100)

class Main:
    def start(self):
        _fixSocket()

        daemon = BMConfigParser().safeGetBoolean('bitmessagesettings', 'daemon')

        try:
            opts, args = getopt.getopt(sys.argv[1:], "hcd",
                ["help", "curses", "daemon"])

        except getopt.GetoptError:
            self.usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
                sys.exit()
            elif opt in ("-d", "--daemon"):
                daemon = True
            elif opt in ("-c", "--curses"):
                state.curses = True

        # is the application already running?  If yes then exit.
        shared.thisapp = singleinstance("", daemon)

        if daemon:
            with shared.printLock:
                print('Running as a daemon. Send TERM signal to end.')
            self.daemonize()

        self.setSignalHandler()

        helper_threading.set_thread_name("PyBitmessage")

        state.dandelion = BMConfigParser().safeGetInt('network', 'dandelion')
        # dandelion requires outbound connections, without them, stem objects will get stuck forever
        if state.dandelion and not BMConfigParser().safeGetBoolean('bitmessagesettings', 'sendoutgoingconnections'):
            state.dandelion = 0

        helper_bootstrap.knownNodes()
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

        Inventory() # init
        Dandelion() # init, needs to be early because other thread may access it early

        # SMTP delivery thread
        if daemon and BMConfigParser().safeGet("bitmessagesettings", "smtpdeliver", '') != '':
            smtpDeliveryThread = smtpDeliver()
            smtpDeliveryThread.start()

        # SMTP daemon thread
        if daemon and BMConfigParser().safeGetBoolean("bitmessagesettings", "smtpd"):
            smtpServerThread = smtpServer()
            smtpServerThread.start()

        # Start the thread that calculates POWs
        objectProcessorThread = objectProcessor()
        objectProcessorThread.daemon = False  # DON'T close the main program even the thread remains. This thread checks the shutdown variable after processing each object.
        objectProcessorThread.start()

        # Start the cleanerThread
        singleCleanerThread = singleCleaner()
        singleCleanerThread.daemon = True  # close the main program even if there are threads left
        singleCleanerThread.start()

        shared.reloadMyAddressHashes()
        shared.reloadBroadcastSendersForWhichImWatching()

        if BMConfigParser().safeGetBoolean('bitmessagesettings', 'apienabled'):
            try:
                apiNotifyPath = BMConfigParser().get(
                    'bitmessagesettings', 'apinotifypath')
            except:
                apiNotifyPath = ''
            if apiNotifyPath != '':
                with shared.printLock:
                    print('Trying to call', apiNotifyPath)

                call([apiNotifyPath, "startingUp"])
            singleAPIThread = singleAPI()
            singleAPIThread.daemon = True  # close the main program even if there are threads left
            singleAPIThread.start()

        BMConnectionPool()
        asyncoreThread = BMNetworkThread()
        asyncoreThread.daemon = True
        asyncoreThread.start()
        for i in range(BMConfigParser().getint("threads", "receive")):
            receiveQueueThread = ReceiveQueueThread(i)
            receiveQueueThread.daemon = True
            receiveQueueThread.start()
        announceThread = AnnounceThread()
        announceThread.daemon = True
        announceThread.start()
        state.invThread = InvThread()
        state.invThread.daemon = True
        state.invThread.start()
        state.addrThread = AddrThread()
        state.addrThread.daemon = True
        state.addrThread.start()
        state.downloadThread = DownloadThread()
        state.downloadThread.daemon = True
        state.downloadThread.start()

        connectToStream(1)

        if BMConfigParser().safeGetBoolean('bitmessagesettings','upnp'):
            import upnp
            upnpThread = upnp.uPnPThread()
            upnpThread.start()

        if daemon == False and BMConfigParser().safeGetBoolean('bitmessagesettings', 'daemon') == False:
            if state.curses == False:
                if not depends.check_pyqt():
                    print('PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API. You can download PyQt from http://www.riverbankcomputing.com/software/pyqt/download   or by searching Google for \'PyQt Download\'. If you want to run in daemon mode, see https://bitmessage.org/wiki/Daemon')
                    print('You can also run PyBitmessage with the new curses interface by providing \'-c\' as a commandline argument.')
                    sys.exit()

                import bitmessageqt
                bitmessageqt.run()
            else:
                if True:
#                if depends.check_curses():
                    print('Running with curses')
                    import bitmessagecurses
                    bitmessagecurses.runwrapper()
        else:
            BMConfigParser().remove_option('bitmessagesettings', 'dontconnect')

        if daemon:
            while state.shutdown == 0:
                sleep(1)

    def daemonize(self):
        grandfatherPid = os.getpid()
        parentPid = None
        try:
            if os.fork():
                # unlock
                shared.thisapp.cleanup()
                # wait until grandchild ready
                while True:
                    sleep(1)
                os._exit(0)
        except AttributeError:
            # fork not implemented
            pass
        else:
            parentPid = os.getpid()
            shared.thisapp.lock() # relock
        os.umask(0)
        try:
            os.setsid()
        except AttributeError:
            # setsid not implemented
            pass
        try:
            if os.fork():
                # unlock
                shared.thisapp.cleanup()
                # wait until child ready
                while True:
                    sleep(1)
                os._exit(0)
        except AttributeError:
            # fork not implemented
            pass
        else:
            shared.thisapp.lock() # relock
        shared.thisapp.lockPid = None # indicate we're the final child
        sys.stdout.flush()
        sys.stderr.flush()
        if not sys.platform.startswith('win'):
            si = file(os.devnull, 'r')
            so = file(os.devnull, 'a+')
            se = file(os.devnull, 'a+', 0)
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
        if parentPid:
            # signal ready
            os.kill(parentPid, signal.SIGTERM)
            os.kill(grandfatherPid, signal.SIGTERM)

    def setSignalHandler(self):
        signal.signal(signal.SIGINT, helper_generic.signal_handler)
        signal.signal(signal.SIGTERM, helper_generic.signal_handler)
        # signal.signal(signal.SIGINT, signal.SIG_DFL)

    def usage(self):
        print 'Usage: ' + sys.argv[0] + ' [OPTIONS]'
        print '''
Options:
  -h, --help            show this help message and exit
  -c, --curses          use curses (text mode) interface
  -d, --daemon          run in daemon (background) mode

All parameters are optional.
'''

    def stop(self):
        with shared.printLock:
            print('Stopping Bitmessage Deamon.')
        shutdown.doCleanShutdown()


    #TODO: nice function but no one is using this 
    def getApiAddress(self):
        if not BMConfigParser().safeGetBoolean('bitmessagesettings', 'apienabled'):
            return None
        address = BMConfigParser().get('bitmessagesettings', 'apiinterface')
        port = BMConfigParser().getint('bitmessagesettings', 'apiport')
        return {'address':address,'port':port}


def main():
    mainprogram = Main()
    mainprogram.start()

if __name__ == "__main__":
    main()


# So far, the creation of and management of the Bitmessage protocol and this
# client is a one-man operation. Bitcoin tips are quite appreciated.
# 1H5XaDA6fYENLbknwZyjiYXYPQaFjjLX2u
