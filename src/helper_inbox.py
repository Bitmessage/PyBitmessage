from helper_sql import *
import shared

def insert(t):
    sqlExecute('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?)''', *t)
    shared.UISignalQueue.put(('changedInboxUnread', None))
    
def trash(msgid):
    sqlExecute('''UPDATE inbox SET folder='trash' WHERE msgid=?''', msgid)
    shared.UISignalQueue.put(('removeInboxRowByMsgid',msgid))
    
def isMessageAlreadyInInbox(toAddress, fromAddress, subject, body, encodingType):
    queryReturn = sqlQuery(
        '''SELECT COUNT(*) FROM inbox WHERE toaddress=? AND fromaddress=? AND subject=? AND message=? AND encodingtype=? ''', toAddress, fromAddress, subject, body, encodingType)
    return queryReturn[0][0] != 0