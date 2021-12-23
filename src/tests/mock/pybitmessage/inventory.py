"""The Inventory singleton"""

# TODO make this dynamic, and watch out for frozen, like with messagetypes
from pybitmessage.singleton import Singleton


# pylint: disable=old-style-class,too-few-public-methods
@Singleton
class Inventory():
    """
    Inventory singleton class which uses storage backends
    to manage the inventory.
    """
    def __init__(self):
        self.numberOfInventoryLookupsPerformed = 0
