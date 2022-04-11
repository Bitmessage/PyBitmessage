"""A test case for partial run class definition"""

import os
import sys
import unittest

from pybitmessage import pathmagic


class TestPartialRun(unittest.TestCase):
    """
    A base class for test cases running some parts of the app,
    e.g. separate threads or packages.
    """

    @classmethod
    def setUpClass(cls):
        cls.dirs = (os.path.abspath(os.curdir), pathmagic.setup())

        import bmconfigparser
        import state

        from debug import logger  # noqa:F401 pylint: disable=unused-variable

        state.shutdown = 0
        cls.state = state
        bmconfigparser.config = cls.config = bmconfigparser.BMConfigParser()
        cls.config.read()

    @classmethod
    def tearDownClass(cls):
        cls.state.shutdown = 1
        # deactivate pathmagic
        os.chdir(cls.dirs[0])
        sys.path.remove(cls.dirs[1])
