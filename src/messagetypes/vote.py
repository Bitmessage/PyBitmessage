import logging

from messagetypes import MsgBase

logger = logging.getLogger('default')


class Vote(MsgBase):
    """Module used to vote"""

    def decode(self, data):
        """decode a vote"""
        # pylint: disable=attribute-defined-outside-init
        self.msgid = data["msgid"]
        self.vote = data["vote"]

    def encode(self, data):
        """Encode a vote"""
        super(Vote, self).__init__()
        try:
            self.data["msgid"] = data["msgid"]
            self.data["vote"] = data["vote"]
        except KeyError as e:
            logger.error("Missing key %s", e)
        return self.data

    def process(self):
        """Encode a vote"""
        logger.debug("msgid: %s", self.msgid)
        logger.debug("vote: %s", self.vote)
