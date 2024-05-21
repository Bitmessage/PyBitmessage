# pylint: disable=too-few-public-methods

"""
Mock Network
"""


class objectracker(object):
    """Mock object tracker"""

    missingObjects = {}


class stats(object):
    """Mock network statistics"""

    @staticmethod
    def connectedHostsList():
        """Mock list of all the connected hosts"""
        return ["conn1", "conn2", "conn3", "conn4"]

    @staticmethod
    def pendingDownload():
        """Mock pending download count"""
        return 0
