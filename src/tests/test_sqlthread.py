"""
    Test for sqlThread
"""

import os
import unittest
from ..helper_sql import sqlStoredProcedure, sql_ready, sqlExecute, SqlBulkExecute, sqlQuery, sqlExecuteScript
from ..class_sqlThread import (sqlThread)
from ..addresses import encodeAddress

import threading

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
        sqlLookup.daemon = True
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
        sqlStoredProcedure('exit')
        for thread in threading.enumerate():
            if thread.name == "SQL":
                thread.join()

    def initialise_database(self, file):
        """
            Initialise DB
        """
        with open(os.path.join(self.root_path, "tests/sql/{}.sql".format(file)), 'r') as sql_as_string:
            # sql_as_string = open(os.path.join(self.root_path, "tests/sql/{}.sql".format(file))).read()
            sql_as_string = sql_as_string.read()
        sqlExecuteScript(sql_as_string)

    def test_create_function(self):
        # call create function
        encoded_str = encodeAddress(4, 1, "21122112211221122112")

        # Initialise Database
        self.initialise_database("create_function")

        sqlExecute('''INSERT INTO testhash (addressversion, hash) VALUES(4, "21122112211221122112")''')
        # call function in query

        # sqlExecute('''UPDATE testhash SET address=(enaddr(testhash.addressversion, 1, hash)) WHERE hash=testhash.hash''')
        sqlExecute('''UPDATE testhash SET address=(enaddr(testhash.addressversion, 1, hash));''')

        # Assertion
        query = sqlQuery('''select * from testhash;''')
        self.assertEqual(query[0][-1], encoded_str, "test case fail for create_function")
        sqlExecute('''DROP TABLE testhash''')
