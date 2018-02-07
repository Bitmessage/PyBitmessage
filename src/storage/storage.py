import collections

InventoryItem = collections.namedtuple('InventoryItem', 'type stream payload expires tag')

class Storage(object):
    pass
#    def __init__(self):
#        super(self.__class__, self).__init__()

class InventoryStorage(Storage, collections.MutableMapping):
    def __init__(self):
#        super(self.__class__, self).__init__()
        self.numberOfInventoryLookupsPerformed = 0

    def __contains__(self, hash):
        raise NotImplementedError

    def __getitem__(self, hash):
        raise NotImplementedError

    def __setitem__(self, hash, value):
        raise NotImplementedError

    def __delitem__(self, hash):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def by_type_and_tag(self, objectType, tag):
        raise NotImplementedError

    def unexpired_hashes_by_stream(self, stream):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def clean(self):
        raise NotImplementedError

class MailboxStorage(Storage, collections.MutableMapping):
    def __init__(self):
#        super(self.__class__, self).__init__()
        pass
