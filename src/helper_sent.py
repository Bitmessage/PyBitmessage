"""
Insert values into sent table
"""

import time
import uuid
import sqlite3
from addresses import decodeAddress
from bmconfigparser import config
from helper_ackPayload import genAckPayload
from helper_sql import sqlExecute, sqlQuery
from dbcompat import dbstr


# pylint: disable=too-many-arguments
def insert(msgid=None, toAddress='[Broadcast subscribers]', fromAddress=None, subject=None,
           message=None, status='msgqueued', ripe=None, ackdata=None, sentTime=None,
           lastActionTime=None, sleeptill=0, retryNumber=0, encoding=2, ttl=None, folder='sent'):
    """Perform an insert into the `sent` table"""
    # pylint: disable=unused-variable
    # pylint: disable-msg=too-many-locals

    valid_addr = True
    if not ripe or not ackdata:
        addr = fromAddress if toAddress == '[Broadcast subscribers]' else toAddress
        new_status, addressVersionNumber, streamNumber, new_ripe = decodeAddress(addr)
        valid_addr = True if new_status == 'success' else False
        if not ripe:
            ripe = new_ripe

        if not ackdata:
            stealthLevel = config.safeGetInt(
                'bitmessagesettings', 'ackstealthlevel')
            new_ackdata = genAckPayload(streamNumber, stealthLevel)
            ackdata = new_ackdata
    if valid_addr:
        msgid = msgid if msgid else uuid.uuid4().bytes
        sentTime = sentTime if sentTime else int(time.time())  # sentTime (this doesn't change)
        lastActionTime = lastActionTime if lastActionTime else int(time.time())

        ttl = ttl if ttl else config.getint('bitmessagesettings', 'ttl')

        t = (sqlite3.Binary(msgid), dbstr(toAddress), sqlite3.Binary(ripe), dbstr(fromAddress), dbstr(subject), dbstr(message), sqlite3.Binary(ackdata),
             sentTime, lastActionTime, sleeptill, dbstr(status), retryNumber, dbstr(folder),
             encoding, ttl)

        sqlExecute('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)
        return ackdata
    else:
        return None


def delete(ack_data):
    """Perform Delete query"""
    rowcount = sqlExecute("DELETE FROM sent WHERE ackdata = ?", sqlite3.Binary(ack_data))
    if rowcount < 1:
        sqlExecute("DELETE FROM sent WHERE ackdata = CAST(? AS TEXT)", ack_data)


def retrieve_message_details(ack_data):
    """Retrieving Message details"""
    data = sqlQuery(
        "select toaddress, fromaddress, subject, message, received from inbox where msgid = ?", sqlite3.Binary(ack_data)
    )
    if len(data) < 1:
        data = sqlQuery(
            "select toaddress, fromaddress, subject, message, received from inbox where msgid = CAST(? AS TEXT)", ack_data
        )
    return data


def trash(ackdata):
    """Mark a message in the `sent` as `trash`"""
    rowcount = sqlExecute(
        '''UPDATE sent SET folder='trash' WHERE ackdata=?''', sqlite3.Binary(ackdata)
    )
    if rowcount < 1:
        rowcount = sqlExecute(
            '''UPDATE sent SET folder='trash' WHERE ackdata=CAST(? AS TEXT)''', ackdata
        )
    return rowcount
