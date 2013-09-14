from helper_sql import *
import shared

def insert(t):
    sqlExecute('''INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?)''', *t)
    
def trash(msgid):
    sqlExecute('''UPDATE inbox SET folder='trash' WHERE msgid=?''', msgid)
    shared.UISignalQueue.put(('removeInboxRowByMsgid',msgid))
    
