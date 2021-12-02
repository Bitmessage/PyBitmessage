"""
`BMConnectionPool` class definition
"""
import logging

import asyncore_pollchoose as asyncore
from bmconfigparser import BMConfigParser
from singleton import Singleton

logger = logging.getLogger('default')

# pylint: disable=too-few-public-methods
@Singleton
class MockBMConnectionPool(object):
    """Pool of all existing connections"""

    def __init__(self):
        self.outboundConnections = {}
        self.inboundConnections = {}
