#!/usr/bin/python2.7

try:
    import msgpack
except ImportError:
    import fallback.umsgpack.umsgpack as msgpack
import string
import zlib

from bmconfigparser import BMConfigParser
import shared
from debug import logger
import messagetypes
from tr import _translate

BITMESSAGE_ENCODING_IGNORE = 0
BITMESSAGE_ENCODING_TRIVIAL = 1
BITMESSAGE_ENCODING_SIMPLE = 2
BITMESSAGE_ENCODING_EXTENDED = 3

class DecompressionSizeException(Exception):
    def __init__(self, size):
        self.size = size


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
        else:
            raise ValueError("Unknown encoding %i" % (encoding))

    def encodeExtended(self, message):
        try:
            msgObj = messagetypes.message.Message()
            self.data = zlib.compress(msgpack.dumps(msgObj.encode(message)), 9)
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
        else:
            self.body = _translate("MsgDecode", "The message has an unknown encoding.\nPerhaps you should upgrade Bitmessage.")
            self.subject = _translate("MsgDecode", "Unknown encoding")

    def decodeExtended(self, data):
        dc = zlib.decompressobj()
        tmp = ""
        while len(tmp) <= BMConfigParser().safeGetInt("zlib", "maxsize"):
            try:
                got = dc.decompress(data, BMConfigParser().safeGetInt("zlib", "maxsize") + 1 - len(tmp))
                # EOF
                if got == "":
                    break
                tmp += got
                data = dc.unconsumed_tail
            except zlib.error:
                logger.error("Error decompressing message")
                raise
        else:
            raise DecompressionSizeException(len(tmp))

        try:
            tmp = msgpack.loads(tmp)
        except (msgpack.exceptions.UnpackException,
                msgpack.exceptions.ExtraData):
            logger.error("Error msgunpacking message")
            raise

        try:
            msgType = tmp[""]
        except KeyError:
            logger.error("Message type missing")
            raise

        msgObj = messagetypes.constructObject(tmp)
        if msgObj is None:
            raise ValueError("Malformed message")
        try:
            msgObj.process()
        except:
            raise ValueError("Malformed message")
        if msgType == "message":
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
        self.body = body

if __name__ == '__main__':
    import random
    messageData = {
        "subject": ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(40)),
        "body": ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10000))
    }
    obj1 = MsgEncode(messageData, 1)
    obj2 = MsgEncode(messageData, 2)
    obj3 = MsgEncode(messageData, 3)
    print "1:%i 2:%i 3:%i" %(len(obj1.data), len(obj2.data), len(obj3.data))

    obj1e = MsgDecode(1, obj1.data)
    # no subject in trivial encoding
    assert messageData["body"] == obj1e.body
    obj2e = MsgDecode(2, obj2.data)
    assert messageData["subject"] == obj2e.subject
    assert messageData["body"] == obj2e.body
    obj3e = MsgDecode(3, obj3.data)
    assert messageData["subject"] == obj3e.subject
    assert messageData["body"] == obj3e.body
