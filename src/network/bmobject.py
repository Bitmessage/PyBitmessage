"""
BMObject and it's exceptions.
"""
import logging
import time

import protocol
import state
from addresses import calculateInventoryHash
from inventory import Inventory
from network.dandelion import Dandelion

logger = logging.getLogger('default')


class BMObjectInsufficientPOWError(Exception):
    """Exception indicating the object
    doesn't have sufficient proof of work."""
    errorCodes = ("Insufficient proof of work")


class BMObjectInvalidDataError(Exception):
    """Exception indicating the data being parsed
    does not match the specification."""
    errorCodes = ("Data invalid")


class BMObjectExpiredError(Exception):
    """Exception indicating the object's lifetime has expired."""
    errorCodes = ("Object expired")


class BMObjectUnwantedStreamError(Exception):
    """Exception indicating the object is in a stream
    we didn't advertise as being interested in."""
    errorCodes = ("Object in unwanted stream")


class BMObjectInvalidError(Exception):
    """The object's data does not match object specification."""
    errorCodes = ("Invalid object")


class BMObjectAlreadyHaveError(Exception):
    """We received a duplicate object (one we already have)"""
    errorCodes = ("Already have this object")


class BMObject(object):  # pylint: disable=too-many-instance-attributes
    """Bitmessage Object as a class."""

    # max TTL, 28 days and 3 hours
    maxTTL = 28 * 24 * 60 * 60 + 10800
    # min TTL, 3 hour (in the past
    minTTL = -3600

    def __init__(
            self,
            nonce,
            expiresTime,
            objectType,
            version,
            streamNumber,
            data,
            payloadOffset
    ):  # pylint: disable=too-many-arguments
        self.nonce = nonce
        self.expiresTime = expiresTime
        self.objectType = objectType
        self.version = version
        self.streamNumber = streamNumber
        self.inventoryHash = calculateInventoryHash(data)
        # copy to avoid memory issues
        self.data = bytearray(data)
        self.tag = self.data[payloadOffset:payloadOffset + 32]

    def checkProofOfWorkSufficient(self):
        """Perform a proof of work check for sufficiency."""
        # Let us check to make sure that the proof of work is sufficient.
        if not protocol.isProofOfWorkSufficient(self.data):
            logger.info('Proof of work is insufficient.')
            raise BMObjectInsufficientPOWError()

    def checkEOLSanity(self):
        """Check if object's lifetime
        isn't ridiculously far in the past or future."""
        # EOL sanity check
        if self.expiresTime - int(time.time()) > BMObject.maxTTL:
            logger.info(
                'This object\'s End of Life time is too far in the future.'
                ' Ignoring it. Time is %i', self.expiresTime)
            # .. todo::  remove from download queue
            raise BMObjectExpiredError()

        if self.expiresTime - int(time.time()) < BMObject.minTTL:
            logger.info(
                'This object\'s End of Life time was too long ago.'
                ' Ignoring the object. Time is %i', self.expiresTime)
            # .. todo::  remove from download queue
            raise BMObjectExpiredError()

    def checkStream(self):
        """Check if object's stream matches streams we are interested in"""
        if self.streamNumber not in state.streamsInWhichIAmParticipating:
            logger.debug(
                'The streamNumber %i isn\'t one we are interested in.',
                self.streamNumber)
            raise BMObjectUnwantedStreamError()

    def checkAlreadyHave(self):
        """
        Check if we already have the object
        (so that we don't duplicate it in inventory
        or advertise it unnecessarily)
        """
        # if it's a stem duplicate, pretend we don't have it
        if Dandelion().hasHash(self.inventoryHash):
            return
        if self.inventoryHash in Inventory():
            raise BMObjectAlreadyHaveError()

    def checkObjectByType(self):
        """Call a object type specific check
        (objects can have additional checks based on their types)"""
        if self.objectType == protocol.OBJECT_GETPUBKEY:
            self.checkGetpubkey()
        elif self.objectType == protocol.OBJECT_PUBKEY:
            self.checkPubkey()
        elif self.objectType == protocol.OBJECT_MSG:
            self.checkMessage()
        elif self.objectType == protocol.OBJECT_BROADCAST:
            self.checkBroadcast()
        # other objects don't require other types of tests

    def checkMessage(self):  # pylint: disable=no-self-use
        """"Message" object type checks."""
        return

    def checkGetpubkey(self):
        """"Getpubkey" object type checks."""
        if len(self.data) < 42:
            logger.info(
                'getpubkey message doesn\'t contain enough data. Ignoring.')
            raise BMObjectInvalidError()

    def checkPubkey(self):
        """"Pubkey" object type checks."""
        # sanity check
        if len(self.data) < 146 or len(self.data) > 440:
            logger.info('pubkey object too short or too long. Ignoring.')
            raise BMObjectInvalidError()

    def checkBroadcast(self):
        """"Broadcast" object type checks."""
        if len(self.data) < 180:
            logger.debug(
                'The payload length of this broadcast'
                ' packet is unreasonably low. Someone is probably'
                ' trying funny business. Ignoring message.')
            raise BMObjectInvalidError()

        # this isn't supported anymore
        if self.version < 2:
            raise BMObjectInvalidError()
