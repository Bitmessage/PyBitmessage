import shared

def insert(t):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(
        '''INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?)''')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    shared.sqlLock.release()
    
def trash(msgid):
    t = (msgid,)
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(
        '''UPDATE inbox SET folder='trash' WHERE msgid=?''')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    shared.sqlLock.release()
    shared.UISignalQueue.put(('removeInboxRowByMsgid',msgid))
    
