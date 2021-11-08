"""Tests for messagetypes module"""
import unittest

from six import text_type

from pybitmessage import messagetypes

sample_data = {"": "message", "subject": "subject", "body": "body"}
invalid_data = {"": "message", "subject": b"\x01\x02\x03", "body": b"\x01\x02\x03\x04"}


class TestMessageTypes(unittest.TestCase):
    """A test case for messagetypes"""

    def test_msg_encode(self):
        """Test msg encode"""
        msgObj = messagetypes.message.Message()
        encoded_message = msgObj.encode(sample_data)
        self.assertEqual(type(encoded_message), dict)
        self.assertEqual(encoded_message["subject"], sample_data["subject"])
        self.assertEqual(encoded_message["body"], sample_data["body"])

    def test_msg_decode(self):
        """Test msg decode"""
        msgObj = messagetypes.constructObject(sample_data)
        self.assertEqual(msgObj.subject, sample_data["subject"])
        self.assertEqual(msgObj.body, sample_data["body"])

    def test_invalid_data_type(self):
        """Test invalid data type"""
        msgObj = messagetypes.constructObject(invalid_data)
        self.assertTrue(isinstance(msgObj.subject, text_type))
        self.assertTrue(isinstance(msgObj.body, text_type))

    def test_msg_process(self):
        """Test msg process"""
        msgObj = messagetypes.constructObject(sample_data)
        self.assertTrue(isinstance(msgObj, messagetypes.message.Message))
        self.assertIsNone(msgObj.process())
