"""Test cases for Helper Inbox"""

import time
import unittest
from pybitmessage.helper_inbox import (
    insert,
    trash,
    delete,
    isMessageAlreadyInInbox,
    undeleteMessage,
)
from pybitmessage.helper_ackPayload import genAckPayload

try:
    # Python 3
    from unittest.mock import patch
except ImportError:
    # Python 2
    from mock import patch


class TestHelperInbox(unittest.TestCase):
    """Test class for Helper Inbox"""

    @patch("pybitmessage.helper_inbox.sqlExecute")
    def test_insert(self, mock_sql_execute):  # pylint: disable=no-self-use
        """Test to perform an insert into the "inbox" table"""
        mock_message_data = (
            "ruyv87bv",
            "BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEgU9U",
            "BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTp5g99U",
            "Test subject",
            int(time.time()),
            "Test message",
            "inbox",
            2,
            0,
            "658gvjhtghv",
        )
        insert(t=mock_message_data)
        mock_sql_execute.assert_called_once()

    @patch("pybitmessage.helper_inbox.sqlExecute")
    def test_trash(self, mock_sql_execute):  # pylint: disable=no-self-use
        """Test marking a message in the `inbox` as `trash`"""
        mock_msg_id = "fefkosghsbse92"
        trash(msgid=mock_msg_id)
        mock_sql_execute.assert_called_once()

    @patch("pybitmessage.helper_inbox.sqlExecute")
    def test_delete(self, mock_sql_execute):  # pylint: disable=no-self-use
        """Test for permanent deletion of message from trash"""
        mock_ack_data = genAckPayload()
        delete(mock_ack_data)
        mock_sql_execute.assert_called_once()

    @patch("pybitmessage.helper_inbox.sqlExecute")
    def test_undeleteMessage(self, mock_sql_execute):  # pylint: disable=no-self-use
        """Test for Undelete the message"""
        mock_msg_id = "fefkosghsbse92"
        undeleteMessage(msgid=mock_msg_id)
        mock_sql_execute.assert_called_once()

    @patch("pybitmessage.helper_inbox.sqlQuery")
    def test_isMessageAlreadyInInbox(self, mock_sql_query):
        """Test for check for previous instances of this message"""
        fake_sigHash = "h4dkn54546"
        # if Message is already in Inbox
        mock_sql_query.return_value = [(1,)]
        result = isMessageAlreadyInInbox(sigHash=fake_sigHash)
        self.assertTrue(result)

        # if Message is not in Inbox
        mock_sql_query.return_value = [(0,)]
        result = isMessageAlreadyInInbox(sigHash=fake_sigHash)
        self.assertFalse(result)
