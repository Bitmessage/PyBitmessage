﻿from __future__ import division

softwareVersion = '0.6.1'
verbose = 1
maximumAgeOfAnObjectThatIAmWillingToAccept = 216000  # This is obsolete with the change to protocol v3 but the singleCleaner thread still hasn't been updated so we need this a little longer.
lengthOfTimeToHoldOnToAllPubkeys = 2419200  # Equals 4 weeks. You could make this longer if you want but making it shorter would not be advisable because there is a very small possibility that it could keep you from obtaining a needed pubkey for a period of time.
maximumAgeOfNodesThatIAdvertiseToOthers = 10800  # Equals three hours
useVeryEasyProofOfWorkForTesting = False  # If you set this to True while on the normal network, you won't be able to send or sometimes receive messages.


# Libraries.
import base64
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
import shutil  # used for moving the data folder and copying keys.dat
import datetime
from os import path, environ
from struct import Struct
import traceback
from binascii import hexlify

# Project imports.
from addresses import *
from class_objectProcessorQueue import ObjectProcessorQueue
import highlevelcrypto
import shared
#import helper_startup
from helper_sql import *
from helper_threading import *


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
inventoryLock = threading.RLock() #Guarantees that two receiveDataThreads don't receive and process the same message concurrently (probably sent by a malicious individual)
printLock = threading.Lock()
appdata = '' #holds the location of the application data storage directory
statusIconColor = 'red'
connectedHostsList = {} #List of hosts to which we are connected. Used to guarantee that the outgoingSynSender threads won't connect to the same remote node twice.
shutdown = 0 #Set to 1 by the doCleanShutdown function. Used to tell the proof of work worker threads to exit.
thisapp = None # singleton lock instance
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
numberOfBytesReceived = 0 # Used for the 'network status' page
numberOfBytesSent = 0 # Used for the 'network status' page
numberOfBytesReceivedLastSecond = 0 # used for the bandwidth rate limit
numberOfBytesSentLastSecond = 0 # used for the bandwidth rate limit
lastTimeWeResetBytesReceived = 0 # used for the bandwidth rate limit
lastTimeWeResetBytesSent = 0 # used for the bandwidth rate limit
sendDataLock = threading.Lock() # used for the bandwidth rate limit
receiveDataLock = threading.Lock() # used for the bandwidth rate limit
daemon = False
needToWriteKnownNodesToDisk = False # If True, the singleCleaner will write it to disk eventually.
maximumLengthOfTimeToBotherResendingMessages = 0
objectProcessorQueue = ObjectProcessorQueue()  # receiveDataThreads dump objects they hear on the network into this queue to be processed.
streamsInWhichIAmParticipating = {}

# sanity check, prevent doing ridiculous PoW
# 20 million PoWs equals approximately 2 days on dev's dual R9 290
ridiculousDifficulty = 20000000

#If changed, these values will cause particularly unexpected behavior: You won't be able to either send or receive messages because the proof of work you do (or demand) won't match that done or demanded by others. Don't change them!
networkDefaultProofOfWorkNonceTrialsPerByte = 1000 #The amount of work that should be performed (and demanded) per byte of the payload.
networkDefaultPayloadLengthExtraBytes = 1000 #To make sending short messages a little more difficult, this value is added to the payload length for use in calculating the proof of work target.

# Remember here the RPC port read from namecoin.conf so we can restore to
# it as default whenever the user changes the "method" selection for
# namecoin integration to "namecoind".
namecoinDefaultRpcPort = "8336"

# When using py2exe or py2app, the variable frozen is added to the sys
# namespace.  This can be used to setup a different code path for 
# binary distributions vs source distributions.
frozen = getattr(sys,'frozen', None)

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

# For UPnP
extPort = None

# for Tor hidden service
socksIP = None

#Compiled struct for packing/unpacking headers
#New code should use CreatePacket instead of Header.pack
Header = Struct('!L12sL4s')

#Service flags
NODE_NETWORK = 1
NODE_SSL = 2

#Bitfield flags
BITFIELD_DOESACK = 1

import collections

InventoryItem = collections.namedtuple('InventoryItem', 'type stream payload expires tag')


class Inventory(collections.MutableMapping):
    def __init__(self):
        super(Inventory, self).__init__()
        self._inventory = {} #of objects (like msg payloads and pubkey payloads) Does not include protocol headers (the first 24 bytes of each packet).
        self._streams = collections.defaultdict(set) # key = streamNumer, value = a set which holds the inventory object hashes that we are aware of. This is used whenever we receive an inv message from a peer to check to see what items are new to us. We don't delete things out of it; instead, the singleCleaner thread clears and refills it every couple hours.

    def __contains__(self, hash):
        global numberOfInventoryLookupsPerformed
        with inventoryLock:
            numberOfInventoryLookupsPerformed += 1
            if hash in self._inventory:
                return True
            return bool(sqlQuery('SELECT 1 FROM inventory WHERE hash=?', hash))

    def __getitem__(self, hash):
        with inventoryLock:
            if hash in self._inventory:
                return self._inventory[hash]
            rows = sqlQuery('SELECT objecttype, streamnumber, payload, expirestime, tag FROM inventory WHERE hash=?', hash)
            if not rows:
                raise KeyError(hash)
            return InventoryItem(*rows[0])

    def __setitem__(self, hash, value):
        with inventoryLock:
            value = InventoryItem(*value)
            self._inventory[hash] = value
            self._streams[value.stream].add(hash)

    def __delitem__(self, hash):
        raise NotImplementedError

    def __iter__(self):
        with inventoryLock:
            hashes = self._inventory.keys()[:]
            hashes += (hash for hash, in sqlQuery('SELECT hash FROM inventory'))
            return hashes.__iter__()

    def __len__(self):
        with inventoryLock:
            return len(self._inventory) + sqlQuery('SELECT count(*) FROM inventory')[0][0]

    def by_type_and_tag(self, type, tag):
        with inventoryLock:
            values = [value for value in self._inventory.values() if value.type == type and value.tag == tag]
            values += (InventoryItem(*value) for value in sqlQuery('SELECT objecttype, streamnumber, payload, expirestime, tag FROM inventory WHERE objecttype=? AND tag=?', type, tag))
            return values

    def hashes_by_stream(self, stream):
        with inventoryLock:
            return self._streams[stream]

    def unexpired_hashes_by_stream(self, stream):
        with inventoryLock:
            t = int(time.time())
            hashes = [hash for hash, value in self._inventory.items() if value.stream == stream and value.expires > t]
            hashes += (payload for payload, in sqlQuery('SELECT hash FROM inventory WHERE streamnumber=? AND expirestime>?', stream, t))
            return hashes

    def flush(self):
        with inventoryLock: # If you use both the inventoryLock and the sqlLock, always use the inventoryLock OUTSIDE of the sqlLock.
            with SqlBulkExecute() as sql:
                for hash, value in self._inventory.items():
                    sql.execute('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)', hash, *value)
                self._inventory.clear()

    def clean(self):
        with inventoryLock:
            sqlExecute('DELETE FROM inventory WHERE expirestime<?',int(time.time()) - (60 * 60 * 3))
            self._streams.clear()
            for hash, value in self.items():
                self._streams[value.stream].add(hash)


inventory = Inventory()


#Create a packet
def CreatePacket(command, payload=''):
    payload_length = len(payload)
    checksum = hashlib.sha512(payload).digest()[0:4]
    
    b = bytearray(Header.size + payload_length)
    Header.pack_into(b, 0, 0xE9BEB4D9, command, payload_length, checksum)
    b[Header.size:] = payload
    return bytes(b)


def encodeHost(host):
    if host.find('.onion') > -1:
        return '\xfd\x87\xd8\x7e\xeb\x43' + base64.b32decode(host.split(".")[0], True)
    elif host.find(':') == -1:
        return '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
            socket.inet_aton(host)
    else:
        return socket.inet_pton(socket.AF_INET6, host)

def haveSSL(server = False):
    # python < 2.7.9's ssl library does not support ECDSA server due to missing initialisation of available curves, but client works ok
    if server == False:
        return True
    elif sys.version_info >= (2,7,9):
        return True
    return False

def checkSocksIP(host):
    try:
        if socksIP is None or not socksIP:
            socksIP = socket.gethostbyname(config.get("bitmessagesettings", "sockshostname"))
    except NameError:
       socksIP = socket.gethostbyname(config.get("bitmessagesettings", "sockshostname"))
    return socksIP == host
        
def assembleVersionMessage(remoteHost, remotePort, myStreamNumber, server = False):
    payload = ''
    payload += pack('>L', 3)  # protocol version.
    payload += pack('>q', NODE_NETWORK|(NODE_SSL if haveSSL(server) else 0))  # bitflags of the services I offer.
    payload += pack('>q', int(time.time()))

    payload += pack(
        '>q', 1)  # boolservices of remote connection; ignored by the remote host.
    if checkSocksIP(remoteHost) and server: # prevent leaking of tor outbound IP
        payload += encodeHost('127.0.0.1')
        payload += pack('>H', 8444)
    else:
        payload += encodeHost(remoteHost)
        payload += pack('>H', remotePort)  # remote IPv6 and port

    payload += pack('>q', 1)  # bitflags of the services I offer.
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + pack(
        '>L', 2130706433)  # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
    # we have a separate extPort and
    # incoming over clearnet or
    # outgoing through clearnet
    if safeConfigGetBoolean('bitmessagesettings', 'upnp') and extPort \
        and ((server and not checkSocksIP(remoteHost)) or \
        (config.get("bitmessagesettings", "socksproxytype") == "none" and not server)):
        payload += pack('>H', extPort)
    elif checkSocksIP(remoteHost) and server: # incoming connection over Tor
        payload += pack('>H', shared.config.getint('bitmessagesettings', 'onionport'))
    else: # no extPort and not incoming over Tor
        payload += pack('>H', shared.config.getint('bitmessagesettings', 'port'))

    random.seed()
    payload += eightBytesOfRandomDataUsedToDetectConnectionsToSelf
    userAgent = '/PyBitmessage:' + shared.softwareVersion + '/'
    payload += encodeVarint(len(userAgent))
    payload += userAgent
    payload += encodeVarint(
        1)  # The number of streams about which I care. PyBitmessage currently only supports 1 per connection.
    payload += encodeVarint(myStreamNumber)

    return CreatePacket('version', payload)

def assembleErrorMessage(fatal=0, banTime=0, inventoryVector='', errorText=''):
    payload = encodeVarint(fatal)
    payload += encodeVarint(banTime)
    payload += encodeVarint(len(inventoryVector))
    payload += inventoryVector
    payload += encodeVarint(len(errorText))
    payload += errorText
    return CreatePacket('error', payload)

def lookupExeFolder():
    if frozen:
        if frozen == "macosx_app":
            # targetdir/Bitmessage.app/Contents/MacOS/Bitmessage
            exeFolder = path.dirname(path.dirname(path.dirname(path.dirname(sys.executable)))) + path.sep
        else:
            exeFolder = path.dirname(sys.executable) + path.sep
    elif __file__:
        exeFolder = path.dirname(__file__) + path.sep
    else:
        exeFolder = ''
    return exeFolder

def lookupAppdataFolder():
    APPNAME = "PyBitmessage"
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
        dataFolder = path.join(environ['APPDATA'].decode(sys.getfilesystemencoding(), 'ignore'), APPNAME) + path.sep
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
    
def codePath():
    if frozen == "macosx_app":
        codePath = os.environ.get("RESOURCEPATH")
    elif frozen: # windows
        codePath = sys._MEIPASS
    else:    
        codePath = os.path.dirname(__file__)
    return codePath

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

def safeConfigGet(section, option, default = None):
    if config.has_option (section, option):
        return config.get(section, option)
    else:
        return default

def decodeWalletImportFormat(WIFstring):
    fullString = arithmetic.changebase(WIFstring,58,256)
    privkey = fullString[:-4]
    if fullString[-4:] != hashlib.sha256(hashlib.sha256(privkey).digest()).digest()[:4]:
        logger.critical('Major problem! When trying to decode one of your private keys, the checksum '
                     'failed. Here are the first 6 characters of the PRIVATE key: %s' % str(WIFstring)[:6])
        os._exit(0)
        return ""
    else:
        #checksum passed
        if privkey[0] == '\x80':
            return privkey[1:]
        else:
            logger.critical('Major problem! When trying to decode one of your private keys, the '
                         'checksum passed but the key doesn\'t begin with hex 80. Here is the '
                         'PRIVATE key: %s' % str(WIFstring))
            os._exit(0)
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
                    privEncryptionKey = hexlify(decodeWalletImportFormat(
                            config.get(addressInKeysFile, 'privencryptionkey')))

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
            MyECSubscriptionCryptorObjects[hash] = highlevelcrypto.makeCryptor(hexlify(privEncryptionKey))
        else:
            doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(encodeVarint(
                addressVersionNumber) + encodeVarint(streamNumber) + hash).digest()).digest()
            tag = doubleHashOfAddressData[32:]
            privEncryptionKey = doubleHashOfAddressData[:32]
            MyECSubscriptionCryptorObjects[tag] = highlevelcrypto.makeCryptor(hexlify(privEncryptionKey))

def isProofOfWorkSufficient(data,
                            nonceTrialsPerByte=0,
                            payloadLengthExtraBytes=0):
    if nonceTrialsPerByte < networkDefaultProofOfWorkNonceTrialsPerByte:
        nonceTrialsPerByte = networkDefaultProofOfWorkNonceTrialsPerByte
    if payloadLengthExtraBytes < networkDefaultPayloadLengthExtraBytes:
        payloadLengthExtraBytes = networkDefaultPayloadLengthExtraBytes
    endOfLifeTime, = unpack('>Q', data[8:16])
    TTL = endOfLifeTime - int(time.time())
    if TTL < 300:
        TTL = 300
    POW, = unpack('>Q', hashlib.sha512(hashlib.sha512(data[
                  :8] + hashlib.sha512(data[8:]).digest()).digest()).digest()[0:8])
    return POW <= 2 ** 64 / (nonceTrialsPerByte*(len(data) + payloadLengthExtraBytes + ((TTL*(len(data)+payloadLengthExtraBytes))/(2 ** 16))))

def doCleanShutdown():
    global shutdown, thisapp
    shutdown = 1 #Used to tell proof of work worker threads and the objectProcessorThread to exit.
    broadcastToSendDataQueues((0, 'shutdown', 'no data'))   
    objectProcessorQueue.put(('checkShutdownVariable', 'no data'))
    for thread in threading.enumerate():
        if thread.isAlive() and isinstance(thread, StoppableThread):
            thread.stopThread()
    
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

    logger.info('Flushing inventory in memory out to disk...')
    UISignalQueue.put((
        'updateStatusBar',
        'Flushing inventory in memory out to disk. This should normally only take a second...'))
    inventory.flush()

    # Verify that the objectProcessor has finished exiting. It should have incremented the 
    # shutdown variable from 1 to 2. This must finish before we command the sqlThread to exit.
    while shutdown == 1:
        time.sleep(.1)
    
    # This one last useless query will guarantee that the previous flush committed and that the
    # objectProcessorThread committed before we close the program.
    sqlQuery('SELECT address FROM subscriptions')
    logger.info('Finished flushing inventory.')
    sqlStoredProcedure('exit')
    
    # Wait long enough to guarantee that any running proof of work worker threads will check the
    # shutdown variable and exit. If the main thread closes before they do then they won't stop.
    time.sleep(.25)
    
    from class_outgoingSynSender import outgoingSynSender
    for thread in threading.enumerate():
        if thread is not threading.currentThread() and isinstance(thread, StoppableThread) and not isinstance(thread, outgoingSynSender):
            logger.debug("Waiting for thread %s", thread.name)
            thread.join()

    if safeConfigGetBoolean('bitmessagesettings','daemon'):
        logger.info('Clean shutdown complete.')
        thisapp.cleanup()
        os._exit(0)
    else:
        logger.info('Core shutdown complete.')

# If you want to command all of the sendDataThreads to do something, like shutdown or send some data, this
# function puts your data into the queues for each of the sendDataThreads. The sendDataThreads are
# responsible for putting their queue into (and out of) the sendDataQueues list.
def broadcastToSendDataQueues(data):
    # logger.debug('running broadcastToSendDataQueues')
    for q in sendDataQueues:
        q.put(data)

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
    elif sys.platform[:7] == 'freebsd':
        # FreeBSD file systems are the same as major Linux file systems
        present_permissions = os.stat(filename)[0]
        disallowed_permissions = stat.S_IRWXG | stat.S_IRWXO
        return present_permissions & disallowed_permissions == 0
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


def decryptAndCheckPubkeyPayload(data, address):
    """
    Version 4 pubkeys are encrypted. This function is run when we already have the 
    address to which we want to try to send a message. The 'data' may come either
    off of the wire or we might have had it already in our inventory when we tried
    to send a msg to this particular address. 
    """
    try:
        status, addressVersion, streamNumber, ripe = decodeAddress(address)
        
        readPosition = 20  # bypass the nonce, time, and object type
        embeddedAddressVersion, varintLength = decodeVarint(data[readPosition:readPosition + 10])
        readPosition += varintLength
        embeddedStreamNumber, varintLength = decodeVarint(data[readPosition:readPosition + 10])
        readPosition += varintLength
        storedData = data[20:readPosition] # We'll store the address version and stream number (and some more) in the pubkeys table.
        
        if addressVersion != embeddedAddressVersion:
            logger.info('Pubkey decryption was UNsuccessful due to address version mismatch.')
            return 'failed'
        if streamNumber != embeddedStreamNumber:
            logger.info('Pubkey decryption was UNsuccessful due to stream number mismatch.')
            return 'failed'
        
        tag = data[readPosition:readPosition + 32]
        readPosition += 32
        signedData = data[8:readPosition] # the time through the tag. More data is appended onto signedData below after the decryption. 
        encryptedData = data[readPosition:]
    
        # Let us try to decrypt the pubkey
        toAddress, cryptorObject = shared.neededPubkeys[tag]
        if toAddress != address:
            logger.critical('decryptAndCheckPubkeyPayload failed due to toAddress mismatch. This is very peculiar. toAddress: %s, address %s' % (toAddress, address))
            # the only way I can think that this could happen is if someone encodes their address data two different ways.
            # That sort of address-malleability should have been caught by the UI or API and an error given to the user. 
            return 'failed'
        try:
            decryptedData = cryptorObject.decrypt(encryptedData)
        except:
            # Someone must have encrypted some data with a different key
            # but tagged it with a tag for which we are watching.
            logger.info('Pubkey decryption was unsuccessful.')
            return 'failed'
        
        readPosition = 0
        bitfieldBehaviors = decryptedData[readPosition:readPosition + 4]
        readPosition += 4
        publicSigningKey = '\x04' + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        publicEncryptionKey = '\x04' + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        specifiedNonceTrialsPerByte, specifiedNonceTrialsPerByteLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += specifiedNonceTrialsPerByteLength
        specifiedPayloadLengthExtraBytes, specifiedPayloadLengthExtraBytesLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += specifiedPayloadLengthExtraBytesLength
        storedData += decryptedData[:readPosition]
        signedData += decryptedData[:readPosition]
        signatureLength, signatureLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
        readPosition += signatureLengthLength
        signature = decryptedData[readPosition:readPosition + signatureLength]
        
        if highlevelcrypto.verify(signedData, signature, hexlify(publicSigningKey)):
            logger.info('ECDSA verify passed (within decryptAndCheckPubkeyPayload)')
        else:
            logger.info('ECDSA verify failed (within decryptAndCheckPubkeyPayload)')
            return 'failed'
    
        sha = hashlib.new('sha512')
        sha.update(publicSigningKey + publicEncryptionKey)
        ripeHasher = hashlib.new('ripemd160')
        ripeHasher.update(sha.digest())
        embeddedRipe = ripeHasher.digest()
    
        if embeddedRipe != ripe:
            # Although this pubkey object had the tag were were looking for and was
            # encrypted with the correct encryption key, it doesn't contain the
            # correct pubkeys. Someone is either being malicious or using buggy software.
            logger.info('Pubkey decryption was UNsuccessful due to RIPE mismatch.')
            return 'failed'
        
        # Everything checked out. Insert it into the pubkeys table.
        
        logger.info('within decryptAndCheckPubkeyPayload, addressVersion: %s, streamNumber: %s \n\
                    ripe %s\n\
                    publicSigningKey in hex: %s\n\
                    publicEncryptionKey in hex: %s' % (addressVersion,
                                                       streamNumber, 
                                                       hexlify(ripe),
                                                       hexlify(publicSigningKey),
                                                       hexlify(publicEncryptionKey)
                                                       )
                    )
    
        t = (address, addressVersion, storedData, int(time.time()), 'yes')
        sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
        return 'successful'
    except varintDecodeError as e:
        logger.info('Pubkey decryption was UNsuccessful due to a malformed varint.')
        return 'failed'
    except Exception as e:
        logger.critical('Pubkey decryption was UNsuccessful because of an unhandled exception! This is definitely a bug! \n%s' % traceback.format_exc())
        return 'failed'

Peer = collections.namedtuple('Peer', ['host', 'port'])

def checkAndShareObjectWithPeers(data):
    """
    This function is called after either receiving an object off of the wire
    or after receiving one as ackdata. 
    Returns the length of time that we should reserve to process this message
    if we are receiving it off of the wire.
    """
    if len(data) > 2 ** 18:
        logger.info('The payload length of this object is too large (%s bytes). Ignoring it.' % len(data))
        return 0
    # Let us check to make sure that the proof of work is sufficient.
    if not isProofOfWorkSufficient(data):
        logger.info('Proof of work is insufficient.')
        return 0
    
    endOfLifeTime, = unpack('>Q', data[8:16])
    if endOfLifeTime - int(time.time()) > 28 * 24 * 60 * 60 + 10800: # The TTL may not be larger than 28 days + 3 hours of wiggle room
        logger.info('This object\'s End of Life time is too far in the future. Ignoring it. Time is %s' % endOfLifeTime)
        return 0
    if endOfLifeTime - int(time.time()) < - 3600: # The EOL time was more than an hour ago. That's too much.
        logger.info('This object\'s End of Life time was more than an hour ago. Ignoring the object. Time is %s' % endOfLifeTime)
        return 0
    intObjectType, = unpack('>I', data[16:20])
    try:
        if intObjectType == 0:
            _checkAndShareGetpubkeyWithPeers(data)
            return 0.1
        elif intObjectType == 1:
            _checkAndSharePubkeyWithPeers(data)
            return 0.1
        elif intObjectType == 2:
            _checkAndShareMsgWithPeers(data)
            return 0.6
        elif intObjectType == 3:
            _checkAndShareBroadcastWithPeers(data)
            return 0.6
        else:
            _checkAndShareUndefinedObjectWithPeers(data)
            return 0.6
    except varintDecodeError as e:
        logger.debug("There was a problem with a varint while checking to see whether it was appropriate to share an object with peers. Some details: %s" % e)
    except Exception as e:
        logger.critical('There was a problem while checking to see whether it was appropriate to share an object with peers. This is definitely a bug! \n%s' % traceback.format_exc())
    return 0
        

def _checkAndShareUndefinedObjectWithPeers(data):
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20 # bypass nonce, time, and object type
    objectVersion, objectVersionLength = decodeVarint(
        data[readPosition:readPosition + 9])
    readPosition += objectVersionLength
    streamNumber, streamNumberLength = decodeVarint(
        data[readPosition:readPosition + 9])
    if not streamNumber in streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.' % streamNumber)
        return
    
    inventoryHash = calculateInventoryHash(data)
    shared.numberOfInventoryLookupsPerformed += 1
    inventoryLock.acquire()
    if inventoryHash in inventory:
        logger.debug('We have already received this undefined object. Ignoring.')
        inventoryLock.release()
        return
    objectType, = unpack('>I', data[16:20])
    inventory[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime,'')
    inventoryLock.release()
    logger.debug('advertising inv with hash: %s' % hexlify(inventoryHash))
    broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))
    
    
def _checkAndShareMsgWithPeers(data):
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20 # bypass nonce, time, and object type
    objectVersion, objectVersionLength = decodeVarint(
        data[readPosition:readPosition + 9])
    readPosition += objectVersionLength
    streamNumber, streamNumberLength = decodeVarint(
        data[readPosition:readPosition + 9])
    if not streamNumber in streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.' % streamNumber)
        return
    readPosition += streamNumberLength
    inventoryHash = calculateInventoryHash(data)
    shared.numberOfInventoryLookupsPerformed += 1
    inventoryLock.acquire()
    if inventoryHash in inventory:
        logger.debug('We have already received this msg message. Ignoring.')
        inventoryLock.release()
        return
    # This msg message is valid. Let's let our peers know about it.
    objectType = 2
    inventory[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime,'')
    inventoryLock.release()
    logger.debug('advertising inv with hash: %s' % hexlify(inventoryHash))
    broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))

    # Now let's enqueue it to be processed ourselves.
    objectProcessorQueue.put((objectType,data))

def _checkAndShareGetpubkeyWithPeers(data):
    if len(data) < 42:
        logger.info('getpubkey message doesn\'t contain enough data. Ignoring.')
        return
    if len(data) > 200:
        logger.info('getpubkey is abnormally long. Sanity check failed. Ignoring object.')
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass the nonce, time, and object type
    requestedAddressVersionNumber, addressVersionLength = decodeVarint(
        data[readPosition:readPosition + 10])
    readPosition += addressVersionLength
    streamNumber, streamNumberLength = decodeVarint(
        data[readPosition:readPosition + 10])
    if not streamNumber in streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.' % streamNumber)
        return
    readPosition += streamNumberLength

    shared.numberOfInventoryLookupsPerformed += 1
    inventoryHash = calculateInventoryHash(data)
    inventoryLock.acquire()
    if inventoryHash in inventory:
        logger.debug('We have already received this getpubkey request. Ignoring it.')
        inventoryLock.release()
        return

    objectType = 0
    inventory[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime,'')
    inventoryLock.release()
    # This getpubkey request is valid. Forward to peers.
    logger.debug('advertising inv with hash: %s' % hexlify(inventoryHash))
    broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))

    # Now let's queue it to be processed ourselves.
    objectProcessorQueue.put((objectType,data))

def _checkAndSharePubkeyWithPeers(data):
    if len(data) < 146 or len(data) > 440:  # sanity check
        return
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass the nonce, time, and object type
    addressVersion, varintLength = decodeVarint(
        data[readPosition:readPosition + 10])
    readPosition += varintLength
    streamNumber, varintLength = decodeVarint(
        data[readPosition:readPosition + 10])
    readPosition += varintLength
    if not streamNumber in streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.' % streamNumber)
        return
    if addressVersion >= 4:
        tag = data[readPosition:readPosition + 32]
        logger.debug('tag in received pubkey is: %s' % hexlify(tag))
    else:
        tag = ''

    shared.numberOfInventoryLookupsPerformed += 1
    inventoryHash = calculateInventoryHash(data)
    inventoryLock.acquire()
    if inventoryHash in inventory:
        logger.debug('We have already received this pubkey. Ignoring it.')
        inventoryLock.release()
        return
    objectType = 1
    inventory[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, tag)
    inventoryLock.release()
    # This object is valid. Forward it to peers.
    logger.debug('advertising inv with hash: %s' % hexlify(inventoryHash))
    broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))


    # Now let's queue it to be processed ourselves.
    objectProcessorQueue.put((objectType,data))


def _checkAndShareBroadcastWithPeers(data):
    if len(data) < 180:
        logger.debug('The payload length of this broadcast packet is unreasonably low. Someone is probably trying funny business. Ignoring message.')
        return
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass the nonce, time, and object type
    broadcastVersion, broadcastVersionLength = decodeVarint(
        data[readPosition:readPosition + 10])
    readPosition += broadcastVersionLength
    if broadcastVersion >= 2:
        streamNumber, streamNumberLength = decodeVarint(data[readPosition:readPosition + 10])
        readPosition += streamNumberLength
        if not streamNumber in streamsInWhichIAmParticipating:
            logger.debug('The streamNumber %s isn\'t one we are interested in.' % streamNumber)
            return
    if broadcastVersion >= 3:
        tag = data[readPosition:readPosition+32]
    else:
        tag = ''
    shared.numberOfInventoryLookupsPerformed += 1
    inventoryLock.acquire()
    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in inventory:
        logger.debug('We have already received this broadcast object. Ignoring.')
        inventoryLock.release()
        return
    # It is valid. Let's let our peers know about it.
    objectType = 3
    inventory[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, tag)
    inventoryLock.release()
    # This object is valid. Forward it to peers.
    logger.debug('advertising inv with hash: %s' % hexlify(inventoryHash))
    broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))

    # Now let's queue it to be processed ourselves.
    objectProcessorQueue.put((objectType,data))

def openKeysFile():
    if 'linux' in sys.platform:
        subprocess.call(["xdg-open", shared.appdata + 'keys.dat'])
    else:
        os.startfile(shared.appdata + 'keys.dat')

def writeKeysFile():
    fileName = shared.appdata + 'keys.dat'
    fileNameBak = fileName + "." + datetime.datetime.now().strftime("%Y%j%H%M%S%f") + '.bak'
    # create a backup copy to prevent the accidental loss due to the disk write failure
    try:
        shutil.copyfile(fileName, fileNameBak)
        # The backup succeeded.
        fileNameExisted = True
    except:
        # The backup failed. This can happen if the file didn't exist before.
        fileNameExisted = False
    # write the file
    with open(fileName, 'wb') as configfile:
        shared.config.write(configfile)
    # delete the backup
    if fileNameExisted:
        os.remove(fileNameBak)

from debug import logger
