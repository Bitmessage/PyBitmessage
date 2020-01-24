"""
Message encoding end decoding functions
"""

import string
import zlib

import messagetypes
from bmconfigparser import BMConfigParser
from debug import logger
from tr import _translate

try:
    import msgpack
except ImportError:
    try:
        import umsgpack as msgpack
    except ImportError:
        import fallback.umsgpack.umsgpack as msgpack

BITMESSAGE_ENCODING_IGNORE = 0
BITMESSAGE_ENCODING_TRIVIAL = 1
BITMESSAGE_ENCODING_SIMPLE = 2
BITMESSAGE_ENCODING_EXTENDED = 3


class MsgEncodeException(Exception):
    """Exception during message encoding"""
    pass


class MsgDecodeException(Exception):
    """Exception during message decoding"""
    pass


class DecompressionSizeException(MsgDecodeException):
    # pylint: disable=super-init-not-called
    """Decompression resulted in too much data (attack protection)"""
    def __init__(self, size):
        self.size = size


class MsgEncode(object):
    """Message encoder class"""
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
            raise MsgEncodeException("Unknown encoding %i" % (encoding))

    def encodeExtended(self, message):
        """Handle extended encoding"""
        try:
            msgObj = messagetypes.message.Message()
            self.data = zlib.compress(msgpack.dumps(msgObj.encode(message)), 9)
        except zlib.error:
            logger.error("Error compressing message")
            raise MsgEncodeException("Error compressing message")
        except msgpack.exceptions.PackException:
            logger.error("Error msgpacking message")
            raise MsgEncodeException("Error msgpacking message")
        self.length = len(self.data)

    def encodeSimple(self, message):
        """Handle simple encoding"""
        self.data = 'Subject:%(subject)s\nBody:%(body)s' % message
        self.length = len(self.data)

    def encodeTrivial(self, message):
        """Handle trivial encoding"""
        self.data = message['body']
        self.length = len(self.data)


class MsgDecode(object):
    """Message decoder class"""
    def __init__(self, encoding, data):
        self.encoding = encoding
        if self.encoding == BITMESSAGE_ENCODING_EXTENDED:
            self.decodeExtended(data)
        elif self.encoding in (
                BITMESSAGE_ENCODING_SIMPLE, BITMESSAGE_ENCODING_TRIVIAL):
            self.decodeSimple(data)
        else:
            self.body = _translate(
                "MsgDecode",
                "The message has an unknown encoding.\n"
                "Perhaps you should upgrade Bitmessage.")
            self.subject = _translate("MsgDecode", "Unknown encoding")

    def decodeExtended(self, data):
        """Handle extended encoding"""
        dc = zlib.decompressobj()
        tmp = ""
        while len(tmp) <= BMConfigParser().safeGetInt("zlib", "maxsize"):
            try:
                got = dc.decompress(
                    data, BMConfigParser().safeGetInt("zlib", "maxsize") +
                    1 - len(tmp))
                # EOF
                if got == "":
                    break
                tmp += got
                data = dc.unconsumed_tail
            except zlib.error:
                logger.error("Error decompressing message")
                raise MsgDecodeException("Error decompressing message")
        else:
            raise DecompressionSizeException(len(tmp))

        try:
            tmp = msgpack.loads(tmp)
        except (msgpack.exceptions.UnpackException,
                msgpack.exceptions.ExtraData):
            logger.error("Error msgunpacking message")
            raise MsgDecodeException("Error msgunpacking message")

        try:
            msgType = tmp[""]
        except KeyError:
            logger.error("Message type missing")
            raise MsgDecodeException("Message type missing")

        msgObj = messagetypes.constructObject(tmp)
        if msgObj is None:
            raise MsgDecodeException("Malformed message")
        try:
            msgObj.process()
        except:
            raise MsgDecodeException("Malformed message")
        if msgType == "message":
            self.subject = msgObj.subject
            self.body = msgObj.body

    def decodeSimple(self, data):
        """Handle simple encoding"""
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
