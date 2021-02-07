import helper_addressbook
from bitmessageqt.support import createAddressIfNeeded

from main import TestBase


class TestAddressbook(TestBase):
    """Test case for addressbook"""

    def test_add_own_address_to_addressbook(self):
        """Checking own address adding in addressbook"""
        try:
            address = createAddressIfNeeded(self.window)
            self.assertFalse(
                helper_addressbook.insert(label='test', address=address))
        except IndexError:
            self.fail("Can't generate addresses")
