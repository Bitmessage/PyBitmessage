import base64
from binascii import hexlify
import hashlib
import random
import socket
import ssl
from struct import pack, unpack, Struct
import sys
import time
import traceback

from addresses import calculateInventoryHash, encodeVarint, decodeVarint, decodeAddress, varintDecodeError
from bmconfigparser import BMConfigParser
from debug import logger
import defaults
from helper_sql import sqlExecute
import highlevelcrypto
from inventory import Inventory
from queues import objectProcessorQueue
import state
from version import softwareVersion

#Service flags
NODE_NETWORK = 1
NODE_SSL = 2

#Bitfield flags
BITFIELD_DOESACK = 1

eightBytesOfRandomDataUsedToDetectConnectionsToSelf = pack(
    '>Q', random.randrange(1, 18446744073709551615))

#Compiled struct for packing/unpacking headers
#New code should use CreatePacket instead of Header.pack
Header = Struct('!L12sL4s')

# Bitfield

def getBitfield(address):
    # bitfield of features supported by me (see the wiki).
    bitfield = 0
    # send ack
    if not BMConfigParser().safeGetBoolean(address, 'dontsendack'):
        bitfield |= BITFIELD_DOESACK
    return pack('>I', bitfield)

def checkBitfield(bitfieldBinary, flags):
    bitfield, = unpack('>I', bitfieldBinary)
    return (bitfield & flags) == flags

def isBitSetWithinBitfield(fourByteString, n):
    # Uses MSB 0 bit numbering across 4 bytes of data
    n = 31 - n
    x, = unpack('>L', fourByteString)
    return x & 2**n != 0

# data handling

def encodeHost(host):
    if host.find('.onion') > -1:
        return '\xfd\x87\xd8\x7e\xeb\x43' + base64.b32decode(host.split(".")[0], True)
    elif host.find(':') == -1:
        return '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
            socket.inet_aton(host)
    else:
        return socket.inet_pton(socket.AF_INET6, host)

def networkType(host):
    if host.find('.onion') > -1:
        return 'onion'
    elif host.find(':') == -1:
        return 'IPv4'
    else:
        return 'IPv6'

# checks

def haveSSL(server = False):
    # python < 2.7.9's ssl library does not support ECDSA server due to missing initialisation of available curves, but client works ok
    if server == False:
        return True
    elif sys.version_info >= (2,7,9):
        return True
    return False

def checkSocksIP(host):
    try:
        if state.socksIP is None or not state.socksIP:
            state.socksIP = socket.gethostbyname(BMConfigParser().get("bitmessagesettings", "sockshostname"))
    # uninitialised
    except NameError:
        state.socksIP = socket.gethostbyname(BMConfigParser().get("bitmessagesettings", "sockshostname"))
    # resolving failure
    except socket.gaierror:
        state.socksIP = BMConfigParser().get("bitmessagesettings", "sockshostname")
    return state.socksIP == host

def isProofOfWorkSufficient(data,
                            nonceTrialsPerByte=0,
                            payloadLengthExtraBytes=0):
    if nonceTrialsPerByte < defaults.networkDefaultProofOfWorkNonceTrialsPerByte:
        nonceTrialsPerByte = defaults.networkDefaultProofOfWorkNonceTrialsPerByte
    if payloadLengthExtraBytes < defaults.networkDefaultPayloadLengthExtraBytes:
        payloadLengthExtraBytes = defaults.networkDefaultPayloadLengthExtraBytes
    endOfLifeTime, = unpack('>Q', data[8:16])
    TTL = endOfLifeTime - int(time.time())
    if TTL < 300:
        TTL = 300
    POW, = unpack('>Q', hashlib.sha512(hashlib.sha512(data[
                  :8] + hashlib.sha512(data[8:]).digest()).digest()).digest()[0:8])
    return POW <= 2 ** 64 / (nonceTrialsPerByte*(len(data) + payloadLengthExtraBytes + ((TTL*(len(data)+payloadLengthExtraBytes))/(2 ** 16))))

# Packet creation

def CreatePacket(command, payload=''):
    payload_length = len(payload)
    checksum = hashlib.sha512(payload).digest()[0:4]
    
    b = bytearray(Header.size + payload_length)
    Header.pack_into(b, 0, 0xE9BEB4D9, command, payload_length, checksum)
    b[Header.size:] = payload
    return bytes(b)

def assembleVersionMessage(remoteHost, remotePort, participatingStreams, server = False):
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

    payload += pack('>q', NODE_NETWORK|(NODE_SSL if haveSSL(server) else 0))  # bitflags of the services I offer.
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + pack(
        '>L', 2130706433)  # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
    # we have a separate extPort and
    # incoming over clearnet or
    # outgoing through clearnet
    if BMConfigParser().safeGetBoolean('bitmessagesettings', 'upnp') and state.extPort \
        and ((server and not checkSocksIP(remoteHost)) or \
        (BMConfigParser().get("bitmessagesettings", "socksproxytype") == "none" and not server)):
        payload += pack('>H', state.extPort)
    elif checkSocksIP(remoteHost) and server: # incoming connection over Tor
        payload += pack('>H', BMConfigParser().getint('bitmessagesettings', 'onionport'))
    else: # no extPort and not incoming over Tor
        payload += pack('>H', BMConfigParser().getint('bitmessagesettings', 'port'))

    random.seed()
    payload += eightBytesOfRandomDataUsedToDetectConnectionsToSelf
    userAgent = '/PyBitmessage:' + softwareVersion + '/'
    payload += encodeVarint(len(userAgent))
    payload += userAgent

    # Streams
    payload += encodeVarint(len(participatingStreams))
    count = 0
    for stream in sorted(participatingStreams):
        payload += encodeVarint(stream)
        count += 1
        # protocol limit, see specification
        if count >= 160000:
            break

    return CreatePacket('version', payload)

def assembleErrorMessage(fatal=0, banTime=0, inventoryVector='', errorText=''):
    payload = encodeVarint(fatal)
    payload += encodeVarint(banTime)
    payload += encodeVarint(len(inventoryVector))
    payload += inventoryVector
    payload += encodeVarint(len(errorText))
    payload += errorText
    return CreatePacket('error', payload)

# Packet decoding

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
        toAddress, cryptorObject = state.neededPubkeys[tag]
        if toAddress != address:
            logger.critical('decryptAndCheckPubkeyPayload failed due to toAddress mismatch. This is very peculiar. toAddress: %s, address %s', toAddress, address)
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
                    publicEncryptionKey in hex: %s', addressVersion,
                                                       streamNumber, 
                                                       hexlify(ripe),
                                                       hexlify(publicSigningKey),
                                                       hexlify(publicEncryptionKey)
                    )
    
        t = (address, addressVersion, storedData, int(time.time()), 'yes')
        sqlExecute('''INSERT INTO pubkeys VALUES (?,?,?,?,?)''', *t)
        return 'successful'
    except varintDecodeError as e:
        logger.info('Pubkey decryption was UNsuccessful due to a malformed varint.')
        return 'failed'
    except Exception as e:
        logger.critical('Pubkey decryption was UNsuccessful because of an unhandled exception! This is definitely a bug! \n%s', traceback.format_exc())
        return 'failed'

def checkAndShareObjectWithPeers(data):
    """
    This function is called after either receiving an object off of the wire
    or after receiving one as ackdata. 
    Returns the length of time that we should reserve to process this message
    if we are receiving it off of the wire.
    """
    if len(data) > 2 ** 18:
        logger.info('The payload length of this object is too large (%s bytes). Ignoring it.', len(data))
        return 0
    # Let us check to make sure that the proof of work is sufficient.
    if not isProofOfWorkSufficient(data):
        logger.info('Proof of work is insufficient.')
        return 0
    
    endOfLifeTime, = unpack('>Q', data[8:16])
    if endOfLifeTime - int(time.time()) > 28 * 24 * 60 * 60 + 10800: # The TTL may not be larger than 28 days + 3 hours of wiggle room
        logger.info('This object\'s End of Life time is too far in the future. Ignoring it. Time is %s', endOfLifeTime)
        return 0
    if endOfLifeTime - int(time.time()) < - 3600: # The EOL time was more than an hour ago. That's too much.
        logger.info('This object\'s End of Life time was more than an hour ago. Ignoring the object. Time is %s', endOfLifeTime)
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
        logger.debug("There was a problem with a varint while checking to see whether it was appropriate to share an object with peers. Some details: %s", e)
    except Exception as e:
        logger.critical('There was a problem while checking to see whether it was appropriate to share an object with peers. This is definitely a bug! \n%s', traceback.format_exc())
    return 0
        

def _checkAndShareUndefinedObjectWithPeers(data):
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20 # bypass nonce, time, and object type
    objectVersion, objectVersionLength = decodeVarint(
        data[readPosition:readPosition + 9])
    readPosition += objectVersionLength
    streamNumber, streamNumberLength = decodeVarint(
        data[readPosition:readPosition + 9])
    if not streamNumber in state.streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.', streamNumber)
        return
    
    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug('We have already received this undefined object. Ignoring.')
        return
    objectType, = unpack('>I', data[16:20])
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime,'')
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
    broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))
    
    
def _checkAndShareMsgWithPeers(data):
    embeddedTime, = unpack('>Q', data[8:16])
    readPosition = 20 # bypass nonce, time, and object type
    objectVersion, objectVersionLength = decodeVarint(
        data[readPosition:readPosition + 9])
    readPosition += objectVersionLength
    streamNumber, streamNumberLength = decodeVarint(
        data[readPosition:readPosition + 9])
    if not streamNumber in state.streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.', streamNumber)
        return
    readPosition += streamNumberLength
    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug('We have already received this msg message. Ignoring.')
        return
    # This msg message is valid. Let's let our peers know about it.
    objectType = 2
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime,'')
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
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
    if not streamNumber in state.streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.', streamNumber)
        return
    readPosition += streamNumberLength

    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug('We have already received this getpubkey request. Ignoring it.')
        return

    objectType = 0
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime,'')
    # This getpubkey request is valid. Forward to peers.
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
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
    if not streamNumber in state.streamsInWhichIAmParticipating:
        logger.debug('The streamNumber %s isn\'t one we are interested in.', streamNumber)
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
        if not streamNumber in state.streamsInWhichIAmParticipating:
            logger.debug('The streamNumber %s isn\'t one we are interested in.', streamNumber)
            return
    if broadcastVersion >= 3:
        tag = data[readPosition:readPosition+32]
    else:
        tag = ''
    inventoryHash = calculateInventoryHash(data)
    if inventoryHash in Inventory():
        logger.debug('We have already received this broadcast object. Ignoring.')
        return
    # It is valid. Let's let our peers know about it.
    objectType = 3
    Inventory()[inventoryHash] = (
        objectType, streamNumber, data, embeddedTime, tag)
    # This object is valid. Forward it to peers.
    logger.debug('advertising inv with hash: %s', hexlify(inventoryHash))
    broadcastToSendDataQueues((streamNumber, 'advertiseobject', inventoryHash))

    # Now let's queue it to be processed ourselves.
    objectProcessorQueue.put((objectType,data))

# If you want to command all of the sendDataThreads to do something, like shutdown or send some data, this
# function puts your data into the queues for each of the sendDataThreads. The sendDataThreads are
# responsible for putting their queue into (and out of) the sendDataQueues list.
def broadcastToSendDataQueues(data):
    # logger.debug('running broadcastToSendDataQueues')
    for q in state.sendDataQueues:
        q.put(data)

# sslProtocolVersion
if sys.version_info >= (2,7,13):
    # this means TLSv1 or higher
    # in the future change to
    # ssl.PROTOCOL_TLS1.2
    sslProtocolVersion = ssl.PROTOCOL_TLS
elif sys.version_info >= (2,7,9):
    # this means any SSL/TLS. SSLv2 and 3 are excluded with an option after context is created
    sslProtocolVersion = ssl.PROTOCOL_SSLv23
else:
    # this means TLSv1, there is no way to set "TLSv1 or higher" or
    # "TLSv1.2" in < 2.7.9
    sslProtocolVersion = ssl.PROTOCOL_TLSv1

# ciphers
if ssl.OPENSSL_VERSION_NUMBER >= 0x10100000 and not ssl.OPENSSL_VERSION.startswith("LibreSSL"):
    sslProtocolCiphers = "AECDH-AES256-SHA@SECLEVEL=0"
else:
    sslProtocolCiphers = "AECDH-AES256-SHA"
