"""
src/messagetypes/message.py
=================================
"""
from debug import logger
from messagetypes import MsgBase
# pylint: disable=attribute-defined-outside-init


class Message(MsgBase):
    """Base method, helps to decode, encode and process the message"""
    def __init__(self):     # pylint: disable=super-init-not-called
        return

    def decode(self, data):
        """Method used for decoding the message"""
        # UTF-8 and variable type validator
        # pylint: disable=unidiomatic-typecheck
        if type(data["subject"]) is str:
            self.subject = unicode(data["subject"], 'utf-8', 'replace')
        else:
            self.subject = unicode(str(data["subject"]), 'utf-8', 'replace')
        if type(data["body"]) is str:
            self.body = unicode(data["body"], 'utf-8', 'replace')
        else:
            self.body = unicode(str(data["body"]), 'utf-8', 'replace')

    def encode(self, data):
        """Method used for encoding the message"""
        # pylint: disable=no-member
        super(Message, self).encode()
        try:
            self.data["subject"] = data["subject"]
            self.data["body"] = data["body"]
        except KeyError as e:
            logger.error("Missing key %s", e)
        return self.data

    def process(self):
        """Method used for process the message"""
        logger.debug("Subject: %i bytes", len(self.subject))
        logger.debug("Body: %i bytes", len(self.body))
