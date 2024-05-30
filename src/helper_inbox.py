"""Helper Inbox performs inbox messages related operations"""

import sqlite3

import queues
from helper_sql import sqlExecute, sqlQuery
from dbcompat import dbstr


def insert(t):
    """Perform an insert into the "inbox" table"""
    u = [sqlite3.Binary(t[0]), dbstr(t[1]), dbstr(t[2]), dbstr(t[3]), dbstr(t[4]), dbstr(t[5]), dbstr(t[6]), t[7], t[8], sqlite3.Binary(t[9])]
    sqlExecute('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?,?)''', *u)
    # shouldn't emit changedInboxUnread and displayNewInboxMessage
    # at the same time
    # queues.UISignalQueue.put(('changedInboxUnread', None))


def trash(msgid):
    """Mark a message in the `inbox` as `trash`"""
    rowcount = sqlExecute('''UPDATE inbox SET folder='trash' WHERE msgid=?''', sqlite3.Binary(msgid))
    if rowcount < 1:
        sqlExecute('''UPDATE inbox SET folder='trash' WHERE msgid=CAST(? AS TEXT)''', msgid)
    queues.UISignalQueue.put(('removeInboxRowByMsgid', msgid))


def delete(ack_data):
    """Permanent delete message from trash"""
    rowcount = sqlExecute("DELETE FROM inbox WHERE msgid = ?", sqlite3.Binary(ack_data))
    if rowcount < 1:
        sqlExecute("DELETE FROM inbox WHERE msgid = CAST(? AS TEXT)", ack_data)


def undeleteMessage(msgid):
    """Undelte the message"""
    rowcount = sqlExecute('''UPDATE inbox SET folder='inbox' WHERE msgid=?''', sqlite3.Binary(msgid))
    if rowcount < 1:
        sqlExecute('''UPDATE inbox SET folder='inbox' WHERE msgid=CAST(? AS TEXT)''', msgid)


def isMessageAlreadyInInbox(sigHash):
    """Check for previous instances of this message"""
    queryReturn = sqlQuery(
        '''SELECT COUNT(*) FROM inbox WHERE sighash=?''', sqlite3.Binary(sigHash))
    if len(queryReturn) < 1:
        queryReturn = sqlQuery(
            '''SELECT COUNT(*) FROM inbox WHERE sighash=CAST(? AS TEXT)''', sigHash)
    return queryReturn[0][0] != 0
