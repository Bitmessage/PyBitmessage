import shared
import threading
import time
import sys
from pyelliptic.openssl import OpenSSL
import ctypes
import hashlib
import highlevelcrypto
from addresses import *
from pyelliptic import arithmetic
import tr

class addressGenerator(threading.Thread):

    def __init__(self):
        # QThread.__init__(self, parent)
        threading.Thread.__init__(self)

    def run(self):
        while True:
            queueValue = shared.addressGeneratorQueue.get()
            nonceTrialsPerByte = 0
            payloadLengthExtraBytes = 0
            if queueValue[0] == 'createChan':
                command, addressVersionNumber, streamNumber, label, deterministicPassphrase = queueValue
                eighteenByteRipe = False
                numberOfAddressesToMake = 1
                numberOfNullBytesDemandedOnFrontOfRipeHash = 1
            elif queueValue[0] == 'joinChan':
                command, chanAddress, label, deterministicPassphrase = queueValue
                eighteenByteRipe = False
                addressVersionNumber = decodeAddress(chanAddress)[1]
                streamNumber = decodeAddress(chanAddress)[2]
                numberOfAddressesToMake = 1
                numberOfNullBytesDemandedOnFrontOfRipeHash = 1
            elif len(queueValue) == 7:
                command, addressVersionNumber, streamNumber, label, numberOfAddressesToMake, deterministicPassphrase, eighteenByteRipe = queueValue
                try:
                    numberOfNullBytesDemandedOnFrontOfRipeHash = shared.config.getint(
                        'bitmessagesettings', 'numberofnullbytesonaddress')
                except:
                    if eighteenByteRipe:
                        numberOfNullBytesDemandedOnFrontOfRipeHash = 2
                    else:
                        numberOfNullBytesDemandedOnFrontOfRipeHash = 1 # the default
            elif len(queueValue) == 9:
                command, addressVersionNumber, streamNumber, label, numberOfAddressesToMake, deterministicPassphrase, eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes = queueValue
                try:
                    numberOfNullBytesDemandedOnFrontOfRipeHash = shared.config.getint(
                        'bitmessagesettings', 'numberofnullbytesonaddress')
                except:
                    if eighteenByteRipe:
                        numberOfNullBytesDemandedOnFrontOfRipeHash = 2
                    else:
                        numberOfNullBytesDemandedOnFrontOfRipeHash = 1 # the default
            else:
                sys.stderr.write(
                    'Programming error: A structure with the wrong number of values was passed into the addressGeneratorQueue. Here is the queueValue: %s\n' % repr(queueValue))
            if addressVersionNumber < 3 or addressVersionNumber > 4:
                sys.stderr.write(
                    'Program error: For some reason the address generator queue has been given a request to create at least one version %s address which it cannot do.\n' % addressVersionNumber)
            if nonceTrialsPerByte == 0:
                nonceTrialsPerByte = shared.config.getint(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
            if nonceTrialsPerByte < shared.networkDefaultProofOfWorkNonceTrialsPerByte:
                nonceTrialsPerByte = shared.networkDefaultProofOfWorkNonceTrialsPerByte
            if payloadLengthExtraBytes == 0:
                payloadLengthExtraBytes = shared.config.getint(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            if payloadLengthExtraBytes < shared.networkDefaultPayloadLengthExtraBytes:
                payloadLengthExtraBytes = shared.networkDefaultPayloadLengthExtraBytes
            if command == 'createRandomAddress':
                shared.UISignalQueue.put((
                    'updateStatusBar', tr.translateText("MainWindow", "Generating one new address")))
                # This next section is a little bit strange. We're going to generate keys over and over until we
                # find one that starts with either \x00 or \x00\x00. Then when we pack them into a Bitmessage address,
                # we won't store the \x00 or \x00\x00 bytes thus making the
                # address shorter.
                startTime = time.time()
                numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix = 0
                potentialPrivSigningKey = OpenSSL.rand(32)
                potentialPubSigningKey = pointMult(potentialPrivSigningKey)
                while True:
                    numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix += 1
                    potentialPrivEncryptionKey = OpenSSL.rand(32)
                    potentialPubEncryptionKey = pointMult(
                        potentialPrivEncryptionKey)
                    # print 'potentialPubSigningKey', potentialPubSigningKey.encode('hex')
                    # print 'potentialPubEncryptionKey',
                    # potentialPubEncryptionKey.encode('hex')
                    ripe = hashlib.new('ripemd160')
                    sha = hashlib.new('sha512')
                    sha.update(
                        potentialPubSigningKey + potentialPubEncryptionKey)
                    ripe.update(sha.digest())
                    # print 'potential ripe.digest',
                    # ripe.digest().encode('hex')
                    if ripe.digest()[:numberOfNullBytesDemandedOnFrontOfRipeHash] == '\x00' * numberOfNullBytesDemandedOnFrontOfRipeHash:
                        break
                print 'Generated address with ripe digest:', ripe.digest().encode('hex')
                print 'Address generator calculated', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix, 'addresses at', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix / (time.time() - startTime), 'addresses per second before finding one with the correct ripe-prefix.'
                address = encodeAddress(addressVersionNumber, streamNumber, ripe.digest())

                # An excellent way for us to store our keys is in Wallet Import Format. Let us convert now.
                # https://en.bitcoin.it/wiki/Wallet_import_format
                privSigningKey = '\x80' + potentialPrivSigningKey
                checksum = hashlib.sha256(hashlib.sha256(
                    privSigningKey).digest()).digest()[0:4]
                privSigningKeyWIF = arithmetic.changebase(
                    privSigningKey + checksum, 256, 58)
                # print 'privSigningKeyWIF',privSigningKeyWIF

                privEncryptionKey = '\x80' + potentialPrivEncryptionKey
                checksum = hashlib.sha256(hashlib.sha256(
                    privEncryptionKey).digest()).digest()[0:4]
                privEncryptionKeyWIF = arithmetic.changebase(
                    privEncryptionKey + checksum, 256, 58)
                # print 'privEncryptionKeyWIF',privEncryptionKeyWIF

                shared.config.add_section(address)
                shared.config.set(address, 'label', label)
                shared.config.set(address, 'enabled', 'true')
                shared.config.set(address, 'decoy', 'false')
                shared.config.set(address, 'noncetrialsperbyte', str(
                    nonceTrialsPerByte))
                shared.config.set(address, 'payloadlengthextrabytes', str(
                    payloadLengthExtraBytes))
                shared.config.set(
                    address, 'privSigningKey', privSigningKeyWIF)
                shared.config.set(
                    address, 'privEncryptionKey', privEncryptionKeyWIF)
                with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                    shared.config.write(configfile)

                # The API and the join and create Chan functionality
                # both need information back from the address generator.
                shared.apiAddressGeneratorReturnQueue.put(address)

                shared.UISignalQueue.put((
                    'updateStatusBar', tr.translateText("MainWindow", "Done generating address. Doing work necessary to broadcast it...")))
                shared.UISignalQueue.put(('writeNewAddressToTable', (
                    label, address, streamNumber)))
                shared.reloadMyAddressHashes()
                if addressVersionNumber == 3:
                    shared.workerQueue.put((
                        'sendOutOrStoreMyV3Pubkey', ripe.digest()))
                elif addressVersionNumber == 4:
                    shared.workerQueue.put((
                        'sendOutOrStoreMyV4Pubkey', address))

            elif command == 'createDeterministicAddresses' or command == 'getDeterministicAddress' or command == 'createChan' or command == 'joinChan':
                if len(deterministicPassphrase) == 0:
                    sys.stderr.write(
                        'WARNING: You are creating deterministic address(es) using a blank passphrase. Bitmessage will do it but it is rather stupid.')
                if command == 'createDeterministicAddresses':
                    statusbar = 'Generating ' + str(
                        numberOfAddressesToMake) + ' new addresses.'
                    shared.UISignalQueue.put((
                        'updateStatusBar', statusbar))
                signingKeyNonce = 0
                encryptionKeyNonce = 1
                listOfNewAddressesToSendOutThroughTheAPI = [
                ]  # We fill out this list no matter what although we only need it if we end up passing the info to the API.

                for i in range(numberOfAddressesToMake):
                    # This next section is a little bit strange. We're going to generate keys over and over until we
                    # find one that has a RIPEMD hash that starts with either \x00 or \x00\x00. Then when we pack them
                    # into a Bitmessage address, we won't store the \x00 or
                    # \x00\x00 bytes thus making the address shorter.
                    startTime = time.time()
                    numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix = 0
                    while True:
                        numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix += 1
                        potentialPrivSigningKey = hashlib.sha512(
                            deterministicPassphrase + encodeVarint(signingKeyNonce)).digest()[:32]
                        potentialPrivEncryptionKey = hashlib.sha512(
                            deterministicPassphrase + encodeVarint(encryptionKeyNonce)).digest()[:32]
                        potentialPubSigningKey = pointMult(
                            potentialPrivSigningKey)
                        potentialPubEncryptionKey = pointMult(
                            potentialPrivEncryptionKey)
                        # print 'potentialPubSigningKey', potentialPubSigningKey.encode('hex')
                        # print 'potentialPubEncryptionKey',
                        # potentialPubEncryptionKey.encode('hex')
                        signingKeyNonce += 2
                        encryptionKeyNonce += 2
                        ripe = hashlib.new('ripemd160')
                        sha = hashlib.new('sha512')
                        sha.update(
                            potentialPubSigningKey + potentialPubEncryptionKey)
                        ripe.update(sha.digest())
                        # print 'potential ripe.digest',
                        # ripe.digest().encode('hex')
                        if ripe.digest()[:numberOfNullBytesDemandedOnFrontOfRipeHash] == '\x00' * numberOfNullBytesDemandedOnFrontOfRipeHash:
                            break

                    print 'ripe.digest', ripe.digest().encode('hex')
                    print 'Address generator calculated', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix, 'addresses at', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix / (time.time() - startTime), 'keys per second.'
                    address = encodeAddress(addressVersionNumber, streamNumber, ripe.digest())

                    saveAddressToDisk = True
                    # If we are joining an existing chan, let us check to make sure it matches the provided Bitmessage address
                    if command == 'joinChan':
                        if address != chanAddress:
                            shared.apiAddressGeneratorReturnQueue.put('chan name does not match address')
                            saveAddressToDisk = False
                    if command == 'getDeterministicAddress':
                        saveAddressToDisk = False

                    if saveAddressToDisk:
                        # An excellent way for us to store our keys is in Wallet Import Format. Let us convert now.
                        # https://en.bitcoin.it/wiki/Wallet_import_format
                        privSigningKey = '\x80' + potentialPrivSigningKey
                        checksum = hashlib.sha256(hashlib.sha256(
                            privSigningKey).digest()).digest()[0:4]
                        privSigningKeyWIF = arithmetic.changebase(
                            privSigningKey + checksum, 256, 58)

                        privEncryptionKey = '\x80' + \
                            potentialPrivEncryptionKey
                        checksum = hashlib.sha256(hashlib.sha256(
                            privEncryptionKey).digest()).digest()[0:4]
                        privEncryptionKeyWIF = arithmetic.changebase(
                            privEncryptionKey + checksum, 256, 58)

                        addressAlreadyExists = False
                        try:
                            shared.config.add_section(address)
                        except:
                            print address, 'already exists. Not adding it again.'
                            addressAlreadyExists = True
                        if not addressAlreadyExists:
                            print 'label:', label
                            shared.config.set(address, 'label', label)
                            shared.config.set(address, 'enabled', 'true')
                            shared.config.set(address, 'decoy', 'false')
                            if command == 'joinChan' or command == 'createChan':
                                shared.config.set(address, 'chan', 'true')
                            shared.config.set(address, 'noncetrialsperbyte', str(
                                nonceTrialsPerByte))
                            shared.config.set(address, 'payloadlengthextrabytes', str(
                                payloadLengthExtraBytes))
                            shared.config.set(
                                address, 'privSigningKey', privSigningKeyWIF)
                            shared.config.set(
                                address, 'privEncryptionKey', privEncryptionKeyWIF)
                            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                                shared.config.write(configfile)

                            shared.UISignalQueue.put(('writeNewAddressToTable', (
                                label, address, str(streamNumber))))
                            listOfNewAddressesToSendOutThroughTheAPI.append(
                                address)
                            shared.myECCryptorObjects[ripe.digest()] = highlevelcrypto.makeCryptor(
                                potentialPrivEncryptionKey.encode('hex'))
                            shared.myAddressesByHash[ripe.digest()] = address
                            tag = hashlib.sha512(hashlib.sha512(encodeVarint(
                                addressVersionNumber) + encodeVarint(streamNumber) + ripe.digest()).digest()).digest()[32:]
                            shared.myAddressesByTag[tag] = address
                            if addressVersionNumber == 3:
                                shared.workerQueue.put((
                                    'sendOutOrStoreMyV3Pubkey', ripe.digest())) # If this is a chan address,
                                        # the worker thread won't send out the pubkey over the network.
                            elif addressVersionNumber == 4:
                                shared.workerQueue.put((
                                    'sendOutOrStoreMyV4Pubkey', address))


                # Done generating addresses.
                if command == 'createDeterministicAddresses' or command == 'joinChan' or command == 'createChan':
                    shared.apiAddressGeneratorReturnQueue.put(
                        listOfNewAddressesToSendOutThroughTheAPI)
                    shared.UISignalQueue.put((
                        'updateStatusBar', tr.translateText("MainWindow", "Done generating address")))
                    # shared.reloadMyAddressHashes()
                elif command == 'getDeterministicAddress':
                    shared.apiAddressGeneratorReturnQueue.put(address)
                #todo: return things to the API if createChan or joinChan assuming saveAddressToDisk
            else:
                raise Exception(
                    "Error in the addressGenerator thread. Thread was given a command it could not understand: " + command)


# Does an EC point multiplication; turns a private key into a public key.
def pointMult(secret):
    # ctx = OpenSSL.BN_CTX_new() #This value proved to cause Seg Faults on
    # Linux. It turns out that it really didn't speed up EC_POINT_mul anyway.
    k = OpenSSL.EC_KEY_new_by_curve_name(OpenSSL.get_curve('secp256k1'))
    priv_key = OpenSSL.BN_bin2bn(secret, 32, 0)
    group = OpenSSL.EC_KEY_get0_group(k)
    pub_key = OpenSSL.EC_POINT_new(group)

    OpenSSL.EC_POINT_mul(group, pub_key, priv_key, None, None, None)
    OpenSSL.EC_KEY_set_private_key(k, priv_key)
    OpenSSL.EC_KEY_set_public_key(k, pub_key)
    # print 'priv_key',priv_key
    # print 'pub_key',pub_key

    size = OpenSSL.i2o_ECPublicKey(k, 0)
    mb = ctypes.create_string_buffer(size)
    OpenSSL.i2o_ECPublicKey(k, ctypes.byref(ctypes.pointer(mb)))
    # print 'mb.raw', mb.raw.encode('hex'), 'length:', len(mb.raw)
    # print 'mb.raw', mb.raw, 'length:', len(mb.raw)

    OpenSSL.EC_POINT_free(pub_key)
    # OpenSSL.BN_CTX_free(ctx)
    OpenSSL.BN_free(priv_key)
    OpenSSL.EC_KEY_free(k)
    return mb.raw
    
    
