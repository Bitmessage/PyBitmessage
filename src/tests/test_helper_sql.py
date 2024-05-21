"""Test cases for helper_sql"""

import unittest

try:
    # Python 3
    from unittest.mock import patch
except ImportError:
    # Python 2
    from mock import patch

import pybitmessage.helper_sql as helper_sql


class TestHelperSql(unittest.TestCase):
    """Test class for helper_sql"""

    @classmethod
    def setUpClass(cls):
        helper_sql.sql_available = True

    @patch("pybitmessage.helper_sql.sqlSubmitQueue.put")
    @patch("pybitmessage.helper_sql.sqlReturnQueue.get")
    def test_sqlquery_no_args(self, mock_sqlreturnqueue_get, mock_sqlsubmitqueue_put):
        """Test sqlQuery with no additional arguments"""
        mock_sqlreturnqueue_get.return_value = ("dummy_result", None)
        result = helper_sql.sqlQuery(
            "SELECT msgid FROM inbox where folder='inbox' ORDER BY received"
        )
        self.assertEqual(mock_sqlsubmitqueue_put.call_count, 2)
        self.assertEqual(result, "dummy_result")

    @patch("pybitmessage.helper_sql.sqlSubmitQueue.put")
    @patch("pybitmessage.helper_sql.sqlReturnQueue.get")
    def test_sqlquery_with_args(self, mock_sqlreturnqueue_get, mock_sqlsubmitqueue_put):
        """Test sqlQuery with additional arguments"""
        mock_sqlreturnqueue_get.return_value = ("dummy_result", None)
        result = helper_sql.sqlQuery(
            "SELECT address FROM addressbook WHERE address=?", "PB-5yfds868gbkj"
        )
        self.assertEqual(mock_sqlsubmitqueue_put.call_count, 2)
        self.assertEqual(result, "dummy_result")

    @patch("pybitmessage.helper_sql.sqlSubmitQueue.put")
    @patch("pybitmessage.helper_sql.sqlReturnQueue.get")
    def test_sqlexecute(self, mock_sqlreturnqueue_get, mock_sqlsubmitqueue_put):
        """Test sqlExecute with valid arguments"""
        mock_sqlreturnqueue_get.return_value = (None, 1)
        rowcount = helper_sql.sqlExecute(
            "UPDATE sent SET status = 'msgqueued'"
            "WHERE ackdata = ? AND folder = 'sent'",
            "1710652313",
        )
        self.assertEqual(mock_sqlsubmitqueue_put.call_count, 3)
        self.assertEqual(rowcount, 1)

    @patch("pybitmessage.helper_sql.SqlBulkExecute.execute")
    def test_sqlexecute_script(self, mock_execute):
        """Test sqlExecuteScript with a SQL script"""
        helper_sql.sqlExecuteScript(
            "CREATE TABLE test (id INTEGER); INSERT INTO test VALUES (1);"
        )
        self.assertTrue(mock_execute.assert_called)

    @patch("pybitmessage.helper_sql.sqlSubmitQueue.put")
    @patch(
        "pybitmessage.helper_sql.sqlReturnQueue.get",
    )
    def test_sqlexecute_chunked(self, mock_sqlreturnqueue_get, mock_sqlsubmitqueue_put):
        """Test sqlExecuteChunked with valid arguments"""
        # side_effect is list of return value (_, rowcount)
        # of sqlReturnQueue.get for each chunk
        CHUNK_COUNT = 6
        CHUNK_SIZE = 999
        ID_COUNT = CHUNK_COUNT * CHUNK_SIZE
        CHUNKS_ROWCOUNT_LIST = [50, 29, 28, 18, 678, 900]
        TOTAL_ROW_COUNT = sum(CHUNKS_ROWCOUNT_LIST)
        mock_sqlreturnqueue_get.side_effect = [(None, rowcount) for rowcount in CHUNKS_ROWCOUNT_LIST]
        args = []
        for i in range(0, ID_COUNT):
            args.append("arg{}".format(i))
        total_row_count_return = helper_sql.sqlExecuteChunked(
            "INSERT INTO table VALUES {}", ID_COUNT, *args
        )
        self.assertEqual(TOTAL_ROW_COUNT, total_row_count_return)
        self.assertTrue(mock_sqlsubmitqueue_put.called)
        self.assertTrue(mock_sqlreturnqueue_get.called)

    @patch("pybitmessage.helper_sql.sqlSubmitQueue.put")
    @patch("pybitmessage.helper_sql.sqlReturnQueue.get")
    def test_sqlexecute_chunked_with_idcount_zero(
        self, mock_sqlreturnqueue_get, mock_sqlsubmitqueue_put
    ):
        """Test sqlExecuteChunked with id count 0"""
        ID_COUNT = 0
        args = list()
        for i in range(0, ID_COUNT):
            args.append("arg{}".format(i))
        total_row_count = helper_sql.sqlExecuteChunked(
            "INSERT INTO table VALUES {}", ID_COUNT, *args
        )
        self.assertEqual(total_row_count, 0)
        self.assertFalse(mock_sqlsubmitqueue_put.called)
        self.assertFalse(mock_sqlreturnqueue_get.called)

    @patch("pybitmessage.helper_sql.sqlSubmitQueue.put")
    @patch("pybitmessage.helper_sql.sqlReturnQueue.get")
    def test_sqlexecute_chunked_with_args_less(
        self, mock_sqlreturnqueue_get, mock_sqlsubmitqueue_put
    ):
        """Test sqlExecuteChunked with length of args less than idcount"""
        ID_COUNT = 12
        args = ["args0", "arg1"]
        total_row_count = helper_sql.sqlExecuteChunked(
            "INSERT INTO table VALUES {}", ID_COUNT, *args
        )
        self.assertEqual(total_row_count, 0)
        self.assertFalse(mock_sqlsubmitqueue_put.called)
        self.assertFalse(mock_sqlreturnqueue_get.called)

    @patch("pybitmessage.helper_sql.sqlSubmitQueue.put")
    @patch("pybitmessage.helper_sql.sqlSubmitQueue.task_done")
    def test_sqlstored_procedure(self, mock_task_done, mock_sqlsubmitqueue_put):
        """Test sqlStoredProcedure with a stored procedure name"""
        helper_sql.sqlStoredProcedure("exit")
        self.assertTrue(mock_task_done.called_once)
        mock_sqlsubmitqueue_put.assert_called_with("terminate")

    @classmethod
    def tearDownClass(cls):
        helper_sql.sql_available = False
