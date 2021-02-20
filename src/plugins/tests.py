import unittest
from importlib import import_module

try:
    import pkg_resources
except ImportError:
    pkg_resources = None


class TestPlugins(unittest.TestCase):
    """Test case for plugins package"""
    def test_get_plugin(self):
        """Import from plugin raises ImportError without pkg_resources"""
        if pkg_resources is None:
            with self.assertRaises(ImportError):
                import_module('plugin')
