from debug import logger
from messagetypes import MsgBase


class Message(MsgBase):
    def __init__(self):
        return

    def decode(self, data):
        # UTF-8 and variable type validator
        if type(data["subject"]) is str:
            self.subject = unicode(data["subject"], 'utf-8', 'replace')
        else:
            self.subject = unicode(str(data["subject"]), 'utf-8', 'replace')
        if type(data["body"]) is str:
            self.body = unicode(data["body"], 'utf-8', 'replace')
        else:
            self.body = unicode(str(data["body"]), 'utf-8', 'replace')

    def encode(self, data):
        super(Message, self).encode()
        try:
            self.data["subject"] = data["subject"]
            self.data["body"] = data["body"]
        except KeyError as e:
            logger.error("Missing key %s", e.name)
        return self.data

    def process(self):
        logger.debug("Subject: %i bytes", len(self.subject))
        logger.debug("Body: %i bytes", len(self.body))
