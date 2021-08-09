"""
Various tests for config
"""

import os
import tempfile
from pybitmessage.bmconfigparser import BMConfigParser
from .test_process import TestProcessProto
from .common import skip_python3

skip_python3()


class TestProcessConfig(TestProcessProto):
    """A test case for keys.dat"""
    home = tempfile.mkdtemp()

    def test_config_defaults(self):
        """Test settings in the generated config"""
        config = BMConfigParser()
        self._stop_process()
        self._kill_process()
        config.read(os.path.join(self.home, 'keys.dat'))

        self.assertEqual(config.safeGetInt(
            'bitmessagesettings', 'settingsversion'), 10)
        self.assertEqual(config.safeGetInt(
            'bitmessagesettings', 'port'), 8444)
        # don't connect
        self.assertTrue(config.safeGetBoolean(
            'bitmessagesettings', 'dontconnect'))
        # API disabled
        self.assertFalse(config.safeGetBoolean(
            'bitmessagesettings', 'apienabled'))

        # extralowdifficulty is false
        self.assertEqual(config.safeGetInt(
            'bitmessagesettings', 'defaultnoncetrialsperbyte'), 1000)
        self.assertEqual(config.safeGetInt(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes'), 1000)
