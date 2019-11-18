"""
Test for network group
"""
import unittest


class TestNetworkGroup(unittest.TestCase):
    """
    Test case for network group
    """
    def test_network_group(self):
        """Test various types of network groups"""
        from pybitmessage.protocol import network_group

        test_ip = '1.2.3.4'
        self.assertEqual('\x01\x02', network_group(test_ip))

        test_ip = '127.0.0.1'
        self.assertEqual('IPv4', network_group(test_ip))

        test_ip = '0102:0304:0506:0708:090A:0B0C:0D0E:0F10'
        self.assertEqual(
            '\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C',
            network_group(test_ip))

        test_ip = 'bootstrap8444.bitmessage.org'
        self.assertEqual(
            'bootstrap8444.bitmessage.org',
            network_group(test_ip))

        test_ip = 'quzwelsuziwqgpt2.onion'
        self.assertEqual(
            test_ip,
            network_group(test_ip))

        test_ip = None
        self.assertEqual(
            None,
            network_group(test_ip))
