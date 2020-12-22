import logging

# from ..messagetypes import MsgBase
# pylint: disable=attribute-defined-outside-init

try:
    from messagetypes import MsgBase
except ModuleNotFoundError:
    from ..messagetypes import MsgBase
logger = logging.getLogger('default')


class Chatmsg(MsgBase):
    """Encapsulate a chatmsg"""
    # pylint: disable=attribute-defined-outside-init

    def decode(self, data):
        """Decode a message"""
        # UTF-8 and variable type validator
        if isinstance(data["message"], str):
            # Unicode is depreciated
            self.message = data["message"]
        else:
            # Unicode is depreciated
            self.message = str(data["message"])

    def encode(self, data):
        """Encode a message"""
        super(Chatmsg, self).__init__()
        try:
            self.data["message"] = data["message"]
        except KeyError as e:
            logger.error("Missing key %s", e)
        return self.data

    def process(self):
        """Process a message"""
        logger.debug("Message: %i bytes", len(self.message))
