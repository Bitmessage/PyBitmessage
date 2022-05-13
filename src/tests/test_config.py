"""
Various tests for config
"""
import logging
import unittest
from six.moves import configparser
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
maxsize = 1048576

[BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih]
label = Test_address1
enabled = true
decoy = false
noncetrialsperbyte = 1000
payloadlengthextrabytes = 1000
privsigningkey = 5HsCSd1UFrsdoAoeSNSP2pUBPbHSaZBJE9GbWa1PwDzPhDz7qwx
privencryptionkey = 5JNNReZVMYSzQEhREV835PNnkNtLsPybd5KMZ2ufeXeEuSTpgeC
"""


# pylint: disable=protected-access
class TestConfig(unittest.TestCase):
    """A test case for bmconfigparser"""

    def setUp(self):
        self.config = BMConfigParser()
        self.config.add_section('bitmessagesettings')

    def test_safeGet(self):
        """safeGet retuns provided default for nonexistent option or None"""
        self.assertIs(
            self.config.safeGet('nonexistent', 'nonexistent'), None)
        self.assertEqual(
            self.config.safeGet('nonexistent', 'nonexistent', 42), 42)

    def test_safeGetBoolean(self):
        """safeGetBoolean returns False for nonexistent option, no default"""
        self.assertIs(
            self.config.safeGetBoolean('nonexistent', 'nonexistent'), False)
        # no arg for default
        # pylint: disable=too-many-function-args
        with self.assertRaises(TypeError):
            self.config.safeGetBoolean('nonexistent', 'nonexistent', True)

    def test_safeGetInt(self):
        """safeGetInt retuns provided default for nonexistent option or 0"""
        self.assertEqual(
            self.config.safeGetInt('nonexistent', 'nonexistent'), 0)
        self.assertEqual(
            self.config.safeGetInt('nonexistent', 'nonexistent', 42), 42)

    def test_safeGetFloat(self):
        """
        safeGetFloat retuns provided default for nonexistent option or 0.0
        """
        self.assertEqual(
            self.config.safeGetFloat('nonexistent', 'nonexistent'), 0.0)
        self.assertEqual(
            self.config.safeGetFloat('nonexistent', 'nonexistent', 42.0), 42.0)

    def test_setTemp(self):
        """Set a temporary value and ensure it's returned by get()"""
        self.config.setTemp('bitmessagesettings', 'connect', 'true')
        self.assertIs(
            self.config.safeGetBoolean('bitmessagesettings', 'connect'), True)
        written_fp = StringIO('')
        self.config.write(written_fp)
        self.config._reset()
        self.config.read_file(written_fp)
        self.assertIs(
            self.config.safeGetBoolean('bitmessagesettings', 'connect'), False)

    def test_reset(self):
        """Some logic for testing _reset()"""
        test_config_object = StringIO(test_config)
        self.config.read_file(test_config_object)
        self.assertEqual(
            self.config.safeGetInt(
                'bitmessagesettings', 'maxaddrperstreamsend'), 100)
        self.config._reset()
        self.assertEqual(self.config.sections(), [])

    def test_defaults(self):
        """Loading defaults"""
        self.config.set('bitmessagesettings', 'maxaddrperstreamsend', '100')
        self.config.read()
        self.assertEqual(
            self.config.safeGetInt(
                'bitmessagesettings', 'maxaddrperstreamsend'), 500)

    def test_disable_identity(self):
        """Test Disable the identity"""
        test_config_object = StringIO(test_config)
        self.config.read_file(test_config_object)
        try:
            address_status = self.config.safeGet('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled')
            if address_status == 'true':
                self.config.setTemp('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled', 'false')
                self.assertEqual(self.config.safeGet('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled'), 'false')
            else:
                self.assertEqual(self.config.safeGet('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled'), 'true')
        except configparser.NoSectionError as err:
            logging.warning("Address does not found: %s", err)

    def test_enable_identity(self):
        """Test Enable the identity"""
        test_config_object = StringIO(test_config)
        self.config.read_file(test_config_object)
        try:
            address_status = self.config.safeGet('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled')
            if address_status == 'false':
                self.config.setTemp('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled', 'true')
                self.assertEqual(self.config.safeGet('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled'), 'true')
            else:
                self.assertEqual(self.config.safeGet('BM-2cUkVw5kgWfNjydbCHW7sewmG6fbkTxcih', 'enabled'), 'false')
        except configparser.NoSectionError as err:
            logging.warning("Address does not found: %s", err)
