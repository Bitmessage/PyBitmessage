"""Tests for inventory"""

import os
import shutil
import struct
import tempfile
import time
import unittest

import six

from pybitmessage import highlevelcrypto
from pybitmessage.storage import storage

from .partial import TestPartialRun


class TestFilesystemInventory(TestPartialRun):
    """A test case for the inventory using filesystem backend"""

    @classmethod
    def setUpClass(cls):
        cls.home = os.environ['BITMESSAGE_HOME'] = tempfile.mkdtemp()
        super(TestFilesystemInventory, cls).setUpClass()

        from inventory import create_inventory_instance
        cls.inventory = create_inventory_instance('filesystem')

    def test_consistency(self):
        """Ensure the inventory is of proper class"""
        if os.path.isfile(os.path.join(self.home, 'messages.dat')):
            # this will likely never happen
            self.fail("Failed to configure filesystem inventory!")

    def test_appending(self):
        """Add a sample message to the inventory"""
        TTL = 24 * 60 * 60
        embedded_time = int(time.time() + TTL)
        msg = struct.pack('>Q', embedded_time) + os.urandom(166)
        invhash = highlevelcrypto.calculateInventoryHash(msg)
        self.inventory[invhash] = (2, 1, msg, embedded_time, b'')

    @classmethod
    def tearDownClass(cls):
        super(TestFilesystemInventory, cls).tearDownClass()
        cls.inventory.flush()
        shutil.rmtree(os.path.join(cls.home, cls.inventory.topDir))


class TestStorageAbstract(unittest.TestCase):
    """A test case for refactoring of the storage abstract classes"""

    def test_inventory_storage(self):
        """Check inherited abstract methods"""
        with six.assertRaisesRegex(
            self, TypeError, "^Can't instantiate abstract class.*"
            "methods __contains__, __delitem__, __getitem__, __iter__,"
            " __len__, __setitem__"
        ):  # pylint: disable=abstract-class-instantiated
            storage.InventoryStorage()
