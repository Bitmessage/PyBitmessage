
import unittest
from binascii import unhexlify
from struct import pack

from pybitmessage import addresses, protocol

from .samples import magic


class TestSerialize(unittest.TestCase):
    """Test serializing and deserializing packet data"""

    def test_varint(self):
        """Test varint encoding and decoding"""
        data = addresses.encodeVarint(0)
        self.assertEqual(data, b'\x00')
        data = addresses.encodeVarint(42)
        self.assertEqual(data, b'*')
        data = addresses.encodeVarint(252)
        self.assertEqual(data, unhexlify('fc'))
        data = addresses.encodeVarint(253)
        self.assertEqual(data, unhexlify('fd00fd'))
        data = addresses.encodeVarint(100500)
        self.assertEqual(data, unhexlify('fe00018894'))
        data = addresses.encodeVarint(65535)
        self.assertEqual(data, unhexlify('fdffff'))
        data = addresses.encodeVarint(4294967295)
        self.assertEqual(data, unhexlify('feffffffff'))
        data = addresses.encodeVarint(4294967296)
        self.assertEqual(data, unhexlify('ff0000000100000000'))
        data = addresses.encodeVarint(18446744073709551615)
        self.assertEqual(data, unhexlify('ffffffffffffffffff'))

        with self.assertRaises(addresses.varintEncodeError):
            addresses.encodeVarint(18446744073709551616)

        value, length = addresses.decodeVarint(b'\xfeaddr')
        self.assertEqual(value, protocol.OBJECT_ADDR)
        self.assertEqual(length, 5)
        value, length = addresses.decodeVarint(b'\xfe\x00tor')
        self.assertEqual(value, protocol.OBJECT_ONIONPEER)
        self.assertEqual(length, 5)

    def test_packet(self):
        """Check the packet created by protocol.CreatePacket()"""
        head = unhexlify(b'%x' % magic)
        self.assertEqual(
            protocol.CreatePacket(b'ping')[:len(head)], head)

    def test_encodehost(self):
        """Check the result of protocol.encodeHost()"""
        self.assertEqual(
            protocol.encodeHost('127.0.0.1'),
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF'
            + pack('>L', 2130706433))
        self.assertEqual(
            protocol.encodeHost('191.168.1.1'),
            unhexlify('00000000000000000000ffffbfa80101'))
        self.assertEqual(
            protocol.encodeHost('1.1.1.1'),
            unhexlify('00000000000000000000ffff01010101'))
        self.assertEqual(
            protocol.encodeHost('0102:0304:0506:0708:090A:0B0C:0D0E:0F10'),
            unhexlify('0102030405060708090a0b0c0d0e0f10'))
        self.assertEqual(
            protocol.encodeHost('quzwelsuziwqgpt2.onion'),
            unhexlify('fd87d87eeb438533622e54ca2d033e7a'))
