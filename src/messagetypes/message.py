import logging

from messagetypes import MsgBase

logger = logging.getLogger('default')


class Message(MsgBase):
    """Encapsulate a message"""
    # pylint: disable=attribute-defined-outside-init

    def decode(self, data):
        """Decode a message"""
        # UTF-8 and variable type validator
        if isinstance(data["subject"], str):
            self.subject = unicode(data["subject"], 'utf-8', 'replace')
        else:
            self.subject = unicode(str(data["subject"]), 'utf-8', 'replace')
        if isinstance(data["body"], str):
            self.body = unicode(data["body"], 'utf-8', 'replace')
        else:
            self.body = unicode(str(data["body"]), 'utf-8', 'replace')

    def encode(self, data):
        """Encode a message"""
        super(Message, self).__init__()
        try:
            self.data["subject"] = data["subject"]
            self.data["body"] = data["body"]
        except KeyError as e:
            logger.error("Missing key %s", e)
        return self.data

    def process(self):
        """Process a message"""
        logger.debug("Subject: %i bytes", len(self.subject))
        logger.debug("Body: %i bytes", len(self.body))
