"""
    Test for sqlThread
"""

import os
import unittest
from ..helper_sql import sqlStoredProcedure, sql_ready, sqlExecute, SqlBulkExecute, sqlQuery, sqlExecuteScript
from ..class_sqlThread import (sqlThread, UpgradeDB)
from ..addresses import encodeAddress
from .common import skip_python3
import time

skip_python3()


class TestSqlThread(unittest.TestCase):
    """
        Test case for SQLThread
    """

    # query file path
    root_path = os.path.dirname(os.path.dirname(__file__))

    @classmethod
    def setUpClass(cls):
        # Start SQL thread
        print("1============")
        sqlLookup = sqlThread()
        print("2============")
        sqlLookup.daemon = False
        print("3============")
        # time.sleep(5)
        sqlLookup.start()
        print("4============")
        # time.sleep(5)
        print("5============")
        sql_ready.wait()
        print("6============")

    @classmethod
    def setUp(cls):
        tables = list(sqlQuery("select name from sqlite_master where type is 'table'"))
        with SqlBulkExecute() as sql:
            for q in tables:
                sql.execute("drop table if exists %s" % q)

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        # Stop sql thread
        sqlStoredProcedure('exit')

    def initialise_database(self, file):
        """
            Initialise DB
        """

        sql_as_string = open(os.path.join(self.root_path, "tests/sql/{}.sql".format(file))).read()
        sqlExecuteScript(sql_as_string)

    def versioning(func):
        def wrapper(*args):
            self = args[0]
            func_name = func.__name__
            version = func_name.rsplit('_', 1)[-1]

            print("-------------------------===============")
            print(func_name)
            print(version)
            print("upgrade_schema_data_", version)
            print("-------------------------===============")

            # Update versions DB mocking
            self.initialise_database("init_version_{}".format(version))

            # Test versions
            upgrade_db = UpgradeDB()
            getattr(upgrade_db, "upgrade_schema_data_{}".format(version))()
            ret = func(*args)
            return ret  # <-- use (self, ...)
        return wrapper

    def test_create_function(self):
        # call create function

        encoded_str = encodeAddress(4, 1, "21122112211221122112")

        # Initialise Database
        self.initialise_database("create_function")

        sqlExecute('''INSERT INTO testhash (addressversion, hash) VALUES(4, "21122112211221122112")''')
        # call function in query

        sqlExecute('''UPDATE testhash SET address=(enaddr(testhash.addressversion, 1, hash)) WHERE hash=testhash.hash''')

        # Assertion
        query = sqlQuery('''select * from testhash;''')
        self.assertEqual(query[0][-1], encoded_str, "test case fail for create_function")
        sqlExecute('''DROP TABLE testhash''')

    def filter_table_column(self, schema, column):
        for x in schema:
            for y in x:
                if y == column:
                    yield y


    @versioning
    def test_sql_thread_version_1(self):
        """
            Test with version 1
        """

        # Assertion after versioning
        res = sqlQuery('''PRAGMA table_info('inventory');''')
        # res = res.fetchall()
        print(res)
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
        res = sqlExecute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='old_addressbook' ''')
        print("res---------------------------------")
        print(res)
        print("res---------------------------------")
        self.assertNotEqual(res, 1, "Table old_addressbook not deleted")
        self.assertEqual(res, -1, "Table old_addressbook not deleted")

        res = sqlQuery('''PRAGMA table_info('addressbook');''')
        # # res = res.fetchall()
        result = list(self.filter_table_column(res, "address"))
        self.assertEqual(result, ['address'], "Data not migrated for version 10")


    # @versioning
    # def test_sql_thread_version_9(self):
    #     """
    #         Test with version 9
    #     """
    #
    #     # Assertion
    #     self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pubkeys_backup' ''')
    #     self.assertNotEqual(self.cur.fetchone(), 1, "Table pubkeys_backup not deleted")
    #
    #     res = self.cur.execute('''PRAGMA table_info('pubkeys');''')
    #     res = res.fetchall()
    #     result = list(self.filter_table_column(res, "address"))
    #     self.assertEqual(result, ['address'], "Data not migrated for version 9")
    #
    # @versioning
    # def test_sql_thread_version_8(self):
    #     """
    #         Test with version 8
    #     """
    #
    #     # Assertion
    #     res = self.cur.execute('''PRAGMA table_info('inbox');''')
    #     res = res.fetchall()
    #     result = list(self.filter_table_column(res, "sighash"))
    #     self.assertEqual(result, ['sighash'], "Data not migrated for version 8")
    #
    # @versioning
    # def test_sql_thread_version_7(self):
    #     """
    #         Test with version 7
    #     """
    #
    #     # Assertion
    #     pubkeys = self.cur.execute('''SELECT * FROM pubkeys ''')
    #     pubkeys = pubkeys.fetchall()
    #     self.assertEqual(pubkeys, [], "Data not migrated for version 7")
    #
    #     inventory = self.cur.execute('''SELECT * FROM inventory ''')
    #     inventory = inventory.fetchall()
    #     self.assertEqual(inventory, [], "Data not migrated for version 7")
    #
    #     sent = self.cur.execute('''SELECT status FROM sent ''')
    #     sent = sent.fetchall()
    #     self.assertEqual(sent, [('msgqueued',), ('msgqueued',)], "Data not migrated for version 7")
    #
    # @versioning
    # def test_sql_thread_version_6(self):
    #     """
    #         Test with version 6
    #     """
    #
    #     # Assertion
    #
    #     inventory = self.cur.execute('''PRAGMA table_info('inventory');''')
    #     inventory = inventory.fetchall()
    #     inventory = list(self.filter_table_column(inventory, "expirestime"))
    #     self.assertEqual(inventory, ['expirestime'], "Data not migrated for version 6")
    #
    #     objectprocessorqueue = self.cur.execute('''PRAGMA table_info('inventory');''')
    #     objectprocessorqueue = objectprocessorqueue.fetchall()
    #     objectprocessorqueue = list(self.filter_table_column(objectprocessorqueue, "objecttype"))
    #     self.assertEqual(objectprocessorqueue, ['objecttype'], "Data not migrated for version 6")
    #
    # @versioning
    # def test_sql_thread_version_5(self):
    #     """
    #         Test with version 5
    #     """
    #
    #     # Assertion
    #     self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='knownnodes' ''')
    #     self.assertNotEqual(self.cur.fetchone(), 1, "Table knownnodes not deleted in versioning 5")
    #     self.cur.execute(
    #         ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='objectprocessorqueue'; ''')
    #     self.assertNotEqual(self.cur.fetchone(), 0, "Table objectprocessorqueue not created in versioning 5")
    #
    # @versioning
    # def test_sql_thread_version_4(self):
    #     """
    #         Test with version 4
    #     """
    #
    #     # Assertion
    #     self.cur.execute('''select * from inventory where objecttype = 'pubkey';''')
    #     self.assertNotEqual(self.cur.fetchone(), 1, "Table inventory not deleted in versioning 4")
    #
    # def test_sql_thread_version_3(self):
    #     """
    #         Test with version 3 and 1 both are same
    #     """
    #     pass
    #
    # @versioning
    # def test_sql_thread_version_2(self):
    #     """
    #         Test with version 2
    #     """
    #
    #     # Assertion
    #     self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='inventory_backup' ''')
    #     self.assertNotEqual(self.cur.fetchone(), 1, "Table inventory_backup not deleted in versioning 2")
