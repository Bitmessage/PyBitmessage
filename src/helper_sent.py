import shared

def insert(t):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(
        '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''')
    shared.sqlSubmitQueue.put(t)
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    shared.sqlLock.release()
    
