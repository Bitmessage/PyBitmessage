"""
Tests for common protocol functions
"""

import sys
import unittest

from pybitmessage import protocol, state
from pybitmessage.helper_startup import fixSocket


class TestProtocol(unittest.TestCase):
    """Main protocol test case"""

    @classmethod
    def setUpClass(cls):
        """Execute fixSocket() before start. Only for Windows?"""
        fixSocket()

    def test_checkIPv4Address(self):
        """Check the results of protocol.checkIPv4Address()"""
        token = 'HELLO'
        # checking protocol.encodeHost()[12:]
        self.assertEqual(  # 127.0.0.1
            token, protocol.checkIPv4Address(b'\x7f\x00\x00\x01', token, True))
        self.assertFalse(
            protocol.checkIPv4Address(b'\x7f\x00\x00\x01', token))
        self.assertEqual(  # 10.42.43.1
            token, protocol.checkIPv4Address(b'\n*+\x01', token, True))
        self.assertFalse(
            protocol.checkIPv4Address(b'\n*+\x01', token, False))
        self.assertEqual(  # 192.168.0.254
            token, protocol.checkIPv4Address(b'\xc0\xa8\x00\xfe', token, True))
        self.assertEqual(  # 172.31.255.254
            token, protocol.checkIPv4Address(b'\xac\x1f\xff\xfe', token, True))
        # self.assertEqual(  # 169.254.1.1
        #     token, protocol.checkIPv4Address(b'\xa9\xfe\x01\x01', token, True))
        # self.assertEqual(  # 254.128.1.1
        #     token, protocol.checkIPv4Address(b'\xfe\x80\x01\x01', token, True))
        self.assertFalse(  # 8.8.8.8
            protocol.checkIPv4Address(b'\x08\x08\x08\x08', token, True))

    def test_checkIPv6Address(self):
        """Check the results of protocol.checkIPv6Address()"""
        test_ip = '2001:db8::ff00:42:8329'
        self.assertEqual(
            'test', protocol.checkIPv6Address(
                protocol.encodeHost(test_ip), 'test'))
        self.assertFalse(
            protocol.checkIPv6Address(
                protocol.encodeHost(test_ip), 'test', True))
        for test_ip in ('fe80::200:5aee:feaa:20a2', 'fdf8:f53b:82e4::53'):
            self.assertEqual(
                'test', protocol.checkIPv6Address(
                    protocol.encodeHost(test_ip), 'test', True))
            self.assertFalse(
                protocol.checkIPv6Address(
                    protocol.encodeHost(test_ip), 'test'))

    def test_check_local(self):
        """Check the logic of TCPConnection.local"""
        self.assertTrue(
            protocol.checkIPAddress(protocol.encodeHost('127.0.0.1'), True))
        self.assertTrue(
            protocol.checkIPAddress(protocol.encodeHost('192.168.0.1'), True))
        self.assertTrue(
            protocol.checkIPAddress(protocol.encodeHost('10.42.43.1'), True))
        self.assertTrue(
            protocol.checkIPAddress(protocol.encodeHost('172.31.255.2'), True))
        self.assertFalse(protocol.checkIPAddress(
            protocol.encodeHost('2001:db8::ff00:42:8329'), True))

        globalhost = protocol.encodeHost('8.8.8.8')
        self.assertFalse(protocol.checkIPAddress(globalhost, True))
        self.assertEqual(protocol.checkIPAddress(globalhost), '8.8.8.8')

    @unittest.skipIf(
        sys.hexversion >= 0x3000000, 'this is still not working with python3')
    def test_check_local_socks(self):
        """The SOCKS part of the local check"""
        self.assertTrue(
            not protocol.checkSocksIP('127.0.0.1')
            or state.socksIP)

    def test_network_group(self):
        """Test various types of network groups"""

        test_ip = '1.2.3.4'
        self.assertEqual(b'\x01\x02', protocol.network_group(test_ip))

        test_ip = '127.0.0.1'
        self.assertEqual('IPv4', protocol.network_group(test_ip))

        self.assertEqual(
            protocol.network_group('8.8.8.8'),
            protocol.network_group('8.8.4.4'))
        self.assertNotEqual(
            protocol.network_group('1.1.1.1'),
            protocol.network_group('8.8.8.8'))

        test_ip = '0102:0304:0506:0708:090A:0B0C:0D0E:0F10'
        self.assertEqual(
            b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C',
            protocol.network_group(test_ip))

        for test_ip in (
                'bootstrap8444.bitmessage.org', 'quzwelsuziwqgpt2.onion', None):
            self.assertEqual(
                test_ip, protocol.network_group(test_ip))
