"""Test cases for shared.py"""

import unittest
from pybitmessage.shared import (
    isAddressInMyAddressBook,
    isAddressInMySubscriptionsList,
    decodeWalletImportFormat,
    reloadMyAddressHashes,
    checkSensitiveFilePermissions,
    fixPotentiallyInvalidUTF8Data,
    reloadBroadcastSendersForWhichImWatching,
    fixSensitiveFilePermissions,
    myECCryptorObjects,
    myAddressesByHash,
    myAddressesByTag,
    MyECSubscriptionCryptorObjects,
)
import stat
import os

try:
    # Python 3
    from unittest.mock import patch, PropertyMock
except ImportError:
    # Python 2
    from mock import patch, PropertyMock


class TestShared(unittest.TestCase):
    """Test class for shared.py"""

    @patch("pybitmessage.shared.sqlQuery")
    def test_isaddress_in_myaddressbook(self, mock_sql_query):
        """Test if address is in MyAddressbook"""
        address = "BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEgU9U"

        # if address is in MyAddressbook
        mock_sql_query.return_value = [address]
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

        address = "BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEe8Sa"

        # if address is in MySubscriptionsList
        mock_sql_query.return_value = ["BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEe8Sa"]
        return_val = isAddressInMySubscriptionsList(address)
        self.assertTrue(return_val)

        # if address is not in MySubscriptionsList
        mock_sql_query.return_value = []
        return_val = isAddressInMySubscriptionsList(address)
        self.assertFalse(return_val)
        self.assertEqual(mock_sql_query.call_count, 2)

    @patch("pybitmessage.shared.os._exit")
    def test_decode_wallet_import_format(self, mock_os_exit):
        """Test if decodeWalletImportFormat works as expected"""
        WIFstring = "5HxWvvfubhXpYYpS3tJkw6fq9jE9j18THftkZjHHfmFiWtmAbrj"
        expected_address = (
            "\x12\xb0\x04\xff\xf7\xf4\xb6\x9e\xf8e\x0ev\x7f\x18\xf1\x1e"
            "\xde\x15\x81H\xb4%f\x07#\xb9\xf9\xa6na\xf7G"
        )
        address = decodeWalletImportFormat(WIFstring=WIFstring)
        self.assertEqual(expected_address, address)

    def test_returns_input_text_if_valid_utf8_string(self):
        """Test if input text is a valid UTF-8 string"""
        input_text = "Hello, World!"
        result = fixPotentiallyInvalidUTF8Data(input_text)
        self.assertEqual(result, input_text)

    def test_handles_input_text_with_invalid_utf8_characters(self):
        """Test if input text is a not a valid UTF-8 string"""
        input_text = b"\x80\x81\x82"
        expexted_output = (
            "Part of the message is corrupt. The message cannot be"
            " displayed the normal way.\n\n" + repr(input_text)
        )
        result = fixPotentiallyInvalidUTF8Data(input_text)
        self.assertEqual(expexted_output, result)

    @patch("pybitmessage.shared.config.getboolean")
    @patch("pybitmessage.shared.config.get")
    @patch("pybitmessage.shared.config.addresses")
    @patch("pybitmessage.shared.checkSensitiveFilePermissions")
    def test_reload_myaddresshashes(
        self,
        mock_check_file_per,
        mock_config_address,
        mock_config_get,
        mock_config_getboolean,
    ):
        """Test for reload my addressHashes"""
        mock_check_file_per.return_value = True
        mock_config_address.return_value = ["BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEgU9U"]
        mock_config_get.return_value = (
            "5HxWvvfubhXpYYpS3tJkw6fq9jE9j18THftkZjHHfmFiWtmAbrj"
        )
        mock_config_getboolean.return_value = True
        # before reload
        self.assertEqual(len(myECCryptorObjects), 0)
        self.assertEqual(len(myAddressesByHash), 0)
        self.assertEqual(len(myAddressesByTag), 0)

        reloadMyAddressHashes()
        # after reload
        self.assertGreater(len(myECCryptorObjects), 0)
        self.assertGreater(len(myAddressesByHash), 0)
        self.assertGreater(len(myAddressesByTag), 0)

    @patch("pybitmessage.shared.sqlQuery")
    def test_reloadBroadcastSendersForWhichImWatching(self, mock_sql_query):
        """Test for reload Broadcast Senders For Which Im Watching"""
        mock_sql_query.return_value = [
            ("BM-2cUGaEcGz9Zft1SPAo8FJtfzyADTpEgU9U",),
        ]
        # before reload
        self.assertEqual(len(MyECSubscriptionCryptorObjects), 0)

        # reloading with addressVersionNumber 1
        reloadBroadcastSendersForWhichImWatching()
        self.assertGreater(len(MyECSubscriptionCryptorObjects), 0)

    @patch("pybitmessage.shared.os.stat")
    @patch(
        "pybitmessage.shared.sys", new_callable=PropertyMock  # pylint: disable=used-before-assignment
    )
    def test_check_sensitive_file_permissions(self, mock_sys, mock_os_stat):
        """Test to check file permissions"""
        filename = "path/to/file"

        # test for windows system
        mock_sys.platform = "win32"
        result = checkSensitiveFilePermissions(filename)
        self.assertTrue(result)

        # test for freebsd system
        mock_sys.platform = "freebsd7"
        mock_os_stat.return_value = os.stat_result(
            sequence=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            dict={
                "st_mode": stat.S_IRUSR,
                "st_ino": 753,
                "st_dev": 1795,
                "st_nlink": 1,
                "st_uid": 1000,
                "st_gid": 0,
                "st_size": 1021,
                "st_atime": 1711587560,
                "st_mtime": 1709449249,
                "st_ctime": 1709449603,
            },
        )
        result = checkSensitiveFilePermissions(filename)
        self.assertTrue(result)

    @patch("pybitmessage.shared.os.chmod")
    @patch("pybitmessage.shared.os.stat")
    def test_fix_sensitive_file_permissions(self, mock_os_stat, mock_chmod):
        """Test to fix file permissions"""
        filename = "path/to/file"
        mock_os_stat.return_value = os.stat_result(
            sequence=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            dict={
                "st_mode": stat.S_IRWXG,
                "st_ino": 753,
                "st_dev": 1795,
                "st_nlink": 1,
                "st_uid": 1000,
                "st_gid": 0,
                "st_size": 1021,
                "st_atime": 1711587560,
                "st_mtime": 1709449249,
                "st_ctime": 1709449603,
            },
        )
        fixSensitiveFilePermissions(filename, False)
        mock_chmod.asset_called_once()
