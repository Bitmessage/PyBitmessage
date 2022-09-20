"""
Storing inventory items
"""

from abc import abstractmethod
from collections import namedtuple
try:
    from collections import MutableMapping  # pylint: disable=deprecated-class
except ImportError:
    from collections.abc import MutableMapping


InventoryItem = namedtuple('InventoryItem', 'type stream payload expires tag')


class InventoryStorage(MutableMapping):
    """
    Base class for storing inventory
    (extendable for other items to store)
    """

    def __init__(self):
        self.numberOfInventoryLookupsPerformed = 0

    @abstractmethod
    def __contains__(self, item):
        pass

    @abstractmethod
    def by_type_and_tag(self, objectType, tag):
        """Return objects filtered by object type and tag"""
        pass

    @abstractmethod
    def unexpired_hashes_by_stream(self, stream):
        """Return unexpired inventory vectors filtered by stream"""
        pass

    @abstractmethod
    def flush(self):
        """Flush cache"""
        pass

    @abstractmethod
    def clean(self):
        """Free memory / perform garbage collection"""
        pass


class MailboxStorage(MutableMapping):
    """An abstract class for storing mails. TODO"""
    pass
