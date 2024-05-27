"""Helper Inbox performs inbox messages related operations"""

import queues
from helper_sql import sqlExecute, sqlQuery
from dbcompat import dbstr


def insert(t):
    """Perform an insert into the "inbox" table"""
    u = [t[0], dbstr(t[1]), dbstr(t[2]), dbstr(t[3]), dbstr(t[4]), dbstr(t[5]), dbstr(t[6]), t[7], t[8], t[9]]
    sqlExecute('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?,?)''', *u)
    # shouldn't emit changedInboxUnread and displayNewInboxMessage
    # at the same time
    # queues.UISignalQueue.put(('changedInboxUnread', None))


def trash(msgid):
    """Mark a message in the `inbox` as `trash`"""
    sqlExecute('''UPDATE inbox SET folder='trash' WHERE msgid=?''', msgid)
    queues.UISignalQueue.put(('removeInboxRowByMsgid', msgid))


def delete(ack_data):
    """Permanent delete message from trash"""
    sqlExecute("DELETE FROM inbox WHERE msgid = ?", ack_data)


def undeleteMessage(msgid):
    """Undelte the message"""
    sqlExecute('''UPDATE inbox SET folder='inbox' WHERE msgid=?''', msgid)


def isMessageAlreadyInInbox(sigHash):
    """Check for previous instances of this message"""
    queryReturn = sqlQuery(
        '''SELECT COUNT(*) FROM inbox WHERE sighash=?''', sigHash)
    return queryReturn[0][0] != 0
