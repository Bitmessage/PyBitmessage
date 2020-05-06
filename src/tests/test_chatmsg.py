"""
Test for chatmsg group
"""
import unittest
from messagetypes.chatmsg import Chatmsg


class TestCharMessage(unittest.TestCase):
    """
    Test case for chat message group
    """
    def test_decode(self):
        """Test various types of decode method"""
        chat_obj = Chatmsg()
        import messagetypes
        result = messagetypes.constructObject({'': 'chatmsg', 'message': 'hello world'})
        self.assertTrue(isinstance(result.message, str))


    def test_encode(self):
        chat_obj = Chatmsg()
        result = chat_obj.encode({'message':'hello world'})
        self.assertTrue(True if result['message'] else False)
