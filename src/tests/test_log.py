"""Tests for logging"""

import subprocess
import unittest
import six

from pybitmessage import proofofwork


class TestLog(unittest.TestCase):
    """A test case for logging"""

    @unittest.skipIf(
        six.PY2, 'assertLogs is new in version 3.4')
    def test_LogOutput(self):
        """Use proofofwork.LogOutput to log output of a shell command"""
        with self.assertLogs('default') as cm:  # pylint: disable=no-member
            with proofofwork.LogOutput('+'):
                subprocess.call(['echo', 'HELLO'])

        self.assertEqual(cm.output, ['INFO:default:+: HELLO\n'])
