from debug import logger
from messagetypes import MsgBase

class Message(MsgBase):
    def __init__(self):
        return

    def decode(self, data):
        self.subject = data["subject"]
        self.body = data["body"]

    def encode(self, data):
        super(Message, self).encode()
        try:
            self.data["subject"] = data["subject"]
            self.data["body"] = data["body"]
        except KeyError as e:
            logger.error("Missing key ", e.name)
        return self.data

    def process(self):
        logger.debug("Subject: %i bytes", len(self.subject))
        logger.debug("Body: %i bytes", len(self.body))
