import collections

neededPubkeys = {}
streamsInWhichIAmParticipating = []
sendDataQueues = [] #each sendData thread puts its queue in this list.

# For UPnP
extPort = None

# for Tor hidden service
socksIP = None

# Network protocols availability, initialised below
networkProtocolAvailability = None

appdata = '' #holds the location of the application data storage directory

shutdown = 0 #Set to 1 by the doCleanShutdown function. Used to tell the proof of work worker threads to exit.

curses = False

sqlReady = False # set to true by sqlTread when ready for processing

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

def resetNetworkProtocolAvailability():
    global networkProtocolAvailability
    networkProtocolAvailability = {'IPv4': None, 'IPv6': None, 'onion': None}

resetNetworkProtocolAvailability()
