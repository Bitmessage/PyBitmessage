"""
Global runtime variables.
"""

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
enableKivy = False
"""enable kivy app and test cases"""
curses = False

maximumNumberOfHalfOpenConnections = 0

maximumLengthOfTimeToBotherResendingMessages = 0

invThread = None
addrThread = None
downloadThread = None
uploadThread = None

ownAddresses = {}

discoveredPeers = {}

dandelion = 0

kivy = False

kivyapp = None

testmode = False

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
