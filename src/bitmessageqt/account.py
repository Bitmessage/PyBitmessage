from PyQt4 import QtCore, QtGui

import shared
import re
import sys
import inspect
from helper_sql import *
from addresses import decodeAddress
from foldertree import AccountMixin
from pyelliptic.openssl import OpenSSL
from utils import str_broadcast_subscribers
import time

def getSortedAccounts():
    configSections = filter(lambda x: x != 'bitmessagesettings', shared.config.sections())
    configSections.sort(cmp = 
        lambda x,y: cmp(unicode(shared.config.get(x, 'label'), 'utf-8').lower(), unicode(shared.config.get(y, 'label'), 'utf-8').lower())
        )
    return configSections

def getSortedSubscriptions(count = False):
    queryreturn = sqlQuery('SELECT label, address, enabled FROM subscriptions ORDER BY label COLLATE NOCASE ASC')
    ret = {}
    for row in queryreturn:
        label, address, enabled = row
        ret[address] = {}
        ret[address]["inbox"] = {}
        ret[address]["inbox"]['label'] = label
        ret[address]["inbox"]['enabled'] = enabled
        ret[address]["inbox"]['count'] = 0
    if count:
        queryreturn = sqlQuery('''SELECT fromaddress, folder, count(msgid) as cnt
            FROM inbox, subscriptions
            WHERE read = 0 AND subscriptions.address = inbox.fromaddress
            GROUP BY inbox.fromaddress, folder''')
        for row in queryreturn:
            address, folder, cnt = row
            ret[address][folder]['count'] = cnt
    return ret

def accountClass(address):
    if not shared.config.has_section(address):
        if address == str_broadcast_subscribers:
            subscription = BroadcastAccount(address)
            if subscription.type != AccountMixin.BROADCAST:
                return None
        else:
            subscription = SubscriptionAccount(address)
            if subscription.type != AccountMixin.SUBSCRIPTION:
                return None
        return subscription
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
    
class AccountColor(AccountMixin):
    def __init__(self, address, type = None):
        self.isEnabled = True
        self.address = address
        if type is None:
            if address is None:
                self.type = AccountMixin.ALL
            elif shared.safeConfigGetBoolean(self.address, 'mailinglist'):
                self.type = AccountMixin.MAILINGLIST
            elif shared.safeConfigGetBoolean(self.address, 'chan'):
                self.type = AccountMixin.CHAN
            elif sqlQuery(
                '''select label from subscriptions where address=?''', self.address):
                self.type = AccountMixin.SUBSCRIPTION
            else:
                self.type = AccountMixin.NORMAL
        else:
            self.type = type
        
    
class BMAccount(object):
    def __init__(self, address = None):
        self.address = address
        self.type = 'normal'
        if shared.config.has_section(address):
            if shared.safeConfigGetBoolean(self.address, 'chan'):
                self.type = AccountMixin.CHAN
            elif shared.safeConfigGetBoolean(self.address, 'mailinglist'):
                self.type = AccountMixin.MAILINGLIST
        elif self.address == str_broadcast_subscribers:
            self.type = AccountMixin.BROADCAST
        else:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''', self.address)
            if queryreturn:
                self.type = AccountMixin.SUBSCRIPTION

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

        
class SubscriptionAccount(BMAccount):
    pass
    

class BroadcastAccount(BMAccount):
    pass
        
        
class GatewayAccount(BMAccount):
    gatewayName = None
    def __init__(self, address):
        super(BMAccount, self).__init__(address)
        
    def send(self):
        status, addressVersionNumber, streamNumber, ripe = decodeAddress(self.toAddress)
        ackdata = OpenSSL.rand(32)
        t = ()
        sqlExecute(
            '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            '',
            self.toAddress,
            ripe,
            self.fromAddress,
            self.subject,
            self.message,
            ackdata,
            int(time.time()), # sentTime (this will never change)
            int(time.time()), # lastActionTime
            0, # sleepTill time. This will get set when the POW gets done.
            'msgqueued',
            0, # retryNumber
            'sent', # folder
            2, # encodingtype
            shared.config.getint('bitmessagesettings', 'ttl')
        )

        shared.workerQueue.put(('sendmessage', self.toAddress))
    
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
        
    def createMessage(self, toAddress, fromAddress, subject, message):
        self.subject = toAddress + " " + subject
        self.toAddress = self.relayAddress
        self.fromAddress = fromAddress
        self.message = message
        
    def register(self, email):
        self.toAddress = self.registrationAddress
        self.subject = email
        self.message = ""
        self.fromAddress = self.address
        self.send()
        
    def unregister(self):
        self.toAddress = self.unregistrationAddress
        self.subject = ""
        self.message = ""
        self.fromAddress = self.address
        self.send()

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
                    self.fromAddress = matches.group(2)
        if toAddress == self.relayAddress:
            matches = self.regExpOutgoing.search(subject)
            if not matches is None:
                if not matches.group(2) is None:
                    self.subject = matches.group(2)
                if not matches.group(1) is None:
                    self.toLabel = matches.group(1)
                    self.toAddress = matches.group(1)