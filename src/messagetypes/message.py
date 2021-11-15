import logging

logger = logging.getLogger('default')


class MsgBase(object):  # pylint: disable=too-few-public-methods
    """Base class for message types"""
    def __init__(self):
        self.data = {"": type(self).__name__.lower()}


class Message(MsgBase):
    """Encapsulate a message"""
    # pylint: disable=attribute-defined-outside-init

    def decode(self, data):
        """Decode a message"""
        # UTF-8 and variable type validator
        subject = data.get("subject", "")
        body = data.get("body", "")
        try:
            data["subject"] = subject.decode('utf-8', 'replace')
        except:
            data["subject"] = ''

        try:
            data["body"] = body.decode('utf-8', 'replace')
        except:
            data["body"] = ''

        self.subject = data["subject"]
        self.body = data["body"]

    def encode(self, data):
        """Encode a message"""
        super(Message, self).__init__()
        self.data["subject"] = data.get("subject", "")
        self.data["body"] = data.get("body", "")

        return self.data

    def process(self):
        """Process a message"""
        logger.debug("Subject: %i bytes", len(self.subject))
        logger.debug("Body: %i bytes", len(self.body))
