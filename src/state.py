neededPubkeys = {}
streamsInWhichIAmParticipating = {}
sendDataQueues = [] #each sendData thread puts its queue in this list.

# For UPnP
extPort = None

# for Tor hidden service
socksIP = None

# Network protocols last check failed
networkProtocolLastFailed = {'IPv4': 0, 'IPv6': 0, 'onion': 0}

appdata = '' #holds the location of the application data storage directory
