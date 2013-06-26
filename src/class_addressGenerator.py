import shared
import threading
import bitmessagemain
import time
from pyelliptic.openssl import OpenSSL
import ctypes
import hashlib
from addresses import *
from pyelliptic import arithmetic
from debug import logger

class addressGenerator(threading.Thread):

    def __init__(self):
        # QThread.__init__(self, parent)
        threading.Thread.__init__(self)

    def run(self):
        while True:
            queueValue = shared.addressGeneratorQueue.get()
            nonceTrialsPerByte = 0
            payloadLengthExtraBytes = 0
            if len(queueValue) == 7:
                command, addressVersionNumber, streamNumber, label, numberOfAddressesToMake, deterministicPassphrase, eighteenByteRipe = queueValue
            elif len(queueValue) == 9:
                command, addressVersionNumber, streamNumber, label, numberOfAddressesToMake, deterministicPassphrase, eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes = queueValue
            else:
                logger.debug(
                    'Invalid queueValue: %s' % queueValue)
            if addressVersionNumber < 3 or addressVersionNumber > 3:
                logger.debug(
                    'The address generator cannot create v%s addresses.' % addressVersionNumber)
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
            if addressVersionNumber == 3:  # currently the only one supported.
                if command == 'createRandomAddress':
                    shared.UISignalQueue.put((
                        'updateStatusBar', bitmessagemain.translateText("MainWindow", "Generating one new address")))
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
                        if eighteenByteRipe:
                            if ripe.digest()[:2] == '\x00\x00':
                                break
                        else:
                            if ripe.digest()[:1] == '\x00':
                                break
                    logger.info('Generated address with ripe digest: %d' % ripe.digest().encode('hex'))
                    print 'Address generator calculated', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix, 'addresses at', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix / (time.time() - startTime), 'addresses per second before finding one with the correct ripe-prefix.'
                    address = encodeAddress(3, streamNumber, ripe.digest())

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

                    # It may be the case that this address is being generated
                    # as a result of a call to the API. Let us put the result
                    # in the necessary queue.
                    bitmessagemain.apiAddressGeneratorReturnQueue.put(address)

                    shared.UISignalQueue.put((
                        'updateStatusBar', bitmessagemain.translateText("MainWindow", "Done generating address. Doing work necessary to broadcast it...")))
                    shared.UISignalQueue.put(('writeNewAddressToTable', (
                        label, address, streamNumber)))
                    shared.reloadMyAddressHashes()
                    shared.workerQueue.put((
                        'doPOWForMyV3Pubkey', ripe.digest()))

                elif command == 'createDeterministicAddresses' or command == 'getDeterministicAddress':
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
                            if eighteenByteRipe:
                                if ripe.digest()[:2] == '\x00\x00':
                                    break
                            else:
                                if ripe.digest()[:1] == '\x00':
                                    break

                        print 'ripe.digest', ripe.digest().encode('hex')
                        print 'Address generator calculated', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix, 'addresses at', numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix / (time.time() - startTime), 'keys per second.'
                        address = encodeAddress(3, streamNumber, ripe.digest())

                        if command == 'createDeterministicAddresses':
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

                            try:
                                shared.config.add_section(address)
                                print 'label:', label
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

                                shared.UISignalQueue.put(('writeNewAddressToTable', (
                                    label, address, str(streamNumber))))
                                listOfNewAddressesToSendOutThroughTheAPI.append(
                                    address)
                                # if eighteenByteRipe:
                                # shared.reloadMyAddressHashes()#This is
                                # necessary here (rather than just at the end)
                                # because otherwise if the human generates a
                                # large number of new addresses and uses one
                                # before they are done generating, the program
                                # will receive a getpubkey message and will
                                # ignore it.
                                shared.myECCryptorObjects[ripe.digest()] = highlevelcrypto.makeCryptor(
                                    potentialPrivEncryptionKey.encode('hex'))
                                shared.myAddressesByHash[
                                    ripe.digest()] = address
                                shared.workerQueue.put((
                                    'doPOWForMyV3Pubkey', ripe.digest()))
                            except:
                                print address, 'already exists. Not adding it again.'

                    # Done generating addresses.
                    if command == 'createDeterministicAddresses':
                        # It may be the case that this address is being
                        # generated as a result of a call to the API. Let us
                        # put the result in the necessary queue.
                        bitmessagemain.apiAddressGeneratorReturnQueue.put(
                            listOfNewAddressesToSendOutThroughTheAPI)
                        shared.UISignalQueue.put((
                            'updateStatusBar', bitmessagemain.translateText("MainWindow", "Done generating address")))
                        # shared.reloadMyAddressHashes()
                    elif command == 'getDeterministicAddress':
                        bitmessagemain.apiAddressGeneratorReturnQueue.put(address)
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
    
    
