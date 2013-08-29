import threading
import Queue

sqlSubmitQueue = Queue.Queue() #SQLITE3 is so thread-unsafe that they won't even let you call it from different threads using your own locks. SQL objects can only be called from one thread.
sqlReturnQueue = Queue.Queue()
sqlLock = threading.Lock()

def sqlQuery(sqlStatement, *args):
    sqlLock.acquire()
    sqlSubmitQueue.put(sqlStatement)

    if args == ():
        sqlSubmitQueue.put('')
    else:
        sqlSubmitQueue.put(args)
    
    queryreturn = sqlReturnQueue.get()
    sqlLock.release()

    return queryreturn

def sqlExecute(sqlStatement, *args):
    sqlLock.acquire()
    sqlSubmitQueue.put(sqlStatement)

    if args == ():
        sqlSubmitQueue.put('')
    else:
        sqlSubmitQueue.put(args)
    
    sqlReturnQueue.get()
    sqlSubmitQueue.put('commit')
    sqlLock.release()

def sqlStoredProcedure(procName):
    sqlLock.acquire()
    sqlSubmitQueue.put(procName)
    sqlLock.release()
