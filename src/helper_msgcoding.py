#!/usr/bin/python2.7

import string
import msgpack
import zlib

from debug import logger
import messagetypes

BITMESSAGE_ENCODING_IGNORE = 0
BITMESSAGE_ENCODING_TRIVIAL = 1
BITMESSAGE_ENCODING_SIMPLE = 2
BITMESSAGE_ENCODING_EXTENDED = 3


class MsgEncode(object):
    def __init__(self, message, encoding=BITMESSAGE_ENCODING_SIMPLE):
        self.data = None
        self.encoding = encoding
        self.length = 0
        if self.encoding == BITMESSAGE_ENCODING_EXTENDED:
            self.encodeExtended(message)
        elif self.encoding == BITMESSAGE_ENCODING_SIMPLE:
            self.encodeSimple(message)
        elif self.encoding == BITMESSAGE_ENCODING_TRIVIAL:
            self.encodeTrivial(message)

    def encodeExtended(self, message):
        try:
            self.data = zlib.compress(msgpack.dumps({"": "message", "subject": message['subject'], "message": ['body']}), 9)
        except zlib.error:
            logger.error("Error compressing message")
            raise
        except msgpack.exceptions.PackException:
            logger.error("Error msgpacking message")
            raise
        self.length = len(self.data)

    def encodeSimple(self, message):
        self.data = 'Subject:' + message['subject'] + '\n' + 'Body:' + message['body']
        self.length = len(self.data)

    def encodeTrivial(self, message):
        self.data = message['body']
        self.length = len(self.data)

class MsgDecode(object):
    def __init__(self, encoding, data):
        self.encoding = encoding
        if self.encoding == BITMESSAGE_ENCODING_EXTENDED:
            self.decodeExtended(data)
        elif self.encoding in [BITMESSAGE_ENCODING_SIMPLE, BITMESSAGE_ENCODING_TRIVIAL]:
            self.decodeSimple(data)
        return

    def decodeExtended(self, data):
        try:
            tmp = msgpack.loads(zlib.decompress(data))
        except zlib.error:
            logger.error("Error decompressing message")
            raise
        except (msgpack.exceptions.UnpackException,
                msgpack.exceptions.ExtraData):
            logger.error("Error msgunpacking message")
            raise

        try:
            msgType = tmp[""]
        except KeyError:
            logger.error("Message type missing")
            raise

        msgObj = messagetypes.constructObject(data)
        if msgObj is None:
            raise ValueError("Malformed message")
        try:
            msgObj.process()
        except:
            raise ValueError("Malformed message")
        if msgType[""] == "message":
            self.subject = msgObj.subject
            self.body = msgObj.body

    def decodeSimple(self, data):
        bodyPositionIndex = string.find(data, '\nBody:')
        if bodyPositionIndex > 1:
            subject = data[8:bodyPositionIndex]
            # Only save and show the first 500 characters of the subject.
            # Any more is probably an attack.
            subject = subject[:500]
            body = data[bodyPositionIndex + 6:]
        else:
            subject = ''
            body = data
        # Throw away any extra lines (headers) after the subject.
        if subject:
            subject = subject.splitlines()[0]
        self.subject = subject
        self.message = body
