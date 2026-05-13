"""Tests for SqliteInventory.flush()"""
# pylint: disable=protected-access,wrong-import-order,wrong-import-position
# pylint: disable=import-outside-toplevel

import os
import tempfile
import threading
import time

from .common import skip_python3
from .partial import TestPartialRun

skip_python3()


class TestInventoryFlush(TestPartialRun):
    """
    Integration test: exercises flush() end-to-end with the real sqlThread
    consumer running, so that type errors in parameter binding surface here
    rather than silently killing a production thread.
    """

    @classmethod
    def setUpClass(cls):
        os.environ['BITMESSAGE_HOME'] = tempfile.gettempdir()
        super(TestInventoryFlush, cls).setUpClass()

        import helper_sql
        from bmconfigparser import config, config_ready
        from class_sqlThread import sqlThread
        from helper_startup import LATEST_SETTINGS_VERSION
        from storage.sqlite import SqliteInventory

        cls._sqlStoredProcedure = staticmethod(helper_sql.sqlStoredProcedure)

        # sqlThread.run() waits on config_ready and then reads
        # settingsversion; normally helper_startup.loadConfig() handles
        # both, but TestPartialRun only calls config.read() which loads
        # default.ini (no settingsversion).  Set the minimum the
        # sqlThread needs so it can initialise the database.
        if not config.has_option(
                'bitmessagesettings', 'settingsversion'):
            config.set(
                'bitmessagesettings', 'settingsversion',
                str(LATEST_SETTINGS_VERSION))
        config_ready.set()

        # test_api_thread replaces helper_sql.sql_ready with a mock
        # that only has wait(); restore a real Event so sqlThread can
        # call .set() on it.  In Python 2 threading.Event is a factory
        # function, not a class, so we duck-type the check.
        cls._original_sql_ready = helper_sql.sql_ready
        if not hasattr(helper_sql.sql_ready, 'set'):
            helper_sql.sql_ready = threading.Event()

        sql_lookup = sqlThread()
        sql_lookup.daemon = True
        sql_lookup.start()
        helper_sql.sql_ready.wait()
        cls.inventory = SqliteInventory()

    @classmethod
    def tearDownClass(cls):
        import helper_sql
        from bmconfigparser import config_ready

        cls._sqlStoredProcedure('exit')
        for thread in threading.enumerate():
            if thread.name == "SQL":
                thread.join(timeout=10)
        helper_sql.sql_ready = cls._original_sql_ready
        # Reset config to default.ini so added settingsversion does
        # not leak into subsequent tests.  Also clear config_ready
        # since it is a one-shot event set by loadConfig().
        cls.config.read()
        config_ready.clear()
        super(TestInventoryFlush, cls).tearDownClass()

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _make_hash(seed):
        """Return a 32-byte hash derived from *seed*."""
        return (b'\x00' * 31 + bytes([seed & 0xFF]))[-32:]

    def _flush_and_check(self, obj_hash, expected_payload=None):
        """
        Flush the inventory to the database, clear both in-memory
        caches so that __contains__ and __getitem__ are forced to
        hit sqlite, then verify the hash is found and (optionally)
        that the payload content survived the round-trip.
        """
        self.inventory.flush()
        self.inventory._objects.clear()
        self.assertIn(obj_hash, self.inventory)
        if expected_payload is not None:
            value = self.inventory[obj_hash]
            self.assertEqual(
                bytes(value.payload), expected_payload,
                "Payload content corrupted after flush")

    # -- test cases -------------------------------------------------------

    def test_flush_payload_roundtrip(self):
        """Payload content must survive the flush round-trip."""
        h = self._make_hash(1)
        payload = b'\x80\x01' + os.urandom(64)
        self.inventory[h] = (
            2, 1, payload,
            int(time.time()) + 3600, b'\xff' * 32)
        self._flush_and_check(h, payload)

    def test_flush_with_empty_tag(self):
        """Empty tag (b'') must not break the INSERT."""
        h = self._make_hash(2)
        payload = b'\x80\x02' + os.urandom(64)
        self.inventory[h] = (
            2, 1, payload,
            int(time.time()) + 3600, b'')
        self._flush_and_check(h, payload)

    def test_flush_multiple_items(self):
        """Flush a batch and verify every row arrives."""
        count = 20
        hashes = [self._make_hash(0x10 + i) for i in range(count)]
        expires = int(time.time()) + 3600

        for i, h in enumerate(hashes):
            self.inventory[h] = (
                2, 1, os.urandom(64), expires, b'\x00' * 32)

        self.inventory.flush()
        self.inventory._objects.clear()

        for i, h in enumerate(hashes):
            self.assertIn(
                h, self.inventory,
                "Item {} missing after batch flush".format(i))

    def test_flush_clears_memory_cache(self):
        """After flush the in-memory _inventory dict must be empty."""
        h = self._make_hash(0xF0)
        self.inventory[h] = (
            2, 1, b'\x00' * 32, int(time.time()) + 3600, b'')
        self.inventory.flush()
        self.assertEqual(len(self.inventory._inventory), 0)
