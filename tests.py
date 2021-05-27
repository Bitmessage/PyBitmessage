#!/usr/bin/env python
"""Custom tests runner script for tox and python3"""
import random  # noseq
import sys
import unittest


def unittest_discover():
    """Explicit test suite creation"""
    if sys.hexversion >= 0x3000000:
        from pybitmessage import pathmagic
        pathmagic.setup()
    loader = unittest.defaultTestLoader
    # randomize the order of tests in test cases
    loader.sortTestMethodsUsing = lambda a, b: random.randint(-1, 1)
    # pybitmessage symlink may disappear on Windows
    return loader.discover('src.tests')


if __name__ == "__main__":
    success = unittest.TextTestRunner(verbosity=2).run(
        unittest_discover()).wasSuccessful()
    try:
        from src.tests import common
    except ImportError:
        checkup = False
        print('ImportError from src.tests')
    else:
        checkup = common.checkup()

    if checkup and not success:
        print(checkup)

    sys.exit(not success or checkup)
