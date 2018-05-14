from binascii import hexlify
import time

from addresses import calculateInventoryHash
from debug import logger
from inventory import Inventory
from network.dandelion import Dandelion
import protocol
import state

class BMObjectInsufficientPOWError(Exception):
    errorCodes = ("Insufficient proof of work")


class BMObjectInvalidDataError(Exception):
    errorCodes = ("Data invalid")


class BMObjectExpiredError(Exception):
    errorCodes = ("Object expired")


class BMObjectUnwantedStreamError(Exception):
    errorCodes = ("Object in unwanted stream")


class BMObjectInvalidError(Exception):
    errorCodes = ("Invalid object")


class BMObjectAlreadyHaveError(Exception):
    errorCodes = ("Already have this object")


class BMObject(object):
    # max TTL, 28 days and 3 hours
    maxTTL = 28 * 24 * 60 * 60 + 10800
    # min TTL, 3 hour (in the past
    minTTL = -3600

    def __init__(self, nonce, expiresTime, objectType, version, streamNumber, data, payloadOffset):
        self.nonce = nonce
        self.expiresTime = expiresTime
        self.objectType = objectType
        self.version = version
        self.streamNumber = streamNumber
        self.inventoryHash = calculateInventoryHash(data)
        # copy to avoid memory issues
        self.data = bytearray(data)
        self.tag = self.data[payloadOffset:payloadOffset+32]

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
        # if it's a stem duplicate, pretend we don't have it
        if Dandelion().hasHash(self.inventoryHash):
            return
        if self.inventoryHash in Inventory():
            raise BMObjectAlreadyHaveError()

    def checkObjectByType(self):
        if self.objectType == protocol.OBJECT_GETPUBKEY:
            self.checkGetpubkey()
        elif self.objectType == protocol.OBJECT_PUBKEY:
            self.checkPubkey()
        elif self.objectType == protocol.OBJECT_MSG:
            self.checkMessage()
        elif self.objectType == protocol.OBJECT_BROADCAST:
            self.checkBroadcast()
        # other objects don't require other types of tests

    def checkMessage(self):
        return

    def checkGetpubkey(self):
        if len(self.data) < 42:
            logger.info('getpubkey message doesn\'t contain enough data. Ignoring.')
            raise BMObjectInvalidError()

    def checkPubkey(self):
        if len(self.data) < 146 or len(self.data) > 440:  # sanity check
            logger.info('pubkey object too short or too long. Ignoring.')
            raise BMObjectInvalidError()

    def checkBroadcast(self):
        if len(self.data) < 180:
            logger.debug('The payload length of this broadcast packet is unreasonably low. Someone is probably trying funny business. Ignoring message.')
            raise BMObjectInvalidError()

        # this isn't supported anymore
        if self.version < 2:
            raise BMObjectInvalidError()
