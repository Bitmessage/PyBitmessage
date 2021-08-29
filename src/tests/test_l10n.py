"""Tests for l10n module"""

import re
import sys
import time
import unittest

from pybitmessage import l10n


class TestL10n(unittest.TestCase):
    """A test case for L10N"""

    def test_l10n_assumptions(self):
        """Check the assumptions made while rewriting the l10n"""
        self.assertFalse(re.search(r'\d', time.strftime("wrong")))
        timestring_type = type(time.strftime(l10n.DEFAULT_TIME_FORMAT))
        self.assertEqual(timestring_type, str)
        if sys.version_info[0] == 2:
            self.assertEqual(timestring_type, bytes)

    def test_getWindowsLocale(self):
        """Check the getWindowsLocale() docstring example"""
        self.assertEqual(l10n.getWindowsLocale("en_EN.UTF-8"), "english")
