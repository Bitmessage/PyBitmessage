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
        """List of all the mock connected hosts"""
        return [
            "conn1", "conn2", "conn3", "conn4"
        ]
