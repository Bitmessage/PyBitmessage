# pylint: disable=too-few-public-methods

"""
    Mock Network
"""


class objectracker(object):
    """Mock object tracker"""
    missingObjects = {}


class stats(object):
    """Mock network statics"""
    @staticmethod
    def connectedHostsList():
        """List of all the connected hosts"""
        return ()
