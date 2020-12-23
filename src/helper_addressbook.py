"""
Insert value into addressbook
"""

from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery


def insert(address, label):
    """perform insert into addressbook"""
    queryreturn = sqlQuery(
        '''SELECT count(*) FROM addressbook WHERE address=?''', address)

    if address not in BMConfigParser().addresses() and not queryreturn[0][0]:
        return sqlExecute('''INSERT INTO addressbook VALUES (?,?)''', label, address) == 1
    return False
