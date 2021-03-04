"""
    Test for sqlThread
"""

import os
import unittest
from ..helper_sql import sqlStoredProcedure, sql_ready, sqlExecute, SqlBulkExecute, sqlQuery, sqlExecuteScript
from ..class_sqlThread import (sqlThread)
from ..addresses import encodeAddress
from .common import skip_python3


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
        sqlLookup = sqlThread()
        sqlLookup.daemon = False
        sqlLookup.start()
        sql_ready.wait()

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
