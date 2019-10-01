"""
src/network/stats.py
====================
"""
import time

from network import asyncore_pollchoose as asyncore
from network.connectionpool import BMConnectionPool
from network.objectracker import missingObjects


lastReceivedTimestamp = time.time()
lastReceivedBytes = 0
currentReceivedSpeed = 0
lastSentTimestamp = time.time()
lastSentBytes = 0
currentSentSpeed = 0


def connectedHostsList():
    """List of all the connected hosts"""
    retval = []
    # import pdb;pdb.set_trace()
    for i in list(BMConnectionPool().inboundConnections.values()) + \
            list(BMConnectionPool().outboundConnections.values()):
        if not i.fullyEstablished:
            continue
        try:
            retval.append(i)
        except AttributeError:
            pass
    return retval


def sentBytes():
    """Sending Bytes"""
    return asyncore.sentBytes


def uploadSpeed():
    """Getting upload speed"""
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
    """Receiving Bytes"""
    return asyncore.receivedBytes


def downloadSpeed():
    """Getting download speed"""
    # pylint: disable=global-statement
    global lastReceivedTimestamp, lastReceivedBytes, currentReceivedSpeed
    currentTimestamp = time.time()
    if int(lastReceivedTimestamp) < int(currentTimestamp):
        currentReceivedBytes = asyncore.receivedBytes
        currentReceivedSpeed = int(
            (currentReceivedBytes - lastReceivedBytes) / (currentTimestamp - lastReceivedTimestamp))
        lastReceivedBytes = currentReceivedBytes
        lastReceivedTimestamp = currentTimestamp
    return currentReceivedSpeed


def pendingDownload():
    """Getting pending downloads"""
    return len(missingObjects)
    # tmp = {}
    # for connection in BMConnectionPool().inboundConnections.values() + \
    #         BMConnectionPool().outboundConnections.values():
    #     for k in connection.objectsNewToMe.keys():
    #         tmp[k] = True
    # return len(tmp)


def pendingUpload():
    """Getting pending uploads"""
    # tmp = {}
    # for connection in BMConnectionPool().inboundConnections.values() + \
    #         BMConnectionPool().outboundConnections.values():
    #     for k in connection.objectsNewToThem.keys():
    #         tmp[k] = True
    # This probably isn't the correct logic so it's disabled
    # return len(tmp)
    return 0
