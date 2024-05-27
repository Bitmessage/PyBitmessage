"""Test cases for shared.py"""

import unittest
from pybitmessage.shared import (
    isAddressInMyAddressBook,
    isAddressInMySubscriptionsList,
    checkSensitiveFilePermissions,
    reloadBroadcastSendersForWhichImWatching,
    fixSensitiveFilePermissions,
    MyECSubscriptionCryptorObjects,
    stat,
    os,
)

from .samples import sample_address

try:
    # Python 3
    from unittest.mock import patch, PropertyMock
except ImportError:
    # Python 2
    from mock import patch, PropertyMock

# mock os.stat data for file
PERMISSION_MODE1 = stat.S_IRUSR  # allow Read permission for the file owner.
PERMISSION_MODE2 = (
    stat.S_IRWXO
)  # allow read, write, serach & execute permission for other users
INODE = 753
DEV = 1795
NLINK = 1
UID = 1000
GID = 0
SIZE = 1021
ATIME = 1711587560
MTIME = 1709449249
CTIME = 1709449603


class TestShared(unittest.TestCase):
    """Test class for shared.py"""

    @patch("pybitmessage.shared.sqlQuery")
    def test_isaddress_in_myaddressbook(self, mock_sql_query):
        """Test if address is in MyAddressbook"""
        address = sample_address

        # if address is in MyAddressbook
        mock_sql_query.return_value = [bytes(address)]
        return_val = isAddressInMyAddressBook(address)
        mock_sql_query.assert_called_once()
        self.assertTrue(return_val)

        # if address is not in MyAddressbook
        mock_sql_query.return_value = []
        return_val = isAddressInMyAddressBook(address)
        self.assertFalse(return_val)
        self.assertEqual(mock_sql_query.call_count, 2)

    @patch("pybitmessage.shared.sqlQuery")
    def test_isaddress_in_mysubscriptionslist(self, mock_sql_query):
        """Test if address is in MySubscriptionsList"""

        address = sample_address

        # if address is in MySubscriptionsList
        mock_sql_query.return_value = [bytes(address)]
        return_val = isAddressInMySubscriptionsList(address)
        self.assertTrue(return_val)

        # if address is not in MySubscriptionsList
        mock_sql_query.return_value = []
        return_val = isAddressInMySubscriptionsList(address)
        self.assertFalse(return_val)
        self.assertEqual(mock_sql_query.call_count, 2)

    @patch("pybitmessage.shared.sqlQuery")
    def test_reloadBroadcastSendersForWhichImWatching(self, mock_sql_query):
        """Test for reload Broadcast Senders For Which Im Watching"""
        mock_sql_query.return_value = [
            (bytes(sample_address),),
        ]
        # before reload
        self.assertEqual(len(MyECSubscriptionCryptorObjects), 0)

        # reloading with addressVersionNumber 1
        reloadBroadcastSendersForWhichImWatching()
        self.assertGreater(len(MyECSubscriptionCryptorObjects), 0)

    @patch("pybitmessage.shared.os.stat")
    @patch(
        "pybitmessage.shared.sys",
        new_callable=PropertyMock,  # pylint: disable=used-before-assignment
    )
    def test_check_sensitive_file_permissions(self, mock_sys, mock_os_stat):
        """Test to check file permissions"""
        fake_filename = "path/to/file"

        # test for windows system
        mock_sys.platform = "win32"
        result = checkSensitiveFilePermissions(fake_filename)
        self.assertTrue(result)

        # test for freebsd system
        mock_sys.platform = "freebsd7"
        # returning file permission mode stat.S_IRUSR
        MOCK_OS_STAT_RETURN = os.stat_result(
            sequence=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            dict={
                "st_mode": PERMISSION_MODE1,
                "st_ino": INODE,
                "st_dev": DEV,
                "st_nlink": NLINK,
                "st_uid": UID,
                "st_gid": GID,
                "st_size": SIZE,
                "st_atime": ATIME,
                "st_mtime": MTIME,
                "st_ctime": CTIME,
            },
        )
        mock_os_stat.return_value = MOCK_OS_STAT_RETURN
        result = checkSensitiveFilePermissions(fake_filename)
        self.assertTrue(result)

    @patch("pybitmessage.shared.os.chmod")
    @patch("pybitmessage.shared.os.stat")
    def test_fix_sensitive_file_permissions(  # pylint: disable=no-self-use
        self, mock_os_stat, mock_chmod
    ):
        """Test to fix file permissions"""
        fake_filename = "path/to/file"

        # returning file permission mode stat.S_IRWXO
        MOCK_OS_STAT_RETURN = os.stat_result(
            sequence=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            dict={
                "st_mode": PERMISSION_MODE2,
                "st_ino": INODE,
                "st_dev": DEV,
                "st_nlink": NLINK,
                "st_uid": UID,
                "st_gid": GID,
                "st_size": SIZE,
                "st_atime": ATIME,
                "st_mtime": MTIME,
                "st_ctime": CTIME,
            },
        )
        mock_os_stat.return_value = MOCK_OS_STAT_RETURN
        fixSensitiveFilePermissions(fake_filename, False)
        mock_chmod.assert_called_once()
