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
    elif type(args[0]) in [list, tuple]:
        sqlSubmitQueue.put(args[0])
    else:
        sqlSubmitQueue.put(args)
    
    queryreturn, rowcount = sqlReturnQueue.get()
    sqlLock.release()

    return queryreturn


def sqlExecuteChunked(sqlStatement, idCount, *args):
    # SQLITE_MAX_VARIABLE_NUMBER,
    # unfortunately getting/setting isn't exposed to python
    sqlExecuteChunked.chunkSize = 999

    if idCount == 0 or idCount > len(args):
        return 0

    totalRowCount = 0
    with sqlLock:
        for i in range(
            len(args) - idCount, len(args),
            sqlExecuteChunked.chunkSize - (len(args) - idCount)
        ):
            chunk_slice = args[
                i:i+sqlExecuteChunked.chunkSize - (len(args) - idCount)
            ]
            sqlSubmitQueue.put(
                sqlStatement.format(','.join('?' * len(chunk_slice)))
            )
            # first static args, and then iterative chunk
            sqlSubmitQueue.put(
                args[0:len(args)-idCount] + chunk_slice
            )
            retVal = sqlReturnQueue.get()
            totalRowCount += retVal[1]
        sqlSubmitQueue.put('commit')
    return totalRowCount


def sqlExecute(sqlStatement, *args):
    sqlLock.acquire()
    sqlSubmitQueue.put(sqlStatement)

    if args == ():
        sqlSubmitQueue.put('')
    else:
        sqlSubmitQueue.put(args)
    
    queryreturn, rowcount = sqlReturnQueue.get()
    sqlSubmitQueue.put('commit')
    sqlLock.release()
    return rowcount

def sqlStoredProcedure(procName):
    sqlLock.acquire()
    sqlSubmitQueue.put(procName)
    sqlLock.release()

class SqlBulkExecute:
    def __enter__(self):
        sqlLock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        sqlSubmitQueue.put('commit')
        sqlLock.release()

    def execute(self, sqlStatement, *args):
        sqlSubmitQueue.put(sqlStatement)
        
        if args == ():
            sqlSubmitQueue.put('')
        else:
            sqlSubmitQueue.put(args)
        sqlReturnQueue.get()

    def query(self, sqlStatement, *args):
        sqlSubmitQueue.put(sqlStatement)

        if args == ():
            sqlSubmitQueue.put('')
        else:
            sqlSubmitQueue.put(args)
        return sqlReturnQueue.get()

