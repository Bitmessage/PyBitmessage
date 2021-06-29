"""Tests for SQL thread"""
# flake8: noqa:E402
import os
import tempfile
import threading
import unittest

# from .common import skip_python3
#
# skip_python3()

os.environ['BITMESSAGE_HOME'] = tempfile.gettempdir()

try:
    from pybitmessage.helper_sql import (
    sqlQuery, sql_ready, sqlStoredProcedure, SqlBulkExecute, sqlExecuteScript, sqlExecute)  # noqa:E402
    from pybitmessage.class_sqlThread import sqlThread, UpgradeDB  # noqa:E402
    from pybitmessage.addresses import encodeAddress  # noqa:E402
except:
    from ..helper_sql import sqlStoredProcedure, sql_ready, sqlExecute, SqlBulkExecute, sqlQuery, sqlExecuteScript  # noqa:E402
    from ..class_sqlThread import (sqlThread, UpgradeDB)  # noqa:E402
    from ..addresses import encodeAddress  # noqa:E402


def filter_table_column(schema, column):
    """
        Filter column from schema
    """
    for x in schema:
        for y in x:
            if y == column:
                yield y


class TestSqlThread(unittest.TestCase):
    """Test case for SQL thread"""

    # query file path
    __name__ = None
    root_path = os.path.dirname(os.path.dirname(__file__))

    @classmethod
    def setUpClass(cls):
        """
            Start SQL thread
        """
        sqlLookup = sqlThread()
        sqlLookup.daemon = True
        sqlLookup.start()
        sql_ready.wait()

    @classmethod
    def setUp(cls):
        """
            Drop all tables before each test case start
        """
        tables = list(sqlQuery("select name from sqlite_master where type is 'table'"))
        with SqlBulkExecute() as sql:
            for q in tables:
                sql.execute("drop table if exists %s" % q)

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        """
            Join the thread
        """
        sqlStoredProcedure('exit')
        for thread in threading.enumerate():
            if thread.name == "SQL":
                thread.join()

    def initialise_database(self, file):  # pylint: disable=W0622, redefined-builtin
        """
            Initialise DB
        """
        with open(os.path.join(self.root_path, "tests/sql/{}.sql".format(file)), 'r') as sql_as_string:
            sql_as_string = sql_as_string.read()

        sqlExecuteScript(sql_as_string)

    def version(self):
        """
            Run SQL Scripts, Initialize DB with respect to versioning
            and Upgrade DB schema for all versions
        """
        def wrapper(*args):
            """
                Run SQL and mocking DB for versions
            """
            # import pdb; pdb.set_trace()
            self = args[0]
            func_name = func.__name__
            version = func_name.rsplit('_', 1)[-1]

            # Update versions DB mocking
            self.initialise_database("init_version_{}".format(version))

            if int(version) == 9:
                sqlThread().create_function()

            # Test versions
            upgrade_db = UpgradeDB()
            upgrade_db._upgrade_one_level_sql_statement(int(version))  # pylint: disable= W0212, protected-access
            return func(*args)  # <-- use (self, ...)
        func = self
        return wrapper

    def test_create_function(self):
        """
            Test create_function and asserting the result
        """

        # call create function
        encoded_str = encodeAddress(4, 1, "21122112211221122112")

        # Initialise Database
        self.initialise_database("create_function")

        sqlExecute('''INSERT INTO testhash (addressversion, hash) VALUES(4, "21122112211221122112")''')
        # call function in query

        sqlExecute('''UPDATE testhash SET address=(enaddr(testhash.addressversion, 1, hash));''')

        # Assertion
        query = sqlQuery('''select * from testhash;''')
        self.assertEqual(query[0][-1], encoded_str, "test case fail for create_function")
        sqlExecute('''DROP TABLE testhash''')

    @version
    def test_sql_thread_version_2(self):
        """
            Test with version 2
        """

        # Assertion
        res = sqlQuery(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='inventory_backup' ''')
        self.assertNotEqual(res[0][0], 1, "Table inventory_backup not deleted in versioning 2")

    @version
    def test_sql_thread_version_3(self):
        """
            Test with version 1
            Version 1 and 3 are same so will skip 3
        """

        # Assertion after versioning
        res = sqlQuery('''PRAGMA table_info('inventory');''')
        result = list(filter_table_column(res, "tag"))
        res = [tup for tup in res if any(i in tup for i in ["tag"])]
        self.assertEqual(result, ['tag'], "Data not migrated for version 1")
        self.assertEqual(res, [(5, 'tag', 'blob', 0, "''", 0)], "Data not migrated for version 1")

    @version
    def test_sql_thread_version_4(self):
        """
            Test with version 4
        """

        # Assertion
        res = sqlQuery('''select * from inventory where objecttype = 'pubkey';''')
        self.assertNotEqual(len(res), 1, "Table inventory not deleted in versioning 4")

    @version
    def test_sql_thread_version_5(self):
        """
            Test with version 5
        """

        # Assertion
        res = sqlQuery(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='knownnodes' ''')

        self.assertNotEqual(res[0][0], 1, "Table knownnodes not deleted in versioning 5")
        res = sqlQuery(''' SELECT count(name) FROM sqlite_master
            WHERE type='table' AND name='objectprocessorqueue'; ''')
        self.assertNotEqual(len(res), 0, "Table objectprocessorqueue not created in versioning 5")

    @version
    def test_sql_thread_version_6(self):
        """
            Test with version 6
        """

        # Assertion

        inventory = sqlQuery('''PRAGMA table_info('inventory');''')
        inventory = list(filter_table_column(inventory, "expirestime"))
        self.assertEqual(inventory, ['expirestime'], "Data not migrated for version 6")

        objectprocessorqueue = sqlQuery('''PRAGMA table_info('inventory');''')
        objectprocessorqueue = list(filter_table_column(objectprocessorqueue, "objecttype"))
        self.assertEqual(objectprocessorqueue, ['objecttype'], "Data not migrated for version 6")

    @version
    def test_sql_thread_version_7(self):
        """
            Test with version 7
        """

        # Assertion
        pubkeys = sqlQuery('''SELECT * FROM pubkeys ''')
        self.assertEqual(pubkeys, [], "Data not migrated for version 7")

        inventory = sqlQuery('''SELECT * FROM inventory ''')
        self.assertEqual(inventory, [], "Data not migrated for version 7")

        sent = sqlQuery('''SELECT status FROM sent ''')
        self.assertEqual(sent, [('msgqueued',), ('msgqueued',)], "Data not migrated for version 7")

    @version
    def test_sql_thread_version_8(self):
        """
            Test with version 8
        """

        # Assertion
        res = sqlQuery('''PRAGMA table_info('inbox');''')
        result = list(filter_table_column(res, "sighash"))
        self.assertEqual(result, ['sighash'], "Data not migrated for version 8")

    @version
    def test_sql_thread_version_9(self):
        """
            Test with version 9
        """

        # Assertion
        res = sqlQuery(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pubkeys_backup' ''')
        self.assertNotEqual(res[0][0], 1, "Table pubkeys_backup not deleted")

        res = sqlQuery('''PRAGMA table_info('pubkeys');''')
        # res = res.fetchall()
        result = list(filter_table_column(res, "address"))
        self.assertEqual(result, ['address'], "Data not migrated for version 9")

    @version
    def test_sql_thread_version_10(self):
        """
            Test with version 10
        """

        # Assertion
        res = sqlQuery(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='old_addressbook' ''')
        self.assertNotEqual(res[0][0], 1, "Table old_addressbook not deleted")
        self.assertEqual(len(res), 1, "Table old_addressbook not deleted")

        res = sqlQuery('''PRAGMA table_info('addressbook');''')
        result = list(filter_table_column(res, "address"))
        self.assertEqual(result, ['address'], "Data not migrated for version 10")
