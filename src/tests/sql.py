"""
SQL related core tests
"""

import unittest

import helper_db


class TestSQL(unittest.TestCase):
    """A test case for common SQL-related functions"""
    test_address_1 = 'BM-2cVRo3WuKL5vDCKq2XJi1yR366nkHgHfcL'
    test_address_2 = 'BM-2cVJn1BusL1j4UezuYkvpqNPCr7kCebeLw'

    def test_subscriptions(self):
        """Put address into subscriptions and check that it was added"""
        self.assertTrue(
            helper_db.put_subscriptions('pass_1', self.test_address_1))
        self.assertFalse(
            helper_db.put_subscriptions('pass_2', self.test_address_1))

        helper_db.put_subscriptions('pass_3', self.test_address_2, False)

        for label, addr in helper_db.get_subscriptions():
            if addr == self.test_address_1:
                self.assertEqual(label, 'pass_1')
                break
        else:
            self.fail('Could not find added address in subscriptions')

        for label, addr in helper_db.get_subscriptions():
            if addr == self.test_address_2:
                self.fail('Got disabled subscription')
