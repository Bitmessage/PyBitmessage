"""
Tests for addresbook validation
"""

import unittest
from pybitmessage.bmconfigparser import BMConfigParser


class TestAddAddressBook(unittest.TestCase):
    """this class is used for testting add address feature"""

    def test_is_own_address_add_to_addressbook(self):
        """Check the logic of TCPConnection.local"""
        own_addresses = BMConfigParser().addresses()
        if own_addresses:
            address = own_addresses[0]
        else:
            address = 'BM-2cWiUsWMo4Po2UyNB3VyQdF3gxGrDX9gNm'

        self.assertTrue(address not in own_addresses)
