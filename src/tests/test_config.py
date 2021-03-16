"""
Various tests for config
"""

import unittest
from pybitmessage.bmconfigparser import BMConfigParser


class TestConfig(unittest.TestCase):
    """A test case for bmconfigparser"""

    def test_safeGet(self):
        """safeGet retuns provided default for nonexistent option or None"""
        self.assertIs(
            BMConfigParser().safeGet('nonexistent', 'nonexistent'), None)
        self.assertEqual(
            BMConfigParser().safeGet('nonexistent', 'nonexistent', 42), 42)

    def test_safeGetBoolean(self):
        """safeGetBoolean returns False for nonexistent option, no default"""
        self.assertIs(
            BMConfigParser().safeGetBoolean('nonexistent', 'nonexistent'),
            False
        )
        # no arg for default
        # pylint: disable=too-many-function-args
        with self.assertRaises(TypeError):
            BMConfigParser().safeGetBoolean(
                'nonexistent', 'nonexistent', True)

    def test_safeGetInt(self):
        """safeGetInt retuns provided default for nonexistent option or 0"""
        self.assertEqual(
            BMConfigParser().safeGetInt('nonexistent', 'nonexistent'), 0)
        self.assertEqual(
            BMConfigParser().safeGetInt('nonexistent', 'nonexistent', 42), 42)
