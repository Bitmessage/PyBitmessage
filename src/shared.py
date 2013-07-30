softwareVersion = '0.3.5'
verbose = 1
maximumAgeOfAnObjectThatIAmWillingToAccept = 216000  # Equals two days and 12 hours.
lengthOfTimeToLeaveObjectsInInventory = 237600  # Equals two days and 18 hours. This should be longer than maximumAgeOfAnObjectThatIAmWillingToAccept so that we don't process messages twice.
lengthOfTimeToHoldOnToAllPubkeys = 2419200  # Equals 4 weeks. You could make this longer if you want but making it shorter would not be advisable because there is a very small possibility that it could keep you from obtaining a needed pubkey for a period of time.
maximumAgeOfObjectsThatIAdvertiseToOthers = 216000  # Equals two days and 12 hours
maximumAgeOfNodesThatIAdvertiseToOthers = 10800  # Equals three hours
useVeryEasyProofOfWorkForTesting = False  # If you set this to True while on the normal network, you won't be able to send or sometimes receive messages.


# Libraries.
import collections
import ConfigParser
import os
import pickle
import Queue
import random
import socket
import sys
import stat
import threading
import time

# Project imports.
from addresses import *
import highlevelcrypto
import shared
import helper_startup



config = ConfigParser.SafeConfigParser()
myECCryptorObjects = {}
MyECSubscriptionCryptorObjects = {}
myAddressesByHash = {} #The key in this dictionary is the RIPE hash which is encoded in an address and value is the address itself.
broadcastSendersForWhichImWatching = {}
workerQueue = Queue.Queue()
sqlSubmitQueue = Queue.Queue() #SQLITE3 is so thread-unsafe that they won't even let you call it from different threads using your own locks. SQL objects can only be called from one thread.
sqlReturnQueue = Queue.Queue()
sqlLock = threading.Lock()
UISignalQueue = Queue.Queue()
addressGeneratorQueue = Queue.Queue()
knownNodesLock = threading.Lock()
knownNodes = {}
sendDataQueues = [] #each sendData thread puts its queue in this list.
inventory = {} #of objects (like msg payloads and pubkey payloads) Does not include protocol headers (the first 24 bytes of each packet).
inventoryLock = threading.Lock() #Guarantees that two receiveDataThreads don't receive and process the same message concurrently (probably sent by a malicious individual)
printLock = threading.Lock()
appdata = '' #holds the location of the application data storage directory
statusIconColor = 'red'
connectedHostsList = {} #List of hosts to which we are connected. Used to guarantee that the outgoingSynSender threads won't connect to the same remote node twice.
shutdown = 0 #Set to 1 by the doCleanShutdown function. Used to tell the proof of work worker threads to exit.
alreadyAttemptedConnectionsList = {
}  # This is a list of nodes to which we have already attempted a connection
alreadyAttemptedConnectionsListLock = threading.Lock()
alreadyAttemptedConnectionsListResetTime = int(
    time.time())  # used to clear out the alreadyAttemptedConnectionsList periodically so that we will retry connecting to hosts to which we have already tried to connect.
numberOfObjectsThatWeHaveYetToCheckAndSeeWhetherWeAlreadyHavePerPeer = {}
neededPubkeys = {}
eightBytesOfRandomDataUsedToDetectConnectionsToSelf = pack(
    '>Q', random.randrange(1, 18446744073709551615))
successfullyDecryptMessageTimings = [
    ]  # A list of the amounts of time it took to successfully decrypt msg messages
apiAddressGeneratorReturnQueue = Queue.Queue(
    )  # The address generator thread uses this queue to get information back to the API thread.
ackdataForWhichImWatching = {}

#If changed, these values will cause particularly unexpected behavior: You won't be able to either send or receive messages because the proof of work you do (or demand) won't match that done or demanded by others. Don't change them!
networkDefaultProofOfWorkNonceTrialsPerByte = 320 #The amount of work that should be performed (and demanded) per byte of the payload. Double this number to double the work.
networkDefaultPayloadLengthExtraBytes = 14000 #To make sending short messages a little more difficult, this value is added to the payload length for use in calculating the proof of work target.

def isInSqlInventory(hash):
    t = (hash,)
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put('''select hash from inventory where hash=?''')
    shared.sqlSubmitQueue.put(t)
    queryreturn = shared.sqlReturnQueue.get()
    shared.sqlLock.release()
    if queryreturn == []:
        return False
    else:
        return True

def assembleVersionMessage(remoteHost, remotePort, myStreamNumber):
    payload = ''
    payload += pack('>L', 2)  # protocol version.
    payload += pack('>q', 1)  # bitflags of the services I offer.
    payload += pack('>q', int(time.time()))

    payload += pack(
        '>q', 1)  # boolservices of remote connection. How can I even know this for sure? This is probably ignored by the remote host.
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
        socket.inet_aton(remoteHost)
    payload += pack('>H', remotePort)  # remote IPv6 and port

    payload += pack('>q', 1)  # bitflags of the services I offer.
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + pack(
        '>L', 2130706433)  # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
    payload += pack('>H', shared.config.getint(
        'bitmessagesettings', 'port'))  # my external IPv6 and port

    random.seed()
    payload += eightBytesOfRandomDataUsedToDetectConnectionsToSelf
    userAgent = '/PyBitmessage:' + shared.softwareVersion + \
        '/'  # Length of userAgent must be less than 253.
    payload += pack('>B', len(
        userAgent))  # user agent string length. If the user agent is more than 252 bytes long, this code isn't going to work.
    payload += userAgent
    payload += encodeVarint(
        1)  # The number of streams about which I care. PyBitmessage currently only supports 1 per connection.
    payload += encodeVarint(myStreamNumber)

    datatosend = '\xe9\xbe\xb4\xd9'  # magic bits, slighly different from Bitcoin's magic bits.
    datatosend = datatosend + 'version\x00\x00\x00\x00\x00'  # version command
    datatosend = datatosend + pack('>L', len(payload))  # payload length
    datatosend = datatosend + hashlib.sha512(payload).digest()[0:4]
    return datatosend + payload

def lookupAppdataFolder():
    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(os.environ["HOME"], "Library/Application Support/", APPNAME) + '/'
        else:
            stringToLog = 'Could not find home folder, please report this message and your OS X version to the BitMessage Github.'
            if 'logger' in globals():
                logger.critical(stringToLog)
            else:
                print stringToLog
            sys.exit()

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = path.join(environ['APPDATA'], APPNAME) + '\\'
    else:
        from shutil import move
        try:
            dataFolder = path.join(environ["XDG_CONFIG_HOME"], APPNAME)
        except KeyError:
            dataFolder = path.join(environ["HOME"], ".config", APPNAME)

        # Migrate existing data to the proper location if this is an existing install
        try:
            move(path.join(environ["HOME"], ".%s" % APPNAME), dataFolder)
            stringToLog = "Moving data folder to %s" % (dataFolder)
            if 'logger' in globals():
                logger.info(stringToLog)
            else:
                print stringToLog
        except IOError:
            # Old directory may not exist.
            pass
        dataFolder = dataFolder + '/'
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
    except Exception, err:
        return False

def decodeWalletImportFormat(WIFstring):
    fullString = arithmetic.changebase(WIFstring,58,256)
    privkey = fullString[:-4]
    if fullString[-4:] != hashlib.sha256(hashlib.sha256(privkey).digest()).digest()[:4]:
        logger.error('Major problem! When trying to decode one of your private keys, the checksum '
                     'failed. Here is the PRIVATE key: %s\n' % str(WIFstring))
        return ""
    else:
        #checksum passed
        if privkey[0] == '\x80':
            return privkey[1:]
        else:
            logger.error('Major problem! When trying to decode one of your private keys, the '
                         'checksum passed but the key doesn\'t begin with hex 80. Here is the '
                         'PRIVATE key: %s\n' % str(WIFstring))
            return ""


def reloadMyAddressHashes():
    logger.debug('reloading keys from keys.dat file')
    myECCryptorObjects.clear()
    myAddressesByHash.clear()
    #myPrivateKeys.clear()

    keyfileSecure = checkSensitiveFilePermissions(appdata + 'keys.dat')
    configSections = config.sections()
    hasEnabledKeys = False
    for addressInKeysFile in configSections:
        if addressInKeysFile <> 'bitmessagesettings':
            isEnabled = config.getboolean(addressInKeysFile, 'enabled')
            if isEnabled:
                hasEnabledKeys = True
                status,addressVersionNumber,streamNumber,hash = decodeAddress(addressInKeysFile)
                if addressVersionNumber == 2 or addressVersionNumber == 3:
                    # Returns a simple 32 bytes of information encoded in 64 Hex characters,
                    # or null if there was an error.
                    privEncryptionKey = decodeWalletImportFormat(
                            config.get(addressInKeysFile, 'privencryptionkey')).encode('hex')

                    if len(privEncryptionKey) == 64:#It is 32 bytes encoded as 64 hex characters
                        myECCryptorObjects[hash] = highlevelcrypto.makeCryptor(privEncryptionKey)
                        myAddressesByHash[hash] = addressInKeysFile

                else:
                    logger.error('Error in reloadMyAddressHashes: Can\'t handle address '
                                 'versions other than 2 or 3.\n')

    if not keyfileSecure:
        fixSensitiveFilePermissions(appdata + 'keys.dat', hasEnabledKeys)

def reloadBroadcastSendersForWhichImWatching():
    logger.debug('reloading subscriptions...')
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
        #Now, for all addresses, even version 2 addresses, we should create Cryptor objects in a dictionary which we will use to attempt to decrypt encrypted broadcast messages.
        privEncryptionKey = hashlib.sha512(encodeVarint(addressVersionNumber)+encodeVarint(streamNumber)+hash).digest()[:32]
        MyECSubscriptionCryptorObjects[hash] = highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex'))

def doCleanShutdown():
    global shutdown
    shutdown = 1 #Used to tell proof of work worker threads to exit.    
    knownNodesLock.acquire()
    UISignalQueue.put(('updateStatusBar','Saving the knownNodes list of peers to disk...'))
    output = open(appdata + 'knownnodes.dat', 'wb')
    logger.info('finished opening knownnodes.dat. Now pickle.dump')
    pickle.dump(knownNodes, output)
    logger.info('Completed pickle.dump. Closing output...')
    output.close()
    knownNodesLock.release()
    logger.info('Finished closing knownnodes.dat output file.')
    UISignalQueue.put(('updateStatusBar','Done saving the knownNodes list of peers to disk.'))

    broadcastToSendDataQueues((0, 'shutdown', 'all'))

    logger.info('Flushing inventory in memory out to disk...')
    UISignalQueue.put((
        'updateStatusBar',
        'Flushing inventory in memory out to disk. This should normally only take a second...'))
    flushInventory()

    # This one last useless query will guarantee that the previous flush committed before we close
    # the program.
    sqlLock.acquire()
    sqlSubmitQueue.put('SELECT address FROM subscriptions')
    sqlSubmitQueue.put('')
    sqlReturnQueue.get()
    sqlSubmitQueue.put('exit')
    sqlLock.release()
    logger.info('Finished flushing inventory.')

    # Wait long enough to guarantee that any running proof of work worker threads will check the
    # shutdown variable and exit. If the main thread closes before they do then they won't stop.
    time.sleep(.25) 

    if safeConfigGetBoolean('bitmessagesettings','daemon'):
        logger.info('Clean shutdown complete.')
        os._exit(0)

# When you want to command a sendDataThread to do something, like shutdown or send some data, this
# function puts your data into the queues for each of the sendDataThreads. The sendDataThreads are
# responsible for putting their queue into (and out of) the sendDataQueues list.
def broadcastToSendDataQueues(data):
    # logger.debug('running broadcastToSendDataQueues')
    for q in sendDataQueues:
        q.put((data))
        
def flushInventory():
    #Note that the singleCleanerThread clears out the inventory dictionary from time to time, although it only clears things that have been in the dictionary for a long time. This clears the inventory dictionary Now.
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

# Checks sensitive file permissions for inappropriate umask during keys.dat creation.
# (Or unwise subsequent chmod.)
#
# Returns true iff file appears to have appropriate permissions.
def checkSensitiveFilePermissions(filename):
    if sys.platform == 'win32':
        # TODO: This might deserve extra checks by someone familiar with
        # Windows systems.
        return True
    else:
        present_permissions = os.stat(filename)[0]
        disallowed_permissions = stat.S_IRWXG | stat.S_IRWXO
        return present_permissions & disallowed_permissions == 0

# Fixes permissions on a sensitive file.
def fixSensitiveFilePermissions(filename, hasEnabledKeys):
    if hasEnabledKeys:
        logger.warning('Keyfile had insecure permissions, and there were enabled keys. '
                       'The truly paranoid should stop using them immediately.')
    else:
        logger.warning('Keyfile had insecure permissions, but there were no enabled keys.')
    try:
        present_permissions = os.stat(filename)[0]
        disallowed_permissions = stat.S_IRWXG | stat.S_IRWXO
        allowed_permissions = ((1<<32)-1) ^ disallowed_permissions
        new_permissions = (
            allowed_permissions & present_permissions)
        os.chmod(filename, new_permissions)

        logger.info('Keyfile permissions automatically fixed.')

    except Exception, e:
        logger.exception('Keyfile permissions could not be fixed.')
        raise

Peer = collections.namedtuple('Peer', ['host', 'port'])

helper_startup.loadConfig()
from debug import logger
