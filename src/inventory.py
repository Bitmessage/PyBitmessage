from bmconfigparser import BMConfigParser
from singleton import Singleton

# TODO make this dynamic, and watch out for frozen, like with messagetypes
import storage.sqlite
import storage.filesystem

@Singleton
class Inventory():
    def __init__(self):
        #super(self.__class__, self).__init__()
        self._moduleName = BMConfigParser().safeGet("inventory", "storage")
        self._inventoryClass = getattr(getattr(storage, self._moduleName), "{}Inventory".format(self._moduleName.title()))
        self._realInventory = self._inventoryClass()
        self.numberOfInventoryLookupsPerformed = 0

    # cheap inheritance copied from asyncore
    def __getattr__(self, attr):
        try:
            if attr == "__contains__":
                self.numberOfInventoryLookupsPerformed += 1
            realRet = getattr(self._realInventory, attr)
        except AttributeError:
            raise AttributeError("%s instance has no attribute '%s'" %(self.__class__.__name__, attr))
        else:
            return realRet
