import shared

def insert(t):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(
        '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    shared.sqlLock.release()
    
def updateStatusByAckData(t):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(
        'UPDATE sent SET status=? WHERE ackdata=?')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    shared.sqlLock.release()
    
def updateStatusForPossibleNewPubKey(t):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(
        '''UPDATE sent SET status='doingmsgpow' WHERE toripe=? AND (status='awaitingpubkey' or status='doingpubkeypow') and folder='sent' ''')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    shared.sqlLock.release()
    
def updateStatusForResend(t):
    shared.sqlSubmitQueue.put(
        '''UPDATE sent SET lastactiontime=?, msgretrynumber=?, status=? WHERE ackdata=?''')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    
def updateStatusForRerequestPubKey(t):
    shared.sqlSubmitQueue.put(
        '''UPDATE sent SET lastactiontime=?, pubkeyretrynumber=?, status='msgqueued' WHERE toripe=?''')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')