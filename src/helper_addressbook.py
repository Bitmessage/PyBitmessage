"""
Insert value into addressbook
"""

from bmconfigparser import config
from helper_sql import sqlExecute
from dbcompat import dbstr


def insert(address, label):
    """perform insert into addressbook"""

    if address not in config.addresses():
        return sqlExecute('''INSERT INTO addressbook VALUES (?,?)''', dbstr(label), dbstr(address)) == 1
    return False
