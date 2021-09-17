# pylint: disable=no-member
"""
Various tests for config
"""
import unittest
import tempfile
import sys
import os

from pybitmessage import paths
from pybitmessage.bmconfigparser import BMConfigParser

test_config = {
    "bitmessagesettings": {
        "maxaddrperstreamsend": 100,
        "maxbootstrapconnections": 20,
        "maxdownloadrate": 0,
        "maxoutboundconnections": 8,
        "maxtotalconnections": 200,
        "maxuploadrate": 0,
        "apiinterface": "127.0.0.1",
        "apiport": 8442,
        "udp": "True"
    },
    "threads": {
        "receive": 3,
    },
    "network": {
        "bind": "",
        "dandelion": 90,
    },
    "inventory": {
        "storage": "sqlite",
        "acceptmismatch": "False",
    },
    "knownnodes": {
        "maxnodes": 20000,
    },
    "zlib": {
        "maxsize": 1048576
    }
}


class TestConfig(unittest.TestCase):
    """A test case for bmconfigparser"""
    config_backup = tempfile.NamedTemporaryFile(suffix='.cfg').name

    def setUp(self):
        """creates a backup of BMConfigparser current state"""
        with open(self.config_backup, 'wb') as configfile:
            BMConfigParser().write(configfile)

    def tearDown(self):
        """restore to the backup of BMConfigparser"""
        BMConfigParser().read(self.config_backup)
        os.remove(self.config_backup)

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

    def test_safeGetFloat(self):
        """safeGetFloat retuns provided default for nonexistent option or 0.0"""
        self.assertEqual(
            BMConfigParser().safeGetFloat('nonexistent', 'nonexistent'), 0.0)
        self.assertEqual(
            BMConfigParser().safeGetFloat('nonexistent', 'nonexistent', 42.0), 42.0)

    def test_reset(self):
        """safeGetInt retuns provided default for bitmessagesettings option or 0"""

        BMConfigParser().read(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'test_pattern', 'test_config.ini'
            )
        )

        self.assertEqual(
            BMConfigParser().safeGetInt('bitmessagesettings', 'maxaddrperstreamsend'), 100)

        BMConfigParser()._reset()
        self.assertEqual(
            BMConfigParser().safeGetInt('bitmessagesettings', 'maxaddrperstreamsend'), 500)
