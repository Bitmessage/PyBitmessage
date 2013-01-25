import rsa
import hashlib
from struct import *

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

    """#check for the BM- at the front of the address. If it isn't there, this address might be for a different version of Bitmessage
    if address[:3] != 'BM-':
        status = 'missingbm'
        return status,0,0,0
    #take off the BM-
    integer = decodeBase58(address[3:])"""

    #changed Bitmessage to accept addresses that lack the "BM-" prefix.
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

def addBMIfNotPresent(address):
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
    #Let's make a new Bitmessage address:
    (pubkey, privkey) = rsa.newkeys(256)
    print privkey['n']
    print privkey['e']
    print privkey['d']
    print privkey['p']
    print privkey['q']

    ripe = hashlib.new('ripemd160')
    sha = hashlib.new('sha512')
    sha.update(convertIntToString(pubkey.n)+convertIntToString(pubkey.e))

    ripe.update(sha.digest())
    #print 'sha digest:', sha.digest()
    #print 'ripe digest:', ripe.digest()
    #print len(sha.digest())
    #print len(ripe.digest())

    #prepend the version number and stream number
    a = '\x01' + '\x08' + ripe.digest()
    #print 'lengh of a at beginning = ', len(a)
    print 'This is the data to be encoded in the address: ', a.encode('hex')

    returnedAddress = encodeAddress(1,8,ripe.digest())
    status,addressVersionNumber,streamNumber,data = decodeAddress(returnedAddress)
    print returnedAddress
    print 'Status:', status
    print 'addressVersionNumber', addressVersionNumber
    print 'streamNumber', streamNumber
    print 'length of data(the ripe hash):', len(data)

    print '\n\nNow let us try making an address with given 2048-bit n and e values.'
    testn = 16691381808213609635656612695328489234826227577985206736118595570304213887605602327717776979169783795560145663031146864154748634207927153095849203939039346778471192284119479329875655789428795925773927040539038073349089996911318012189546542694411685389074592231210678771416758973061752125295462189928432307067746658691146428088703129795340914596189054255127032271420140641112277113597275245807890920656563056790943850440012709593297328230145129809419550219898595770524436575484115680960823105256137731976622290028349172297572826751147335728017861413787053794003722218722212196385625462088929496952843002425059308041193
    teste = 65537
    ripe = hashlib.new('ripemd160')
    sha = hashlib.new('sha512')
    sha.update(convertIntToString(testn)+convertIntToString(teste))
    ripe.update(sha.digest())
    encodedAddress = encodeAddress(1,1,ripe.digest())
    print encodedAddress
    status,addressVersionNumber,streamNumber,data = decodeAddress(encodedAddress)
    print 'Status:', status
    print 'addressVersionNumber', addressVersionNumber
    print 'streamNumber', streamNumber
    print 'length of data(the ripe hash):', len(data)

