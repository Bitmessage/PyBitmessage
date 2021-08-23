"""
A thread for creating addresses
"""
import hashlib
import time
from binascii import hexlify

import defaults
import highlevelcrypto
import queues
import shared
import state
import tr
from addresses import decodeAddress, encodeAddress, encodeVarint
from bmconfigparser import BMConfigParser
from fallback import RIPEMD160Hash
from network import StoppableThread
from pyelliptic import arithmetic
from pyelliptic.openssl import OpenSSL
from six.moves import configparser, queue


class AddressGeneratorException(Exception):
    '''Generic AddressGenerator exception'''
    pass


class addressGenerator(StoppableThread):
    """A thread for creating addresses"""

    name = "addressGenerator"

    def stopThread(self):
        try:
            queues.addressGeneratorQueue.put(("stopThread", "data"))
        except queue.Full:
            self.logger.error('addressGeneratorQueue is Full')

        super(addressGenerator, self).stopThread()

    def run(self):
        """
        Process the requests for addresses generation
        from `.queues.addressGeneratorQueue`
        """
        # pylint: disable=too-many-locals, too-many-branches
        # pylint: disable=protected-access, too-many-statements
        # pylint: disable=too-many-nested-blocks

        while state.shutdown == 0:
            queueValue = queues.addressGeneratorQueue.get()
            nonceTrialsPerByte = 0
            payloadLengthExtraBytes = 0
            live = True
            if queueValue[0] == 'createChan':
                command, addressVersionNumber, streamNumber, label, \
                    deterministicPassphrase, live = queueValue
                eighteenByteRipe = False
                numberOfAddressesToMake = 1
                numberOfNullBytesDemandedOnFrontOfRipeHash = 1
            elif queueValue[0] == 'joinChan':
                command, chanAddress, label, deterministicPassphrase, \
                    live = queueValue
                eighteenByteRipe = False
                addressVersionNumber = decodeAddress(chanAddress)[1]
                streamNumber = decodeAddress(chanAddress)[2]
                numberOfAddressesToMake = 1
                numberOfNullBytesDemandedOnFrontOfRipeHash = 1
            elif len(queueValue) == 7:
                command, addressVersionNumber, streamNumber, label, \
                    numberOfAddressesToMake, deterministicPassphrase, \
                    eighteenByteRipe = queueValue

                numberOfNullBytesDemandedOnFrontOfRipeHash = \
                    BMConfigParser().safeGetInt(
                        'bitmessagesettings',
                        'numberofnullbytesonaddress',
                        2 if eighteenByteRipe else 1
                    )
            elif len(queueValue) == 9:
                command, addressVersionNumber, streamNumber, label, \
                    numberOfAddressesToMake, deterministicPassphrase, \
                    eighteenByteRipe, nonceTrialsPerByte, \
                    payloadLengthExtraBytes = queueValue

                numberOfNullBytesDemandedOnFrontOfRipeHash = \
                    BMConfigParser().safeGetInt(
                        'bitmessagesettings',
                        'numberofnullbytesonaddress',
                        2 if eighteenByteRipe else 1
                    )
            elif queueValue[0] == 'stopThread':
                break
            else:
                self.logger.error(
                    'Programming error: A structure with the wrong number'
                    ' of values was passed into the addressGeneratorQueue.'
                    ' Here is the queueValue: %r\n', queueValue)
            if addressVersionNumber < 3 or addressVersionNumber > 4:
                self.logger.error(
                    'Program error: For some reason the address generator'
                    ' queue has been given a request to create at least'
                    ' one version %s address which it cannot do.\n',
                    addressVersionNumber)
            if nonceTrialsPerByte == 0:
                nonceTrialsPerByte = BMConfigParser().getint(
                    'bitmessagesettings', 'defaultnoncetrialsperbyte')
            if nonceTrialsPerByte < \
                    defaults.networkDefaultProofOfWorkNonceTrialsPerByte:
                nonceTrialsPerByte = \
                    defaults.networkDefaultProofOfWorkNonceTrialsPerByte
            if payloadLengthExtraBytes == 0:
                payloadLengthExtraBytes = BMConfigParser().getint(
                    'bitmessagesettings', 'defaultpayloadlengthextrabytes')
            if payloadLengthExtraBytes < \
                    defaults.networkDefaultPayloadLengthExtraBytes:
                payloadLengthExtraBytes = \
                    defaults.networkDefaultPayloadLengthExtraBytes
            if command == 'createRandomAddress':
                queues.UISignalQueue.put((
                    'updateStatusBar',
                    tr._translate(
                        "MainWindow", "Generating one new address")
                ))
                # This next section is a little bit strange. We're going
                # to generate keys over and over until we find one
                # that starts with either \x00 or \x00\x00. Then when
                # we pack them into a Bitmessage address, we won't store
                # the \x00 or \x00\x00 bytes thus making the address shorter.
                startTime = time.time()
                numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix = 0
                potentialPrivSigningKey = OpenSSL.rand(32)
                potentialPubSigningKey = highlevelcrypto.pointMult(
                    potentialPrivSigningKey)
                while True:
                    numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix += 1
                    potentialPrivEncryptionKey = OpenSSL.rand(32)
                    potentialPubEncryptionKey = highlevelcrypto.pointMult(
                        potentialPrivEncryptionKey)
                    sha = hashlib.new('sha512')
                    sha.update(
                        potentialPubSigningKey + potentialPubEncryptionKey)
                    ripe = RIPEMD160Hash(sha.digest()).digest()
                    if (
                        ripe[:numberOfNullBytesDemandedOnFrontOfRipeHash]
                        == b'\x00' * numberOfNullBytesDemandedOnFrontOfRipeHash
                    ):
                        break
                self.logger.info(
                    'Generated address with ripe digest: %s', hexlify(ripe))
                try:
                    self.logger.info(
                        'Address generator calculated %s addresses at %s'
                        ' addresses per second before finding one with'
                        ' the correct ripe-prefix.',
                        numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix,
                        numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix
                        / (time.time() - startTime))
                except ZeroDivisionError:
                    # The user must have a pretty fast computer.
                    # time.time() - startTime equaled zero.
                    pass
                address = encodeAddress(
                    addressVersionNumber, streamNumber, ripe)

                # An excellent way for us to store our keys
                # is in Wallet Import Format. Let us convert now.
                # https://en.bitcoin.it/wiki/Wallet_import_format
                privSigningKey = b'\x80' + potentialPrivSigningKey
                checksum = hashlib.sha256(hashlib.sha256(
                    privSigningKey).digest()).digest()[0:4]
                privSigningKeyWIF = arithmetic.changebase(
                    privSigningKey + checksum, 256, 58)

                privEncryptionKey = b'\x80' + potentialPrivEncryptionKey
                checksum = hashlib.sha256(hashlib.sha256(
                    privEncryptionKey).digest()).digest()[0:4]
                privEncryptionKeyWIF = arithmetic.changebase(
                    privEncryptionKey + checksum, 256, 58)

                BMConfigParser().add_section(address)
                BMConfigParser().set(address, 'label', label)
                BMConfigParser().set(address, 'enabled', 'true')
                BMConfigParser().set(address, 'decoy', 'false')
                BMConfigParser().set(address, 'noncetrialsperbyte', str(
                    nonceTrialsPerByte))
                BMConfigParser().set(address, 'payloadlengthextrabytes', str(
                    payloadLengthExtraBytes))
                BMConfigParser().set(
                    address, 'privsigningkey', privSigningKeyWIF)
                BMConfigParser().set(
                    address, 'privencryptionkey', privEncryptionKeyWIF)
                BMConfigParser().save()

                # The API and the join and create Chan functionality
                # both need information back from the address generator.
                queues.apiAddressGeneratorReturnQueue.put(address)

                queues.UISignalQueue.put((
                    'updateStatusBar',
                    tr._translate(
                        "MainWindow",
                        "Done generating address. Doing work necessary"
                        " to broadcast it...")
                ))
                queues.UISignalQueue.put(('writeNewAddressToTable', (
                    label, address, streamNumber)))
                shared.reloadMyAddressHashes()
                if addressVersionNumber == 3:
                    queues.workerQueue.put((
                        'sendOutOrStoreMyV3Pubkey', ripe))
                elif addressVersionNumber == 4:
                    queues.workerQueue.put((
                        'sendOutOrStoreMyV4Pubkey', address))

            elif command == 'createDeterministicAddresses' \
                    or command == 'getDeterministicAddress' \
                    or command == 'createChan' or command == 'joinChan':
                if not deterministicPassphrase:
                    self.logger.warning(
                        'You are creating deterministic'
                        ' address(es) using a blank passphrase.'
                        ' Bitmessage will do it but it is rather stupid.')
                if command == 'createDeterministicAddresses':
                    queues.UISignalQueue.put((
                        'updateStatusBar',
                        tr._translate(
                            "MainWindow",
                            "Generating %1 new addresses."
                        ).arg(str(numberOfAddressesToMake))
                    ))
                signingKeyNonce = 0
                encryptionKeyNonce = 1
                # We fill out this list no matter what although we only
                # need it if we end up passing the info to the API.
                listOfNewAddressesToSendOutThroughTheAPI = []

                for _ in range(numberOfAddressesToMake):
                    # This next section is a little bit strange. We're
                    # going to generate keys over and over until we find
                    # one that has a RIPEMD hash that starts with either
                    # \x00 or \x00\x00. Then when we pack them into a
                    # Bitmessage address, we won't store the \x00 or
                    # \x00\x00 bytes thus making the address shorter.
                    startTime = time.time()
                    numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix = 0
                    while True:
                        numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix += 1
                        potentialPrivSigningKey = hashlib.sha512(
                            deterministicPassphrase
                            + encodeVarint(signingKeyNonce)
                        ).digest()[:32]
                        potentialPrivEncryptionKey = hashlib.sha512(
                            deterministicPassphrase
                            + encodeVarint(encryptionKeyNonce)
                        ).digest()[:32]
                        potentialPubSigningKey = highlevelcrypto.pointMult(
                            potentialPrivSigningKey)
                        potentialPubEncryptionKey = highlevelcrypto.pointMult(
                            potentialPrivEncryptionKey)
                        signingKeyNonce += 2
                        encryptionKeyNonce += 2
                        sha = hashlib.new('sha512')
                        sha.update(
                            potentialPubSigningKey + potentialPubEncryptionKey)
                        ripe = RIPEMD160Hash(sha.digest()).digest()
                        if (
                            ripe[:numberOfNullBytesDemandedOnFrontOfRipeHash]
                            == b'\x00' * numberOfNullBytesDemandedOnFrontOfRipeHash
                        ):
                            break

                    self.logger.info(
                        'Generated address with ripe digest: %s', hexlify(ripe))
                    try:
                        self.logger.info(
                            'Address generator calculated %s addresses'
                            ' at %s addresses per second before finding'
                            ' one with the correct ripe-prefix.',
                            numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix,
                            numberOfAddressesWeHadToMakeBeforeWeFoundOneWithTheCorrectRipePrefix
                            / (time.time() - startTime)
                        )
                    except ZeroDivisionError:
                        # The user must have a pretty fast computer.
                        # time.time() - startTime equaled zero.
                        pass
                    address = encodeAddress(
                        addressVersionNumber, streamNumber, ripe)

                    saveAddressToDisk = True
                    # If we are joining an existing chan, let us check
                    # to make sure it matches the provided Bitmessage address
                    if command == 'joinChan':
                        if address != chanAddress:
                            listOfNewAddressesToSendOutThroughTheAPI.append(
                                'chan name does not match address')
                            saveAddressToDisk = False
                    if command == 'getDeterministicAddress':
                        saveAddressToDisk = False

                    if saveAddressToDisk and live:
                        # An excellent way for us to store our keys is
                        # in Wallet Import Format. Let us convert now.
                        # https://en.bitcoin.it/wiki/Wallet_import_format
                        privSigningKey = b'\x80' + potentialPrivSigningKey
                        checksum = hashlib.sha256(hashlib.sha256(
                            privSigningKey).digest()).digest()[0:4]
                        privSigningKeyWIF = arithmetic.changebase(
                            privSigningKey + checksum, 256, 58)

                        privEncryptionKey = b'\x80' + \
                            potentialPrivEncryptionKey
                        checksum = hashlib.sha256(hashlib.sha256(
                            privEncryptionKey).digest()).digest()[0:4]
                        privEncryptionKeyWIF = arithmetic.changebase(
                            privEncryptionKey + checksum, 256, 58)

                        try:
                            BMConfigParser().add_section(address)
                            addressAlreadyExists = False
                        except configparser.DuplicateSectionError:
                            addressAlreadyExists = True

                        if addressAlreadyExists:
                            self.logger.info(
                                '%s already exists. Not adding it again.',
                                address
                            )
                            queues.UISignalQueue.put((
                                'updateStatusBar',
                                tr._translate(
                                    "MainWindow",
                                    "%1 is already in 'Your Identities'."
                                    " Not adding it again."
                                ).arg(address)
                            ))
                        else:
                            self.logger.debug('label: %s', label)
                            BMConfigParser().set(address, 'label', label)
                            BMConfigParser().set(address, 'enabled', 'true')
                            BMConfigParser().set(address, 'decoy', 'false')
                            if command == 'joinChan' \
                                    or command == 'createChan':
                                BMConfigParser().set(address, 'chan', 'true')
                            BMConfigParser().set(
                                address, 'noncetrialsperbyte',
                                str(nonceTrialsPerByte))
                            BMConfigParser().set(
                                address, 'payloadlengthextrabytes',
                                str(payloadLengthExtraBytes))
                            BMConfigParser().set(
                                address, 'privSigningKey',
                                privSigningKeyWIF)
                            BMConfigParser().set(
                                address, 'privEncryptionKey',
                                privEncryptionKeyWIF)
                            BMConfigParser().save()

                            queues.UISignalQueue.put((
                                'writeNewAddressToTable',
                                (label, address, str(streamNumber))
                            ))
                            listOfNewAddressesToSendOutThroughTheAPI.append(
                                address)
                            shared.myECCryptorObjects[ripe] = \
                                highlevelcrypto.makeCryptor(
                                    hexlify(potentialPrivEncryptionKey))
                            shared.myAddressesByHash[ripe] = address
                            tag = hashlib.sha512(hashlib.sha512(
                                encodeVarint(addressVersionNumber)
                                + encodeVarint(streamNumber) + ripe
                            ).digest()).digest()[32:]
                            shared.myAddressesByTag[tag] = address
                            if addressVersionNumber == 3:
                                # If this is a chan address,
                                # the worker thread won't send out
                                # the pubkey over the network.
                                queues.workerQueue.put((
                                    'sendOutOrStoreMyV3Pubkey', ripe))
                            elif addressVersionNumber == 4:
                                queues.workerQueue.put((
                                    'sendOutOrStoreMyV4Pubkey', address))
                            queues.UISignalQueue.put((
                                'updateStatusBar',
                                tr._translate(
                                    "MainWindow", "Done generating address")
                            ))
                    elif saveAddressToDisk and not live \
                            and not BMConfigParser().has_section(address):
                        listOfNewAddressesToSendOutThroughTheAPI.append(
                            address)

                # Done generating addresses.
                if command == 'createDeterministicAddresses' \
                        or command == 'joinChan' or command == 'createChan':
                    queues.apiAddressGeneratorReturnQueue.put(
                        listOfNewAddressesToSendOutThroughTheAPI)
                elif command == 'getDeterministicAddress':
                    queues.apiAddressGeneratorReturnQueue.put(address)
            else:
                raise AddressGeneratorException(
                    "Error in the addressGenerator thread. Thread was"
                    + " given a command it could not understand: " + command)
            queues.addressGeneratorQueue.task_done()
