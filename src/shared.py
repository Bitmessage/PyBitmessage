softwareVersion = '0.3.1'

import threading
import sys
from addresses import *
import highlevelcrypto
import Queue
import pickle
import os

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

#If changed, these values will cause particularly unexpected behavior: You won't be able to either send or receive messages because the proof of work you do (or demand) won't match that done or demanded by others. Don't change them!
networkDefaultProofOfWorkNonceTrialsPerByte = 320 #The amount of work that should be performed (and demanded) per byte of the payload. Double this number to double the work.
networkDefaultPayloadLengthExtraBytes = 14000 #To make sending short messages a little more difficult, this value is added to the payload length for use in calculating the proof of work target.

def lookupAppdataFolder():
    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            print 'Could not find home folder, please report this message and your OS X version to the BitMessage Github.'
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
        sys.stderr.write('Major problem! When trying to decode one of your private keys, the checksum failed. Here is the PRIVATE key: %s\n' % str(WIFstring))
        return ""
    else:
        #checksum passed
        if privkey[0] == '\x80':
            return privkey[1:]
        else:
            sys.stderr.write('Major problem! When trying to decode one of your private keys, the checksum passed but the key doesn\'t begin with hex 80. Here is the PRIVATE key: %s\n' % str(WIFstring))
            return ""


def reloadMyAddressHashes():
    printLock.acquire()
    print 'reloading keys from keys.dat file'
    printLock.release()
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
                    privEncryptionKey = decodeWalletImportFormat(config.get(addressInKeysFile, 'privencryptionkey')).encode('hex') #returns a simple 32 bytes of information encoded in 64 Hex characters, or null if there was an error
                    if len(privEncryptionKey) == 64:#It is 32 bytes encoded as 64 hex characters
                        myECCryptorObjects[hash] = highlevelcrypto.makeCryptor(privEncryptionKey)
                        myAddressesByHash[hash] = addressInKeysFile
                else:
                    sys.stderr.write('Error in reloadMyAddressHashes: Can\'t handle address versions other than 2 or 3.\n')

def reloadBroadcastSendersForWhichImWatching():
    printLock.acquire()
    print 'reloading subscriptions...'
    printLock.release()
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
    knownNodesLock.acquire()
    UISignalQueue.put(('updateStatusBar','Saving the knownNodes list of peers to disk...'))
    output = open(appdata + 'knownnodes.dat', 'wb')
    print 'finished opening knownnodes.dat. Now pickle.dump'
    pickle.dump(knownNodes, output)
    print 'Completed pickle.dump. Closing output...'
    output.close()
    knownNodesLock.release()
    printLock.acquire()
    print 'Finished closing knownnodes.dat output file.'
    printLock.release()
    UISignalQueue.put(('updateStatusBar','Done saving the knownNodes list of peers to disk.'))

    broadcastToSendDataQueues((0, 'shutdown', 'all'))

    printLock.acquire()
    print 'Flushing inventory in memory out to disk...'
    printLock.release()
    UISignalQueue.put(('updateStatusBar','Flushing inventory in memory out to disk. This should normally only take a second...'))
    flushInventory()

    #This one last useless query will guarantee that the previous flush committed before we close the program.
    sqlLock.acquire()
    sqlSubmitQueue.put('SELECT address FROM subscriptions')
    sqlSubmitQueue.put('')
    sqlReturnQueue.get()
    sqlSubmitQueue.put('exit')
    sqlLock.release()
    printLock.acquire()
    print 'Finished flushing inventory.'
    printLock.release()
    

    if safeConfigGetBoolean('bitmessagesettings','daemon'):
        printLock.acquire()
        print 'Done.'
        printLock.release()
        os._exit(0)

#Wen you want to command a sendDataThread to do something, like shutdown or send some data, this function puts your data into the queues for each of the sendDataThreads. The sendDataThreads are responsible for putting their queue into (and out of) the sendDataQueues list.
def broadcastToSendDataQueues(data):
    #print 'running broadcastToSendDataQueues'
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