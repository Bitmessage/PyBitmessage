"""
src/addresses.py
================

"""
# pylint: disable=redefined-outer-name,inconsistent-return-statements

import hashlib
from binascii import hexlify, unhexlify
from struct import pack, unpack

from debug import logger


ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def encodeBase58(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        # print 'num is:', num
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def decodeBase58(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    num = 0

    try:
        for char in string:
            num *= base
            num += alphabet.index(char)
    except:  # ValueError
        # character not found (like a space character or a 0)
        return 0
    return num


def encodeVarint(integer):
    """Convert integer into varint bytes"""
    if integer < 0:
        logger.error('varint cannot be < 0')
        raise SystemExit
    if integer < 253:
        return pack('>B', integer)
    if integer >= 253 and integer < 65536:
        return pack('>B', 253) + pack('>H', integer)
    if integer >= 65536 and integer < 4294967296:
        return pack('>B', 254) + pack('>I', integer)
    if integer >= 4294967296 and integer < 18446744073709551616:
        return pack('>B', 255) + pack('>Q', integer)
    if integer >= 18446744073709551616:
        logger.error('varint cannot be >= 18446744073709551616')
        raise SystemExit


class varintDecodeError(Exception):
    """Exception class for decoding varint data"""
    pass


def decodeVarint(data):
    """
    Decodes an encoded varint to an integer and returns it.
    Per protocol v3, the encoded value must be encoded with
    the minimum amount of data possible or else it is malformed.
    Returns a tuple: (theEncodedValue, theSizeOfTheVarintInBytes)
    """

    if not data:
        return (0, 0)
    firstByte, = unpack('>B', data[0:1])
    if firstByte < 253:
        # encodes 0 to 252
        return (firstByte, 1)  # the 1 is the length of the varint
    if firstByte == 253:
        # encodes 253 to 65535
        if len(data) < 3:
            raise varintDecodeError(
                'The first byte of this varint as an integer is %s'
                ' but the total length is only %s. It needs to be'
                ' at least 3.' % (firstByte, len(data)))
        encodedValue, = unpack('>H', data[1:3])
        if encodedValue < 253:
            raise varintDecodeError(
                'This varint does not encode the value with the lowest'
                ' possible number of bytes.')
        return (encodedValue, 3)
    if firstByte == 254:
        # encodes 65536 to 4294967295
        if len(data) < 5:
            raise varintDecodeError(
                'The first byte of this varint as an integer is %s'
                ' but the total length is only %s. It needs to be'
                ' at least 5.' % (firstByte, len(data)))
        encodedValue, = unpack('>I', data[1:5])
        if encodedValue < 65536:
            raise varintDecodeError(
                'This varint does not encode the value with the lowest'
                ' possible number of bytes.')
        return (encodedValue, 5)
    if firstByte == 255:
        # encodes 4294967296 to 18446744073709551615
        if len(data) < 9:
            raise varintDecodeError(
                'The first byte of this varint as an integer is %s'
                ' but the total length is only %s. It needs to be'
                ' at least 9.' % (firstByte, len(data)))
        encodedValue, = unpack('>Q', data[1:9])
        if encodedValue < 4294967296:
            raise varintDecodeError(
                'This varint does not encode the value with the lowest'
                ' possible number of bytes.')
        return (encodedValue, 9)


def calculateInventoryHash(data):
    """Calculate inventory hash from object data"""
    sha = hashlib.new('sha512')
    sha2 = hashlib.new('sha512')
    sha.update(data)
    sha2.update(sha.digest())
    return sha2.digest()[0:32]


def encodeAddress(version, stream, ripe):
    """Convert ripe to address"""
    if version >= 2 and version < 4:
        if len(ripe) != 20:
            raise Exception(
                'Programming error in encodeAddress: The length of'
                ' a given ripe hash was not 20.'
            )
        if ripe[:2] == '\x00\x00':
            ripe = ripe[2:]
        elif ripe[:1] == '\x00':
            ripe = ripe[1:]
    elif version == 4:
        if len(ripe) != 20:
            raise Exception(
                'Programming error in encodeAddress: The length of'
                ' a given ripe hash was not 20.')
        ripe = ripe.lstrip('\x00')

    storedBinaryData = encodeVarint(version) + encodeVarint(stream) + ripe

    # Generate the checksum
    sha = hashlib.new('sha512')
    sha.update(storedBinaryData)
    currentHash = sha.digest()
    sha = hashlib.new('sha512')
    sha.update(currentHash)
    checksum = sha.digest()[0:4]

    asInt = int(hexlify(storedBinaryData) + hexlify(checksum), 16)
    return 'BM-' + encodeBase58(asInt)


def decodeAddress(address):
    """
    returns (status, address version number, stream number,
    data (almost certainly a ripe hash))
    """
    # pylint: disable=too-many-return-statements,too-many-statements,too-many-return-statements,too-many-branches
    address = str(address).strip()

    if address[:3] == 'BM-':
        integer = decodeBase58(address[3:])
    else:
        integer = decodeBase58(address)
    if integer == 0:
        status = 'invalidcharacters'
        return status, 0, 0, ''
    # after converting to hex, the string will be prepended
    # with a 0x and appended with a L
    # import pdb;pdb.set_trace()
    hexdata = hex(integer)[2:]

    if len(hexdata) % 2 != 0:
        hexdata = '0' + hexdata

    data = unhexlify(hexdata)
    checksum = data[-4:]

    sha = hashlib.new('sha512')
    sha.update(data[:-4])
    currentHash = sha.digest()
    sha = hashlib.new('sha512')
    sha.update(currentHash)

    if checksum != sha.digest()[0:4]:
        status = 'checksumfailed'
        return status, 0, 0, ''

    try:
        addressVersionNumber, bytesUsedByVersionNumber = decodeVarint(data[:9])
    except varintDecodeError as e:
        logger.error(str(e))
        status = 'varintmalformed'
        return status, 0, 0, ''

    if addressVersionNumber > 4:
        logger.error('cannot decode address version numbers this high')
        status = 'versiontoohigh'
        return status, 0, 0, ''
    elif addressVersionNumber == 0:
        logger.error('cannot decode address version numbers of zero.')
        status = 'versiontoohigh'
        return status, 0, 0, ''

    try:
        streamNumber, bytesUsedByStreamNumber = \
            decodeVarint(data[bytesUsedByVersionNumber:])
    except varintDecodeError as e:
        logger.error(str(e))
        status = 'varintmalformed'
        return status, 0, 0, ''

    status = 'success'
    if addressVersionNumber == 1:
        return status, addressVersionNumber, streamNumber, data[-24:-4]
    elif addressVersionNumber == 2 or addressVersionNumber == 3:
        embeddedRipeData = \
            data[bytesUsedByVersionNumber + bytesUsedByStreamNumber:-4]
        if len(embeddedRipeData) == 19:
            return status, addressVersionNumber, streamNumber, \
                '\x00' + embeddedRipeData
        elif len(embeddedRipeData) == 20:
            return status, addressVersionNumber, streamNumber, \
                embeddedRipeData
        elif len(embeddedRipeData) == 18:
            return status, addressVersionNumber, streamNumber, \
                '\x00\x00'.encode('utf-8') + embeddedRipeData
        elif len(embeddedRipeData) < 18:
            return 'ripetooshort', 0, 0, ''
        elif len(embeddedRipeData) > 20:
            return 'ripetoolong', 0, 0, ''
        return 'otherproblem', 0, 0, ''
    elif addressVersionNumber == 4:
        embeddedRipeData = \
            data[bytesUsedByVersionNumber + bytesUsedByStreamNumber:-4]
        if embeddedRipeData[0:1] == '\x00':
            # In order to enforce address non-malleability, encoded
            # RIPE data must have NULL bytes removed from the front
            return 'encodingproblem', 0, 0, ''
        elif len(embeddedRipeData) > 20:
            return 'ripetoolong', 0, 0, ''
        elif len(embeddedRipeData) < 4:
            return 'ripetooshort', 0, 0, ''
        x00string = '\x00' * (20 - len(embeddedRipeData))
        return status, addressVersionNumber, streamNumber, \
            x00string + embeddedRipeData


def addBMIfNotPresent(address):
    """Prepend BM- to an address if it doesn't already have it"""
    address = str(address).strip()
    return address if address[:3] == 'BM-' else 'BM-' + address


# TODO: make test case
if __name__ == "__main__":
    from pyelliptic import arithmetic

    print(
        '\nLet us make an address from scratch. Suppose we generate two'
        ' random 32 byte values and call the first one the signing key'
        ' and the second one the encryption key:'
    )
    privateSigningKey = \
        '93d0b61371a54b53df143b954035d612f8efa8a3ed1cf842c2186bfd8f876665'
    privateEncryptionKey = \
        '4b0b73a54e19b059dc274ab69df095fe699f43b17397bca26fdf40f4d7400a3a'
    print(
        '\nprivateSigningKey = %s\nprivateEncryptionKey = %s' %
        (privateSigningKey, privateEncryptionKey)
    )
    print(
        '\nNow let us convert them to public keys by doing'
        ' an elliptic curve point multiplication.'
    )
    publicSigningKey = arithmetic.privtopub(privateSigningKey)
    publicEncryptionKey = arithmetic.privtopub(privateEncryptionKey)
    print(
        '\npublicSigningKey = %s\npublicEncryptionKey = %s' %
        (publicSigningKey, publicEncryptionKey)
    )

    print(
        '\nNotice that they both begin with the \\x04 which specifies'
        ' the encoding type. This prefix is not send over the wire.'
        ' You must strip if off before you send your public key across'
        ' the wire, and you must add it back when you receive a public key.'
    )

    publicSigningKeyBinary = \
        arithmetic.changebase(publicSigningKey, 16, 256, minlen=64)
    publicEncryptionKeyBinary = \
        arithmetic.changebase(publicEncryptionKey, 16, 256, minlen=64)

    ripe = hashlib.new('ripemd160')
    sha = hashlib.new('sha512')
    sha.update(publicSigningKeyBinary + publicEncryptionKeyBinary)

    ripe.update(sha.digest())
    addressVersionNumber = 2
    streamNumber = 1
    print(
        '\nRipe digest that we will encode in the address: %s' %
        hexlify(ripe.digest())
    )
    returnedAddress = \
        encodeAddress(addressVersionNumber, streamNumber, ripe.digest())
    print('Encoded address: %s' % returnedAddress)
    status, addressVersionNumber, streamNumber, data = \
        decodeAddress(returnedAddress)
    print(
        '\nAfter decoding address:\n\tStatus: %s'
        '\n\taddressVersionNumber %s'
        '\n\tstreamNumber %s'
        '\n\tlength of data (the ripe hash): %s'
        '\n\tripe data: %s' %
        (status, addressVersionNumber, streamNumber, len(data), hexlify(data))
    )
