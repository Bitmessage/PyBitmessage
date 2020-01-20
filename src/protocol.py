"""
Low-level protocol-related functions.
"""
# pylint: disable=too-many-boolean-expressions,too-many-return-statements
# pylint: disable=too-many-locals,too-many-statements

import base64
import hashlib
import random
import socket
import sys
import time
from binascii import hexlify
from struct import pack, unpack, Struct

import defaults
import highlevelcrypto
import state
from addresses import (
    encodeVarint, decodeVarint, decodeAddress, varintDecodeError)
from bmconfigparser import BMConfigParser
from debug import logger
from fallback import RIPEMD160Hash
from helper_sql import sqlExecute
from version import softwareVersion

# Service flags
#: This is a normal network node
NODE_NETWORK = 1
#: This node supports SSL/TLS in the current connect (python < 2.7.9
#: only supports an SSL client, so in that case it would only have this
#: on when the connection is a client).
NODE_SSL = 2
# (Proposal) This node may do PoW on behalf of some its peers
# (PoW offloading/delegating), but it doesn't have to. Clients may have
# to meet additional requirements (e.g. TLS authentication)
# NODE_POW = 4
#: Node supports dandelion
NODE_DANDELION = 8

# Bitfield flags
BITFIELD_DOESACK = 1

# Error types
STATUS_WARNING = 0
STATUS_ERROR = 1
STATUS_FATAL = 2

# Object types
OBJECT_GETPUBKEY = 0
OBJECT_PUBKEY = 1
OBJECT_MSG = 2
OBJECT_BROADCAST = 3
OBJECT_ONIONPEER = 0x746f72
OBJECT_I2P = 0x493250
OBJECT_ADDR = 0x61646472

eightBytesOfRandomDataUsedToDetectConnectionsToSelf = pack(
    '>Q', random.randrange(1, 18446744073709551615))

# Compiled struct for packing/unpacking headers
# New code should use CreatePacket instead of Header.pack
Header = Struct('!L12sL4s')

VersionPacket = Struct('>LqQ20s4s36sH')

# Bitfield


def getBitfield(address):
    """Get a bitfield from an address"""
    # bitfield of features supported by me (see the wiki).
    bitfield = 0
    # send ack
    if not BMConfigParser().safeGetBoolean(address, 'dontsendack'):
        bitfield |= BITFIELD_DOESACK
    return pack('>I', bitfield)


def checkBitfield(bitfieldBinary, flags):
    """Check if a bitfield matches the given flags"""
    bitfield, = unpack('>I', bitfieldBinary)
    return (bitfield & flags) == flags


def isBitSetWithinBitfield(fourByteString, n):
    """Check if a particular bit is set in a bitfeld"""
    # Uses MSB 0 bit numbering across 4 bytes of data
    n = 31 - n
    x, = unpack('>L', fourByteString)
    return x & 2**n != 0


# ip addresses


def encodeHost(host):
    """Encode a given host to be used in low-level socket operations"""
    if type(host) == bytes:
        onion = 'onion'.encode()
        colon = ':'.encode()
        full_stop = '.'.encode()
    else:
        onion = 'onion'
        colon = ':'
        full_stop = '.'
    if host.find(onion) > -1:
        return '\xfd\x87\xd8\x7e\xeb\x43'.encode(
            'raw_unicode_escape') + base64.b32decode(
                host.split(full_stop)[0], True)
    elif host.find(colon) == -1:
        return '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF'.encode('raw_unicode_escape') + \
            socket.inet_aton(host)
    return socket.inet_pton(socket.AF_INET6, host)


def networkType(host):
    """Determine if a host is IPv4, IPv6 or an onion address"""
    if host.find('.onion') > -1:
        return 'onion'
    elif host.find(':') == -1:
        return 'IPv4'
    return 'IPv6'


def network_group(host):
    """Canonical identifier of network group
       simplified, borrowed from
       GetGroup() in src/netaddresses.cpp in bitcoin core"""
    if not isinstance(host, str):
        return None
    network_type = networkType(host)
    try:
        raw_host = encodeHost(host)
    except socket.error:
        return host
    if network_type == 'IPv4':
        decoded_host = checkIPv4Address(raw_host[12:], True)
        if decoded_host:
            # /16 subnet
            return raw_host[12:14]
    elif network_type == 'IPv6':
        decoded_host = checkIPv6Address(raw_host, True)
        if decoded_host:
            # /32 subnet
            return raw_host[0:12]
    else:
        # just host, e.g. for tor
        return host
    # global network type group for local, private, unroutable
    return network_type


def checkIPAddress(host, private=False):

    """Returns hostStandardFormat if it is a valid IP address, otherwise returns False"""
    if host[0:12] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF'.encode('raw_unicode_escape'):
        hostStandardFormat = socket.inet_ntop(socket.AF_INET, host[12:])
        return checkIPv4Address(host[12:], hostStandardFormat, private)
    elif host[0:6] == '\xfd\x87\xd8\x7e\xeb\x43'.encode('raw_unicode_escape'):
        # Onion, based on BMD/bitcoind
        hostStandardFormat = base64.b32encode(host[6:]) + ".onion".encode()
        if private:
            return False
        return hostStandardFormat
    else:
        try:
            hostStandardFormat = socket.inet_ntop(socket.AF_INET6, host)
        except ValueError:
            return False
        if hostStandardFormat == "":
            # This can happen on Windows systems which are
            # not 64-bit compatible so let us drop the IPv6 address.
            return False
        return checkIPv6Address(host, hostStandardFormat, private)


def checkIPv4Address(host, hostStandardFormat, private=False):

    """Returns hostStandardFormat if it is an IPv4 address, otherwise returns False"""

    if host[0] == '\x7F'.encode('raw_unicode_escape'):  # 127/8
        if not private:
            logger.debug(
                'Ignoring IP address in loopback range: %s',
                hostStandardFormat)
        return hostStandardFormat if private else False
    if host[0] == '\x0A'.encode('raw_unicode_escape'):  # 10/8
        if not private:
            logger.debug(
                'Ignoring IP address in private range: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    if host[0:2] == '\xC0\xA8'.encode('raw_unicode_escape'):  # 192.168/16
        if not private:
            logger.debug(
                'Ignoring IP address in private range: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    # 172.16/12
    if host[0:2] >= '\xAC\x10'.encode('raw_unicode_escape') and host[0:2] < '\xAC\x20'.encode('raw_unicode_escape'):
        if not private:
            logger.debug(
                'Ignoring IP address in private range: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    return False if private else hostStandardFormat


def checkIPv6Address(host, hostStandardFormat, private=False):
    """Returns hostStandardFormat if it is an IPv6 address, otherwise returns False"""
    if host == ('\x00'.encode() * 15) + '\x01'.encode():

        if not private:
            logger.debug('Ignoring loopback address: {}'.format(hostStandardFormat))
        return False
    if host[0] == '\xFE' and (ord(host[1]) & 0xc0) == 0x80:
        if not private:
            logger.debug('Ignoring local address: {}'.format(hostStandardFormat))
        return hostStandardFormat if private else False
    if (ord(host[0:1]) & 0xfe) == 0xfc:
        if not private:
            logger.debug('Ignoring unique local address: {}'.format(hostStandardFormat))

        return hostStandardFormat if private else False
    return False if private else hostStandardFormat


def haveSSL(server=False):
    """
    Predicate to check if ECDSA server support is required and available

    python < 2.7.9's ssl library does not support ECDSA server due to
    missing initialisation of available curves, but client works ok
    """
    return False
    if not server:
        return True
    elif sys.version_info >= (2, 7, 9):
        return True
    return False


def checkSocksIP(host):
    """Predicate to check if we're using a SOCKS proxy"""
    sockshostname = BMConfigParser().safeGet(
        'bitmessagesettings', 'sockshostname')
    try:
        if not state.socksIP:
            state.socksIP = socket.gethostbyname(sockshostname)
    except NameError:  # uninitialised
        state.socksIP = socket.gethostbyname(sockshostname)
    except (TypeError, socket.gaierror):  # None, resolving failure
        state.socksIP = sockshostname
    return state.socksIP == host


def isProofOfWorkSufficient(
        data, nonceTrialsPerByte=0, payloadLengthExtraBytes=0, recvTime=0):
    """
    Validate an object's Proof of Work using method described
    `here <https://bitmessage.org/wiki/Proof_of_work>`_

    Arguments:
        int nonceTrialsPerByte (default: from `.defaults`)
        int payloadLengthExtraBytes (default: from `.defaults`)
        float recvTime (optional) UNIX epoch time when object was
          received from the network (default: current system time)
    Returns:
        True if PoW valid and sufficient, False in all other cases
    """
    if nonceTrialsPerByte < defaults.networkDefaultProofOfWorkNonceTrialsPerByte:
        nonceTrialsPerByte = defaults.networkDefaultProofOfWorkNonceTrialsPerByte
    if payloadLengthExtraBytes < defaults.networkDefaultPayloadLengthExtraBytes:
        payloadLengthExtraBytes = defaults.networkDefaultPayloadLengthExtraBytes
    endOfLifeTime, = unpack('>Q', data[8:16])
    TTL = endOfLifeTime - (int(recvTime) if recvTime else int(time.time()))
    if TTL < 300:
        TTL = 300
    POW, = unpack('>Q', hashlib.sha512(hashlib.sha512(
        data[:8] + hashlib.sha512(data[8:]).digest()
    ).digest()).digest()[0:8])
    return POW <= 2 ** 64 / (
        nonceTrialsPerByte * (
            len(data) + payloadLengthExtraBytes +
            ((TTL * (len(data) + payloadLengthExtraBytes)) / (2 ** 16))))


# Packet creation


def CreatePacket(command, payload=''):
    """Construct and return a number of bytes from a payload"""
    payload = payload if type(payload) in [bytes, bytearray] else payload.encode()
    payload_length = len(payload)
    checksum = hashlib.sha512(payload).digest()[0:4]
    byte = bytearray(Header.size + payload_length)
    Header.pack_into(byte, 0, 0xE9BEB4D9, command.encode(), payload_length, checksum)
    byte[Header.size:] = payload
    return bytes(byte)


def assembleVersionMessage(remoteHost, remotePort, participatingStreams, server=False, nodeid=None):
    """Construct the payload of a version message, return the resultng bytes of running CreatePacket() on it"""
    payload = bytes()

    payload += pack('>L', 3)  # protocol version.
    # bitflags of the services I offer.
    payload += pack(
        '>q',
        NODE_NETWORK |
        (NODE_SSL if haveSSL(server) else 0) |
        (NODE_DANDELION if state.dandelion else 0)
    )
    payload += pack('>q', int(time.time()))

    # boolservices of remote connection; ignored by the remote host.
    payload += pack('>q', 1)
    if checkSocksIP(remoteHost) and server:
        # prevent leaking of tor outbound IP
        payload += encodeHost('127.0.0.1')
        payload += pack('>H', 8444)
    else:
        # use first 16 bytes if host data is longer
        # for example in case of onion v3 service
        try:
            payload += encodeHost(remoteHost)[:16]
        except socket.error:
            payload += encodeHost('127.0.0.1')
        payload += pack('>H', remotePort)  # remote IPv6 and port

    # bitflags of the services I offer.
    payload += pack(
        '>q',
        NODE_NETWORK |
        (NODE_SSL if haveSSL(server) else 0) |
        (NODE_DANDELION if state.dandelion else 0)
    )
    # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
    # python3 need to check
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF'.encode('raw_unicode_escape') + pack('>L', 2130706433)

    # we have a separate extPort and incoming over clearnet
    # or outgoing through clearnet
    extport = BMConfigParser().safeGetInt('bitmessagesettings', 'extport')
    if (
        extport and ((server and not checkSocksIP(remoteHost)) or (
            BMConfigParser().get('bitmessagesettings', 'socksproxytype')
            == 'none' and not server))
    ):
        payload += pack('>H', extport)
    elif checkSocksIP(remoteHost) and server:  # incoming connection over Tor
        payload += pack('>H', int(BMConfigParser().safeGet('bitmessagesettings', 'onionport')))
    else:  # no extport and not incoming over Tor
        payload += pack('>H', int(BMConfigParser().safeGet('bitmessagesettings', 'port')))

    if nodeid is not None:
        payload += nodeid[0:8]
    else:
        payload += eightBytesOfRandomDataUsedToDetectConnectionsToSelf
    userAgent = '/PyBitmessage:' + softwareVersion + '/'
    payload += encodeVarint(len(userAgent))
    payload += userAgent.encode()

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
    """
    Construct the payload of an error message,
    return the resulting bytes of running `CreatePacket` on it
    """
    payload = encodeVarint(fatal)
    payload += encodeVarint(banTime)
    payload += encodeVarint(len(inventoryVector))
    payload += inventoryVector.encode() if type(payload) == bytes else inventoryVector
    payload += encodeVarint(len(errorText))
    payload += errorText.encode() if type(payload) == bytes else errorText
    return CreatePacket('error', payload)


# Packet decoding


def decryptAndCheckPubkeyPayload(data, address):
    """
    Version 4 pubkeys are encrypted. This function is run when we
    already have the address to which we want to try to send a message.
    The 'data' may come either off of the wire or we might have had it
    already in our inventory when we tried to send a msg to this
    particular address.
    """
    try:
        addressVersion, streamNumber, ripe = decodeAddress(address)[1:]

        readPosition = 20  # bypass the nonce, time, and object type
        embeddedAddressVersion, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
        readPosition += varintLength
        embeddedStreamNumber, varintLength = decodeVarint(
            data[readPosition:readPosition + 10])
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
        publicSigningKey = '\x04' + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        publicEncryptionKey = '\x04' + decryptedData[readPosition:readPosition + 64]
        readPosition += 64
        specifiedNonceTrialsPerByteLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])[1]
        readPosition += specifiedNonceTrialsPerByteLength
        specifiedPayloadLengthExtraBytesLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])[1]
        readPosition += specifiedPayloadLengthExtraBytesLength
        storedData += decryptedData[:readPosition]
        signedData += decryptedData[:readPosition]
        signatureLength, signatureLengthLength = decodeVarint(
            decryptedData[readPosition:readPosition + 10])
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
        embeddedRipe = RIPEMD160Hash(sha.digest()).digest()

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
            ' an unhandled exception! This is definitely a bug!',
            exc_info=True
        )
        return 'failed'
