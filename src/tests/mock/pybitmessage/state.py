"""
src/state.py
=================================
"""
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

maximumLengthOfTimeToBotherResendingMessages = 0

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
    """This method helps to reset the availability of network protocol"""
    # pylint: disable=global-statement
    global networkProtocolAvailability
    networkProtocolAvailability = {'IPv4': None, 'IPv6': None, 'onion': None}


resetNetworkProtocolAvailability()

dandelion = 0

testmode = False

kivy = False

association = ''

kivyapp = None

navinstance = None

mail_id = 0

myAddressObj = None

detailPageType = None

ackdata = None

status = None

screen_density = None

msg_counter_objs = None

check_sent_acc = None

sent_count = 0

inbox_count = 0

trash_count = 0

draft_count = 0

all_count = 0

searcing_text = ''

search_screen = ''

send_draft_mail = None

is_allmail = False

in_composer = False

availabe_credit = 0

in_sent_method = False

in_search_mode = False

clientHasReceivedIncomingConnections = False
"""used by API command clientStatus"""

numberOfMessagesProcessed = 0
numberOfBroadcastsProcessed = 0
numberOfPubkeysProcessed = 0

statusIconColor = 'red'
"""
GUI status icon color
.. note:: bad style, refactor it
"""

ackdataForWhichImWatching = {}

thisapp = None
"""Singleton instance"""

imageDir = None
