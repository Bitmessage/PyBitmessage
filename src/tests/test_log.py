"""Tests for logging"""

import subprocess
import sys
import unittest

from pybitmessage import proofofwork


class TestLog(unittest.TestCase):
    """A test case for logging"""

    @unittest.skipIf(
        sys.hexversion < 0x3000000, 'assertLogs is new in version 3.4')
    def test_LogOutput(self):
        """Use proofofwork.LogOutput to log output of a shell command"""
        def echo():
            """Call the echo shell command"""
            with proofofwork.LogOutput():
                subprocess.call(['echo', 'HELLO'])
        self.assertLogs(echo(), 'HELLO')  # pylint: disable=no-member
