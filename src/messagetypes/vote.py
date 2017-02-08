from debug import logger
from messagetypes import MsgBase

class Vote(MsgBase):
    def __init__(self):
        return

    def decode(self, data):
        self.msgid = data["msgid"]
        self.vote = data["vote"]

    def encode(self, data):
        super(Vote, self).encode()
        try:
            self.data["msgid"] = data["msgid"]
            self.data["vote"] = data["vote"]
        except KeyError as e:
            logger.error("Missing key %s", e.name)
        return self.data

    def process(self):
        logger.debug("msgid: %s", self.msgid)
        logger.debug("vote: %s", self.vote)
