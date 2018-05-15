from __future__ import division

# Libraries.
import os
import sys
import stat
import time
import threading
import traceback
import hashlib
import subprocess
from struct import unpack
from binascii import hexlify
from pyelliptic import arithmetic

# Project imports.
import protocol
import state
import highlevelcrypto
from bmconfigparser import BMConfigParser
from debug import logger
from addresses import (
    decodeAddress, encodeVarint, decodeVarint, varintDecodeError,
    calculateInventoryHash
)
from helper_sql import sqlQuery, sqlExecute
from inventory import Inventory
from queues import objectProcessorQueue


verbose = 1
# This is obsolete with the change to protocol v3
# but the singleCleaner thread still hasn't been updated
# so we need this a little longer.
maximumAgeOfAnObjectThatIAmWillingToAccept = 216000
# Equals 4 weeks. You could make this longer if you want
# but making it shorter would not be advisable because
# there is a very small possibility that it could keep you
# from obtaining a needed pubkey for a period of time.
lengthOfTimeToHoldOnToAllPubkeys = 2419200
maximumAgeOfNodesThatIAdvertiseToOthers = 10800  # Equals three hours
# If you set this to True while on the normal network,
# you won't be able to send or sometimes receive messages.
useVeryEasyProofOfWorkForTesting = False


myECCryptorObjects = {}
MyECSubscriptionCryptorObjects = {}
# The key in this dictionary is the RIPE hash which is encoded
# in an address and value is the address itself.
myAddressesByHash = {}
# The key in this dictionary is the tag generated from the address.
myAddressesByTag = {}
broadcastSendersForWhichImWatching = {}
printLock = threading.Lock()
statusIconColor = 'red'
# List of hosts to which we are connected. Used to guarantee
# that the outgoingSynSender threads won't connect to the same
# remote node twice.
connectedHostsList = {}
thisapp = None  # singleton lock instance
alreadyAttemptedConnectionsList = {
}  # This is a list of nodes to which we have already attempted a connection
alreadyAttemptedConnectionsListLock = threading.Lock()
# used to clear out the alreadyAttemptedConnectionsList periodically
# so that we will retry connecting to hosts to which we have already
# tried to connect.
alreadyAttemptedConnectionsListResetTime = int(time.time())
# A list of the amounts of time it took to successfully decrypt msg messages
successfullyDecryptMessageTimings = []
ackdataForWhichImWatching = {}
# used by API command clientStatus
clientHasReceivedIncomingConnections = False
numberOfMessagesProcessed = 0
numberOfBroadcastsProcessed = 0
numberOfPubkeysProcessed = 0

# If True, the singleCleaner will write it to disk eventually.
needToWriteKnownNodesToDisk = False

maximumLengthOfTimeToBotherResendingMessages = 0
timeOffsetWrongCount = 0


def isAddressInMyAddressBook(address):
    queryreturn = sqlQuery(
        '''select address from addressbook where address=?''',
        address)
    return queryreturn != []


# At this point we should really just have a isAddressInMy(book, address)...
def isAddressInMySubscriptionsList(address):
    queryreturn = sqlQuery(
        '''select * from subscriptions where address=?''',
        str(address))
    return queryreturn != []


def isAddressInMyAddressBookSubscriptionsListOrWhitelist(address):
    if isAddressInMyAddressBook(address):
        return True

    queryreturn = sqlQuery(
        '''SELECT address FROM whitelist where address=?'''
        ''' and enabled = '1' ''',
        address)
    if queryreturn != []:
        return True

    queryreturn = sqlQuery(
        '''select address from subscriptions where address=?'''
        ''' and enabled = '1' ''',
        address)
    if queryreturn != []:
        return True
    return False


def decodeWalletImportFormat(WIFstring):
    fullString = arithmetic.changebase(WIFstring, 58, 256)
    privkey = fullString[:-4]
    if fullString[-4:] != \
       hashlib.sha256(hashlib.sha256(privkey).digest()).digest()[:4]:
        logger.critical(
            'Major problem! When trying to decode one of your'
            ' private keys, the checksum failed. Here are the first'
            ' 6 characters of the PRIVATE key: %s',
            str(WIFstring)[:6]
        )
        os._exit(0)
        # return ""
    elif privkey[0] == '\x80':  # checksum passed
        return privkey[1:]

    logger.critical(
        'Major problem! When trying to decode one of your  private keys,'
        ' the checksum passed but the key doesn\'t begin with hex 80.'
        ' Here is the PRIVATE key: %s', WIFstring
    )
    os._exit(0)


def reloadMyAddressHashes():
    logger.debug('reloading keys from keys.dat file')
    myECCryptorObjects.clear()
    myAddressesByHash.clear()
    myAddressesByTag.clear()
    # myPrivateKeys.clear()

    keyfileSecure = checkSensitiveFilePermissions(state.appdata + 'keys.dat')
    hasEnabledKeys = False
    for addressInKeysFile in BMConfigParser().addresses():
        isEnabled = BMConfigParser().getboolean(addressInKeysFile, 'enabled')
        if isEnabled:
            hasEnabledKeys = True
            # status
            _, addressVersionNumber, streamNumber, hash = \
                decodeAddress(addressInKeysFile)
            if addressVersionNumber in (2, 3, 4):
                # Returns a simple 32 bytes of information encoded
                # in 64 Hex characters, or null if there was an error.
                privEncryptionKey = hexlify(decodeWalletImportFormat(
                    BMConfigParser().get(addressInKeysFile, 'privencryptionkey'))
                )

                # It is 32 bytes encoded as 64 hex characters
                if len(privEncryptionKey) == 64:
                    myECCryptorObjects[hash] = \
                        highlevelcrypto.makeCryptor(privEncryptionKey)
                    myAddressesByHash[hash] = addressInKeysFile
                    tag = hashlib.sha512(hashlib.sha512(
                        encodeVarint(addressVersionNumber) +
                        encodeVarint(streamNumber) + hash).digest()
                    ).digest()[32:]
                    myAddressesByTag[tag] = addressInKeysFile

            else:
                logger.error(
                    'Error in reloadMyAddressHashes: Can\'t handle'
                    ' address versions other than 2, 3, or 4.\n'
                )

    if not keyfileSecure:
        fixSensitiveFilePermissions(state.appdata + 'keys.dat', hasEnabledKeys)


def reloadBroadcastSendersForWhichImWatching():
    broadcastSendersForWhichImWatching.clear()
    MyECSubscriptionCryptorObjects.clear()
    queryreturn = sqlQuery('SELECT address FROM subscriptions where enabled=1')
    logger.debug('reloading subscriptions...')
    for row in queryreturn:
        address, = row
        # status
        _, addressVersionNumber, streamNumber, hash = decodeAddress(address)
        if addressVersionNumber == 2:
            broadcastSendersForWhichImWatching[hash] = 0
        # Now, for all addresses, even version 2 addresses,
        # we should create Cryptor objects in a dictionary which we will
        # use to attempt to decrypt encrypted broadcast messages.

        if addressVersionNumber <= 3:
            privEncryptionKey = hashlib.sha512(
                encodeVarint(addressVersionNumber) +
                encodeVarint(streamNumber) + hash
            ).digest()[:32]
            MyECSubscriptionCryptorObjects[hash] = \
                highlevelcrypto.makeCryptor(hexlify(privEncryptionKey))
        else:
            doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(
                encodeVarint(addressVersionNumber) +
                encodeVarint(streamNumber) + hash
            ).digest()).digest()
            tag = doubleHashOfAddressData[32:]
            privEncryptionKey = doubleHashOfAddressData[:32]
            MyECSubscriptionCryptorObjects[tag] = \
                highlevelcrypto.makeCryptor(hexlify(privEncryptionKey))


def fixPotentiallyInvalidUTF8Data(text):
    try:
        unicode(text, 'utf-8')
        return text
    except:
        return 'Part of the message is corrupt. The message cannot be' \
           ' displayed the normal way.\n\n' + repr(text)


# Checks sensitive file permissions for inappropriate umask
# during keys.dat creation. (Or unwise subsequent chmod.)
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
            # Skip known problems for non-Win32 filesystems
            # without POSIX permissions.
            fstype = subprocess.check_output(
                'stat -f -c "%%T" %s' % (filename),
                shell=True,
                stderr=subprocess.STDOUT
            )
            if 'fuseblk' in fstype:
                logger.info(
                    'Skipping file permissions check for %s.'
                    ' Filesystem fuseblk detected.', filename)
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
        logger.warning(
            'Keyfile had insecure permissions, and there were enabled'
            ' keys. The truly paranoid should stop using them immediately.')
    else:
        logger.warning(
            'Keyfile had insecure permissions, but there were no enabled keys.'
        )
    try:
        present_permissions = os.stat(filename)[0]
        disallowed_permissions = stat.S_IRWXG | stat.S_IRWXO
        allowed_permissions = ((1 << 32) - 1) ^ disallowed_permissions
        new_permissions = (
            allowed_permissions & present_permissions)
        os.chmod(filename, new_permissions)

        logger.info('Keyfile permissions automatically fixed.')

    except Exception:
        logger.exception('Keyfile permissions could not be fixed.')
        raise


def isBitSetWithinBitfield(fourByteString, n):
    # Uses MSB 0 bit numbering across 4 bytes of data
    n = 31 - n
    x, = unpack('>L', fourByteString)
    return x & 2**n != 0


def decryptAndCheckPubkeyPayload(data, address):
    """
    Version 4 pubkeys are encrypted. This function is run when we
    already have the address to which we want to try to send a message.
    The 'data' may come either off of the wire or we might have had it
    already in our inventory when we tried to send a msg to this
    particular address.
    """
    try:
        # status
        _, addressVersion, streamNumber, ripe = decodeAddress(address)

        readPosition = 20  # bypass the nonce, time, and object type
        embeddedAddressVersion, varintLength = \
            decodeVarint(data[readPosition:readPosition + 10])
        readPosition += varintLength
        embeddedStreamNumber, varintLength = \
            decodeVarint(data[readPosition:readPosition + 10])
        readPosition += varintLength
        # We'll store the address version and stream number
        # (and some more) in the pubkeys table.
        storedData = data[20:readPosition]

        if addressVersion != embeddedAddressVersion:
            logger.info(
                'Pubkey decryption was UNsuccessful'
                ' due to address version mismatch.')
            return 'failed'
        if streamNumber != embeddedStreamNumber:
            logger.info(
                'Pubkey decryption was UNsuccessful'
                ' due to stream number mismatch.')
            return 'failed'

        tag = data[readPosition:readPosition + 32]
        readPosition += 32
        # the time through the tag. More data is appended onto
        # signedData below after the decryption.
        signedData = data[8:readPosition]
        encryptedData = data[readPosition:]

        # Let us try to decrypt the pubkey
        toAddress, cryptorObject = state.neededPubkeys[tag]
        if toAddress != address:
            logger.critical(
                'decryptAndCheckPubkeyPayload failed due to toAddress'
                ' mismatch. This is very peculiar.'
                ' toAddress: %s, address %s',
                toAddress, address
            )
            # the only way I can think that this could happen
            # is if someone encodes their address data two different ways.
            # That sort of address-malleability should have been caught
            # by the UI or API and an error given to the user.
            return 'failed'
        try:
            decryptedData = cryptorObject.decrypt(encryptedData)
        except:
            # Someone must have encrypted some data with a different key
            # but tagged it with a tag for which we are watching.
            logger.info('Pubkey decryption was unsuccessful.')
            return 'failed'

        readPosition = 0
        # bitfieldBehaviors = decryptedData[readPosition:readPosition + 4]
        readPosition += 4
        publicSigningKey = \
            '\x04' + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        publicEncryptionKey = \
            '\x04' + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        specifiedNonceTrialsPerByte, specifiedNonceTrialsPerByteLength = \
            decodeVarint(decryptedData[readPosition:readPosition + 10])
        readPosition += specifiedNonceTrialsPerByteLength
        specifiedPayloadLengthExtraBytes, \
            specifiedPayloadLengthExtraBytesLength = \
            decodeVarint(decryptedData[readPosition:readPosition + 10])
        readPosition += specifiedPayloadLengthExtraBytesLength
        storedData += decryptedData[:readPosition]
        signedData += decryptedData[:readPosition]
        signatureLength, signatureLengthLength = \
            decodeVarint(decryptedData[readPosition:readPosition + 10])
        readPosition += signatureLengthLength
        signature = decryptedData[readPosition:readPosition + signatureLength]

        if not highlevelcrypto.verify(
                signedData, signature, hexlify(publicSigningKey)):
            logger.info(
                'ECDSA verify failed (within decryptAndCheckPubkeyPayload)')
            return 'failed'

        logger.info(
            'ECDSA verify passed (within decryptAndCheckPubkeyPayload)')

        sha = hashlib.new('sha512')
        sha.update(publicSigningKey + publicEncryptionKey)
        ripeHasher = hashlib.new('ripemd160')
        ripeHasher.update(sha.digest())
        embeddedRipe = ripeHasher.digest()

        if embeddedRipe != ripe:
            # Although this pubkey object had the tag were were looking for
            # and was encrypted with the correct encryption key,
            # it doesn't contain the correct pubkeys. Someone is
            # either being malicious or using buggy software.
            logger.info(
                'Pubkey decryption was UNsuccessful due to RIPE mismatch.')
            return 'failed'

        # Everything checked out. Insert it into the pubkeys table.

        logger.info(
            'within decryptAndCheckPubkeyPayload, '
            'addressVersion: %s, streamNumber: %s\nripe %s\n'
            'publicSigningKey in hex: %s\npublicEncryptionKey in hex: %s',
            addressVersion, streamNumber, hexlify(ripe),
            hexlify(publicSigningKey), hexlify(publicEncryptionKey)
        )

        t = (address, addressVersion, storedData, int(time.time()), 'yes')
        sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
        return 'successful'
    except varintDecodeError:
        logger.info(
            'Pubkey decryption was UNsuccessful due to a malformed varint.')
        return 'failed'
    except Exception:
        logger.critical(
            'Pubkey decryption was UNsuccessful because of'
            ' an unhandled exception! This is definitely a bug! \n%s' %
            traceback.format_exc()
        )
        return 'failed'


def checkAndShareObjectWithPeers(data):
    """
    This function is called after either receiving an object
    off of the wire or after receiving one as ackdata.
    Returns the length of time that we should reserve to process
    this message if we are receiving it off of the wire.
    """
    if len(data) > 2 ** 18:
        logger.info(
            'The payload length of this object is too large (%i bytes).'
            ' Ignoring it.', len(data)
        )
        return 0
    # Let us check to make sure that the proof of work is sufficient.
    if not protocol.isProofOfWorkSufficient(data):
        logger.info('Proof of work is insufficient.')
        return 0

    endOfLifeTime, = unpack('>Q', data[8:16])
    # The TTL may not be larger than 28 days + 3 hours of wiggle room
    if endOfLifeTime - int(time.time()) > 28 * 24 * 60 * 60 + 10800:
        logger.info(
            'This object\'s End of Life time is too far in the future.'
            ' Ignoring it. Time is %s', endOfLifeTime
        )
        return 0
    # The EOL time was more than an hour ago. That's too much.
    if endOfLifeTime - int(time.time()) < -3600:
        logger.info(
            'This object\'s End of Life time was more than an hour ago.'
            ' Ignoring the object. Time is %s' % endOfLifeTime
        )
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
        logger.debug(
            'There was a problem with a varint while checking'
            ' to see whether it was appropriate to share an object'
            ' with peers. Some details: %s' % e)
    except Exception:
        logger.critical(
            'There was a problem while checking to see whether it was'
            ' appropriate to share an object with peers. This is'
            ' definitely a bug! \n%s' % traceback.format_exc())
    return 0


def _checkAndShareUndefinedObjectWithPeers(data):
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass nonce, time, and object type
    objectVersion, objectVersionLength = decodeVarint(
        data[readPosition:readPosition + 9])
    readPosition += objectVersionLength
    streamNumber, streamNumberLength = decodeVarint(
        data[readPosition:readPosition + 9])
    if streamNumber not in state.streamsInWhichIAmParticipating:
        logger.debug(
            'The streamNumber %i isn\'t one we are interested in.',
            streamNumber
        )
        return

    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug(
            'We have already received this undefined object. Ignoring.')
        return
    objectType, = unpack('>I', data[16:20])
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, '')
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
    protocol.broadcastToSendDataQueues(
        (streamNumber, 'advertiseobject', inventoryHash))


def _checkAndShareMsgWithPeers(data):
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass nonce, time, and object type
    objectVersion, objectVersionLength = \
        decodeVarint(data[readPosition:readPosition + 9])
    readPosition += objectVersionLength
    streamNumber, streamNumberLength = \
        decodeVarint(data[readPosition:readPosition + 9])
    if streamNumber not in state.streamsInWhichIAmParticipating:
        logger.debug(
            'The streamNumber %i isn\'t one we are interested in.',
            streamNumber
        )
        return
    readPosition += streamNumberLength
    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug('We have already received this msg message. Ignoring.')
        return
    # This msg message is valid. Let's let our peers know about it.
    objectType = 2
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, '')
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
    protocol.broadcastToSendDataQueues(
        (streamNumber, 'advertiseobject', inventoryHash))

    # Now let's enqueue it to be processed ourselves.
    objectProcessorQueue.put((objectType, data))


def _checkAndShareGetpubkeyWithPeers(data):
    if len(data) < 42:
        logger.info(
            'getpubkey message doesn\'t contain enough data. Ignoring.')
        return
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass the nonce, time, and object type
    requestedAddressVersionNumber, addressVersionLength = \
        decodeVarint(data[readPosition:readPosition + 10])
    readPosition += addressVersionLength
    streamNumber, streamNumberLength = \
        decodeVarint(data[readPosition:readPosition + 10])
    if streamNumber not in state.streamsInWhichIAmParticipating:
        logger.debug(
            'The streamNumber %i isn\'t one we are interested in.',
            streamNumber
        )
        return
    readPosition += streamNumberLength

    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug(
            'We have already received this getpubkey request. Ignoring it.')
        return

    objectType = 0
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, '')
    # This getpubkey request is valid. Forward to peers.
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
    protocol.broadcastToSendDataQueues(
        (streamNumber, 'advertiseobject', inventoryHash))

    # Now let's queue it to be processed ourselves.
    objectProcessorQueue.put((objectType, data))


def _checkAndSharePubkeyWithPeers(data):
    if len(data) < 146 or len(data) > 440:  # sanity check
        return
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass the nonce, time, and object type
    addressVersion, varintLength = \
        decodeVarint(data[readPosition:readPosition + 10])
    readPosition += varintLength
    streamNumber, varintLength = \
        decodeVarint(data[readPosition:readPosition + 10])
    readPosition += varintLength
    if streamNumber not in state.streamsInWhichIAmParticipating:
        logger.debug(
            'The streamNumber %i isn\'t one we are interested in.',
            streamNumber
        )
        return
    if addressVersion >= 4:
        tag = data[readPosition:readPosition + 32]
        logger.debug('tag in received pubkey is: %s', hexlify(tag))
    else:
        tag = ''

    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug('We have already received this pubkey. Ignoring it.')
        return
    objectType = 1
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, tag)
    # This object is valid. Forward it to peers.
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
    protocol.broadcastToSendDataQueues(
        (streamNumber, 'advertiseobject', inventoryHash))

    # Now let's queue it to be processed ourselves.
    objectProcessorQueue.put((objectType, data))


def _checkAndShareBroadcastWithPeers(data):
    if len(data) < 180:
        logger.debug(
            'The payload length of this broadcast packet is unreasonably low.'
            ' Someone is probably trying funny business. Ignoring message.')
        return
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20  # bypass the nonce, time, and object type
    broadcastVersion, broadcastVersionLength = \
        decodeVarint(data[readPosition:readPosition + 10])
    readPosition += broadcastVersionLength
    if broadcastVersion >= 2:
        streamNumber, streamNumberLength = \
            decodeVarint(data[readPosition:readPosition + 10])
        readPosition += streamNumberLength
        if streamNumber not in state.streamsInWhichIAmParticipating:
            logger.debug(
                'The streamNumber %i isn\'t one we are interested in.',
                streamNumber
            )
            return
    if broadcastVersion >= 3:
        tag = data[readPosition:readPosition+32]
    else:
        tag = ''
    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug(
            'We have already received this broadcast object. Ignoring.')
        return
    # It is valid. Let's let our peers know about it.
    objectType = 3
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, tag)
    # This object is valid. Forward it to peers.
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
    protocol.broadcastToSendDataQueues(
        (streamNumber, 'advertiseobject', inventoryHash))

    # Now let's queue it to be processed ourselves.
    objectProcessorQueue.put((objectType, data))


def openKeysFile():
    if 'linux' in sys.platform:
        subprocess.call(["xdg-open", state.appdata + 'keys.dat'])
    else:
        os.startfile(state.appdata + 'keys.dat')
