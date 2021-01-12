"""
Tests for RandomTrackingDict class
"""
import random
import unittest

from time import time


class TestRandomTrackingDict(unittest.TestCase):
    """
    Main protocol test case
    """

    @staticmethod
    def randString():
        """helper function for tests, generates a random string"""
        retval = b''
        for _ in range(32):
            retval += chr(random.randint(0, 255))
        return retval

    def test_check_randomtrackingdict(self):
        """Check the logic of RandomTrackingDict class"""
        from pybitmessage.randomtrackingdict import RandomTrackingDict
        a = []
        k = RandomTrackingDict()

        a.append(time())
        for i in range(50000):
            k[self.randString()] = True
        a.append(time())

        while k:
            retval = k.randomKeys(1000)
            if not retval:
                self.fail("error getting random keys")

            try:
                k.randomKeys(100)
                self.fail("bad")
            except KeyError:
                pass
            for i in retval:
                del k[i]
        a.append(time())

        for x in range(len(a) - 1):
            self.assertLess(a[x + 1] - a[x], 10)
