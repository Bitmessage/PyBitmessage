"""
src/messagetypes/vote.py
=================================
"""
from debug import logger
from messagetypes import MsgBase
# pylint: disable=attribute-defined-outside-init


class Vote(MsgBase):
    """Base method, helps to decode, encode and process the message"""
    def __init__(self):    # pylint: disable=super-init-not-called
        return

    def decode(self, data):
        """Method used for decoding the message"""
        self.msgid = data["msgid"]
        self.vote = data["vote"]

    def encode(self, data):
        """Method used for encoding the message"""
        # pylint: disable=no-member
        super(Vote, self).encode()
        try:
            self.data["msgid"] = data["msgid"]
            self.data["vote"] = data["vote"]
        except KeyError as e:
            logger.error("Missing key %s", e.name)
        return self.data

    def process(self):
        """Method used for process the message"""
        logger.debug("msgid: %s", self.msgid)
        logger.debug("vote: %s", self.vote)
