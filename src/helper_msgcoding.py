#!/usr/bin/python2.7

import msgpack
import zlib

from debug import logger

BITMESSAGE_ENCODING_IGNORE = 0
BITMESSAGE_ENCODING_TRIVIAL = 1
BITMESSAGE_ENCODING_SIMPLE = 2
BITMESSAGE.ENCODING_EXTENDED = 3

class MsgEncode(object):
    def __init__(self, message, encoding = BITMESSAGE_ENCODING_SIMPLE):
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
            logger.error ("Error compressing message")
            raise
        except msgpack.exceptions.PackException:
            logger.error ("Error msgpacking message")
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
            logger.error ("Error decompressing message")
            raise
        except (msgpack.exceptions.UnpackException,
                msgpack.exceptions.ExtraData):
            logger.error ("Error msgunpacking message")
            raise
        try:
            if tmp[""] == "message":
                self.body = tmp["body"]
                self.subject = tmp["subject"]
        except:
            logger.error ("Malformed message")
            raise

    def decodeSimple(self, data):
        bodyPositionIndex = string.find(data, '\nBody:')
        if bodyPositionIndex > 1:
            subject = message[8:bodyPositionIndex]
            # Only save and show the first 500 characters of the subject.
            # Any more is probably an attack.
            subject = subject[:500]
            body = message[bodyPositionIndex + 6:]
        else:
            subject = ''
            body = message
        # Throw away any extra lines (headers) after the subject.
        if subject:
            subject = subject.splitlines()[0]
        self.subject = subject
        self.message = body
