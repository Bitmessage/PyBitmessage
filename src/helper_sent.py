"""
Insert values into sent table
"""

import uuid
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute


def insert(t):
    """Perform an insert into the `sent` table"""
    if not t[0] or not t[-1]:
        temp = list(t)
        if not t[0]:
            temp[0] = uuid.uuid4().bytes    # if msgid is empty the put uuid
        if not t[-1]:
            temp[-1] = BMConfigParser().getint('bitmessagesettings', 'ttl')
        t = tuple(temp)
    sqlExecute('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)
