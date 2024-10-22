#!/usr/bin/env python
"""Custom tests runner script for tox and python3"""
import random  # noseq
import sys
import unittest
import six


def unittest_discover():
    """Explicit test suite creation"""
    if six.PY3:
        from pybitmessage import pathmagic
        pathmagic.setup()
    loader = unittest.defaultTestLoader
    # randomize the order of tests in test cases
    loader.sortTestMethodsUsing = lambda a, b: random.randint(-1, 1)
    # pybitmessage symlink disappears on Windows!
    testsuite = loader.discover('pybitmessage.tests')
    testsuite.addTests([loader.discover('pybitmessage.pyelliptic')])

    return testsuite


if __name__ == "__main__":
    success = unittest.TextTestRunner(verbosity=2).run(
        unittest_discover()).wasSuccessful()
    try:
        from pybitmessage.tests import common
    except ImportError:
        checkup = False
    else:
        checkup = common.checkup()

    if checkup and not success:
        print(checkup)

    sys.exit(not success or checkup)
