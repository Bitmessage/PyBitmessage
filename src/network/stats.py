"""
src/network/stats.py
====================
"""

import time

import asyncore_pollchoose as asyncore
from network.connectionpool import BMConnectionPool
from state import missingObjects

lastReceivedTimestamp = time.time()
lastReceivedBytes = 0
currentReceivedSpeed = 0
lastSentTimestamp = time.time()
lastSentBytes = 0
currentSentSpeed = 0


def connectedHostsList():
    """"""
    retval = []
    for i in BMConnectionPool().inboundConnections.values() + \
            BMConnectionPool().outboundConnections.values():
        if not i.fullyEstablished:
            continue
        try:
            retval.append(i)
        except AttributeError:
            pass
    return retval


def sentBytes():
    """"""
    return asyncore.sentBytes


def uploadSpeed():
    """"""
    # pylint: disable=global-statement
    global lastSentTimestamp, lastSentBytes, currentSentSpeed

    currentTimestamp = time.time()
    if int(lastSentTimestamp) < int(currentTimestamp):
        currentSentBytes = asyncore.sentBytes
        currentSentSpeed = int((currentSentBytes - lastSentBytes) / (currentTimestamp - lastSentTimestamp))
        lastSentBytes = currentSentBytes
        lastSentTimestamp = currentTimestamp
    return currentSentSpeed


def receivedBytes():
    """"""
    return asyncore.receivedBytes


def downloadSpeed():
    """"""
    # pylint: disable=global-statement
    global lastReceivedTimestamp, lastReceivedBytes, currentReceivedSpeed

    currentTimestamp = time.time()
    if int(lastReceivedTimestamp) < int(currentTimestamp):
        currentReceivedBytes = asyncore.receivedBytes
        currentReceivedSpeed = int((currentReceivedBytes - lastReceivedBytes) /
                                   (currentTimestamp - lastReceivedTimestamp))
        lastReceivedBytes = currentReceivedBytes
        lastReceivedTimestamp = currentTimestamp
    return currentReceivedSpeed


def pendingDownload():
    """"""
    return len(missingObjects)


def pendingUpload():
    """"""
    return 0
