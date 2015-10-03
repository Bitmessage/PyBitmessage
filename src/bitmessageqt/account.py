from PyQt4 import QtCore, QtGui

import shared
import re
import sys
import inspect
from helper_sql import *

def accountClass(address):
    if not shared.config.has_section(address):
        return None
    try:
        gateway = shared.config.get(address, "gateway")
        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
#            obj = g(address)
            if issubclass(cls, GatewayAccount) and cls.gatewayName == gateway:
                return cls(address)
        # general gateway
        return GatewayAccount(address)
    except:
        pass
    # no gateway
    return BMAccount(address)

class BMAccount(object):
    def __init__(self, address = None):
        self.address = address
        
    def getLabel(self, address = None):
        if address is None:
            address = self.address
        label = address
        if shared.config.has_section(address):
            label = shared.config.get(address, 'label')
        queryreturn = sqlQuery(
            '''select label from addressbook where address=?''', address)
        if queryreturn != []:
            for row in queryreturn:
                label, = row
        else:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''', address)
            if queryreturn != []:
                for row in queryreturn:
                    label, = row
        return label
        
    def parseMessage(self, toAddress, fromAddress, subject, message):
        self.toAddress = toAddress
        self.fromAddress = fromAddress
        self.subject = subject
        self.message = message
        self.fromLabel = self.getLabel(fromAddress)
        self.toLabel = self.getLabel(toAddress)

class GatewayAccount(BMAccount):
    gatewayName = None
    def __init__(self, address):
        super(BMAccount, self).__init__(address)
    
    def parseMessage(self, toAddress, fromAddress, subject, message):
        super(BMAccount, self).parseMessage(toAddress, fromAddress, subject, message)

class MailchuckAccount(GatewayAccount):
    # set "gateway" in keys.dat to this
    gatewayName = "mailchuck"
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
                    self.fromLabel = matches.group(2)
        if toAddress == self.relayAddress:
            matches = self.regExpOutgoing.search(subject)
            if not matches is None:
                if not matches.group(2) is None:
                    self.subject = matches.group(2)
                if not matches.group(1) is None:
                    self.toLabel = matches.group(1)        