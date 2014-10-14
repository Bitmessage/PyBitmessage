#!/usr/bin/env python2.7
# Copyright (c) 2012 Jonathan Warren
# Copyright (c) 2012 The Bitmessage developers
# Distributed under the MIT/X11 software license. See the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Right now, PyBitmessage only support connecting to stream 1. It doesn't
# yet contain logic to expand into further streams.

# The software version variable is now held in shared.py


import sys
#Version check
#Older versions of Python don't support the print function while Python 3 doesn't
#like the print statement, so we use sys.stdout for the version check. After this
#check we can then use the print function in the remainder of this file. Currently
#in order to use logging, a lot of unnecessary code needs to be executed which could
#potentially render this version check useless. So logging won't be used here until
#there is a more efficient way to configure logging
if sys.hexversion >= 0x3000000:
    msg = "PyBitmessage does not support Python 3. Python 2.7.3 or later is required. Your version: %s" % sys.version
    #logger.critical(msg)
    sys.stdout.write(msg)
    sys.exit(0)
if sys.hexversion < 0x20703F0:
    msg = "You should use Python 2.7.3 or greater (but not Python 3). Your version: %s" % sys.version
    #logger.critical(msg)
    sys.stdout.write(msg)
    sys.exit(0)

import signal  # Used to capture a Ctrl-C keypress so that Bitmessage can shutdown gracefully.
# The next 3 are used for the API
import singleton
import os
import socket
import ctypes
from struct import pack

from SimpleXMLRPCServer import SimpleXMLRPCServer
from api import MySimpleXMLRPCRequestHandler
from helper_startup import isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections

import shared
from helper_sql import sqlQuery
import threading

# Classes
#from helper_sql import *
#from class_sqlThread import *
from class_sqlThread import sqlThread
from class_singleCleaner import singleCleaner
#from class_singleWorker import *
from class_objectProcessor import objectProcessor
from class_outgoingSynSender import outgoingSynSender
from class_singleListener import singleListener
from class_singleWorker import singleWorker
#from class_addressGenerator import *
from class_addressGenerator import addressGenerator
from debug import logger

# Helper Functions
import helper_bootstrap
import helper_generic

from subprocess import call
import time
    

def connectToStream(streamNumber):
    shared.streamsInWhichIAmParticipating[streamNumber] = 'no data'
    selfInitiatedConnections[streamNumber] = {}
    shared.inventorySets[streamNumber] = set()
    queryData = sqlQuery('''SELECT hash FROM inventory WHERE streamnumber=?''', streamNumber)
    for row in queryData:
        shared.inventorySets[streamNumber].add(row[0])

    
    if isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections():
        # Some XP and Vista systems can only have 10 outgoing connections at a time.
        maximumNumberOfHalfOpenConnections = 9
    else:
        maximumNumberOfHalfOpenConnections = 64
    for i in range(maximumNumberOfHalfOpenConnections):
        a = outgoingSynSender()
        a.setup(streamNumber, selfInitiatedConnections)
        a.start()

def _fixWinsock():
    if not ('win32' in sys.platform) and not ('win64' in sys.platform):
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
class singleAPI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        se = SimpleXMLRPCServer((shared.config.get('bitmessagesettings', 'apiinterface'), shared.config.getint(
            'bitmessagesettings', 'apiport')), MySimpleXMLRPCRequestHandler, True, True)
        se.register_introspection_functions()
        se.serve_forever()

# This is a list of current connections (the thread pointers at least)
selfInitiatedConnections = {}

if shared.useVeryEasyProofOfWorkForTesting:
    shared.networkDefaultProofOfWorkNonceTrialsPerByte = int(
        shared.networkDefaultProofOfWorkNonceTrialsPerByte / 100)
    shared.networkDefaultPayloadLengthExtraBytes = int(
        shared.networkDefaultPayloadLengthExtraBytes / 100)

class Main:
    def start(self, daemon=False):
        _fixWinsock()

        shared.daemon = daemon
        # is the application already running?  If yes then exit.
        thisapp = singleton.singleinstance()

        # get curses flag
        curses = False
        if '-c' in sys.argv:
            curses = True

        signal.signal(signal.SIGINT, helper_generic.signal_handler)
        # signal.signal(signal.SIGINT, signal.SIG_DFL)

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

        if shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
            try:
                apiNotifyPath = shared.config.get(
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

        connectToStream(1)

        singleListenerThread = singleListener()
        singleListenerThread.setup(selfInitiatedConnections)
        singleListenerThread.daemon = True  # close the main program even if there are threads left
        singleListenerThread.start()

        if daemon == False and shared.safeConfigGetBoolean('bitmessagesettings', 'daemon') == False:
            if curses == False:
                try:
                    from PyQt4 import QtCore, QtGui
                except Exception as err:
                    print('PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API. You can download PyQt from http://www.riverbankcomputing.com/software/pyqt/download   or by searching Google for \'PyQt Download\'. If you want to run in daemon mode, see https://bitmessage.org/wiki/Daemon')
                    print('Error message:', err)
                    print('You can also run PyBitmessage with the new curses interface by providing \'-c\' as a commandline argument.')
                    os._exit(0)

                import bitmessageqt
                bitmessageqt.run()
            else:
                print('Running with curses')
                import bitmessagecurses
                bitmessagecurses.runwrapper()
        else:
            shared.config.remove_option('bitmessagesettings', 'dontconnect')

            if daemon:
                with shared.printLock:
                    print('Running as a daemon. The main program should exit this thread.')
            else:
                with shared.printLock:
                    print('Running as a daemon. You can use Ctrl+C to exit.')
                while True:
                    time.sleep(20)

    def stop(self):
        with shared.printLock:
            print('Stopping Bitmessage Deamon.')
        shared.doCleanShutdown()


    #TODO: nice function but no one is using this 
    def getApiAddress(self):
        if not shared.safeConfigGetBoolean('bitmessagesettings', 'apienabled'):
            return None
        address = shared.config.get('bitmessagesettings', 'apiinterface')
        port = shared.config.getint('bitmessagesettings', 'apiport')
        return {'address':address,'port':port}

if __name__ == "__main__":
    mainprogram = Main()
    mainprogram.start()


# So far, the creation of and management of the Bitmessage protocol and this
# client is a one-man operation. Bitcoin tips are quite appreciated.
# 1H5XaDA6fYENLbknwZyjiYXYPQaFjjLX2u
