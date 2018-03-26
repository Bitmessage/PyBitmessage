from PyQt4 import QtCore, QtGui

import queues
import re
import sys
import inspect
from helper_sql import *
from helper_ackPayload import genAckPayload
from addresses import decodeAddress
from bmconfigparser import BMConfigParser
from foldertree import AccountMixin
from pyelliptic.openssl import OpenSSL
from utils import str_broadcast_subscribers
import time

def getSortedAccounts():
    configSections = BMConfigParser().addresses()
    configSections.sort(cmp = 
        lambda x,y: cmp(unicode(BMConfigParser().get(x, 'label'), 'utf-8').lower(), unicode(BMConfigParser().get(y, 'label'), 'utf-8').lower())
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
            FROM inbox, subscriptions ON subscriptions.address = inbox.fromaddress
            WHERE read = 0 AND toaddress = ?
            GROUP BY inbox.fromaddress, folder''', str_broadcast_subscribers)
        for row in queryreturn:
            address, folder, cnt = row
            if not folder in ret[address]:
                ret[address][folder] = {
                    'label': ret[address]['inbox']['label'],
                    'enabled': ret[address]['inbox']['enabled']
                }
            ret[address][folder]['count'] = cnt
    return ret

def accountClass(address):
    if not BMConfigParser().has_section(address):
        # FIXME: This BROADCAST section makes no sense
        if address == str_broadcast_subscribers:
            subscription = BroadcastAccount(address)
            if subscription.type != AccountMixin.BROADCAST:
                return None
        else:
            subscription = SubscriptionAccount(address)
            if subscription.type != AccountMixin.SUBSCRIPTION:
                # e.g. deleted chan
                return NoAccount(address)
        return subscription
    try:
        gateway = BMConfigParser().get(address, "gateway")
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
            elif BMConfigParser().safeGetBoolean(self.address, 'mailinglist'):
                self.type = AccountMixin.MAILINGLIST
            elif BMConfigParser().safeGetBoolean(self.address, 'chan'):
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
        self.type = AccountMixin.NORMAL
        if BMConfigParser().has_section(address):
            if BMConfigParser().safeGetBoolean(self.address, 'chan'):
                self.type = AccountMixin.CHAN
            elif BMConfigParser().safeGetBoolean(self.address, 'mailinglist'):
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
        if BMConfigParser().has_section(address):
            label = BMConfigParser().get(address, 'label')
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
        if isinstance(subject, unicode):
            self.subject = subject.encode('utf-8', 'ignore').decode('utf-8')    ####  str(subject)  not ascii
        else:
            self.subject = subject
        self.message = message
        self.fromLabel = self.getLabel(fromAddress)
        self.toLabel = self.getLabel(toAddress)


class NoAccount(BMAccount):
    def __init__(self, address = None):
        self.address = address
        self.type = AccountMixin.NORMAL

    def getLabel(self, address = None):
        if address is None:
            address = self.address
        return address

        
class SubscriptionAccount(BMAccount):
    pass
    

class BroadcastAccount(BMAccount):
    pass
        
        
class GatewayAccount(BMAccount):
    gatewayName = None
    ALL_OK = 0
    REGISTRATION_DENIED = 1
    def __init__(self, address):
        super(GatewayAccount, self).__init__(address)
        
    def send(self):
        status, addressVersionNumber, streamNumber, ripe = decodeAddress(self.toAddress)
        stealthLevel = BMConfigParser().safeGetInt('bitmessagesettings', 'ackstealthlevel')
        ackdata = genAckPayload(streamNumber, stealthLevel)
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
            min(BMConfigParser().getint('bitmessagesettings', 'ttl'), 86400 * 2) # not necessary to have a TTL higher than 2 days
        )

        queues.workerQueue.put(('sendmessage', self.toAddress))
    
    def parseMessage(self, toAddress, fromAddress, subject, message):
        super(GatewayAccount, self).parseMessage(toAddress, fromAddress, subject, message)

class MailchuckAccount(GatewayAccount):
    # set "gateway" in keys.dat to this
    gatewayName = "mailchuck"
    registrationAddress = "BM-2cVYYrhaY5Gbi3KqrX9Eae2NRNrkfrhCSA"
    unregistrationAddress = "BM-2cVMAHTRjZHCTPMue75XBK5Tco175DtJ9J"
    relayAddress = "BM-2cWim8aZwUNqxzjMxstnUMtVEUQJeezstf"
    regExpIncoming = re.compile("(.*)MAILCHUCK-FROM::(\S+) \| (.*)")
    regExpOutgoing = re.compile("(\S+) (.*)")
    def __init__(self, address):
        super(MailchuckAccount, self).__init__(address)
        self.feedback = self.ALL_OK
        
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

    def status(self):
        self.toAddress = self.registrationAddress
        self.subject = "status"
        self.message = ""
        self.fromAddress = self.address
        self.send()

    def settings(self):
        self.toAddress = self.registrationAddress
        self.subject = "config"
        self.message = QtGui.QApplication.translate("Mailchuck", """# You can use this to configure your email gateway account
# Uncomment the setting you want to use
# Here are the options:
# 
# pgp: server
# The email gateway will create and maintain PGP keys for you and sign, verify,
# encrypt and decrypt on your behalf. When you want to use PGP but are lazy,
# use this. Requires subscription.
#
# pgp: local
# The email gateway will not conduct PGP operations on your behalf. You can
# either not use PGP at all, or use it locally.
#
# attachments: yes
# Incoming attachments in the email will be uploaded to MEGA.nz, and you can
# download them from there by following the link. Requires a subscription.
#
# attachments: no
# Attachments will be ignored.
# 
# archive: yes
# Your incoming emails will be archived on the server. Use this if you need
# help with debugging problems or you need a third party proof of emails. This
# however means that the operator of the service will be able to read your
# emails even after they have been delivered to you.
#
# archive: no
# Incoming emails will be deleted from the server as soon as they are relayed
# to you.
#
# masterpubkey_btc: BIP44 xpub key or electrum v1 public seed
# offset_btc: integer (defaults to 0)
# feeamount: number with up to 8 decimal places
# feecurrency: BTC, XBT, USD, EUR or GBP
# Use these if you want to charge people who send you emails. If this is on and
# an unknown person sends you an email, they will be requested to pay the fee
# specified. As this scheme uses deterministic public keys, you will receive
# the money directly. To turn it off again, set "feeamount" to 0. Requires
# subscription.
""")
        self.fromAddress = self.address

    def parseMessage(self, toAddress, fromAddress, subject, message):
        super(MailchuckAccount, self).parseMessage(toAddress, fromAddress, subject, message)
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
        self.feedback = self.ALL_OK
        if fromAddress == self.registrationAddress and self.subject == "Registration Request Denied":
            self.feedback = self.REGISTRATION_DENIED
        return self.feedback
