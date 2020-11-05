"""
Insert values into sent table
"""

import time
import uuid
from addresses import decodeAddress
from bmconfigparser import BMConfigParser
from helper_ackPayload import genAckPayload
from helper_sql import sqlExecute


def insert(t, is_testcase=False):
    """Perform an insert into the `sent` table"""
    all_fields_availabe = all([True if i else False for i in t])
    if not all_fields_availabe:
        temp = list(t)
        if not temp[0]:
            temp[0] = uuid.uuid4().bytes    # if msgid is empty the put uuid
        if not temp[2] or not temp[6]:
            status, addressVersionNumber, streamNumber, ripe = decodeAddress(temp[1])
            if not temp[2]:
                temp[2] = ripe
            if not temp[6]:
                stealthLevel = BMConfigParser().safeGetInt(
                    'bitmessagesettings', 'ackstealthlevel')
                ackdata = genAckPayload(streamNumber, stealthLevel)
                temp[6] = ackdata
        if not temp[7]:  # sentTime
            temp[7] = int(time.time())
        if not temp[8]:  # lastActionTime
            temp[8] = int(time.time())
        if not temp[9] and temp[9] != 0:  # sleeptill
            temp[9] = 0
        if not temp[10]:
            temp[10] = 'msgqueued'
        if not temp[11] and temp[11] != 0:
            temp[11] = 0
        if not temp[12]:
            temp[12] = 'sent'
        if not temp[13]:
            temp[13] = 2  # checking encoding
        if not temp[14]:
            temp[14] = BMConfigParser().getint('bitmessagesettings', 'ttl')
        t = tuple(temp)
    sqlExecute('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)
    return t if is_testcase else None
