"""
src/storage/storage.py
======================
"""

import collections

InventoryItem = collections.namedtuple('InventoryItem', 'type stream payload expires tag')


class InventoryStorage(collections.MutableMapping):
    """"""

    def __init__(self):
        # pylint: disable=super-init-not-called
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
        """"""
        raise NotImplementedError

    def unexpired_hashes_by_stream(self, stream):
        """"""
        raise NotImplementedError

    def flush(self):
        """"""
        raise NotImplementedError

    def clean(self):
        """"""
        raise NotImplementedError


class MailboxStorage(collections.MutableMapping):  # pylint: disable=abstract-method,no-init
    """"""
    pass
