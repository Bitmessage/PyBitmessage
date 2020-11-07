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
    # pylint: disable=unused-variable

    if '' in t or 0 in t:
        temp = list(t)
        temp_dict = {
            0: uuid.uuid4().bytes,  # if msgid is empty the put uuid
            7: int(time.time()),  # sentTime
            8: int(time.time()),  # lastActionTime
            9: 0,  # sleeptill
            10: 'msgqueued',
            11: 0,  # retryNumber
            12: 'sent',  # folder
            13: 2,  # encoding
            14: BMConfigParser().getint('bitmessagesettings', 'ttl')
        }

        if not temp[2] or not temp[6]:
            status, addressVersionNumber, streamNumber, ripe = decodeAddress(temp[1])
            if not temp[2]:
                temp_dict[2] = ripe

            if not temp[6]:
                stealthLevel = BMConfigParser().safeGetInt(
                    'bitmessagesettings', 'ackstealthlevel')
                ackdata = genAckPayload(streamNumber, stealthLevel)
                temp_dict[6] = ackdata

        for i in dict(enumerate(temp)):
            if not temp[i]:
                temp[i] = temp_dict[i]
        t = tuple(temp)
    sqlExecute('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)
    return t if is_testcase else None
