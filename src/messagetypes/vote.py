"""
src/messagetypes/vote.py
========================
"""

from debug import logger
from messagetypes import MsgBase


class Vote(MsgBase):
    """Unused at this time"""
    # pylint: disable=attribute-defined-outside-init

    def decode(self, data):
        """Decode a vote"""
        self.msgid = data["msgid"]
        self.vote = data["vote"]

    def encode(self, data):
        """Encode a vote"""
        try:
            self.data["msgid"] = data["msgid"]
            self.data["vote"] = data["vote"]
        except KeyError as error:
            logger.error("Missing key %s", error)
        return self.data

    def process(self):
        """Process a vote"""
        logger.debug("msgid: %s", self.msgid)
        logger.debug("vote: %s", self.vote)
