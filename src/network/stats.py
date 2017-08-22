import time

from network.connectionpool import BMConnectionPool
import asyncore_pollchoose as asyncore

lastReceivedTimestamp = time.time()
lastReceivedBytes = 0
currentReceivedSpeed = 0
lastSentTimestamp = time.time()
lastSentBytes = 0
currentSentSpeed = 0

def connectedHostsList():
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
    return asyncore.sentBytes

def uploadSpeed():
    global lastSentTimestamp, lastSentBytes, currentSentSpeed
    currentTimestamp = time.time()
    if int(lastSentTimestamp) < int(currentTimestamp):
        currentSentBytes = asyncore.sentBytes
        currentSentSpeed = int((currentSentBytes - lastSentBytes) / (currentTimestamp - lastSentTimestamp))
        lastSentBytes = currentSentBytes
        lastSentTimestamp = currentTimestamp
    return currentSentSpeed

def receivedBytes():
    return asyncore.receivedBytes

def downloadSpeed():
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
    tmp = {}
    for connection in BMConnectionPool().inboundConnections.values() + \
            BMConnectionPool().outboundConnections.values():
        for k in connection.objectsNewToMe.keys():
            tmp[k] = True
    return len(tmp)

def pendingUpload():
    tmp = {}
    for connection in BMConnectionPool().inboundConnections.values() + \
            BMConnectionPool().outboundConnections.values():
        for k in connection.objectsNewToThem.keys():
            tmp[k] = True
    #This probably isn't the correct logic so it's disabled
    #return len(tmp)
    return 0
