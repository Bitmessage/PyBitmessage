import hashlib
from struct import *
from pyelliptic import arithmetic

#There is another copy of this function in Bitmessagemain.py
def convertIntToString(n):
    a = __builtins__.hex(n)
    if a[-1:] == 'L':
        a = a[:-1]
    if (len(a) % 2) == 0:
        return a[2:].decode('hex')
    else:
        return ('0'+a[2:]).decode('hex')

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def encodeBase58(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        #print 'num is:', num
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
    strlen = len(string)
    num = 0

    try:
        power = strlen - 1
        for char in string:
            num += alphabet.index(char) * (base ** power)
            power -= 1
    except:
        #character not found (like a space character or a 0)
        return 0
    return num

def encodeVarint(integer):
    if integer < 0:
        print 'varint cannot be < 0'
        raise SystemExit
    if integer < 253:
        return pack('>B',integer)
    if integer >= 253 and integer < 65536:
        return pack('>B',253) + pack('>H',integer)
    if integer >= 65536 and integer < 4294967296:
        return pack('>B',254) + pack('>I',integer)
    if integer >= 4294967296 and integer < 18446744073709551616:
        return pack('>B',255) + pack('>Q',integer)
    if integer >= 18446744073709551616:
        print 'varint cannot be >= 18446744073709551616'
        raise SystemExit

def decodeVarint(data):
    if len(data) == 0:
        return (0,0)
    firstByte, = unpack('>B',data[0:1])
    if firstByte < 253:
        return (firstByte,1) #the 1 is the length of the varint
    if firstByte == 253:
        a, = unpack('>H',data[1:3])
        return (a,3)
    if firstByte == 254:
        a, = unpack('>I',data[1:5])
        return (a,5)
    if firstByte == 255:
        a, = unpack('>Q',data[1:9])
        return (a,9)



def calculateInventoryHash(data):
    sha = hashlib.new('sha512')
    sha2 = hashlib.new('sha512')
    sha.update(data)
    sha2.update(sha.digest())
    return sha2.digest()[0:32]

def encodeAddress(version,stream,ripe):
    if version >= 2:
        if len(ripe) != 20:
            raise Exception("Programming error in encodeAddress: The length of a given ripe hash was not 20.")
        if ripe[:2] == '\x00\x00':
            ripe = ripe[2:]
        elif ripe[:1] == '\x00':
            ripe = ripe[1:]
    a = encodeVarint(version) + encodeVarint(stream) + ripe
    sha = hashlib.new('sha512')
    sha.update(a)
    currentHash = sha.digest()
    #print 'sha after first hashing: ', sha.hexdigest()
    sha = hashlib.new('sha512')
    sha.update(currentHash)
    #print 'sha after second hashing: ', sha.hexdigest()

    checksum = sha.digest()[0:4]
    #print 'len(a) = ', len(a)
    #print 'checksum = ', checksum.encode('hex')
    #print 'len(checksum) = ', len(checksum)

    asInt = int(a.encode('hex') + checksum.encode('hex'),16)
    #asInt = int(checksum.encode('hex') + a.encode('hex'),16)
    # print asInt
    return 'BM-'+ encodeBase58(asInt)

def decodeAddress(address):
    #returns (status, address version number, stream number, data (almost certainly a ripe hash))

    address = str(address).strip()

    if address[:3] == 'BM-':
        integer = decodeBase58(address[3:])
    else:
        integer = decodeBase58(address)
    if integer == 0:
        status = 'invalidcharacters'
        return status,0,0,0
    #after converting to hex, the string will be prepended with a 0x and appended with a L
    hexdata = hex(integer)[2:-1]

    if len(hexdata) % 2 != 0:
        hexdata = '0' + hexdata

    #print 'hexdata', hexdata

    data = hexdata.decode('hex')
    checksum = data[-4:]

    sha = hashlib.new('sha512')
    sha.update(data[:-4])
    currentHash = sha.digest()
    #print 'sha after first hashing: ', sha.hexdigest()
    sha = hashlib.new('sha512')
    sha.update(currentHash)
    #print 'sha after second hashing: ', sha.hexdigest()

    if checksum != sha.digest()[0:4]:
        status = 'checksumfailed'
        return status,0,0,0
    #else:
    #    print 'checksum PASSED'

    addressVersionNumber, bytesUsedByVersionNumber = decodeVarint(data[:9])
    #print 'addressVersionNumber', addressVersionNumber
    #print 'bytesUsedByVersionNumber', bytesUsedByVersionNumber

    if addressVersionNumber > 2:
        print 'cannot decode address version numbers this high'
        status = 'versiontoohigh'
        return status,0,0,0
    elif addressVersionNumber == 0:
        print 'cannot decode address version numbers of zero.'
        status = 'versiontoohigh'
        return status,0,0,0

    streamNumber, bytesUsedByStreamNumber = decodeVarint(data[bytesUsedByVersionNumber:])
    #print streamNumber
    status = 'success'
    if addressVersionNumber == 1:
        return status,addressVersionNumber,streamNumber,data[-24:-4]
    elif addressVersionNumber == 2:
        if len(data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]) == 19:
            return status,addressVersionNumber,streamNumber,'\x00'+data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]
        elif len(data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]) == 20:
            return status,addressVersionNumber,streamNumber,data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]
        elif len(data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]) == 18:
            return status,addressVersionNumber,streamNumber,'\x00\x00'+data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]
        elif len(data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]) < 18:
            return 'ripetooshort',0,0,0
        elif len(data[bytesUsedByVersionNumber+bytesUsedByStreamNumber:-4]) > 20:
            return 'ripetoolong',0,0,0
        else:
            return 'otherproblem',0,0,0

def addBMIfNotPresent(address):
    address = str(address).strip()
    if address[:3] != 'BM-':
        return 'BM-'+address
    else:
        return address

def addressStream(address):
    #returns the stream number of an address or False if there is a problem with the address.

    #check for the BM- at the front of the address. If it isn't there, this address might be for a different version of Bitmessage
    if address[:3] != 'BM-':
        status = 'missingbm'
        return False
    #here we take off the BM-
    integer = decodeBase58(address[3:])
    #after converting to hex, the string will be prepended with a 0x and appended with a L
    hexdata = hex(integer)[2:-1]

    if len(hexdata) % 2 != 0:
        hexdata = '0' + hexdata

    #print 'hexdata', hexdata

    data = hexdata.decode('hex')
    checksum = data[-4:]

    sha = hashlib.new('sha512')
    sha.update(data[:-4])
    currentHash = sha.digest()
    #print 'sha after first hashing: ', sha.hexdigest()
    sha = hashlib.new('sha512')
    sha.update(currentHash)
    #print 'sha after second hashing: ', sha.hexdigest()

    if checksum != sha.digest()[0:4]:
        print 'checksum failed'
        status = 'checksumfailed'
        return False
    #else:
    #    print 'checksum PASSED'

    addressVersionNumber, bytesUsedByVersionNumber = decodeVarint(data[:9])
    #print 'addressVersionNumber', addressVersionNumber
    #print 'bytesUsedByVersionNumber', bytesUsedByVersionNumber

    if addressVersionNumber < 1:
        print 'cannot decode version address version numbers this high'
        status = 'versiontoohigh'
        return False

    streamNumber, bytesUsedByStreamNumber = decodeVarint(data[bytesUsedByVersionNumber:9+bytesUsedByVersionNumber])
    #print streamNumber
    status = 'success'
    return streamNumber


if __name__ == "__main__":
    print 'Let us make an address from scratch. Suppose we generate two random 32 byte values and call the first one the signing key and the second one the encryption key:'
    privateSigningKey = '93d0b61371a54b53df143b954035d612f8efa8a3ed1cf842c2186bfd8f876665'
    privateEncryptionKey = '4b0b73a54e19b059dc274ab69df095fe699f43b17397bca26fdf40f4d7400a3a'
    print 'privateSigningKey =', privateSigningKey
    print 'privateEncryptionKey =', privateEncryptionKey
    print 'Now let us convert them to public keys by doing an elliptic curve point multiplication.'
    publicSigningKey = arithmetic.privtopub(privateSigningKey)
    publicEncryptionKey = arithmetic.privtopub(privateEncryptionKey)
    print 'publicSigningKey =', publicSigningKey
    print 'publicEncryptionKey =', publicEncryptionKey

    print 'Notice that they both begin with the \\x04 which specifies the encoding type. This prefix is not send over the wire. You must strip if off before you send your public key across the wire, and you must add it back when you receive a public key.'

    publicSigningKeyBinary = arithmetic.changebase(publicSigningKey,16,256,minlen=64)
    publicEncryptionKeyBinary = arithmetic.changebase(publicEncryptionKey,16,256,minlen=64)

    ripe = hashlib.new('ripemd160')
    sha = hashlib.new('sha512')
    sha.update(publicSigningKeyBinary+publicEncryptionKeyBinary)

    ripe.update(sha.digest())
    addressVersionNumber = 2
    streamNumber = 1
    print 'Ripe digest that we will encode in the address:', ripe.digest().encode('hex')
    returnedAddress = encodeAddress(addressVersionNumber,streamNumber,ripe.digest())
    print 'Encoded address:', returnedAddress
    status,addressVersionNumber,streamNumber,data = decodeAddress(returnedAddress)
    print '\nAfter decoding address:'
    print 'Status:', status
    print 'addressVersionNumber', addressVersionNumber
    print 'streamNumber', streamNumber
    print 'length of data(the ripe hash):', len(data)
    print 'ripe data:', data.encode('hex')

