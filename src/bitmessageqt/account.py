# pylint: disable=too-many-instance-attributes,attribute-defined-outside-init
"""
account.py
==========

Account related functions.

"""

from __future__ import absolute_import

import inspect
import re
import sys
import time

from PyQt4 import QtGui

import queues
from addresses import decodeAddress
from bmconfigparser import config
from helper_ackPayload import genAckPayload
from helper_sql import sqlQuery, sqlExecute
from .foldertree import AccountMixin
from .utils import str_broadcast_subscribers


def getSortedAccounts():
    """Get a sorted list of configSections"""

    configSections = config.addresses()
    configSections.sort(
        cmp=lambda x, y: cmp(
            unicode(
                config.get(
                    x,
                    'label'),
                'utf-8').lower(),
            unicode(
                config.get(
                    y,
                    'label'),
                'utf-8').lower()))
    return configSections


def getSortedSubscriptions(count=False):
    """
    Actually return a grouped dictionary rather than a sorted list

    :param count: Whether to count messages for each fromaddress in the inbox
    :type count: bool, default False
    :retuns: dict keys are addresses, values are dicts containing settings
    :rtype: dict, default {}
    """
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
            if folder not in ret[address]:
                ret[address][folder] = {
                    'label': ret[address]['inbox']['label'],
                    'enabled': ret[address]['inbox']['enabled']
                }
            ret[address][folder]['count'] = cnt
    return ret


def accountClass(address):
    """Return a BMAccount for the address"""
    if not config.has_section(address):
        # .. todo:: This BROADCAST section makes no sense
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
        gateway = config.get(address, "gateway")
        for _, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if issubclass(cls, GatewayAccount) and cls.gatewayName == gateway:
                return cls(address)
        # general gateway
        return GatewayAccount(address)
    except:
        pass
    # no gateway
    return BMAccount(address)


class AccountColor(AccountMixin):  # pylint: disable=too-few-public-methods
    """Set the type of account"""

    def __init__(self, address, address_type=None):
        self.isEnabled = True
        self.address = address
        if address_type is None:
            if address is None:
                self.type = AccountMixin.ALL
            elif config.safeGetBoolean(self.address, 'mailinglist'):
                self.type = AccountMixin.MAILINGLIST
            elif config.safeGetBoolean(self.address, 'chan'):
                self.type = AccountMixin.CHAN
            elif sqlQuery(
                    '''select label from subscriptions where address=?''', self.address):
                self.type = AccountMixin.SUBSCRIPTION
            else:
                self.type = AccountMixin.NORMAL
        else:
            self.type = address_type


class BMAccount(object):
    """Encapsulate a Bitmessage account"""

    def __init__(self, address=None):
        self.address = address
        self.type = AccountMixin.NORMAL
        if config.has_section(address):
            if config.safeGetBoolean(self.address, 'chan'):
                self.type = AccountMixin.CHAN
            elif config.safeGetBoolean(self.address, 'mailinglist'):
                self.type = AccountMixin.MAILINGLIST
        elif self.address == str_broadcast_subscribers:
            self.type = AccountMixin.BROADCAST
        else:
            queryreturn = sqlQuery(
                '''select label from subscriptions where address=?''', self.address)
            if queryreturn:
                self.type = AccountMixin.SUBSCRIPTION

    def getLabel(self, address=None):
        """Get a label for this bitmessage account"""
        if address is None:
            address = self.address
        label = config.safeGet(address, 'label', address)
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
        """Set metadata and address labels on self"""

        self.toAddress = toAddress
        self.fromAddress = fromAddress
        if isinstance(subject, unicode):
            self.subject = str(subject)
        else:
            self.subject = subject
        self.message = message
        self.fromLabel = self.getLabel(fromAddress)
        self.toLabel = self.getLabel(toAddress)


class NoAccount(BMAccount):
    """Override the __init__ method on a BMAccount"""

    def __init__(self, address=None):  # pylint: disable=super-init-not-called
        self.address = address
        self.type = AccountMixin.NORMAL

    def getLabel(self, address=None):
        if address is None:
            address = self.address
        return address


class SubscriptionAccount(BMAccount):
    """Encapsulate a subscription account"""
    pass


class BroadcastAccount(BMAccount):
    """Encapsulate a broadcast account"""
    pass


class GatewayAccount(BMAccount):
    """Encapsulate a gateway account"""

    gatewayName = None
    ALL_OK = 0
    REGISTRATION_DENIED = 1

    def __init__(self, address):
        super(GatewayAccount, self).__init__(address)

    def send(self):
        """Override the send method for gateway accounts"""

        # pylint: disable=unused-variable
        status, addressVersionNumber, streamNumber, ripe = decodeAddress(self.toAddress)
        stealthLevel = config.safeGetInt('bitmessagesettings', 'ackstealthlevel')
        ackdata = genAckPayload(streamNumber, stealthLevel)
        sqlExecute(
            '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            '',
            self.toAddress,
            ripe,
            self.fromAddress,
            self.subject,
            self.message,
            ackdata,
            int(time.time()),  # sentTime (this will never change)
            int(time.time()),  # lastActionTime
            0,  # sleepTill time. This will get set when the POW gets done.
            'msgqueued',
            0,  # retryNumber
            'sent',  # folder
            2,  # encodingtype
            # not necessary to have a TTL higher than 2 days
            min(config.getint('bitmessagesettings', 'ttl'), 86400 * 2)
        )

        queues.workerQueue.put(('sendmessage', self.toAddress))


class MailchuckAccount(GatewayAccount):
    """Encapsulate a particular kind of gateway account"""

    # set "gateway" in keys.dat to this
    gatewayName = "mailchuck"
    registrationAddress = "BM-2cVYYrhaY5Gbi3KqrX9Eae2NRNrkfrhCSA"
    unregistrationAddress = "BM-2cVMAHTRjZHCTPMue75XBK5Tco175DtJ9J"
    relayAddress = "BM-2cWim8aZwUNqxzjMxstnUMtVEUQJeezstf"
    regExpIncoming = re.compile(r"(.*)MAILCHUCK-FROM::(\S+) \| (.*)")
    regExpOutgoing = re.compile(r"(\S+) (.*)")

    def __init__(self, address):
        super(MailchuckAccount, self).__init__(address)
        self.feedback = self.ALL_OK

    def createMessage(self, toAddress, fromAddress, subject, message):
        """createMessage specific to a MailchuckAccount"""
        self.subject = toAddress + " " + subject
        self.toAddress = self.relayAddress
        self.fromAddress = fromAddress
        self.message = message

    def register(self, email):
        """register specific to a MailchuckAccount"""
        self.toAddress = self.registrationAddress
        self.subject = email
        self.message = ""
        self.fromAddress = self.address
        self.send()

    def unregister(self):
        """unregister specific to a MailchuckAccount"""
        self.toAddress = self.unregistrationAddress
        self.subject = ""
        self.message = ""
        self.fromAddress = self.address
        self.send()

    def status(self):
        """status specific to a MailchuckAccount"""
        self.toAddress = self.registrationAddress
        self.subject = "status"
        self.message = ""
        self.fromAddress = self.address
        self.send()

    def settings(self):
        """settings specific to a MailchuckAccount"""

        self.toAddress = self.registrationAddress
        self.subject = "config"
        self.message = QtGui.QApplication.translate(
            "Mailchuck",
            """# You can use this to configure your email gateway account
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
        """parseMessage specific to a MailchuckAccount"""

        super(MailchuckAccount, self).parseMessage(toAddress, fromAddress, subject, message)
        if fromAddress == self.relayAddress:
            matches = self.regExpIncoming.search(subject)
            if matches is not None:
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
            if matches is not None:
                if not matches.group(2) is None:
                    self.subject = matches.group(2)
                if not matches.group(1) is None:
                    self.toLabel = matches.group(1)
                    self.toAddress = matches.group(1)
        self.feedback = self.ALL_OK
        if fromAddress == self.registrationAddress and self.subject == "Registration Request Denied":
            self.feedback = self.REGISTRATION_DENIED
        return self.feedback
