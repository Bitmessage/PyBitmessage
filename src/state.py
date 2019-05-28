import collections

neededPubkeys = {}
streamsInWhichIAmParticipating = []

# For UPnP
extPort = None

# for Tor hidden service
socksIP = None

# Network protocols availability, initialised below
networkProtocolAvailability = None

appdata = ''  # holds the location of the application data storage directory

# Set to 1 by the doCleanShutdown function.
# Used to tell the proof of work worker threads to exit.
shutdown = 0

# Component control flags - set on startup, do not change during runtime
#     The defaults are for standalone GUI (default operating mode)
enableNetwork = True  # enable network threads
enableObjProc = True  # enable object processing threads
enableAPI = True  # enable API (if configured)
enableGUI = True  # enable GUI (QT or ncurses)
enableSTDIO = False  # enable STDIO threads
curses = False

sqlReady = False  # set to true by sqlTread when ready for processing

maximumNumberOfHalfOpenConnections = 0

invThread = None
addrThread = None
downloadThread = None
uploadThread = None

ownAddresses = {}

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

discoveredPeers = {}

Peer = collections.namedtuple('Peer', ['host', 'port'])


def resetNetworkProtocolAvailability():
    global networkProtocolAvailability
    networkProtocolAvailability = {'IPv4': None, 'IPv6': None, 'onion': None}


resetNetworkProtocolAvailability()

dandelion = 0

testmode = False

kivy = False

association = ''

kivyapp = None

navinstance = None

totalSentMail = 0

sentMailTime = 0

dynamicAddressList = []

myAddressObj = None