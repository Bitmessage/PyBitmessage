"""
Global runtime variables.
"""
import collections

neededPubkeys = {}
streamsInWhichIAmParticipating = []

extPort = None
"""For UPnP"""

socksIP = None
"""for Tor hidden service"""

appdata = ''
"""holds the location of the application data storage directory"""

shutdown = 0
"""
Set to 1 by the `.shutdown.doCleanShutdown` function.
Used to tell the threads to exit.
"""

# Component control flags - set on startup, do not change during runtime
#     The defaults are for standalone GUI (default operating mode)
enableNetwork = True
"""enable network threads"""
enableObjProc = True
"""enable object processing thread"""
enableAPI = True
"""enable API (if configured)"""
enableGUI = True
"""enable GUI (QT or ncurses)"""
enableSTDIO = False
"""enable STDIO threads"""
curses = False

sqlReady = False
"""set to true by `.threads.sqlThread` when ready for processing"""

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
    """This method helps to reset the availability of network protocol"""
    # pylint: disable=global-statement
    global networkProtocolAvailability
    networkProtocolAvailability = {'IPv4': None, 'IPv6': None, 'onion': None}


resetNetworkProtocolAvailability()

discoveredPeers = {}

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
