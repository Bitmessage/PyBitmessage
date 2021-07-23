"""
Tests for common protocol functions
"""

import unittest


class TestProtocol(unittest.TestCase):
    """Main protocol test case"""

    def test_check_local(self):
        """Check the logic of TCPConnection.local"""
        from pybitmessage import protocol, state

        self.assertTrue(
            protocol.checkIPAddress(protocol.encodeHost('127.0.0.1'), True))
        self.assertTrue(
            protocol.checkIPAddress(protocol.encodeHost('192.168.0.1'), True))

        self.assertTrue(
            not protocol.checkSocksIP('127.0.0.1')
            or state.socksIP)
