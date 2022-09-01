
import unittest
from pybitmessage.bitmessagekivy.load_kivy_screens_data import load_screen_json
from .common import skip_screen_checks
from .common import ordered


class TestLoadScreenData(unittest.TestCase):
    """Screen Data Json test"""

    @skip_screen_checks
    @ordered
    def test_load_json(self):
        """Test to load a valid json"""
        loaded_screen_names = load_screen_json()
        self.assertEqual(loaded_screen_names[2], 'success')

    @skip_screen_checks
    @ordered
    def test_load_invalid_file(self):
        """Test to load an invalid json"""
        file_name = 'invalid_screens_data.json'
        with self.assertRaises(OSError):
            load_screen_json(file_name)
