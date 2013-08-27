import shared

def sqlQuery(sqlStatement, *args):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(sqlStatement)

    if args == ():
        shared.sqlSubmitQueue.put('')
    else:
        shared.sqlSubmitQueue.put(args)
    
    queryreturn = shared.sqlReturnQueue.get()
    shared.sqlLock.release()

    return queryreturn

def sqlExecute(sqlStatement, *args):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(sqlStatement)

    if args == ():
        shared.sqlSubmitQueue.put('')
    else:
        shared.sqlSubmitQueue.put(args)
    
    shared.sqlReturnQueue.get()
    shared.sqlSubmitQueue.put('commit')
    shared.sqlLock.release()

def sqlStoredProcedure(procName):
    shared.sqlLock.acquire()
    shared.sqlSubmitQueue.put(procName)
    shared.sqlLock.release()
