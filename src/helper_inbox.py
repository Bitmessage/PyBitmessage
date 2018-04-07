"""Helper Inbox performs inbox messagese related operations."""

from helper_sql import sqlExecute, sqlQuery
import queues


def insert(t):
    sqlExecute('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?,?)''', *t)
    # shouldn't emit changedInboxUnread and displayNewInboxMessage
    # at the same time
    # queues.UISignalQueue.put(('changedInboxUnread', None))


def trash(msgid):
    sqlExecute('''UPDATE inbox SET folder='trash' WHERE msgid=?''', msgid)
    queues.UISignalQueue.put(('removeInboxRowByMsgid', msgid))


def isMessageAlreadyInInbox(sigHash):
    queryReturn = sqlQuery(
        '''SELECT COUNT(*) FROM inbox WHERE sighash=?''', sigHash)
    return queryReturn[0][0] != 0
