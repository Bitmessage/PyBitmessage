"""
`BMConnectionPool` class definition
"""
import logging

import asyncore_pollchoose as asyncore
from bmconfigparser import BMConfigParser
from singleton import Singleton

logger = logging.getLogger('default')


@Singleton
class MockBMConnectionPool(object):
    """Pool of all existing connections"""

    def __init__(self):
        asyncore.set_rates(
            BMConfigParser().safeGetInt(
                "bitmessagesettings", "maxdownloadrate"),
            BMConfigParser().safeGetInt(
                "bitmessagesettings", "maxuploadrate")
        )
        self.outboundConnections = {}
        self.inboundConnections = {}
