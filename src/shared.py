softwareVersion = '0.4.1'
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
from os import path, environ

# Project imports.
from addresses import *
import highlevelcrypto
import shared
import helper_startup
from helper_sql import *


config = ConfigParser.SafeConfigParser()
myECCryptorObjects = {}
MyECSubscriptionCryptorObjects = {}
myAddressesByHash = {} #The key in this dictionary is the RIPE hash which is encoded in an address and value is the address itself.
myAddressesByTag = {} # The key in this dictionary is the tag generated from the address.
broadcastSendersForWhichImWatching = {}
workerQueue = Queue.Queue()
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
numberOfObjectsThatWeHaveYetToGetPerPeer = {}
neededPubkeys = {}
eightBytesOfRandomDataUsedToDetectConnectionsToSelf = pack(
    '>Q', random.randrange(1, 18446744073709551615))
successfullyDecryptMessageTimings = [
    ]  # A list of the amounts of time it took to successfully decrypt msg messages
apiAddressGeneratorReturnQueue = Queue.Queue(
    )  # The address generator thread uses this queue to get information back to the API thread.
ackdataForWhichImWatching = {}
clientHasReceivedIncomingConnections = False #used by API command clientStatus
numberOfMessagesProcessed = 0
numberOfBroadcastsProcessed = 0
numberOfPubkeysProcessed = 0
numberOfInventoryLookupsPerformed = 0
daemon = False
inventorySets = {} # key = streamNumer, value = a set which holds the inventory object hashes that we are aware of. This is used whenever we receive an inv message from a peer to check to see what items are new to us. We don't delete things out of it; instead, the singleCleaner thread clears and refills it every couple hours.
needToWriteKnownNodesToDisk = False # If True, the singleCleaner will write it to disk eventually.

#If changed, these values will cause particularly unexpected behavior: You won't be able to either send or receive messages because the proof of work you do (or demand) won't match that done or demanded by others. Don't change them!
networkDefaultProofOfWorkNonceTrialsPerByte = 320 #The amount of work that should be performed (and demanded) per byte of the payload. Double this number to double the work.
networkDefaultPayloadLengthExtraBytes = 14000 #To make sending short messages a little more difficult, this value is added to the payload length for use in calculating the proof of work target.

# Remember here the RPC port read from namecoin.conf so we can restore to
# it as default whenever the user changes the "method" selection for
# namecoin integration to "namecoind".
namecoinDefaultRpcPort = "8336"

# When using py2exe or py2app, the variable frozen is added to the sys
# namespace.  This can be used to setup a different code path for 
# binary distributions vs source distributions.
frozen = getattr(sys,'frozen', None)

def isInSqlInventory(hash):
    queryreturn = sqlQuery('''select hash from inventory where hash=?''', hash)
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
    userAgent = '/PyBitmessage:' + shared.softwareVersion + '/'
    payload += encodeVarint(len(userAgent))
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
    if "BITMESSAGE_HOME" in environ:
        dataFolder = environ["BITMESSAGE_HOME"]
        if dataFolder[-1] not in [os.path.sep, os.path.altsep]:
            dataFolder += os.path.sep
    elif sys.platform == 'darwin':
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
    queryreturn = sqlQuery(
        '''select address from addressbook where address=?''',
        address)
    return queryreturn != []

#At this point we should really just have a isAddressInMy(book, address)...
def isAddressInMySubscriptionsList(address):
    queryreturn = sqlQuery(
        '''select * from subscriptions where address=?''',
        str(address))
    return queryreturn != []

def isAddressInMyAddressBookSubscriptionsListOrWhitelist(address):
    if isAddressInMyAddressBook(address):
        return True

    queryreturn = sqlQuery('''SELECT address FROM whitelist where address=? and enabled = '1' ''', address)
    if queryreturn <> []:
        return True

    queryreturn = sqlQuery(
        '''select address from subscriptions where address=? and enabled = '1' ''',
        address)
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
        logger.critical('Major problem! When trying to decode one of your private keys, the checksum '
                     'failed. Here is the PRIVATE key: %s' % str(WIFstring))
        return ""
    else:
        #checksum passed
        if privkey[0] == '\x80':
            return privkey[1:]
        else:
            logger.critical('Major problem! When trying to decode one of your private keys, the '
                         'checksum passed but the key doesn\'t begin with hex 80. Here is the '
                         'PRIVATE key: %s' % str(WIFstring))
            return ""


def reloadMyAddressHashes():
    logger.debug('reloading keys from keys.dat file')
    myECCryptorObjects.clear()
    myAddressesByHash.clear()
    myAddressesByTag.clear()
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
                if addressVersionNumber == 2 or addressVersionNumber == 3 or addressVersionNumber == 4:
                    # Returns a simple 32 bytes of information encoded in 64 Hex characters,
                    # or null if there was an error.
                    privEncryptionKey = decodeWalletImportFormat(
                            config.get(addressInKeysFile, 'privencryptionkey')).encode('hex')

                    if len(privEncryptionKey) == 64:#It is 32 bytes encoded as 64 hex characters
                        myECCryptorObjects[hash] = highlevelcrypto.makeCryptor(privEncryptionKey)
                        myAddressesByHash[hash] = addressInKeysFile
                        tag = hashlib.sha512(hashlib.sha512(encodeVarint(
                            addressVersionNumber) + encodeVarint(streamNumber) + hash).digest()).digest()[32:]
                        myAddressesByTag[tag] = addressInKeysFile

                else:
                    logger.error('Error in reloadMyAddressHashes: Can\'t handle address versions other than 2, 3, or 4.\n')

    if not keyfileSecure:
        fixSensitiveFilePermissions(appdata + 'keys.dat', hasEnabledKeys)

def reloadBroadcastSendersForWhichImWatching():
    broadcastSendersForWhichImWatching.clear()
    MyECSubscriptionCryptorObjects.clear()
    queryreturn = sqlQuery('SELECT address FROM subscriptions where enabled=1')
    logger.debug('reloading subscriptions...')
    for row in queryreturn:
        address, = row
        status,addressVersionNumber,streamNumber,hash = decodeAddress(address)
        if addressVersionNumber == 2:
            broadcastSendersForWhichImWatching[hash] = 0
        #Now, for all addresses, even version 2 addresses, we should create Cryptor objects in a dictionary which we will use to attempt to decrypt encrypted broadcast messages.
        
        if addressVersionNumber <= 3:
            privEncryptionKey = hashlib.sha512(encodeVarint(addressVersionNumber)+encodeVarint(streamNumber)+hash).digest()[:32]
            MyECSubscriptionCryptorObjects[hash] = highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex'))
        else:
            doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                addressVersionNumber) + encodeVarint(streamNumber) + hash).digest()).digest()
            tag = doubleHashOfAddressData[32:]
            privEncryptionKey = doubleHashOfAddressData[:32]
            MyECSubscriptionCryptorObjects[tag] = highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex'))

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
    sqlQuery('SELECT address FROM subscriptions')
    sqlStoredProcedure('exit')
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
        q.put(data)
        
def flushInventory():
    #Note that the singleCleanerThread clears out the inventory dictionary from time to time, although it only clears things that have been in the dictionary for a long time. This clears the inventory dictionary Now.
    with SqlBulkExecute() as sql:
        for hash, storedValue in inventory.items():
            objectType, streamNumber, payload, receivedTime, tag = storedValue
            sql.execute('''INSERT INTO inventory VALUES (?,?,?,?,?,?)''',
                       hash,objectType,streamNumber,payload,receivedTime,tag)
            del inventory[hash]

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
        try:
            # Skip known problems for non-Win32 filesystems without POSIX permissions.
            import subprocess
            fstype = subprocess.check_output('stat -f -c "%%T" %s' % (filename),
                                             shell=True,
                                             stderr=subprocess.STDOUT)
            if 'fuseblk' in fstype:
                logger.info('Skipping file permissions check for %s. Filesystem fuseblk detected.',
                            filename)
                return True
        except:
            # Swallow exception here, but we might run into trouble later!
            logger.error('Could not determine filesystem type. %s', filename)
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
    
def isBitSetWithinBitfield(fourByteString, n):
    # Uses MSB 0 bit numbering across 4 bytes of data
    n = 31 - n
    x, = unpack('>L', fourByteString)
    return x & 2**n != 0

def decryptAndCheckPubkeyPayload(payload, address):
    status, addressVersion, streamNumber, ripe = decodeAddress(address)
    doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
        addressVersion) + encodeVarint(streamNumber) + ripe).digest()).digest()
    # this function expects that the nonce is Not included in payload.
    readPosition = 8  # for the time
    embeddedVersionNumber, varintLength = decodeVarint(
        payload[readPosition:readPosition + 10])
    if embeddedVersionNumber != addressVersion:
        with shared.printLock:
            print 'Pubkey decryption was UNsuccessful due to address version mismatch. This shouldn\'t have happened.'
        return 'failed'
    readPosition += varintLength
    embeddedStreamNumber, varintLength = decodeVarint(
        payload[readPosition:readPosition + 10])
    if embeddedStreamNumber != streamNumber:
        with shared.printLock:
            print 'Pubkey decryption was UNsuccessful due to stream number mismatch. This shouldn\'t have happened.'
        return 'failed'
    readPosition += varintLength
    signedData = payload[:readPosition] # Some of the signed data is not encrypted so let's keep it for now.
    toTag = payload[readPosition:readPosition+32]
    readPosition += 32 #for the tag
    encryptedData = payload[readPosition:]
    # Let us try to decrypt the pubkey
    privEncryptionKey = doubleHashOfAddressData[:32]
    cryptorObject = highlevelcrypto.makeCryptor(privEncryptionKey.encode('hex'))
    try:
        decryptedData = cryptorObject.decrypt(encryptedData)
    except:
        # Someone must have encrypted some data with a different key
        # but tagged it with a tag for which we are watching.
        with shared.printLock:
            print 'Pubkey decryption was UNsuccessful. This shouldn\'t have happened.'
        return 'failed'
    print 'Pubkey decryption successful'
    readPosition = 4 # bypass the behavior bitfield
    publicSigningKey = '\x04' + decryptedData[readPosition:readPosition + 64]
    # Is it possible for a public key to be invalid such that trying to
    # encrypt or sign with it will cause an error? If it is, we should
    # probably test these keys here.
    readPosition += 64
    publicEncryptionKey = '\x04' + decryptedData[readPosition:readPosition + 64]
    readPosition += 64
    specifiedNonceTrialsPerByte, specifiedNonceTrialsPerByteLength = decodeVarint(
        decryptedData[readPosition:readPosition + 10])
    readPosition += specifiedNonceTrialsPerByteLength
    specifiedPayloadLengthExtraBytes, specifiedPayloadLengthExtraBytesLength = decodeVarint(
        decryptedData[readPosition:readPosition + 10])
    readPosition += specifiedPayloadLengthExtraBytesLength
    signedData += decryptedData[:readPosition]
    signatureLength, signatureLengthLength = decodeVarint(
        decryptedData[readPosition:readPosition + 10])
    readPosition += signatureLengthLength
    signature = decryptedData[readPosition:readPosition + signatureLength]
    try:
        if not highlevelcrypto.verify(signedData, signature, publicSigningKey.encode('hex')):
            print 'ECDSA verify failed (within decryptAndCheckPubkeyPayload).'
            return 'failed'
        print 'ECDSA verify passed (within decryptAndCheckPubkeyPayload)'
    except Exception as err:
        print 'ECDSA verify failed (within decryptAndCheckPubkeyPayload)', err
        return 'failed'

    sha = hashlib.new('sha512')
    sha.update(publicSigningKey + publicEncryptionKey)
    ripeHasher = hashlib.new('ripemd160')
    ripeHasher.update(sha.digest())
    embeddedRipe = ripeHasher.digest()

    if embeddedRipe != ripe:
        # Although this pubkey object had the tag were were looking for and was
        # encrypted with the correct encryption key, it doesn't contain the
        # correct keys. Someone is either being malicious or using buggy software.
        with shared.printLock:
            print 'Pubkey decryption was UNsuccessful due to RIPE mismatch. This shouldn\'t have happened.'
        return 'failed'
    
    t = (ripe, addressVersion, signedData, int(time.time()), 'yes')
    sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
    return 'successful'

Peer = collections.namedtuple('Peer', ['host', 'port'])

helper_startup.loadConfig()
from debug import logger
