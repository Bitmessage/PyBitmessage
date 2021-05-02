"""Tests for SQL thread"""

import os
import tempfile
import threading
import unittest

os.environ['BITMESSAGE_HOME'] = tempfile.gettempdir()  # noqa:E402

from pybitmessage.helper_sql import sqlQuery, sql_ready, sqlStoredProcedure
from pybitmessage.class_sqlThread import sqlThread
from pybitmessage.addresses import encodeAddress


class TestSqlThread(unittest.TestCase):
    """Test case for SQL thread"""

    @classmethod
    def setUpClass(cls):
        # Start SQL thread
        sqlLookup = sqlThread()
        sqlLookup.daemon = True
        sqlLookup.start()
        sql_ready.wait()

    @classmethod
    def tearDownClass(cls):
        sqlStoredProcedure('exit')
        for thread in threading.enumerate():
            if thread.name == "SQL":
                thread.join()

    def test_create_function(self):
        """Check the result of enaddr function"""
        encoded_str = encodeAddress(4, 1, "21122112211221122112")

        query = sqlQuery('SELECT enaddr(4, 1, "21122112211221122112")')
        self.assertEqual(
            query[0][-1], encoded_str, "test case fail for create_function")
