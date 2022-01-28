# pylint: disable=no-member, no-self-use
"""
Various tests for config
"""
import unittest

from six import StringIO
from pybitmessage.bmconfigparser import BMConfigParser

test_config = """[bitmessagesettings]
maxaddrperstreamsend = 100
maxbootstrapconnections = 10
maxdownloadrate = 0
maxoutboundconnections = 8
maxtotalconnections = 100
maxuploadrate = 0
apiinterface = 127.0.0.1
apiport = 8442
udp = True

[threads]
receive = 3

[network]
bind = None
dandelion = 90

[inventory]
storage = sqlite
acceptmismatch = False

[knownnodes]
maxnodes = 15000

[zlib]
maxsize = 1048576"""


class TestConfig(unittest.TestCase):
    """A test case for bmconfigparser"""
    configfile = StringIO('')

    def test_safeGet(self):
        """safeGet retuns provided default for nonexistent option or None"""
        config = BMConfigParser()
        self.assertIs(
            config.safeGet('nonexistent', 'nonexistent'), None)
        self.assertEqual(
            config.safeGet('nonexistent', 'nonexistent', 42), 42)

    def test_safeGetBoolean(self):
        """safeGetBoolean returns False for nonexistent option, no default"""
        config = BMConfigParser()
        self.assertIs(
            config.safeGetBoolean('nonexistent', 'nonexistent'),
            False
        )
        # no arg for default
        # pylint: disable=too-many-function-args
        with self.assertRaises(TypeError):
            config.safeGetBoolean(
                'nonexistent', 'nonexistent', True)

    def test_safeGetInt(self):
        """safeGetInt retuns provided default for nonexistent option or 0"""
        config = BMConfigParser()
        self.assertEqual(
            config.safeGetInt('nonexistent', 'nonexistent'), 0)
        self.assertEqual(
            config.safeGetInt('nonexistent', 'nonexistent', 42), 42)

    def test_safeGetFloat(self):
        """safeGetFloat retuns provided default for nonexistent option or 0.0"""
        config = BMConfigParser()
        self.assertEqual(
            config.safeGetFloat('nonexistent', 'nonexistent'), 0.0)
        self.assertEqual(
            config.safeGetFloat('nonexistent', 'nonexistent', 42.0), 42.0)

    def test_reset(self):
        """safeGetInt retuns provided default for bitmessagesettings option or 0"""
        config = BMConfigParser()
        test_config_object = StringIO(test_config)
        config.readfp(test_config_object)
        self.assertEqual(
            config.safeGetInt('bitmessagesettings', 'maxaddrperstreamsend'), 100)
        # pylint: disable=protected-access
        config._reset()
        self.assertEqual(config.sections(), [])

    def test_defaults(self):
        """Loading defaults"""
        config = BMConfigParser()
        config.add_section('bitmessagesettings')
        config.set("bitmessagesettings", "maxaddrperstreamsend", "100")
        config.read()
        self.assertEqual(
            config.safeGetInt('bitmessagesettings', 'maxaddrperstreamsend'), 500)
