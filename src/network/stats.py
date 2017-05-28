import time

from bmconfigparser import BMConfigParser
from network.connectionpool import BMConnectionPool
from inventory import PendingDownloadQueue, PendingUpload
import asyncore_pollchoose as asyncore
import shared
import throttle

lastReceivedTimestamp = time.time()
lastReceivedBytes = 0
currentReceivedSpeed = 0
lastSentTimestamp = time.time()
lastSentBytes = 0
currentSentSpeed = 0

def connectedHostsList():
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        retval = []
        for i in BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values():
            if not i.connected:
                continue
            try:
                retval.append((i.destination, i.streams[0]))
            except AttributeError:
                pass
        return retval
    else:
        return shared.connectedHostsList.items()

def sentBytes():
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        return asyncore.sentBytes
    else:
        return throttle.SendThrottle().total

def uploadSpeed():
    global lastSentTimestamp, lastSentBytes, currentSentSpeed
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        currentTimestamp = time.time()
        if int(lastSentTimestamp) < int(currentTimestamp):
            currentSentBytes = asyncore.sentBytes
            currentSentSpeed = int((currentSentBytes - lastSentBytes) / (currentTimestamp - lastSentTimestamp))
            lastSentBytes = currentSentBytes
            lastSentTimestamp = currentTimestamp
        return currentSentSpeed
    else:
        return throttle.sendThrottle().getSpeed()

def receivedBytes():
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        return asyncore.receivedBytes
    else:
        return throttle.ReceiveThrottle().total

def downloadSpeed():
    global lastReceivedTimestamp, lastReceivedBytes, currentReceivedSpeed
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        currentTimestamp = time.time()
        if int(lastReceivedTimestamp) < int(currentTimestamp):
            currentReceivedBytes = asyncore.receivedBytes
            currentReceivedSpeed = int((currentReceivedBytes - lastReceivedBytes) / (currentTimestamp - lastReceivedTimestamp))
            lastReceivedBytes = currentReceivedBytes
            lastReceivedTimestamp = currentTimestamp
        return currentReceivedSpeed
    else:
        return throttle.ReceiveThrottle().getSpeed()

def pendingDownload():
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        tmp = {}
        for connection in BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values():
            for k in connection.objectsNewToMe.keys():
                tmp[k] = True
        return len(tmp)
    else:
        return PendingDownloadQueue.totalSize()

def pendingUpload():
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        return 0
        tmp = {}
        for connection in BMConnectionPool().inboundConnections.values() + BMConnectionPool().outboundConnections.values():
            for k in connection.objectsNewToThem.keys():
                tmp[k] = True
        return len(tmp)
    else:
        return PendingUpload().len()
