from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import *
from debug import logger
from messagetypes import MsgBase


class Message(MsgBase):
    def __init__(self):
        return

    def decode(self, data):
        # UTF-8 and variable type validator
        if type(data["subject"]) is str:
            self.subject = str(data["subject"], 'utf-8', 'replace')
        else:
            self.subject = str(str(data["subject"]), 'utf-8', 'replace')
        if type(data["body"]) is str:
            self.body = str(data["body"], 'utf-8', 'replace')
        else:
            self.body = str(str(data["body"]), 'utf-8', 'replace')

    def encode(self, data):
        super(Message, self).encode()
        try:
            self.data["subject"] = data["subject"]
            self.data["body"] = data["body"]
        except KeyError as e:
            logger.error("Missing key %s", e)
        return self.data

    def process(self):
        logger.debug("Subject: %i bytes", len(self.subject))
        logger.debug("Body: %i bytes", len(self.body))
