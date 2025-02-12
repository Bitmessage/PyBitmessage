"""Test cases for helper_sent class"""

import unittest
from pybitmessage.helper_sent import insert, delete, trash, retrieve_message_details

try:
    # Python 3
    from unittest.mock import patch
except ImportError:
    # Python 2
    from mock import patch


class TestHelperSent(unittest.TestCase):
    """Test class for helper_sent"""

    @patch("pybitmessage.helper_sent.sqlExecute")
    def test_insert_valid_address(self, mock_sql_execute):
        """Test insert with valid address"""
        VALID_ADDRESS = "BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEgU9U"
        ackdata = insert(
            msgid=b"123456",
            toAddress="[Broadcast subscribers]",
            fromAddress=VALID_ADDRESS,
            subject="Test Subject",
            message="Test Message",
            status="msgqueued",
            sentTime=1234567890,
            lastActionTime=1234567890,
            sleeptill=0,
            retryNumber=0,
            encoding=2,
            ttl=3600,
            folder="sent",
        )
        mock_sql_execute.assert_called_once()
        self.assertIsNotNone(ackdata)

    def test_insert_invalid_address(self):
        """Test insert with invalid address"""
        INVALID_ADDRESS = "TEST@1245.780"
        ackdata = insert(toAddress=INVALID_ADDRESS)
        self.assertIsNone(ackdata)

    @patch("pybitmessage.helper_sent.sqlExecute")
    def test_delete(self, mock_sql_execute):
        """Test delete function"""
        delete(b"ack_data")
        self.assertTrue(mock_sql_execute.called)
        mock_sql_execute.assert_called_once_with(
            "DELETE FROM sent WHERE ackdata = ?", b"ack_data"
        )

    @patch("pybitmessage.helper_sent.sqlQuery")
    def test_retrieve_valid_message_details(self, mock_sql_query):
        """Test retrieving valid message details"""
        return_data = [
            (
                b"to@example.com",
                b"from@example.com",
                b"Test Subject",
                b"Test Message",
                b"2022-01-01",
            )
        ]
        mock_sql_query.return_value = return_data
        result = retrieve_message_details("12345")
        self.assertEqual(result, return_data)

    @patch("pybitmessage.helper_sent.sqlExecute")
    def test_trash(self, mock_sql_execute):
        """Test marking a message as 'trash'"""
        ackdata = b"ack_data"
        mock_sql_execute.return_value = 1
        rowcount = trash(ackdata)
        self.assertEqual(rowcount, 1)
