#!/usr/bin/env python
"""Custom tests runner script for tox and python3"""
import random  # noseq
import sys
import unittest


def unittest_discover():
    """Explicit test suite creation"""
    loader = unittest.defaultTestLoader
    loader.sortTestMethodsUsing = lambda a, b: random.randint(-1, 1)
    return loader.discover('src.bitmessagekivy.tests')


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest_discover())
    sys.exit(not result.wasSuccessful())
