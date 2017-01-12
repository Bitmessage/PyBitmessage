import collections

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

# If the trustedpeer option is specified in keys.dat then this will
# contain a Peer which will be connected to instead of using the
# addresses advertised by other peers. The client will only connect to
# this peer and the timing attack mitigation will be disabled in order
# to download data faster. The expected use case is where the user has
# a fast connection to a trusted server where they run a BitMessage
# daemon permanently. If they then run a second instance of the client
# on a local machine periodically when they want to check for messages
# it will sync with the network a lot faster without compromising
# security.
trustedPeer = None

Peer = collections.namedtuple('Peer', ['host', 'port'])
