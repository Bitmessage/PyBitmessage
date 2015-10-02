from PyQt4 import QtCore, QtGui

import shared
import re
import sys

def accountClass(address):
    if not shared.config.has_section(address):
        return None
    try:
        gateway = shared.config.get(address, "gateway")
        if (gateway == "mailchuck"):
            return MailchuckAccount(address)
        else:
            return GatewayAccount(address)
    except:
        return BMAccount(address)

class BMAccount(object):
    def __init__(self, address):
        self.address = address
        
    def parseMessage(self, toAddress, fromAddress, subject, message):
        self.toAddress = toAddress
        self.fromAddress = fromAddress
        self.subject = subject
        self.message = message

class GatewayAccount(BMAccount):
    def __init__(self, address):
        super(BMAccount, self).__init__(address)
    
    def parseMessage(self, toAddress, fromAddress, subject, message):
        super(BMAccount, self).parseMessage(toAddress, fromAddress, subject, message)

class MailchuckAccount(GatewayAccount):
    registrationAddress = "BM-2cVYYrhaY5Gbi3KqrX9Eae2NRNrkfrhCSA"
    unregistrationAddress = "BM-2cVMAHTRjZHCTPMue75XBK5Tco175DtJ9J"
    relayAddress = "BM-2cWim8aZwUNqxzjMxstnUMtVEUQJeezstf"
    regExpIncoming = re.compile("(.*)MAILCHUCK-FROM::(\S+) \| (.*)")
    regExpOutgoing = re.compile("(\S+) (.*)")
    def __init__(self, address):
        super(GatewayAccount, self).__init__(address)

    def parseMessage(self, toAddress, fromAddress, subject, message):
        super(GatewayAccount, self).parseMessage(toAddress, fromAddress, subject, message)
        if fromAddress == self.relayAddress:
            matches = self.regExpIncoming.search(subject)
            if not matches is None:
                self.subject = ""
                if not matches.group(1) is None:
                    self.subject += matches.group(1)
                if not matches.group(3) is None:
                    self.subject += matches.group(3)
                if not matches.group(2) is None:
                    self.fromAddress = matches.group(2)
        if toAddress == self.relayAddress:
            matches = self.regExpOutgoing.search(subject)
            if not matches is None:
                if not matches.group(2) is None:
                    self.subject = matches.group(2)
                if not matches.group(1) is None:
                    self.toAddress = matches.group(1)        