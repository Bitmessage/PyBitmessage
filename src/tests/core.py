import unittest


class TestCore(unittest.TestCase):
    """Test case, which runs from main pybitmessage thread"""
    def test_pass(self):
        pass


def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCore)
    return unittest.TextTestRunner(verbosity=2).run(suite)
