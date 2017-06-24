from binascii import hexlify
import time

from addresses import calculateInventoryHash
from debug import logger
from inventory import Inventory
import protocol
import state

class BMObjectInsufficientPOWError(Exception): pass


class BMObjectInvalidDataError(Exception): pass


class BMObjectExpiredError(Exception): pass


class BMObjectUnwantedStreamError(Exception): pass


class BMObjectInvalidError(Exception): pass


class BMObjectAlreadyHaveError(Exception):
    pass


class BMObject(object):
    # max TTL, 28 days and 3 hours
    maxTTL = 28 * 24 * 60 * 60 + 10800
    # min TTL, 3 hour (in the past
    minTTL = -3600

    def __init__(self, nonce, expiresTime, objectType, version, streamNumber, data):
        self.nonce = nonce
        self.expiresTime = expiresTime
        self.objectType = objectType
        self.version = version
        self.streamNumber = streamNumber
        self.inventoryHash = calculateInventoryHash(data)
        self.data = data
        self.tag = ''

    def checkProofOfWorkSufficient(self):
        # Let us check to make sure that the proof of work is sufficient.
        if not protocol.isProofOfWorkSufficient(self.data):
            logger.info('Proof of work is insufficient.')
            raise BMObjectInsufficientPOWError()

    def checkEOLSanity(self):
        # EOL sanity check
        if self.expiresTime - int(time.time()) > BMObject.maxTTL:
            logger.info('This object\'s End of Life time is too far in the future. Ignoring it. Time is %i', self.expiresTime)
            # TODO: remove from download queue
            raise BMObjectExpiredError()

        if self.expiresTime - int(time.time()) < BMObject.minTTL:
            logger.info('This object\'s End of Life time was too long ago. Ignoring the object. Time is %i', self.expiresTime)
            # TODO: remove from download queue
            raise BMObjectExpiredError()

    def checkStream(self):
        if self.streamNumber not in state.streamsInWhichIAmParticipating:
            logger.debug('The streamNumber %i isn\'t one we are interested in.', self.streamNumber)
            raise BMObjectUnwantedStreamError()

    def checkAlreadyHave(self):
        if self.inventoryHash in Inventory():
            raise BMObjectAlreadyHaveError()

    def checkMessage(self):
        return

    def checkGetpubkey(self):
        if len(self.data) < 42:
            logger.info('getpubkey message doesn\'t contain enough data. Ignoring.')
            raise BMObjectInvalidError()

    def checkPubkey(self, tag):
        if len(self.data) < 146 or len(self.data) > 440:  # sanity check
            logger.info('pubkey object too short or too long. Ignoring.')
            raise BMObjectInvalidError()
        if self.version >= 4:
            self.tag = tag
            logger.debug('tag in received pubkey is: %s' % hexlify(tag))

    def checkBroadcast(self, tag):
        if len(self.data) < 180:
            logger.debug('The payload length of this broadcast packet is unreasonably low. Someone is probably trying funny business. Ignoring message.')
            raise BMObjectInvalidError()

        # this isn't supported anymore
        if self.version < 2:
            raise BMObjectInvalidError()

        if self.version >= 3:
            self.tag = tag
            logger.debug('tag in received broadcast is: %s' % hexlify(tag))
