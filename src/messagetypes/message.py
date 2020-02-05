import logging

from messagetypes import MsgBase
# pylint: disable=attribute-defined-outside-init

logger = logging.getLogger('default')


class Message(MsgBase):
    """Encapsulate a message"""
    # pylint: disable=attribute-defined-outside-init

    def decode(self, data):
        """Decode a message"""
        # UTF-8 and variable type validator
        if isinstance(data["subject"], str):
            # Unicode is depreciated
            self.subject =data["subject"]
        else:
            # Unicode is depreciated
            self.subject = str(data["subject"])
        if isinstance(data["body"], str):
            # Unicode is depreciated
            self.body = data["body"]
        else:
            # Unicode is depreciated
            self.body = str(data["body"])

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
