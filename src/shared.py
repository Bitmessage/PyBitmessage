softwareVersion = '0.3.3-2'

import threading
import sys
from addresses import *
import highlevelcrypto
import Queue
import pickle
import os
import time
from debug import logger

myECCryptorObjects = {}
MyECSubscriptionCryptorObjects = {}

# The key in this dictionary is the RIPE hash which is encoded in an address and
# value is the address itself.
myAddressesByHash = {}
broadcastSendersForWhichImWatching = {}
workerQueue = Queue.Queue()

# SQLite3 is so thread-unsafe that they won't even let you call it from
# different threads using your own locks. SQL objects can only be called
# from one thread.
sqlSubmitQueue = Queue.Queue()
sqlReturnQueue = Queue.Queue()
sqlLock = threading.Lock()
UISignalQueue = Queue.Queue()
addressGeneratorQueue = Queue.Queue()
knownNodesLock = threading.Lock()
knownNodes = {}

# Each sendData thread puts its queue in this list.
sendDataQueues = []

# Inventory of objects (like msg payloads and pubkey payloads)
# Does not includeprotocol headers (the first 24 bytes of each packet).
inventory = {}

# Guarantees that two receiveDataThreads don't receive and process the same
# message concurrently (probably sent by a malicious individual)
inventoryLock = threading.Lock()
printLock = threading.Lock() # DEPRECATED

# Holds the location of the application data storage directory
appdata = ''
statusIconColor = 'red'

# List of hosts to which we are connected. Used to guarantee that the
# outgoingSynSender threads won't connect to the same remote node twice.
connectedHostsList = {}

# Set to 1 by the doCleanShutdown function. Used to tell the proof of
# work worker threads to exit.
shutdown = 0

# If changed, these values will cause particularly unexpected behavior:
# You won't be able to either send or receive messages because the proof
# of work you do (or demand) won't match that done or demanded by others.
# Don't change them!

# The amount of work that should be performed (and demanded) per byte of
# the payload. Double this number to double the work.
networkDefaultProofOfWorkNonceTrialsPerByte = 320

# To make sending short messages a little more difficult, this value is
# added to the payload length for use in calculating the proof of work
# target.
networkDefaultPayloadLengthExtraBytes = 14000

def lookupAppdataFolder():
    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            logger.error('Could not find home folder, please report this message and your OS X version to the BitMessage Github.')
            sys.exit()

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = path.join(environ['APPDATA'], APPNAME) + '\\'
    else:
        dataFolder = path.expanduser(path.join("~", "." + APPNAME + "/"))
    return dataFolder

def isAddressInMyAddressBook(address):
    t = (address,)
    sqlLock.acquire()
    sqlSubmitQueue.put('''select address from addressbook where address=?''')
    sqlSubmitQueue.put(t)
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()
    return queryreturn != []

#At this point we should really just have a isAddressInMy(book, address)...
def isAddressInMySubscriptionsList(address):
    t = (str(address),) # As opposed to Qt str
    sqlLock.acquire()
    sqlSubmitQueue.put('''select * from subscriptions where address=?''')
    sqlSubmitQueue.put(t)
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()
    return queryreturn != []

def isAddressInMyAddressBookSubscriptionsListOrWhitelist(address):
    if isAddressInMyAddressBook(address):
        return True

    sqlLock.acquire()
    sqlSubmitQueue.put('''SELECT address FROM whitelist where address=? and enabled = '1' ''')
    sqlSubmitQueue.put((address,))
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()
    if queryreturn <> []:
        return True

    sqlLock.acquire()
    sqlSubmitQueue.put('''select address from subscriptions where address=? and enabled = '1' ''')
    sqlSubmitQueue.put((address,))
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()
    if queryreturn <> []:
        return True
    return False

def safeConfigGetBoolean(section,field):
        try:
            return config.getboolean(section,field)
        except:
            return False

def decodeWalletImportFormat(WIFstring):
    fullString = arithmetic.changebase(WIFstring,58,256)
    privkey = fullString[:-4]
    if fullString[-4:] != hashlib.sha256(hashlib.sha256(privkey).digest()).digest()[:4]:
        logger.error('Private key checksum failed: %s' % str(WIFstring))
        return ""
    else: # checksum passed
        if privkey[0] == '\x80':
            return privkey[1:]
        else:
            logger.error("Private key decoding failed! Key doesn't begin with hex 80: %s" % str(WIFstring))
            return ""


def reloadMyAddressHashes():
    logger.info('Reloading keys from keys.dat file')
    myECCryptorObjects.clear()
    myAddressesByHash.clear()
    #myPrivateKeys.clear()
    configSections = config.sections()
    for addressInKeysFile in configSections:
        if addressInKeysFile <> 'bitmessagesettings':
            isEnabled = config.getboolean(addressInKeysFile, 'enabled')
            if isEnabled:
                status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
                if addressVersionNumber == 2 or addressVersionNumber == 3:
                    # returns a simple 32 bytes of information encoded in 64 Hex characters,
                    # or null if there was an error
                    privEncryptionKey = decodeWalletImportFormat(
                                            config.get(addressInKeysFile, 'privencryptionkey')).encode('hex')
                    if len(privEncryptionKey) == 64: # It is 32 bytes encoded as 64 hex characters
                        myECCryptorObjects[hash] = highlevelcrypto.makeCryptor(privEncryptionKey)
                        myAddressesByHash[hash] = addressInKeysFile
                else:
                    logger.debug("Error: Can't handle address versions other than 2 or 3")

def reloadBroadcastSendersForWhichImWatching():
    logger.info('Reloading subscriptions...')
    broadcastSendersForWhichImWatching.clear()
    MyECSubscriptionCryptorObjects.clear()
    sqlLock.acquire()
    sqlSubmitQueue.put('SELECT address FROM subscriptions where enabled=1')
    sqlSubmitQueue.put('')
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()
    for row in queryreturn:
        address, = row
        status,addressVersionNumber,streamNumber,hash = decodeAddress(address)
        if addressVersionNumber == 2:
            broadcastSendersForWhichImWatching[hash] = 0
        # Now, for all addresses, even version 2 addresses, we should create
        # Cryptor objects in a dictionary which we will use to attempt to
        # decrypt encrypted broadcast messages.
        privEncryptionKey = hashlib.sha512(encodeVarint(addressVersionNumber)+encodeVarint(streamNumber)+hash).digest()[:32]
        MyECSubscriptionCryptorObjects[hash] = highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex'))

def doCleanShutdown():
    global shutdown
    shutdown = 1 # Used to tell proof of work worker threads to exit.    
    knownNodesLock.acquire()
    UISignalQueue.put(('updateStatusBar','Saving the knownNodes list of peers to disk...'))
    output = open(appdata + 'knownnodes.dat', 'wb')
    logger.info('Finished opening knownnodes.dat. Now pickle.dump')
    pickle.dump(knownNodes, output)
    logger.info('Completed pickle.dump. Closing output...')
    output.close()
    knownNodesLock.release()
    logger.info('Finished closing knownnodes.dat output file.')
    UISignalQueue.put(('updateStatusBar','Done saving the knownNodes list of peers to disk.'))

    broadcastToSendDataQueues((0, 'shutdown', 'all'))

    logger.info('Flushing inventory in memory out to disk...')
    UISignalQueue.put(('updateStatusBar','Flushing inventory in memory out to disk. This should normally only take a second...'))
    flushInventory()

    # This one last useless query will guarantee that the previous flush
    # committed before we close the program.
    sqlLock.acquire()
    sqlSubmitQueue.put('SELECT address FROM subscriptions')
    sqlSubmitQueue.put('')
    sqlReturnQueue.get()
    sqlSubmitQueue.put('exit')
    sqlLock.release()
    logger.info('Finished flushing inventory.')

    # Wait long enough to guarantee that any running proof of work worker
    # threads will check the shutdown variable and exit. If the main
    # thread closes before they do then they won't stop.
    time.sleep(.25) 

    if safeConfigGetBoolean('bitmessagesettings','daemon'):
        logger.info('Done.')
        os._exit(0)

def broadcastToSendDataQueues(data):
    """
    When you want to command a sendDataThread to do something, like shutdown or
    send some data, this function puts your data into the queues for each of
    the sendDataThreads. The sendDataThreads are responsible for putting their
    queue into (and out of) the sendDataQueues list.
    """
    #logger.info('Running broadcastToSendDataQueues')
    for q in sendDataQueues:
        q.put((data))
        
def flushInventory():
    """
    Note that the singleCleanerThread clears out the inventory dictionary from
    time to time, although it only clears things that have been in the
    dictionary for a long time. This clears the inventory dictionary *now*.
    """
    sqlLock.acquire()
    for hash, storedValue in inventory.items():
        objectType, streamNumber, payload, receivedTime = storedValue
        t = (hash,objectType,streamNumber,payload,receivedTime)
        sqlSubmitQueue.put('''INSERT INTO inventory VALUES (?,?,?,?,?)''')
        sqlSubmitQueue.put(t)
        sqlReturnQueue.get()
        del inventory[hash]
    sqlSubmitQueue.put('commit')
    sqlLock.release()

def fixPotentiallyInvalidUTF8Data(text):
    try:
        unicode(text,'utf-8')
        return text
    except:
        output = 'Part of the message is corrupt. The message cannot be displayed the normal way.\n\n' + repr(text)
        return output
