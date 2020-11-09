"""
Insert values into sent table
"""

import time
import uuid
from addresses import decodeAddress
from bmconfigparser import BMConfigParser
from helper_ackPayload import genAckPayload
from helper_sql import sqlExecute


# pylint: disable=too-many-arguments
def insert(msgid, toAddress, ripe, fromAddress, subject, message, ackdata,
           sentTime, lastActionTime, sleeptill=0, status='msgqueued',
           retryNumber=0, folder='sent', encoding=2, ttl=0, is_testcase=False):
    """Perform an insert into the `sent` table"""
    # pylint: disable=unused-variable
    # pylint: disable-msg=too-many-locals

    msgid = msgid if msgid else uuid.uuid4().bytes

    if not ripe or not ackdata:
        new_status, addressVersionNumber, streamNumber, new_ripe = decodeAddress(toAddress)
        if not ripe:
            ripe = new_ripe

        if not ackdata:
            stealthLevel = BMConfigParser().safeGetInt(
                'bitmessagesettings', 'ackstealthlevel')
            new_ackdata = genAckPayload(streamNumber, stealthLevel)
            ackdata = new_ackdata

    sentTime = sentTime if sentTime else int(time.time())
    lastActionTime = lastActionTime if lastActionTime else int(time.time())

    sleeptill = sleeptill if sleeptill else 0
    status = status if status else 'msgqueued'
    retryNumber = retryNumber if retryNumber else 0
    folder = folder if folder else 'sent'
    encoding = encoding if encoding else 2

    ttl = ttl if ttl else BMConfigParser().getint('bitmessagesettings', 'ttl')

    t = (msgid, toAddress, ripe, fromAddress, subject, message, ackdata,
         sentTime, lastActionTime, sleeptill, status, retryNumber, folder,
         encoding, ttl)

    sqlExecute('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)
    return t if is_testcase else None
