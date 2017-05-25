from bmconfigparser import BMConfigParser
from network.connectionpool import BMConnectionPool
import asyncore_pollchoose as asyncore
import shared
import throttle

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
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        return 0
    else:
        return throttle.sendThrottle().getSpeed()

def receivedBytes():
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        return asyncore.receivedBytes
    else:
        return throttle.ReceiveThrottle().total

def downloadSpeed():
    if BMConfigParser().safeGetBoolean("network", "asyncore"):
        return 0
    else:
        return throttle.ReceiveThrottle().getSpeed()
