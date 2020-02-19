"""
SQL-related functions defined here are really pass the queries (or other SQL
commands) to :class:`.threads.sqlThread` through `sqlSubmitQueue` queue and check
or return the result got from `sqlReturnQueue`.

This is done that way because :mod:`sqlite3` is so thread-unsafe that they
won't even let you call it from different threads using your own locks.
SQLite objects can only be used from one thread.

.. note:: This actually only applies for certain deployments, and/or
   really old version of sqlite. I haven't actually seen it anywhere.
   Current versions do have support for threading and multiprocessing.
   I don't see an urgent reason to refactor this, but it should be noted
   in the comment that the problem is mostly not valid. Sadly, last time
   I checked, there is no reliable way to check whether the library is
   or isn't thread-safe.
"""

import Queue
import threading

sqlSubmitQueue = Queue.Queue()
"""the queue for SQL"""
sqlReturnQueue = Queue.Queue()
"""the queue for results"""
sqlLock = threading.Lock()


def sqlQuery(sqlStatement, *args):
    """
    Query sqlite and return results

    :param str sqlStatement: SQL statement string
    :param list args: SQL query parameters
    :rtype: list
    """
    sqlLock.acquire()
    sqlSubmitQueue.put(sqlStatement)

    if args == ():
        sqlSubmitQueue.put('')
    elif isinstance(args[0], (list, tuple)):
        sqlSubmitQueue.put(args[0])
    else:
        sqlSubmitQueue.put(args)
    queryreturn, _ = sqlReturnQueue.get()
    sqlLock.release()

    return queryreturn


def sqlExecuteChunked(sqlStatement, idCount, *args):
    """Execute chunked SQL statement to avoid argument limit"""
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
                i:i + sqlExecuteChunked.chunkSize - (len(args) - idCount)
            ]
            sqlSubmitQueue.put(
                sqlStatement.format(','.join('?' * len(chunk_slice)))
            )
            # first static args, and then iterative chunk
            sqlSubmitQueue.put(
                args[0:len(args) - idCount] + chunk_slice
            )
            retVal = sqlReturnQueue.get()
            totalRowCount += retVal[1]
        sqlSubmitQueue.put('commit')
    return totalRowCount


def sqlExecute(sqlStatement, *args):
    """Execute SQL statement (optionally with arguments)"""
    sqlLock.acquire()
    sqlSubmitQueue.put(sqlStatement)

    if args == ():
        sqlSubmitQueue.put('')
    else:
        sqlSubmitQueue.put(args)
    _, rowcount = sqlReturnQueue.get()
    sqlSubmitQueue.put('commit')
    sqlLock.release()
    return rowcount


def sqlStoredProcedure(procName):
    """Schedule procName to be run"""
    sqlLock.acquire()
    sqlSubmitQueue.put(procName)
    sqlLock.release()


class SqlBulkExecute(object):
    """This is used when you have to execute the same statement in a cycle."""

    def __enter__(self):
        sqlLock.acquire()
        return self

    def __exit__(self, exc_type, value, traceback):
        sqlSubmitQueue.put('commit')
        sqlLock.release()

    @staticmethod
    def execute(sqlStatement, *args):
        """Used for statements that do not return results."""
        sqlSubmitQueue.put(sqlStatement)

        if args == ():
            sqlSubmitQueue.put('')
        else:
            sqlSubmitQueue.put(args)
        sqlReturnQueue.get()
