"""Tests for inventory"""

import os
import shutil
import struct
import sys
import tempfile
import time
import unittest

from pybitmessage.addresses import calculateInventoryHash

from .partial import TestPartialRun
from .samples import sample_msg_template


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

    @unittest.skipIf(
        sys.hexversion >= 0x3000000, 'item assignment is broken on python3')
    def test_appending(self):
        """Add a sample message to the inventory"""
        TTL = 24 * 60 * 60
        embedded_time = int(time.time() + TTL)
        msg = struct.pack('>Q', embedded_time) + sample_msg_template
        invhash = calculateInventoryHash(msg)
        self.inventory[invhash] = (2, 1, msg, embedded_time, '')

    @classmethod
    def tearDownClass(cls):
        super(TestFilesystemInventory, cls).tearDownClass()
        cls.inventory.flush()
        shutil.rmtree(os.path.join(cls.home, cls.inventory.topDir))
