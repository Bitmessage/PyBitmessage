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
def insert(msgid=None, toAddress=None, fromAddress=None, subject=None, message=None,
           status=None, ripe=None, ackdata=None, sentTime=None, lastActionTime=None,
           sleeptill=0, retryNumber=0, encoding=2, ttl=None, folder='sent'):
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

    sentTime = sentTime if sentTime else int(time.time())  # sentTime (this doesn't change)
    lastActionTime = lastActionTime if lastActionTime else int(time.time())

    status = status if status else 'msgqueued'
    ttl = ttl if ttl else BMConfigParser().getint('bitmessagesettings', 'ttl')

    t = (msgid, toAddress, ripe, fromAddress, subject, message, ackdata,
         sentTime, lastActionTime, sleeptill, status, retryNumber, folder,
         encoding, ttl)

    sqlExecute('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)
    return msgid
