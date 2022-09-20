"""
Storing inventory items
"""

from collections import namedtuple
try:
    from collections import MutableMapping  # pylint: disable=deprecated-class
except ImportError:
    from collections.abc import MutableMapping


InventoryItem = namedtuple('InventoryItem', 'type stream payload expires tag')


class Storage(object):  # pylint: disable=too-few-public-methods
    """Base class for storing inventory
    (extendable for other items to store)"""
    pass


class InventoryStorage(Storage, MutableMapping):
    """Module used for inventory storage"""

    def __init__(self):  # pylint: disable=super-init-not-called
        self.numberOfInventoryLookupsPerformed = 0

    def __contains__(self, _):
        raise NotImplementedError

    def __getitem__(self, _):
        raise NotImplementedError

    def __setitem__(self, _, value):
        raise NotImplementedError

    def __delitem__(self, _):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def by_type_and_tag(self, objectType, tag):
        """Return objects filtered by object type and tag"""
        raise NotImplementedError

    def unexpired_hashes_by_stream(self, stream):
        """Return unexpired inventory vectors filtered by stream"""
        raise NotImplementedError

    def flush(self):
        """Flush cache"""
        raise NotImplementedError

    def clean(self):
        """Free memory / perform garbage collection"""
        raise NotImplementedError


class MailboxStorage(Storage, MutableMapping):
    """Method for storing mails"""

    def __delitem__(self, key):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError
