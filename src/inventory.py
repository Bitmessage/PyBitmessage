"""The Inventory"""

# TODO make this dynamic, and watch out for frozen, like with messagetypes
import storage.filesystem
import storage.sqlite
from bmconfigparser import config


def create_inventory_instance(backend="sqlite"):
    """
    Create an instance of the inventory class
    defined in `storage.<backend>`.
    """
    return getattr(
        getattr(storage, backend),
        "{}Inventory".format(backend.title()))()


class Inventory(object):
    """
    Inventory class which uses storage backends
    to manage the inventory.
    """
    def __init__(self):
        self._moduleName = config.safeGet("inventory", "storage")
        self._realInventory = create_inventory_instance(self._moduleName)
        self.numberOfInventoryLookupsPerformed = 0

    def __getattr__(self, attr):
        """cheap inheritance copied from asyncore"""
        if attr == "__contains__":
            self.numberOfInventoryLookupsPerformed += 1
        try:
            realRet = getattr(self._realInventory, attr)
        except AttributeError:
            raise AttributeError(
                "%s instance has no attribute '%s'" %
                (self.__class__.__name__, attr)
            )
        else:
            return realRet

    def __contains__(self, key):
        """
        Look up inventory item by hash.
        This method is needed due to how new-style classes work.
        """
        self.numberOfInventoryLookupsPerformed += 1
        return key in self._realInventory

    def __getitem__(self, key):
        """hint for pylint, this is dictionary like object"""
        return self._realInventory[key]

    def __setitem__(self, key, value):
        self._realInventory[key] = value
