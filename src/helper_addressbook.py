"""
Insert value into addressbook
"""

from helper_sql import sqlExecute


def insert(address, label):
    """perform insert into addressbook"""

    sqlExecute('''INSERT INTO addressbook VALUES (?,?)''', label, address)
