#!/usr/bin/python2.7
# Copyright (c) 2012-2016 Jonathan Warren
# Copyright (c) 2012-2018 The Bitmessage developers
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

import ctypes
import getopt
# Used to capture a Ctrl-C keypress so that Bitmessage can shutdown gracefully.
import signal
import socket
import time
from struct import pack

from helper_startup import (
    isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections
)
from singleinstance import singleinstance

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
from network.uploadthread import UploadThread

# Helper Functions
import helper_generic
import helper_threading

def connectToStream(streamNumber):
    state.streamsInWhichIAmParticipating.append(streamNumber)
    selfInitiatedConnections[streamNumber] = {}

    if isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections():
        # Some XP and Vista systems can only have 10 outgoing connections
        # at a time.
        state.maximumNumberOfHalfOpenConnections = 9
    else:
        state.maximumNumberOfHalfOpenConnections = 64
    try:
        # don't overload Tor
        if BMConfigParser().get(
                'bitmessagesettings', 'socksproxytype') != 'none':
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

        daemon = BMConfigParser().safeGetBoolean(
            'bitmessagesettings', 'daemon')

        try:
            opts, args = getopt.getopt(
                sys.argv[1:], "hcdt",
                ["help", "curses", "daemon", "test"])

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
            elif opt in ("-t", "--test"):
                state.testmode = True
                if os.path.isfile(os.path.join(
                        state.appdata, 'unittest.lock')):
                    daemon = True
                state.enableGUI = False  # run without a UI
                # Fallback: in case when no api command was issued
                state.last_api_response = time.time()
                # Apply special settings
                config = BMConfigParser()
                config.set(
                    'bitmessagesettings', 'apienabled', 'true')
                config.set(
                    'bitmessagesettings', 'apiusername', 'username')
                config.set(
                    'bitmessagesettings', 'apipassword', 'password')
                config.set(
                    'bitmessagesettings', 'apinotifypath',
                    os.path.join(app_dir, 'tests', 'apinotify_handler.py')
                )

        if daemon:
            state.enableGUI = False  # run without a UI


        if state.enableGUI and not state.curses and not state.kivy and not depends.check_pyqt():
        # is the application already running?  If yes then exit.
            sys.exit(
                'PyBitmessage requires PyQt unless you want'
                ' to run it as a daemon and interact with it'
                ' using the API. You can download PyQt from '
                'http://www.riverbankcomputing.com/software/pyqt/download'
                ' or by searching Google for \'PyQt Download\'.'
                ' If you want to riverbankcomputingun in daemon mode, see '
                'https://bitmessage.org/wiki/Daemon\n'
                'You can also run PyBitmessage with'
                ' the new curses interface by providing'
                ' \'-c\' as a commandline argument.'
            )
        # is the application already running?  If yes then exit.
        shared.thisapp = singleinstance("", daemon)

        if daemon:
            with shared.printLock:
                print('Running as a daemon. Send TERM signal to end.')
            self.daemonize()

        self.setSignalHandler()

        helper_threading.set_thread_name("PyBitmessage")

        state.dandelion = BMConfigParser().safeGetInt('network', 'dandelion')
        # dandelion requires outbound connections, without them,
        # stem objects will get stuck forever
        if state.dandelion and not BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'sendoutgoingconnections'):
            state.dandelion = 0
        knownnodes.readKnownNodes()
        # Not needed if objproc is disabled
        if state.enableObjProc:

            # Start the address generation thread
            addressGeneratorThread = addressGenerator()
            # close the main program even if there are threads left
            addressGeneratorThread.daemon = True
            addressGeneratorThread.start()
            print("Thread 284 begins.....................................................................")

            # Start the thread that calculates POWs
            singleWorkerThread = singleWorker()
            print("Thread 288 begins.....................................................................")
            # close the main program even if there are threads left
            singleWorkerThread.daemon = True
            singleWorkerThread.start()
            print("Thread 292 begins.....................................................................")

        # Start the SQL thread
        sqlLookup = sqlThread()
        print("Thread 296 begins.....................................................................")
        # DON'T close the main program even if there are threads left.
        # The closeEvent should command this thread to exit gracefully.
        sqlLookup.daemon = False
        sqlLookup.start()
        print("Thread 301 begins.....................................................................")
        Inventory()  # init
        # init, needs to be early because other thread may access it early
        Dandelion()
        print("Thread 305 begins.....................................................................")
        # Enable object processor and SMTP only if objproc enabled
        if state.enableObjProc:
            print("Thread 308 begins.....................................................................")
            # SMTP delivery thread
            if daemon and BMConfigParser().safeGet(
                    "bitmessagesettings", "smtpdeliver", '') != '':
                print("Thread 311 begins.....................................................................")
                from class_smtpDeliver import smtpDeliver
                smtpDeliveryThread = smtpDeliver()
                smtpDeliveryThread.start()

            # SMTP daemon thread
            if daemon and BMConfigParser().safeGetBoolean(
                    "bitmessagesettings", "smtpd"):
                print("Thread 320 begins.....................................................................")
                from class_smtpServer import smtpServer
                smtpServerThread = smtpServer()
                smtpServerThread.start()

            # Start the thread that calculates POWs
            objectProcessorThread = objectProcessor()
            print("Thread 327 begins.....................................................................")
            # DON'T close the main program even the thread remains.
            # This thread checks the shutdown variable after processing
            # each object.
            objectProcessorThread.daemon = False
            objectProcessorThread.start()
            print("Thread 333 begins.....................................................................")
        # Start the cleanerThread
        singleCleanerThread = singleCleaner()
        # close the main program even if there are threads left
        singleCleanerThread.daemon = True
        singleCleanerThread.start()
        print("Thread 339 begins.....................................................................")
        # Not needed if objproc disabled
        if state.enableObjProc:
            print("Thread 344 begins.....................................................................")
            shared.reloadMyAddressHashes()
            print("Thread 345 begins.....................................................................")
            shared.reloadBroadcastSendersForWhichImWatching()
            # API is also objproc dependent
            if BMConfigParser().safeGetBoolean('bitmessagesettings', 'apienabled'):
                import api  # pylint: disable=relative-import
                singleAPIThread = api.singleAPI()
                # close the main program even if there are threads left
                singleAPIThread.daemon = True
                singleAPIThread.start()
                print("Thread 362 begins.....................................................................")
        # start network components if networking is enabled
        if state.enableNetwork:
            print("Thread 365 begins.....................................................................")
            BMConnectionPool()
            asyncoreThread = BMNetworkThread()
            print("Thread 366 begins.....................................................................")
            asyncoreThread.daemon = True
            asyncoreThread.start()
            print("Thread 367 begins.....................................................................")
            for i in range(BMConfigParser().getint("threads", "receive")):
                print("Thread 368 begins.....................................................................")
                receiveQueueThread = ReceiveQueueThread(i)
                receiveQueueThread.daemon = True
                receiveQueueThread.start()
            print("Thread 369 begins.....................................................................")
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
            state.uploadThread = UploadThread()
            state.uploadThread.daemon = True
            state.uploadThread.start()
            print("Thread 387 begins.....................................................................")

            connectToStream(1)
            print("Thread 390 begins.....................................................................")
            if BMConfigParser().safeGetBoolean(
                    'bitmessagesettings', 'upnp'):
                import upnp
                upnpThread = upnp.uPnPThread()
                print("Thread 395 begins.....................................................................")
                upnpThread.start()
            print("Thread 396 begins.....................................................................")
        else:
            print("Thread 398 begins.....................................................................")
            # Populate with hardcoded value (same as connectToStream above)
            state.streamsInWhichIAmParticipating.append(1)
        print("Thread 402 begins.....................................................................")
        if not daemon and state.enableGUI:
            print("Thread 404 begins.....................................................................")
            if state.curses:
                if not depends.check_curses():
                    sys.exit()
                print('Running with curses')
                import bitmessagecurses
                bitmessagecurses.runwrapper()

            elif state.kivy:
                print("Thread 406 begins.....................................................................")
                BMConfigParser().remove_option('bitmessagesettings', 'dontconnect')
                print("Thread 408 begins.....................................................................")
                from bitmessagekivy.mpybit import NavigateApp
                print("Thread 4100 begins.....................................................................")
                NavigateApp().run()
            else:
                print("Thread 417 begins.....................................................................")
                import bitmessageqt
                bitmessageqt.run()
        else:
            BMConfigParser().remove_option('bitmessagesettings', 'dontconnect')

        if daemon:
            while state.shutdown == 0:
                time.sleep(1)
                if (state.testmode and
                        time.time() - state.last_api_response >= 30):
                    self.stop()
        elif not state.enableGUI:
            from tests import core as test_core  # pylint: disable=relative-import
            test_core_result = test_core.run()
            state.enableGUI = True
            self.stop()
            test_core.cleanup()
            sys.exit(
                'Core tests failed!'
                if test_core_result.errors or test_core_result.failures
                else 0
            )

    def daemonize(self):
        grandfatherPid = os.getpid()
        parentPid = None
        try:
            if os.fork():
                # unlock
                shared.thisapp.cleanup()
                # wait until grandchild ready
                while True:
                    time.sleep(1)
                os._exit(0)
        except AttributeError:
            # fork not implemented
            pass
        else:
            parentPid = os.getpid()
            shared.thisapp.lock()  # relock

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
                    time.sleep(1)
                os._exit(0)
        except AttributeError:
            # fork not implemented
            pass
        else:
            shared.thisapp.lock()  # relock
        shared.thisapp.lockPid = None  # indicate we're the final child
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
  -t, --test            dryrun, make testing

All parameters are optional.
'''

    def stop(self):
        with shared.printLock:
            print('Stopping Bitmessage Deamon.')
        shutdown.doCleanShutdown()

    # TODO: nice function but no one is using this
    def getApiAddress(self):
        if not BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'apienabled'):
            return None
        address = BMConfigParser().get('bitmessagesettings', 'apiinterface')
        port = BMConfigParser().getint('bitmessagesettings', 'apiport')
        return {'address': address, 'port': port}


def main():
    mainprogram = Main()
    mainprogram.start()


if __name__ == "__main__":
    main()


# So far, the creation of and management of the Bitmessage protocol and this
# client is a one-man operation. Bitcoin tips are quite appreciated.
# 1H5XaDA6fYENLbknwZyjiYXYPQaFjjLX2u
