import unittest


class BitmessageTestCase(unittest.TestCase):
    """Unit Test Integration"""

    def __init__(self, methodName="runTest", myapp=None):
        super(BitmessageTestCase, self).__init__(methodName)
        self.myapp = myapp

    @staticmethod
    def bitmessage_testloader(testcaseclass, myapp=None):
        """Test Loader"""
        testnames = unittest.TestLoader().getTestCaseNames(testcaseclass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcaseclass(name, myapp))
        return suite
