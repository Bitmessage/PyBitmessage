"""
Insert value into addressbook
"""

from bmconfigparser import config
from helper_sql import sqlExecute


def insert(address, label):
    """perform insert into addressbook"""

    if address not in config.addresses():
        return sqlExecute('''INSERT INTO addressbook VALUES (?,?)''', label, address) == 1
    return False
