"""
Various tests to Enable and Disable the identity
"""

import unittest
from six import StringIO
from six.moves import configparser
from pybitmessage.bmconfigparser import BMConfigParser


address_obj = """[BM-enabled_identity]
label = Test_address_1
enabled = true

[BM-disabled_identity]
label = Test_address_2
enabled = false
"""


# pylint: disable=protected-access
class TestAddressEnableDisable(unittest.TestCase):
    """A test case for bmconfigparser"""

    def setUp(self):
        self.config = BMConfigParser()
        self.config.read_file(StringIO(address_obj))

    def test_enable_enabled_identity(self):
        """Test enabling already enabled identity"""
        self.config.enable_address('BM-enabled_identity')
        self.assertEqual(self.config.safeGet('BM-enabled_identity', 'enabled'), 'true')

    def test_enable_disabled_identity(self):
        """Test enabling the Disabled identity"""
        self.config.enable_address('BM-disabled_identity')
        self.assertEqual(self.config.safeGet('BM-disabled_identity', 'enabled'), 'true')

    def test_enable_non_existent_identity(self):
        """Test enable non-existent address"""
        with self.assertRaises(configparser.NoSectionError):
            self.config.enable_address('non_existent_address')

    def test_disable_disabled_identity(self):
        """Test disabling already disabled identity"""
        self.config.disable_address('BM-disabled_identity')
        self.assertEqual(self.config.safeGet('BM-disabled_identity', 'enabled'), 'false')

    def test_disable_enabled_identity(self):
        """Test Disabling the Enabled identity"""
        self.config.disable_address('BM-enabled_identity')
        self.assertEqual(self.config.safeGet('BM-enabled_identity', 'enabled'), 'false')

    def test_disable_non_existent_identity(self):
        """Test dsiable non-existent address"""
        with self.assertRaises(configparser.NoSectionError):
            self.config.disable_address('non_existent_address')
