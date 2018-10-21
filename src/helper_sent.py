"""
src/helper_sent.py
==================
"""

from helper_sql import sqlExecute


def insert(t):
    """Perform an insert into the `sent` table"""
    sqlExecute('''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', *t)
