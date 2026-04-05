# pylint: disable=too-few-public-methods

"""
Mock Network
"""


class objectracker(object):
    """Mock object tracker"""

    missingObjects = {}


class stats(object):
    """Mock network statistics"""

    pool = None

    @staticmethod
    def init(pool_instance):
        """Mock init with pool reference"""
        stats.pool = pool_instance

    @staticmethod
    def connectedHostsList():
        """Mock list of all the connected hosts"""
        return ["conn1", "conn2", "conn3", "conn4"]

    @staticmethod
    def sentBytes():
        """Mock sent bytes"""
        return 1

    @staticmethod
    def receivedBytes():
        """Mock received bytes"""
        return 1

    @staticmethod
    def pendingDownload():
        """Mock pending download count"""
        return 0
