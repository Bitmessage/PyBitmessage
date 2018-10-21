"""
src/inventory.py
================

.. todo:: make imports dynamic, and watch out for frozen, like with messagetypes
"""

import storage.filesystem
import storage.sqlite
from bmconfigparser import BMConfigParser
from singleton import Singleton


@Singleton
class Inventory:
    """Manage an Inventory"""
    # pylint: disable=old-style-class,too-few-public-methods
    def __init__(self):
        self._moduleName = BMConfigParser().safeGet("inventory", "storage")
        self._inventoryClass = getattr(
            getattr(
                storage, self._moduleName), "{}Inventory".format(
                    self._moduleName.title()))
        self._realInventory = self._inventoryClass()
        self.numberOfInventoryLookupsPerformed = 0

    # cheap inheritance copied from asyncore
    def __getattr__(self, attr):
        try:
            if attr == "__contains__":
                self.numberOfInventoryLookupsPerformed += 1
            realRet = getattr(self._realInventory, attr)
        except AttributeError:
            raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, attr))
        else:
            return realRet
