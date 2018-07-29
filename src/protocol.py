# pylint: disable=too-many-boolean-expressions,too-many-return-statements,too-many-locals,too-many-statements
"""
protocol.py
===========

Low-level protocol-related functions.
"""

from __future__ import absolute_import

import base64
from binascii import hexlify
import hashlib
import os
import random
import socket
import ssl
from struct import pack, unpack, Struct
import sys
import time
import traceback

import defaults
import highlevelcrypto
import state
from addresses import calculateInventoryHash, encodeVarint, decodeVarint, decodeAddress, varintDecodeError
from bmconfigparser import BMConfigParser
from debug import logger
from helper_sql import sqlExecute
from version import softwareVersion
import inventory
import queues


# Service flags
NODE_NETWORK = 1
NODE_SSL = 2
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
OBJECT_I2P = 0x493250
OBJECT_ADDR = 0x61646472

eightBytesOfRandomDataUsedToDetectConnectionsToSelf = pack(
    '>Q', random.randrange(1, 18446744073709551615))

# Compiled struct for packing/unpacking headers
# New code should use CreatePacket instead of Header.pack
Header = Struct('!L12sL4s')

VersionPacket = Struct('>LqQ20s4s36sH')

def calculateDoubleHash(data):
    return hashlib.sha512(hashlib.sha512(data).digest()).digest()

def calculateRipeHash(data):
    return hashlib.new("ripemd160", hashlib.sha512(data).digest()).digest()

def calculateAddressTag(version, stream, ripe):
    doubleHash = calculateDoubleHash(
        encodeVarint(version) +
        encodeVarint(stream) +
        ripe
    )

    return doubleHash[: 32], doubleHash[32: ]

# ip addresses


def encodeHost(host):
    """Encode a given host to be used in low-level socket operations"""
    if host.find('.onion') > -1:
        return '\xfd\x87\xd8\x7e\xeb\x43' + base64.b32decode(host.split(".")[0], True)
    elif host.find(':') == -1:
        return '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + \
            socket.inet_aton(host)
    return socket.inet_pton(socket.AF_INET6, host)


def networkType(host):
    """Determine if a host is IPv4, IPv6 or an onion address"""
    if host.find('.onion') > -1:
        return 'onion'
    elif host.find(':') == -1:
        return 'IPv4'
    return 'IPv6'


def checkIPAddress(host, private=False):
    """Returns hostStandardFormat if it is a valid IP address, otherwise returns False"""
    if host[0:12] == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF':
        hostStandardFormat = socket.inet_ntop(socket.AF_INET, host[12:])
        return checkIPv4Address(host[12:], hostStandardFormat, private)
    elif host[0:6] == '\xfd\x87\xd8\x7e\xeb\x43':
        # Onion, based on BMD/bitcoind
        hostStandardFormat = base64.b32encode(host[6:]).lower() + ".onion"
        if private:
            return False
        return hostStandardFormat
    else:
        try:
            hostStandardFormat = socket.inet_ntop(socket.AF_INET6, host)
        except ValueError:
            return False
        if hostStandardFormat == "":
            # This can happen on Windows systems which are not 64-bit compatible
            # so let us drop the IPv6 address.
            return False
        return checkIPv6Address(host, hostStandardFormat, private)


def checkIPv4Address(host, hostStandardFormat, private=False):
    """Returns hostStandardFormat if it is an IPv4 address, otherwise returns False"""
    if host[0] == '\x7F':  # 127/8
        if not private:
            logger.debug('Ignoring IP address in loopback range: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    if host[0] == '\x0A':  # 10/8
        if not private:
            logger.debug('Ignoring IP address in private range: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    if host[0:2] == '\xC0\xA8':  # 192.168/16
        if not private:
            logger.debug('Ignoring IP address in private range: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    if host[0:2] >= '\xAC\x10' and host[0:2] < '\xAC\x20':  # 172.16/12
        if not private:
            logger.debug('Ignoring IP address in private range: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    return False if private else hostStandardFormat


def checkIPv6Address(host, hostStandardFormat, private=False):
    """Returns hostStandardFormat if it is an IPv6 address, otherwise returns False"""
    if host == ('\x00' * 15) + '\x01':
        if not private:
            logger.debug('Ignoring loopback address: %s', hostStandardFormat)
        return False
    if host[0] == '\xFE' and (ord(host[1]) & 0xc0) == 0x80:
        if not private:
            logger.debug('Ignoring local address: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    if (ord(host[0]) & 0xfe) == 0xfc:
        if not private:
            logger.debug('Ignoring unique local address: %s', hostStandardFormat)
        return hostStandardFormat if private else False
    return False if private else hostStandardFormat


def haveSSL(server=False):
    """
    Predicate to check if ECDSA server support is required and available

    python < 2.7.9's ssl library does not support ECDSA server due to
    missing initialisation of available curves, but client works ok
    """
    if not server:
        return True
    elif sys.version_info >= (2, 7, 9):
        return True
    return False


def checkSocksIP(host):
    """Predicate to check if we're using a SOCKS proxy"""
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
                            payloadLengthExtraBytes=0,
                            recvTime=0):
    """
    Validate an object's Proof of Work using method described in:
        https://bitmessage.org/wiki/Proof_of_work
    Arguments:
        int nonceTrialsPerByte (default: from default.py)
        int payloadLengthExtraBytes (default: from default.py)
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
    POW, = unpack('>Q', hashlib.sha512(hashlib.sha512(data[
        :8] + hashlib.sha512(data[8:]).digest()).digest()).digest()[0:8])
    return POW <= 2 ** 64 / (nonceTrialsPerByte *
                             (len(data) + payloadLengthExtraBytes +
                              ((TTL * (len(data) + payloadLengthExtraBytes)) / (2 ** 16))))


# Packet creation


def CreatePacket(command, payload=''):
    """Construct and return a number of bytes from a payload"""
    payload_length = len(payload)
    checksum = hashlib.sha512(payload).digest()[0:4]

    b = bytearray(Header.size + payload_length)
    Header.pack_into(b, 0, 0xE9BEB4D9, command, payload_length, checksum)
    b[Header.size:] = payload
    return bytes(b)


def assembleVersionMessage(remoteHost, remotePort, participatingStreams, server=False, nodeid=None):
    """Construct the payload of a version message, return the resultng bytes of running CreatePacket() on it"""
    payload = ''
    payload += pack('>L', 3)  # protocol version.
    # bitflags of the services I offer.
    payload += pack(
        '>q',
        NODE_NETWORK |
        (NODE_SSL if haveSSL(server) else 0) |
        (NODE_DANDELION if state.dandelion else 0)
    )
    payload += pack('>q', int(time.time()))

    payload += pack(
        '>q', 1)  # boolservices of remote connection; ignored by the remote host.
    if checkSocksIP(remoteHost) and server:  # prevent leaking of tor outbound IP
        payload += encodeHost('127.0.0.1')
        payload += pack('>H', 8444)
    else:
        payload += encodeHost(remoteHost)
        payload += pack('>H', remotePort)  # remote IPv6 and port

    # bitflags of the services I offer.
    payload += pack(
        '>q',
        NODE_NETWORK |
        (NODE_SSL if haveSSL(server) else 0) |
        (NODE_DANDELION if state.dandelion else 0)
    )
    # = 127.0.0.1. This will be ignored by the remote host. The actual remote connected IP will be used.
    payload += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + pack('>L', 2130706433)
    # we have a separate extPort and incoming over clearnet or outgoing through clearnet
    if BMConfigParser().safeGetBoolean('bitmessagesettings', 'upnp') and state.extPort \
        and ((server and not checkSocksIP(remoteHost)) or
             (BMConfigParser().get("bitmessagesettings", "socksproxytype") == "none" and not server)):
        payload += pack('>H', state.extPort)
    elif checkSocksIP(remoteHost) and server:  # incoming connection over Tor
        payload += pack('>H', BMConfigParser().getint('bitmessagesettings', 'onionport'))
    else:  # no extPort and not incoming over Tor
        payload += pack('>H', BMConfigParser().getint('bitmessagesettings', 'port'))

    random.seed()
    if nodeid is not None:
        payload += nodeid[0:8]
    else:
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
    """Construct the payload of an error message, return the resultng bytes of running CreatePacket() on it"""
    payload = encodeVarint(fatal)
    payload += encodeVarint(banTime)
    payload += encodeVarint(len(inventoryVector))
    payload += inventoryVector
    payload += encodeVarint(len(errorText))
    payload += errorText
    return CreatePacket('error', payload)


# Packet decoding

def decryptAndCheckV4Pubkey(payload, address, cryptor):
    status, version, stream, ripe = decodeAddress(address)

    readPosition = 20

    try:
        embeddedVersion, readLength = decodeVarint(payload[readPosition: readPosition + 9])
        readPosition += readLength

        embeddedStream, readLength = decodeVarint(payload[readPosition: readPosition + 9])
        readPosition += readLength
    except:
        return None

    if embeddedVersion != 4:
        logger.info("Pubkey decryption failed due to address version mismatch")

        return None

    if embeddedStream != stream:
        logger.info("Pubkey decryption failed due to stream number mismatch")

        return None

    result = payload[20: readPosition]

    tag = payload[readPosition: readPosition + 32]
    readPosition += 32

    if len(tag) < 32:
        return None

    signedData = payload[8: readPosition]
    ciphertext = payload[readPosition: ]

    try:
        plaintext = cryptor.decrypt(ciphertext)
    except:
        logger.info("Pubkey decryption failed")

        return None

    readPosition = 0

    try:
        bitfield = unpack(">I", plaintext[readPosition: readPosition + 4])
        readPosition += 4
    except:
        return None

    publicSigningKey = "\x04" + plaintext[readPosition: readPosition + 64]
    readPosition += 64

    publicEncryptionKey = "\x04" + plaintext[readPosition: readPosition + 64]
    readPosition += 64

    if len(publicSigningKey) != 65 or len(publicEncryptionKey) != 65:
        return None

    embeddedRipe = calculateRipeHash(publicSigningKey + publicEncryptionKey)

    if embeddedRipe != ripe:
        logger.info("Pubkey decryption failed due to RIPE mismatch")

        return None

    try:
        byteDifficulty, readLength = decodeVarint(plaintext[readPosition: readPosition + 9])
        readPosition += readLength

        lengthExtension, readLength = decodeVarint(plaintext[readPosition: readPosition + 9])
        readPosition += readLength
    except:
        return None

    result += plaintext[: readPosition]
    signedData += plaintext[: readPosition]

    signatureLength, readLength = decodeVarint(plaintext[readPosition: readPosition + 9])
    readPosition += readLength

    signature = plaintext[readPosition: readPosition + signatureLength]

    if len(signature) != signatureLength:
        return None

    if not highlevelcrypto.verify(signedData, signature, hexlify(publicSigningKey)):
        logger.info("Invalid signature on a pubkey")

        return None

    return result

def checkAndShareObjectWithPeers(payload):
    if len(payload) > 2 ** 18:
        logger.info("The payload length of this object is too large (%i bytes)", len(payload))

        return None

    if not isProofOfWorkSufficient(payload):
        logger.info("Proof of work is insufficient")

        return None

    readPosition = 8

    try:
        expiryTime, objectType = unpack(">QI", payload[readPosition: readPosition + 12])
        readPosition += 12

        version, readLength = decodeVarint(payload[readPosition: readPosition + 9])
        readPosition += readLength

        stream, readLength = decodeVarint(payload[readPosition: readPosition + 9])
        readPosition += readLength
    except:
        logger.info("Error parsing object header")

        return None

    tag = payload[readPosition: readPosition + 32]

    TTL = expiryTime - int(time.time())

    # TTL may not be lesser than -1 hour or larger than 28 days + 3 hours of wiggle room

    if TTL < -3600:
        logger.info("This object\'s expiry time was more than an hour ago: %s", expiryTime)

        return None
    elif TTL > 28 * 24 * 60 * 60 + 10800:
        logger.info("This object\'s expiry time is too far in the future: %s", expiryTime)

        return None

    if stream not in state.streamsInWhichIAmParticipating:
        logger.info("The stream number %i isn\'t one we are interested in", stream)

        return None

    if objectType == 0:
        if len(payload) < 42:
            logger.info("Too short \"getpubkey\" message")

            return None
    elif objectType == 1:
        if len(payload) < 146 or len(payload) > 440:
            logger.info("Invalid length \"pubkey\"")

            return None
    elif objectType == 3:
        if len(payload) < 180:
            logger.info("Too short \"broadcast\" message")

            return None

        if version == 1:
            logger.info("Obsolete \"broadcast\" message version")

            return None

    inventoryHash = calculateDoubleHash(payload)[: 32]

    if inventoryHash in inventory.Inventory():
        logger.info("We already have this object")

        return inventoryHash
    else:
        inventory.Inventory()[inventoryHash] = objectType, stream, payload, expiryTime, buffer(tag)
        queues.invQueue.put((stream, inventoryHash))

        logger.info("Broadcasting inventory object with hash: %s", hexlify(inventoryHash))

        queues.objectProcessorQueue.put((objectType, payload))

        return inventoryHash

# sslProtocolVersion
if sys.version_info >= (2, 7, 13):
    # this means TLSv1 or higher
    # in the future change to
    # ssl.PROTOCOL_TLS1.2
    sslProtocolVersion = ssl.PROTOCOL_TLS  # pylint: disable=no-member
elif sys.version_info >= (2, 7, 9):
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
