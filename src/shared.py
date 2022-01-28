"""
Some shared functions

.. deprecated:: 0.6.3
  Should be moved to different places and this file removed,
  but it needs refactoring.
"""
from __future__ import division

# Libraries.
import hashlib
import os
import stat
import subprocess
import sys
from binascii import hexlify

# Project imports.
import highlevelcrypto
import state
from addresses import decodeAddress, encodeVarint
from bmconfigparser import config
from debug import logger
from helper_sql import sqlQuery

from pyelliptic import arithmetic


myECCryptorObjects = {}
MyECSubscriptionCryptorObjects = {}
# The key in this dictionary is the RIPE hash which is encoded
# in an address and value is the address itself.
myAddressesByHash = {}
# The key in this dictionary is the tag generated from the address.
myAddressesByTag = {}
broadcastSendersForWhichImWatching = {}


def isAddressInMyAddressBook(address):
    """Is address in my addressbook?"""
    queryreturn = sqlQuery(
        '''select address from addressbook where address=?''',
        address)
    return queryreturn != []


# At this point we should really just have a isAddressInMy(book, address)...
def isAddressInMySubscriptionsList(address):
    """Am I subscribed to this address?"""
    queryreturn = sqlQuery(
        '''select * from subscriptions where address=?''',
        str(address))
    return queryreturn != []


def isAddressInMyAddressBookSubscriptionsListOrWhitelist(address):
    """
    Am I subscribed to this address, is it in my addressbook or whitelist?
    """
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
    # pylint: disable=inconsistent-return-statements
    """
    Convert private key from base58 that's used in the config file to
    8-bit binary string
    """
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
        os._exit(0)  # pylint: disable=protected-access
        # return ""
    elif privkey[0] == '\x80':  # checksum passed
        return privkey[1:]

    logger.critical(
        'Major problem! When trying to decode one of your  private keys,'
        ' the checksum passed but the key doesn\'t begin with hex 80.'
        ' Here is the PRIVATE key: %s', WIFstring
    )
    os._exit(0)  # pylint: disable=protected-access


def reloadMyAddressHashes():
    """Reload keys for user's addresses from the config file"""
    logger.debug('reloading keys from keys.dat file')
    myECCryptorObjects.clear()
    myAddressesByHash.clear()
    myAddressesByTag.clear()
    # myPrivateKeys.clear()

    keyfileSecure = checkSensitiveFilePermissions(os.path.join(
        state.appdata, 'keys.dat'))
    hasEnabledKeys = False
    for addressInKeysFile in config.addresses():
        isEnabled = config.getboolean(addressInKeysFile, 'enabled')
        if isEnabled:
            hasEnabledKeys = True
            # status
            addressVersionNumber, streamNumber, hashobj = decodeAddress(addressInKeysFile)[1:]
            if addressVersionNumber in (2, 3, 4):
                # Returns a simple 32 bytes of information encoded
                # in 64 Hex characters, or null if there was an error.
                privEncryptionKey = hexlify(decodeWalletImportFormat(
                    config.get(addressInKeysFile, 'privencryptionkey')))
                # It is 32 bytes encoded as 64 hex characters
                if len(privEncryptionKey) == 64:
                    myECCryptorObjects[hashobj] = \
                        highlevelcrypto.makeCryptor(privEncryptionKey)
                    myAddressesByHash[hashobj] = addressInKeysFile
                    tag = hashlib.sha512(hashlib.sha512(
                        encodeVarint(addressVersionNumber)
                        + encodeVarint(streamNumber) + hashobj).digest()).digest()[32:]
                    myAddressesByTag[tag] = addressInKeysFile
            else:
                logger.error(
                    'Error in reloadMyAddressHashes: Can\'t handle'
                    ' address versions other than 2, 3, or 4.'
                )

    if not keyfileSecure:
        fixSensitiveFilePermissions(os.path.join(
            state.appdata, 'keys.dat'), hasEnabledKeys)


def reloadBroadcastSendersForWhichImWatching():
    """
    Reinitialize runtime data for the broadcasts I'm subscribed to
    from the config file
    """
    broadcastSendersForWhichImWatching.clear()
    MyECSubscriptionCryptorObjects.clear()
    queryreturn = sqlQuery('SELECT address FROM subscriptions where enabled=1')
    logger.debug('reloading subscriptions...')
    for row in queryreturn:
        address, = row
        # status
        addressVersionNumber, streamNumber, hashobj = decodeAddress(address)[1:]
        if addressVersionNumber == 2:
            broadcastSendersForWhichImWatching[hashobj] = 0
        # Now, for all addresses, even version 2 addresses,
        # we should create Cryptor objects in a dictionary which we will
        # use to attempt to decrypt encrypted broadcast messages.

        if addressVersionNumber <= 3:
            privEncryptionKey = hashlib.sha512(
                encodeVarint(addressVersionNumber)
                + encodeVarint(streamNumber) + hashobj
            ).digest()[:32]
            MyECSubscriptionCryptorObjects[hashobj] = \
                highlevelcrypto.makeCryptor(hexlify(privEncryptionKey))
        else:
            doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(
                encodeVarint(addressVersionNumber)
                + encodeVarint(streamNumber) + hashobj
            ).digest()).digest()
            tag = doubleHashOfAddressData[32:]
            privEncryptionKey = doubleHashOfAddressData[:32]
            MyECSubscriptionCryptorObjects[tag] = \
                highlevelcrypto.makeCryptor(hexlify(privEncryptionKey))


def fixPotentiallyInvalidUTF8Data(text):
    """Sanitise invalid UTF-8 strings"""
    try:
        text.decode('utf-8')
        return text
    except UnicodeDecodeError:
        return 'Part of the message is corrupt. The message cannot be' \
            ' displayed the normal way.\n\n' + repr(text)


def checkSensitiveFilePermissions(filename):
    """
    :param str filename: path to the file
    :return: True if file appears to have appropriate permissions.
    """
    if sys.platform == 'win32':
        # .. todo:: This might deserve extra checks by someone familiar with
        # Windows systems.
        return True
    elif sys.platform[:7] == 'freebsd':
        # FreeBSD file systems are the same as major Linux file systems
        present_permissions = os.stat(filename)[0]
        disallowed_permissions = stat.S_IRWXG | stat.S_IRWXO
        return present_permissions & disallowed_permissions == 0
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
    except:  # noqa:E722
        # Swallow exception here, but we might run into trouble later!
        logger.error('Could not determine filesystem type. %s', filename)
    present_permissions = os.stat(filename)[0]
    disallowed_permissions = stat.S_IRWXG | stat.S_IRWXO
    return present_permissions & disallowed_permissions == 0


# Fixes permissions on a sensitive file.
def fixSensitiveFilePermissions(filename, hasEnabledKeys):
    """Try to change file permissions to be more restrictive"""
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
