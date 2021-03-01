"""
    Test for sqlThread blind signatures
"""

import os
import unittest
import sqlite3
import sys
from ..state import appdata
from ..helper_sql import sqlStoredProcedure
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

    def normalize_version(self, file):
        try:
            root_path = os.path.dirname(os.path.dirname(__file__))
            sql_file_path = os.path.join(root_path, 'tests/sql/')
            sql_file_path = os.path.join(sql_file_path, "init_version_{}.sql".format(file))
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

    def versioning(func):
        def wrapper(*args):
            self = args[0]
            func_name = func.__name__
            version = func_name.rsplit('_', 1)[-1]

            # Update versions DB mocking
            self.normalize_version(version)

            # Test versions
            upgrade_db = UpgradeDB()
            upgrade_db.cur = self.cur
            getattr(upgrade_db, "upgrade_schema_data_{}".format(version))()
            ret = func(*args)
            return ret  # <-- use (self, ...)
        return wrapper

    def change_state(self):
        self.normalize_version("1")

    @versioning
    def test_sql_thread_version_1(self):
        """
            Test with version 1
        """

        # Assertion after versioning
        res = self.cur.execute('''PRAGMA table_info('inventory');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "tag"))
        res = [tup for tup in res if any(i in tup for i in ["tag"])]
        self.assertEqual(result, ['tag'], "Data not migrated for version 1")
        self.assertEqual(res, [(5, 'tag', 'blob', 0, "''", 0)], "Data not migrated for version 1")

    @versioning
    def test_sql_thread_version_10(self):
        """
            Test with version 10
        """

        # Assertion
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='old_addressbook' ''')
        self.assertNotEqual(self.cur.fetchone(), 1, "Table old_addressbook not deleted")

        res = self.cur.execute('''PRAGMA table_info('addressbook');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "address"))
        self.assertEqual(result, ['address'], "Data not migrated for version 10")

    @versioning
    def test_sql_thread_version_9(self):
        """
            Test with version 9
        """

        # Assertion
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pubkeys_backup' ''')
        self.assertNotEqual(self.cur.fetchone(), 1, "Table pubkeys_backup not deleted")

        res = self.cur.execute('''PRAGMA table_info('pubkeys');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "address"))
        self.assertEqual(result, ['address'], "Data not migrated for version 9")

    @versioning
    def test_sql_thread_version_8(self):
        """
            Test with version 8
        """

        # Assertion
        res = self.cur.execute('''PRAGMA table_info('inbox');''')
        res = res.fetchall()
        result = list(self.filter_table_column(res, "sighash"))
        self.assertEqual(result, ['sighash'], "Data not migrated for version 8")

    @versioning
    def test_sql_thread_version_7(self):
        """
            Test with version 7
        """

        # Assertion
        pubkeys = self.cur.execute('''SELECT * FROM pubkeys ''')
        pubkeys = pubkeys.fetchall()
        self.assertEqual(pubkeys, [], "Data not migrated for version 7")

        inventory = self.cur.execute('''SELECT * FROM inventory ''')
        inventory = inventory.fetchall()
        self.assertEqual(inventory, [], "Data not migrated for version 7")

        sent = self.cur.execute('''SELECT status FROM sent ''')
        sent = sent.fetchall()
        self.assertEqual(sent, [('msgqueued',), ('msgqueued',)], "Data not migrated for version 7")

    @versioning
    def test_sql_thread_version_6(self):
        """
            Test with version 6
        """

        # Assertion

        inventory = self.cur.execute('''PRAGMA table_info('inventory');''')
        inventory = inventory.fetchall()
        inventory = list(self.filter_table_column(inventory, "expirestime"))
        self.assertEqual(inventory, ['expirestime'], "Data not migrated for version 6")

        objectprocessorqueue = self.cur.execute('''PRAGMA table_info('inventory');''')
        objectprocessorqueue = objectprocessorqueue.fetchall()
        objectprocessorqueue = list(self.filter_table_column(objectprocessorqueue, "objecttype"))
        self.assertEqual(objectprocessorqueue, ['objecttype'], "Data not migrated for version 6")

    @versioning
    def test_sql_thread_version_5(self):
        """
            Test with version 5
        """

        # Assertion
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='knownnodes' ''')
        self.assertNotEqual(self.cur.fetchone(), 1, "Table knownnodes not deleted in versioning 5")
        self.cur.execute(
            ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='objectprocessorqueue'; ''')
        self.assertNotEqual(self.cur.fetchone(), 0, "Table objectprocessorqueue not created in versioning 5")

    @versioning
    def test_sql_thread_version_4(self):
        """
            Test with version 4
        """

        # Assertion
        self.cur.execute('''select * from inventory where objecttype = 'pubkey';''')
        self.assertNotEqual(self.cur.fetchone(), 1, "Table inventory not deleted in versioning 4")

    def test_sql_thread_version_3(self):
        """
            Test with version 3 and 1 both are same
        """
        pass

    @versioning
    def test_sql_thread_version_2(self):
        """
            Test with version 2
        """

        # Assertion
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='inventory_backup' ''')
        self.assertNotEqual(self.cur.fetchone(), 1, "Table inventory_backup not deleted in versioning 2")
