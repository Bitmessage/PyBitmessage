"""
    Test for sqlThread blind signatures
"""

import os
import unittest
import shutil  # used for moving the messages.dat file
import sqlite3
import sys
import threading
import time
# print sys.path
# import state
# import sql
# from sql import init_version_1.sql
from ..state import appdata
from ..helper_sql import sqlStoredProcedure
# import threading
# from hashlib import sha256
# from ..helper_sql import sqlQuery
# from ..version import softwareVersion
# from common import cleanup
from ..class_sqlThread import (sqlThread, UpgradeDB)


class TestSqlThread(unittest.TestCase):
    """
        Test case for SQLThread
    """

    conn = sqlite3.connect(appdata + 'messages.dat')
    conn.text_factory = str
    cur = conn.cursor()

    @classmethod
    def setUpClass(cls):
        # Start SQL thread
        sqlLookup = sqlThread()
        sqlLookup.daemon = False
        sqlLookup.start()

    @classmethod
    def setUp(cls):
        tables = list(cls.cur.execute("select name from sqlite_master where type is 'table'"))
        cls.cur.executescript(';'.join(["drop table if exists %s" % i for i in tables]))

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        # Stop sql thread
        sqlStoredProcedure('exit')

    def db_connection(self):
        conn = sqlite3.connect(appdata + 'messages.dat')
        conn.text_factory = str
        return conn.cursor()

    def normalize_version(self, file):
        try:
            root_path = os.path.dirname(os.path.dirname(__file__))
            sql_file_path = os.path.join(root_path, 'tests/sql/')
            sql_file_path = os.path.join(sql_file_path, "init_version_"+file+".sql")
            sql_file = open(sql_file_path)
            sql_as_string = sql_file.read()
            self.cur.executescript(sql_as_string)
            self.conn.commit()
        except Exception as err:
            if str(err) == 'table inbox already exists':
                return "table inbox already exists"
            else:
                sys.stderr.write(
                    'ERROR trying to create database file (message.dat). Error message: %s\n' % str(err))
                os._exit(0)

    def filter_table_column(self, schema, column):
        for x in schema:
            for y in x:
                if y == column:
                    yield y

    def test_sql_thread_version_1(self):
        """
            Test with version 1
        """

        # normalise Db for version 1
        self.normalize_version("1")

        # Test versioning
        upgrade_db = UpgradeDB()
        upgrade_db.cur = self.cur
        upgrade_db.upgrade_schema_data_1()

        # Assertion after versioning
        res = self.cur.execute('''PRAGMA table_info('inventory');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "tag"))
        res = [tup for tup in res if any(i in tup for i in ["tag"])]
        self.assertEqual(result, ['tag'] , "Data not migrated for version 1")
        self.assertEqual(res, [(5, 'tag', 'blob', 0, "''", 0)] , "Data not migrated for version 1")


    def test_sql_thread_version_10(self):
        """
            Test with version 10
        """

        # Update version 10
        self.normalize_version("10")

        # Test versioning
        upgrade_db = UpgradeDB()
        upgrade_db.cur = self.cur
        upgrade_db.upgrade_schema_data_10()

        # Assertion
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='old_addressbook' ''')
        self.assertNotEqual(self.cur.fetchone(), 1 , "Table old_addressbook not deleted")

        res = self.cur.execute('''PRAGMA table_info('addressbook');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "address"))
        self.assertEqual(result, ['address'] , "Data not migrated for version 10")


    def test_sql_thread_version_9(self):
        """
            Test with version 9
        """

        # Update version 9
        self.normalize_version("9")

        # Test versioning
        upgrade_db = UpgradeDB()
        upgrade_db.cur = self.cur
        upgrade_db.upgrade_schema_data_9()

        # Assertion
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pubkeys_backup' ''')
        self.assertNotEqual(self.cur.fetchone(), 1 , "Table pubkeys_backup not deleted")

        res = self.cur.execute('''PRAGMA table_info('pubkeys');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "address"))
        self.assertEqual(result, ['address'] , "Data not migrated for version 9")


    def test_sql_thread_version_8(self):
        """
            Test with version 8
        """

        # Update version 8
        self.normalize_version("8")

        # Test versioning
        upgrade_db = UpgradeDB()
        upgrade_db.cur = self.cur
        upgrade_db.upgrade_schema_data_8()

        # # Assertion
        res = self.cur.execute('''PRAGMA table_info('inbox');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "sighash"))
        self.assertEqual(result, ['sighash'] , "Data not migrated for version 8")


